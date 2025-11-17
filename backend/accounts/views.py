from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, RegistrationKey
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer
from patients.models import Patient, MedicalRecord, PatientDoctorRelation, Case, CaseMessage, MessageReaction
from django.http import JsonResponse
from hospitals.models import Hospital
from django.core.management import call_command
from django.utils import timezone
import json
from pathlib import Path
from datetime import date


def get_patient_queryset(user):
    """Получить queryset пациентов в зависимости от роли пользователя."""
    if user.role == 'superadmin':
        return Patient.objects.all()
    elif user.role == 'hospital_admin':
        return Patient.objects.filter(hospital=user.hospital)
    else:  # doctor
        return Patient.objects.filter(
            treating_doctors__doctor=user,
            treating_doctors__is_active=True
        ).distinct()


def get_medical_record_queryset(user):
    """Получить queryset медицинских карточек в зависимости от роли пользователя."""
    if user.role == 'superadmin':
        return MedicalRecord.objects.all()
    elif user.role == 'hospital_admin':
        return MedicalRecord.objects.filter(patient__hospital=user.hospital)
    else:  # doctor
        return MedicalRecord.objects.filter(doctor=user)


@login_required
def cabinet_view(request):
    """Личный кабинет врача - HTML страница."""
    user = request.user
    
    patients_queryset = get_patient_queryset(user)
    records_queryset = get_medical_record_queryset(user)
    
    # Консилиумы врача
    cases_queryset = Case.objects.filter(doctors=user).select_related('patient', 'created_by').prefetch_related('doctors')
    
    # Статистика
    total_patients = patients_queryset.count()
    total_records = records_queryset.count()
    total_cases = cases_queryset.count()
    active_cases = cases_queryset.filter(status__in=['urgent', 'monitoring']).count()
    
    # Общее количество непрочитанных сообщений
    total_unread = 0
    for case in cases_queryset:
        total_unread += case.get_unread_count(user)
    
    # Последние 5 консилиумов
    recent_cases = []
    for case in cases_queryset[:5]:
        recent_cases.append({
            'case': case,
            'unread_count': case.get_unread_count(user),
        })
    
    # Все пациенты
    all_patients = list(patients_queryset.select_related('hospital'))
    
    # Последние 5 карточек
    recent_records = list(records_queryset.select_related('patient', 'doctor')[:5])
    
    context = {
        'user': user,
        'total_patients': total_patients,
        'total_records': total_records,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'total_unread': total_unread,
        'recent_cases': recent_cases,
        'all_patients': all_patients,
        'recent_records': recent_records,
    }
    
    return render(request, 'accounts/cabinet.html', context)


@login_required
def cases_view(request):
    """Страница 'Мои консилиумы'."""
    user = request.user
    
    # Все консилиумы врача
    cases_queryset = Case.objects.filter(doctors=user).select_related('patient', 'created_by').prefetch_related('doctors')
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status', '')
    if status_filter:
        cases_queryset = cases_queryset.filter(status=status_filter)
    
    # Подготовка данных для шаблона
    cases_data = []
    for case in cases_queryset:
        cases_data.append({
            'case': case,
            'unread_count': case.get_unread_count(user),
            'doctors': case.doctors.all()[:3],  # Первые 3 врача для аватаров
        })
    
    context = {
        'user': user,
        'cases': cases_data,
        'status_filter': status_filter,
        'total_cases': cases_queryset.count(),
    }
    
    return render(request, 'accounts/cases.html', context)


def load_consilium_templates():
    """Загрузить шаблоны консилиумов из JSON файла."""
    templates_path = Path(__file__).parent.parent / 'patients' / 'consilium_templates.json'
    try:
        with open(templates_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return []


@login_required
def create_case_view(request):
    """Создание нового консилиума."""
    user = request.user
    
    # Загружаем шаблоны
    templates = load_consilium_templates()
    
    # Получаем список пациентов врача
    patients_queryset = get_patient_queryset(user)
    patients_list = list(patients_queryset)
    
    # Получаем список всех врачей для выбора участников
    all_doctors = User.objects.filter(role__in=['doctor', 'hospital_admin', 'superadmin']).exclude(id=user.id)
    
    if request.method == 'POST':
        # Получаем данные из формы
        patient_id = request.POST.get('patient')
        template_id = request.POST.get('template_id')
        diagnosis = request.POST.get('diagnosis', '').strip()
        description = request.POST.get('description', '').strip()
        status = request.POST.get('status', 'monitoring')
        admission_date = request.POST.get('admission_date')
        selected_doctors = request.POST.getlist('doctors')
        
        # Валидация
        errors = {}
        
        if not patient_id:
            errors['patient'] = 'Необходимо выбрать пациента'
        else:
            try:
                patient = Patient.objects.get(id=patient_id)
                # Проверяем доступ к пациенту
                if user.role == 'doctor' and patient not in patients_queryset:
                    errors['patient'] = 'У вас нет доступа к этому пациенту'
            except Patient.DoesNotExist:
                errors['patient'] = 'Пациент не найден'
        
        if not diagnosis:
            errors['diagnosis'] = 'Диагноз обязателен'
        
        if not description:
            errors['description'] = 'Описание случая обязательно'
        
        if not admission_date:
            errors['admission_date'] = 'Дата поступления обязательна'
        
        if not selected_doctors:
            errors['doctors'] = 'Необходимо выбрать хотя бы одного врача'
        
        if errors:
            import json as json_module
            context = {
                'templates': json_module.dumps(templates, ensure_ascii=False),
                'templates_list': templates,
                'patients': patients_list,
                'all_doctors': all_doctors,
                'errors': errors,
                'form_data': request.POST,
            }
            return render(request, 'accounts/create_case.html', context)
        
        # Создаем консилиум
        try:
            case = Case.objects.create(
                patient=patient,
                created_by=user,
                diagnosis=diagnosis,
                description=description,
                status=status,
                admission_date=admission_date
            )
            
            # Добавляем врачей (включая создателя)
            doctors_to_add = [user]
            for doctor_id in selected_doctors:
                try:
                    doctor = User.objects.get(id=doctor_id)
                    doctors_to_add.append(doctor)
                except User.DoesNotExist:
                    pass
            
            case.doctors.set(doctors_to_add)
            
            messages.success(request, 'Консилиум успешно создан!')
            return redirect('accounts:case_detail', case_id=case.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при создании консилиума: {str(e)}')
            import json as json_module
            context = {
                'templates': json_module.dumps(templates, ensure_ascii=False),
                'templates_list': templates,
                'patients': patients_list,
                'all_doctors': all_doctors,
                'errors': {'general': 'Ошибка при создании консилиума'},
                'form_data': request.POST,
            }
            return render(request, 'accounts/create_case.html', context)
    
    # GET запрос - показываем форму
    import json as json_module
    context = {
        'templates': json_module.dumps(templates, ensure_ascii=False),
        'templates_list': templates,  # Для отображения в шаблоне
        'patients': patients_list,
        'all_doctors': all_doctors,
    }
    return render(request, 'accounts/create_case.html', context)


@login_required
def case_detail_view(request, case_id):
    """Детальная страница консилиума с чатом."""
    user = request.user
    
    try:
        case = Case.objects.prefetch_related('doctors', 'messages__author').get(id=case_id)
    except Case.DoesNotExist:
        messages.error(request, 'Консилиум не найден.')
        return redirect('accounts:cases')
    
    # Проверка доступа: завершенные консилиумы доступны всем врачам, активные - только участникам
    if case.status != 'stable':
        # Для активных консилиумов проверяем участие
        has_access = False
        
        if user.role == 'superadmin':
            has_access = True
        elif user.role == 'hospital_admin' and user.hospital:
            # Администратор больницы может видеть консилиумы врачей своей больницы
            if case.patient and case.patient.hospital == user.hospital:
                has_access = True
            elif case.doctors.filter(hospital=user.hospital).exists():
                has_access = True
            elif case.created_by and case.created_by.hospital == user.hospital:
                has_access = True
        elif user in case.doctors.all() or case.created_by == user:
            # Участник или создатель
            has_access = True
        
        if not has_access:
            messages.error(request, 'У вас нет доступа к этому консилиуму.')
            return redirect('accounts:cases')
    
    # Гарантируем, что создатель присутствует среди участников
    try:
        if case.created_by and case.created_by not in case.doctors.all():
            case.doctors.add(case.created_by)
    except Exception:
        pass
    
    # Обработка отправки сообщения
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            CaseMessage.objects.create(
                case=case,
                author=user,
                content=content,
                is_read=False
            )
            messages.success(request, 'Сообщение отправлено.')
            return redirect('accounts:case_detail', case_id=case_id)
        else:
            messages.error(request, 'Сообщение не может быть пустым.')
    
    # Получаем все сообщения с реакциями
    messages_list = case.messages.all().select_related('author').prefetch_related('reactions__user')
    
    # Помечаем сообщения как прочитанные (кроме своих)
    for msg in messages_list:
        if msg.author != user and not msg.is_read:
            msg.is_read = True
            msg.save()
    
    # Подготовка данных для шаблона
    messages_data = []
    for msg in messages_list:
        # Группируем реакции по типу
        reactions_by_type = {}
        user_reactions = []
        for reaction in msg.reactions.all():
            if reaction.reaction not in reactions_by_type:
                reactions_by_type[reaction.reaction] = []
            reactions_by_type[reaction.reaction].append(reaction.user.email)
            if reaction.user == user:
                user_reactions.append(reaction.reaction)
        
        messages_data.append({
            'message': msg,
            'is_own': msg.author == user,
            'reactions': reactions_by_type,
            'user_reactions': user_reactions,
        })
    
    # Проверяем, может ли пользователь завершить консилиум
    can_complete = False
    if case.status != 'stable':
        if user.role == 'superadmin':
            can_complete = True
        elif user.role == 'hospital_admin' and user.hospital:
            # Администратор больницы может завершить консилиумы врачей своей больницы
            if case.patient and case.patient.hospital == user.hospital:
                can_complete = True
            elif case.doctors.filter(hospital=user.hospital).exists():
                can_complete = True
            elif case.created_by and case.created_by.hospital == user.hospital:
                can_complete = True
        elif user in case.doctors.all() or case.created_by == user:
            # Участник или создатель
            can_complete = True
    
    context = {
        'user': user,
        'case': case,
        'messages': messages_data,
        'doctors': list(case.doctors.all().order_by('email')),
        'unread_count': case.get_unread_count(user),
        'can_complete': can_complete,
    }
    
    return render(request, 'accounts/case_detail.html', context)


@login_required
def manage_patient_doctors_view(request, patient_id):
    """Управление связями пациент-врач."""
    user = request.user
    
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, 'Пациент не найден.')
        return redirect('accounts:cabinet')
    
    # Проверка доступа
    if user.role == 'doctor':
        # Врач может управлять только своими пациентами
        if not PatientDoctorRelation.objects.filter(patient=patient, doctor=user, is_active=True).exists():
            messages.error(request, 'У вас нет доступа к этому пациенту.')
            return redirect('accounts:cabinet')
    elif user.role == 'hospital_admin':
        # Админ больницы может управлять пациентами своей больницы
        if patient.hospital != user.hospital:
            messages.error(request, 'У вас нет доступа к этому пациенту.')
            return redirect('accounts:cabinet')
    # superadmin имеет доступ ко всем
    
    # Получаем текущих врачей пациента
    current_relations = PatientDoctorRelation.objects.filter(patient=patient, is_active=True).select_related('doctor')
    current_doctors = [rel.doctor for rel in current_relations]
    
    # Получаем всех доступных врачей
    if user.role == 'superadmin':
        available_doctors = User.objects.filter(role__in=['doctor', 'hospital_admin', 'superadmin'])
    elif user.role == 'hospital_admin':
        available_doctors = User.objects.filter(
            role__in=['doctor', 'hospital_admin'],
            hospital=user.hospital
        )
    else:  # doctor
        available_doctors = User.objects.filter(
            role__in=['doctor', 'hospital_admin'],
            hospital=user.hospital
        ) if user.hospital else User.objects.filter(role='doctor')
    
    # Исключаем уже назначенных врачей
    available_doctors = available_doctors.exclude(id__in=[d.id for d in current_doctors])
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add':
            doctor_id = request.POST.get('doctor_id')
            try:
                doctor = User.objects.get(id=doctor_id)
                # Проверяем, что врач доступен
                if doctor not in available_doctors:
                    messages.error(request, 'Невозможно добавить этого врача.')
                    return redirect('accounts:manage_patient_doctors', patient_id=patient_id)
                
                # Создаем или активируем связь
                relation, created = PatientDoctorRelation.objects.get_or_create(
                    patient=patient,
                    doctor=doctor,
                    defaults={'is_active': True}
                )
                if not created and not relation.is_active:
                    relation.is_active = True
                    relation.save()
                
                messages.success(request, f'Врач {doctor.email} добавлен к пациенту.')
            except User.DoesNotExist:
                messages.error(request, 'Врач не найден.')
        
        elif action == 'remove':
            relation_id = request.POST.get('relation_id')
            try:
                relation = PatientDoctorRelation.objects.get(id=relation_id, patient=patient)
                # Нельзя удалить связь, если это единственный врач
                if PatientDoctorRelation.objects.filter(patient=patient, is_active=True).count() <= 1:
                    messages.error(request, 'Нельзя удалить последнего врача у пациента.')
                else:
                    relation.is_active = False
                    relation.save()
                    messages.success(request, 'Врач удален из списка лечащих врачей.')
            except PatientDoctorRelation.DoesNotExist:
                messages.error(request, 'Связь не найдена.')
        
        return redirect('accounts:manage_patient_doctors', patient_id=patient_id)
    
    context = {
        'patient': patient,
        'current_relations': current_relations,
        'available_doctors': available_doctors,
    }
    
    return render(request, 'accounts/manage_patient_doctors.html', context)


@login_required
def toggle_reaction_view(request, message_id):
    """Добавить или удалить реакцию на сообщение (AJAX)."""
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        message = CaseMessage.objects.get(id=message_id)
        # Проверяем, что пользователь имеет доступ к консилиуму
        if request.user not in message.case.doctors.all():
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        reaction_type = request.POST.get('reaction', '').strip()
        
        if reaction_type not in ['👍', '👎']:
            return JsonResponse({'error': 'Invalid reaction'}, status=400)
        
        # Проверяем, есть ли уже такая реакция от этого пользователя
        existing_reaction = MessageReaction.objects.filter(
            message=message,
            user=request.user,
            reaction=reaction_type
        ).first()
        
        if existing_reaction:
            # Удаляем реакцию
            existing_reaction.delete()
            action = 'removed'
        else:
            # Добавляем реакцию
            MessageReaction.objects.create(
                message=message,
                user=request.user,
                reaction=reaction_type
            )
            action = 'added'
        
        # Получаем обновленные реакции
        reactions_by_type = {}
        user_reactions = []
        for reaction in message.reactions.all():
            if reaction.reaction not in reactions_by_type:
                reactions_by_type[reaction.reaction] = []
            reactions_by_type[reaction.reaction].append(reaction.user.email)
            if reaction.user == request.user:
                user_reactions.append(reaction.reaction)
        
        # Преобразуем в формат для JSON (список email'ов)
        reactions_json = {}
        for reaction_type, users in reactions_by_type.items():
            reactions_json[reaction_type] = users
        
        return JsonResponse({
            'success': True,
            'action': action,
            'reactions': reactions_json,
            'user_reactions': user_reactions,
        })
        
    except CaseMessage.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def delete_all_cases_view(request):
    """Удалить все консилиумы (только суперАдмин)."""
    user = request.user
    if user.role != 'superadmin':
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        MessageReaction.objects.all().delete()
        CaseMessage.objects.all().delete()
        Case.objects.all().delete()
        messages.success(request, 'Все консилиумы удалены.')
        return redirect('accounts:cabinet')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')


@login_required
def delete_my_cases_view(request):
    """Удалить все консилиумы текущего пользователя (для суперАдмина, админа больницы и врача)."""
    user = request.user
    if user.role not in ['superadmin', 'hospital_admin', 'doctor']:
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        from django.db.models import Q
        my_cases_qs = Case.objects.filter(Q(doctors=user) | Q(created_by=user)).order_by().distinct()
        my_cases_ids = list(my_cases_qs.values_list('id', flat=True))
        # Удаляем сначала реакции, потом сообщения, затем кейсы
        MessageReaction.objects.filter(message__case_id__in=my_cases_ids).delete()
        CaseMessage.objects.filter(case_id__in=my_cases_ids).delete()
        deleted_count = len(my_cases_ids)
        Case.objects.filter(id__in=my_cases_ids).delete()
        messages.success(request, f'Удалено моих консилиумов: {deleted_count}.')
        return redirect('accounts:cabinet')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')

@login_required
def generate_patients_view(request):
    """Сгенерировать тестовых пациентов (по умолчанию 5).
    
    Права:
    - superadmin: может генерировать (жестко ограничено 5), без привязки к врачу
    - hospital_admin: может генерировать (количество из запроса), пациенты привязываются к его больнице
    - doctor: недоступно
    """
    user = request.user
    if user.role not in ['superadmin', 'hospital_admin']:
        messages.error(request, 'Недостаточно прав для генерации пациентов.')
        return redirect('accounts:cabinet')
    
    requested_count = int(request.GET.get('count', '5'))
    if user.role == 'superadmin':
        count = 5  # жесткий лимит
    else:
        count = max(1, requested_count)
    
    base_num = Patient.objects.count() + 1
    created = 0
    for i in range(count):
        Patient.objects.create(
            first_name=f'Тест_{base_num + i}',
            last_name='Пациент',
            middle_name='Демо',
            date_of_birth=date(1980 + (i % 30), (i % 12) + 1, min(28, (i % 28) + 1)),
            gender='male' if i % 2 == 0 else 'female',
            phone=f'+7000000{base_num + i:04d}',
            email=f'demo_{base_num + i}@example.com',
            hospital=user.hospital if user.role == 'hospital_admin' else None,
        )
        created += 1
    messages.success(request, f'Сгенерировано пациентов: {created}.')
    return redirect('accounts:cabinet')


@login_required
def clear_my_patients_view(request):
    """Очистить всех пациентов у текущего врача (деактивировать связи)."""
    user = request.user
    if user.role != 'doctor':
        messages.error(request, 'Доступно только для врачей.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        PatientDoctorRelation.objects.filter(doctor=user, is_active=True).update(is_active=False)
        messages.success(request, 'Все текущие пациенты отвязаны от вас.')
        return redirect('accounts:cabinet')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')


@login_required
def import_emias_patients_view(request):
    """Выгрузить пациентов из ЕМИАС (генерирует 3 пациента и привязывает к текущему врачу)."""
    user = request.user
    if user.role != 'doctor':
        messages.error(request, 'Доступно только для врачей.')
        return redirect('accounts:my_patients')
    
    if request.method == 'POST':
        from datetime import date, timedelta
        import random
        
        # Русские имена и фамилии
        first_names_male = ['Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей']
        first_names_female = ['Анна', 'Мария', 'Елена', 'Наталья', 'Ольга']
        last_names = ['Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов']
        middle_names_male = ['Александрович', 'Дмитриевич', 'Максимович', 'Сергеевич', 'Андреевич']
        middle_names_female = ['Александровна', 'Дмитриевна', 'Максимовна', 'Сергеевна', 'Андреевна']
        
        created_count = 0
        base_num = Patient.objects.count() + 1
        
        for i in range(3):
            # Случайный пол
            gender = random.choice(['M', 'F'])
            
            if gender == 'M':
                first_name = random.choice(first_names_male)
                middle_name = random.choice(middle_names_male)
            else:
                first_name = random.choice(first_names_female)
                middle_name = random.choice(middle_names_female)
            
            last_name = random.choice(last_names)
            
            # Дата рождения (от 25 до 75 лет назад)
            years_ago = random.randint(25, 75)
            birth_date = date.today() - timedelta(days=years_ago * 365 + random.randint(0, 365))
            
            # Телефон
            phone = f"+7{random.randint(900, 999)}{random.randint(1000000, 9999999)}"
            
            # Email
            email = f"{first_name.lower()}.{last_name.lower()}{base_num + i}@example.com"
            
            # Создаем пациента
            patient = Patient.objects.create(
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                date_of_birth=birth_date,
                gender=gender,
                phone=phone,
                email=email,
                hospital=user.hospital if hasattr(user, 'hospital') and user.hospital else None,
                emias_last_synced=timezone.now(),  # Устанавливаем время синхронизации
            )
            
            # Привязываем пациента к врачу
            PatientDoctorRelation.objects.get_or_create(
                patient=patient,
                doctor=user,
                defaults={'is_active': True}
            )
            
            created_count += 1
        
        messages.success(request, f'Выгружено {created_count} пациентов из ЕМИАС.')
        return redirect('accounts:my_patients')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:my_patients')


@login_required
def my_patients_view(request):
    """Страница со списком 'Мои пациенты' для врача."""
    user = request.user
    if user.role != 'doctor':
        messages.error(request, 'Доступно только для врачей.')
        return redirect('accounts:cabinet')
    
    patients_qs = get_patient_queryset(user)
    
    # Поиск по ФИО или номеру карты
    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q as Qexpr
        # Пробуем найти по номеру карты (ID)
        try:
            card_id = int(q)
            patients_qs = patients_qs.filter(id=card_id)
        except ValueError:
            # Поиск по ФИО
            patients_qs = patients_qs.filter(
                Qexpr(first_name__icontains=q) |
                Qexpr(last_name__icontains=q) |
                Qexpr(middle_name__icontains=q)
            )
    
    # Подсчет статистики (до применения поиска)
    base_patients_qs = get_patient_queryset(user)
    total_count = base_patients_qs.count()
    
    # Подсчет активных и критичных пациентов
    from django.db.models import Exists, OuterRef
    active_cases = Case.objects.filter(
        patient=OuterRef('pk'),
        doctors=user,
        status__in=['urgent', 'monitoring']
    )
    critical_cases = Case.objects.filter(
        patient=OuterRef('pk'),
        doctors=user,
        status='urgent'
    )
    
    active_count = base_patients_qs.filter(Exists(active_cases)).count()
    critical_count = base_patients_qs.filter(Exists(critical_cases)).count()
    
    patients = list(patients_qs.select_related('hospital').prefetch_related('cases__doctors'))
    
    context = {
        'patients': patients,
        'query': q,
        'total_count': total_count,
        'active_count': active_count,
        'critical_count': critical_count,
    }
    return render(request, 'accounts/my_patients.html', context)


@login_required
def patient_detail_anonymous_view(request, case_id, patient_id):
    """Анонимная карточка пациента для завершенных консилиумов."""
    user = request.user
    
    try:
        case = Case.objects.get(id=case_id, status='stable')
        patient = Patient.objects.prefetch_related('medical_records', 'cases__doctors').get(id=patient_id)
    except Case.DoesNotExist:
        messages.error(request, 'Консилиум не найден.')
        return redirect('accounts:knowledge_base')
    except Patient.DoesNotExist:
        messages.error(request, 'Пациент не найден.')
        return redirect('accounts:knowledge_base')
    
    # Проверяем, что пациент действительно связан с этим консилиумом
    if case.patient_id != patient.id:
        messages.error(request, 'Неверная связь консилиума и пациента.')
        return redirect('accounts:case_detail', case_id=case_id)
    
    # Получаем данные из последней медицинской карты
    last_record = patient.medical_records.order_by('-visit_date').first()
    
    # Аллергии
    allergies = patient.get_allergies_list()
    
    # Лабораторные результаты
    lab_results = patient.get_last_lab_results()
    
    # Текущие препараты
    current_medications = []
    if last_record and last_record.current_medications:
        current_medications = [m.strip() for m in last_record.current_medications.split(',') if m.strip()]
    
    # Хронические заболевания
    chronic_diseases = []
    if last_record and last_record.chronic_diseases:
        chronic_diseases = [d.strip() for d in last_record.chronic_diseases.split(',') if d.strip()]
    
    # Последняя госпитализация
    last_hospitalization = patient.last_hospitalization
    
    context = {
        'patient': patient,
        'case': case,
        'allergies': allergies,
        'lab_results': lab_results,
        'current_medications': current_medications,
        'chronic_diseases': chronic_diseases,
        'last_hospitalization': last_hospitalization,
        'last_record': last_record,
        'is_anonymous': True,  # Флаг для анонимного режима
    }
    return render(request, 'accounts/patient_detail_anonymous.html', context)


@login_required
def patient_detail_view(request, patient_id):
    """Детальная страница пациента."""
    user = request.user
    
    try:
        patient = Patient.objects.prefetch_related('medical_records', 'cases__doctors').get(id=patient_id)
    except Patient.DoesNotExist:
        messages.error(request, 'Пациент не найден.')
        return redirect('accounts:my_patients')
    
    # Проверка доступа (только если врач имеет доступ к пациенту)
    if user.role == 'doctor':
        if not patient.treating_doctors.filter(doctor=user, is_active=True).exists():
            messages.error(request, 'У вас нет доступа к этому пациенту.')
            return redirect('accounts:my_patients')
    elif user.role == 'hospital_admin':
        if patient.hospital != user.hospital:
            messages.error(request, 'У вас нет доступа к этому пациенту.')
            return redirect('accounts:cabinet')
    
    # Получаем данные из последней медицинской карты
    last_record = patient.medical_records.order_by('-visit_date').first()
    
    # Аллергии
    allergies = patient.get_allergies_list()
    
    # Лабораторные результаты
    lab_results = patient.get_last_lab_results()
    
    # Текущие препараты
    current_medications = []
    if last_record and last_record.current_medications:
        current_medications = [m.strip() for m in last_record.current_medications.split(',') if m.strip()]
    
    # Хронические заболевания
    chronic_diseases = []
    if last_record and last_record.chronic_diseases:
        chronic_diseases = [d.strip() for d in last_record.chronic_diseases.split(',') if d.strip()]
    
    # Последняя госпитализация
    last_hospitalization = patient.last_hospitalization
    
    # Консилиумы пациента
    patient_cases = patient.cases.filter(doctors=user).order_by('-created_at')[:10]
    
    context = {
        'patient': patient,
        'allergies': allergies,
        'lab_results': lab_results,
        'current_medications': current_medications,
        'chronic_diseases': chronic_diseases,
        'last_hospitalization': last_hospitalization,
        'patient_cases': patient_cases,
        'last_record': last_record,
    }
    return render(request, 'accounts/patient_detail.html', context)


@login_required
def complete_case_view(request, case_id):
    """Завершить консилиум и опционально добавить в базу знаний."""
    user = request.user
    
    try:
        case = Case.objects.get(id=case_id)
    except Case.DoesNotExist:
        messages.error(request, 'Консилиум не найден.')
        return redirect('accounts:cases')
    
    # Проверка доступа:
    # - Участники консилиума или создатель могут завершить
    # - Администратор больницы может завершить консилиумы врачей своей больницы
    # - Суперадмин может завершить любой консилиум
    has_access = False
    
    if user.role == 'superadmin':
        has_access = True
    elif user.role == 'hospital_admin' and user.hospital:
        # Администратор больницы может завершить консилиумы врачей своей больницы
        if case.patient and case.patient.hospital == user.hospital:
            has_access = True
        # Также если хотя бы один врач-участник из его больницы
        elif case.doctors.filter(hospital=user.hospital).exists():
            has_access = True
        elif case.created_by and case.created_by.hospital == user.hospital:
            has_access = True
    elif user in case.doctors.all() or case.created_by == user:
        # Участник или создатель
        has_access = True
    
    if not has_access:
        messages.error(request, 'У вас нет прав для завершения этого консилиума.')
        return redirect('accounts:case_detail', case_id=case_id)
    
    # Проверка, что консилиум еще не завершен
    if case.status == 'stable':
        messages.info(request, 'Консилиум уже завершен.')
        return redirect('accounts:case_detail', case_id=case_id)
    
    if request.method == 'POST':
        add_to_knowledge_base = request.POST.get('add_to_knowledge_base', '') == 'on'
        
        # Завершаем консилиум
        case.status = 'stable'
        case.save()
        
        if add_to_knowledge_base:
            messages.success(request, 'Консилиум завершен и добавлен в базу знаний.')
        else:
            messages.success(request, 'Консилиум завершен.')
        
        return redirect('accounts:case_detail', case_id=case_id)
    
    # Показываем форму подтверждения
    context = {
        'case': case,
    }
    return render(request, 'accounts/complete_case.html', context)


@login_required
def knowledge_base_view(request):
    """База знаний - поиск по завершенным консилиумам."""
    from django.db.models import Count, Q
    
    # Получаем завершенные кейсы (статус 'stable')
    completed_cases = Case.objects.filter(status='stable').select_related('patient', 'created_by').prefetch_related('doctors', 'messages')
    
    # Поиск по запросу
    query = request.GET.get('q', '').strip()
    specialty_filter = request.GET.get('specialty', '').strip()
    
    if query:
        # Поиск по диагнозу, МКБ-коду, описанию
        completed_cases = completed_cases.filter(
            Q(diagnosis__icontains=query) |
            Q(description__icontains=query) |
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query)
        )
    
    # Фильтр по специальности (только если выбран, не "Все")
    if specialty_filter and specialty_filter != 'all':
        completed_cases = completed_cases.filter(doctors__specialty=specialty_filter).distinct()
    
    # Подсчет статистики
    total_cases = Case.objects.filter(status='stable').count()
    total_doctors = User.objects.filter(cases__status='stable').distinct().count()
    total_specialties = User.objects.filter(
        cases__status='stable',
        specialty__isnull=False
    ).values('specialty').distinct().count()
    
    # Получаем список специальностей для фильтров
    specialties = User.objects.filter(
        cases__status='stable',
        specialty__isnull=False
    ).values_list('specialty', flat=True).distinct().order_by('specialty')
    
    # Формируем результаты
    results = []
    for case in completed_cases[:50]:  # Ограничиваем до 50 результатов
        
        # Вычисляем длительность консилиума
        duration_minutes = 0
        if case.messages.exists():
            first_message = case.messages.order_by('created_at').first()
            last_message = case.messages.order_by('-created_at').first()
            if first_message and last_message:
                delta = last_message.created_at - first_message.created_at
                duration_minutes = int(delta.total_seconds() / 60)
        
        # Получаем итоговое решение (последнее сообщение или заглушка)
        decision = "Решение принято"
        last_message = case.messages.order_by('-created_at').first()
        if last_message:
            decision_text = last_message.content[:100]
            if len(last_message.content) > 100:
                decision_text += "..."
            decision = decision_text
        
        # Получаем коморбидности из медицинских карт
        comorbidities = []
        last_record = case.patient.medical_records.order_by('-visit_date').first()
        if last_record and last_record.chronic_diseases:
            comorbidities = [d.strip() for d in last_record.chronic_diseases.split(',') if d.strip()][:3]
        
        results.append({
            'case': case,
            'duration_minutes': duration_minutes,
            'decision': decision,
            'comorbidities': comorbidities,
            'doctors_count': case.doctors.count(),
            'messages_count': case.messages.count(),
        })
    
    context = {
        'query': query,
        'specialty_filter': specialty_filter,
        'total_cases': total_cases,
        'total_doctors': total_doctors,
        'total_specialties': total_specialties,
        'specialties': specialties,
        'results': results,
    }
    return render(request, 'accounts/knowledge_base.html', context)


@login_required
def generate_stable_cases_view(request):
    """Сгенерировать завершенные консилиумы для базы знаний (только суперадмин)."""
    user = request.user
    if user.role != 'superadmin':
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        from datetime import date, timedelta
        import random
        
        # Диагнозы (МКБ-10)
        diagnoses = [
            'I10 Эссенциальная (первичная) гипертензия',
            'E11 Сахарный диабет 2 типа',
            'J44 Другая хроническая обструктивная легочная болезнь',
            'I25 Хроническая ишемическая болезнь сердца',
            'I21.9 Острый инфаркт миокарда неуточненный',
            'I63.9 Церебральный инфаркт неуточненный',
            'G93.4 Энцефалопатия неуточненная',
            'N18 Хроническая болезнь почек',
            'I50 Сердечная недостаточность',
            'J18 Пневмония неуточненного возбудителя',
        ]
        
        # Описания случаев
        descriptions = [
            'Пациент поступил с жалобами на головную боль и повышение артериального давления. Требуется консилиум для определения тактики лечения.',
            'Сложный случай, требующий мнения нескольких специалистов. Необходимо обсуждение тактики лечения.',
            'Пациент с множественными сопутствующими заболеваниями. Требуется комплексный подход к лечению.',
            'Необходимо определить показания к инвазивным вмешательствам и оптимальную антитромботическую терапию.',
            'Требуется консилиум для определения тактики лечения и необходимости оперативного вмешательства.',
        ]
        
        # Получаем пациентов и врачей
        patients = list(Patient.objects.all())
        doctors = list(User.objects.filter(role='doctor'))
        
        if not patients:
            messages.error(request, 'Нет пациентов в базе. Сначала создайте пациентов.')
            return redirect('accounts:cabinet')
        
        if not doctors:
            messages.error(request, 'Нет врачей в базе. Сначала создайте врачей.')
            return redirect('accounts:cabinet')
        
        created_count = 0
        count = 5  # Генерируем 5 консилиумов
        
        for i in range(count):
            # Случайный пациент
            patient = random.choice(patients)
            
            # Случайные врачи (от 2 до 4)
            num_doctors = random.randint(2, min(4, len(doctors)))
            case_doctors = random.sample(doctors, num_doctors)
            
            # Случайный диагноз
            diagnosis = random.choice(diagnoses)
            
            # Случайное описание
            description = random.choice(descriptions)
            
            # Дата поступления (от 30 до 90 дней назад)
            days_ago = random.randint(30, 90)
            admission_date = date.today() - timedelta(days=days_ago)
            
            # Создаем завершенный консилиум
            case = Case.objects.create(
                patient=patient,
                created_by=case_doctors[0],
                diagnosis=diagnosis,
                description=description,
                status='stable',  # Завершенный консилиум
                admission_date=admission_date
            )
            
            # Добавляем врачей
            case.doctors.set(case_doctors)
            
            # Создаем несколько сообщений (от 3 до 8)
            num_messages = random.randint(3, 8)
            message_contents = [
                'Рассмотрел случай. Предлагаю следующую тактику лечения.',
                'Согласен с коллегами. Необходимо дополнительное обследование.',
                'Рекомендую консервативное лечение с последующим контролем.',
                'Предлагаю рассмотреть возможность оперативного вмешательства.',
                'Требуется уточнение некоторых моментов из анамнеза.',
                'Согласен с предложенной тактикой. Можно приступать к лечению.',
                'Рекомендую мониторинг состояния пациента в течение недели.',
                'Предлагаю скорректировать дозировку препаратов.',
            ]
            
            for j in range(num_messages):
                author = random.choice(case_doctors)
                # Время сообщения - в течение консилиума (от начала до конца)
                message_delta = timedelta(
                    minutes=random.randint(0, num_messages * 30)
                )
                message_time = timezone.now() - timedelta(days=days_ago) + message_delta
                
                content = random.choice(message_contents)
                msg = CaseMessage.objects.create(
                    case=case,
                    author=author,
                    content=content,
                    is_read=True  # Все сообщения прочитаны в завершенных консилиумах
                )
                # Обновляем время создания сообщения
                CaseMessage.objects.filter(id=msg.id).update(created_at=message_time)
            
            created_count += 1
        
        messages.success(request, f'Сгенерировано {created_count} завершенных консилиумов для базы знаний.')
        return redirect('accounts:knowledge_base')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')


@login_required
def generate_doctors_view(request):
    """Сгенерировать 10 пользователей с ролью 'doctor'."""
    user = request.user
    if user.role not in ['superadmin', 'hospital_admin']:
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    created = 0
    created_emails = []
    specialties = [
        'Кардиолог',
        'Невролог',
        'Пульмонолог',
        'Анестезиолог-реаниматолог',
        'Рентгенолог',
        'Гастроэнтеролог',
        'Хирург',
        'Нефролог',
        'Уролог',
        'ЛОР',
    ]
    start_index = User.objects.filter(role='doctor').count() + 1
    for i in range(start_index, start_index + 10):
        email = f'doctor{i}@example.com'
        if User.objects.filter(email=email).exists():
            continue
        doctor = User.objects.create_user(
            username=email,  # username обязателен в кастомной модели (REQUIRED_FIELDS)
            email=email,
            password='Doctor123!',
            role='doctor',
            hospital=user.hospital if user.hospital else None,
        )
        # назначаем специализацию по кругу
        doctor.specialty = specialties[(i - start_index) % len(specialties)]
        doctor.save(update_fields=['specialty'])
        created += 1
        created_emails.append(email)
    if created:
        messages.success(request, f'Создано врачей: {created}. Пароль: Doctor123! Эмейлы: {", ".join(created_emails)}')
    else:
        messages.info(request, 'Новые врачи не созданы (все логины уже заняты).')
    return redirect('accounts:cabinet')


@login_required
def delete_hospital_cases_view(request):
    """Удалить все консилиумы врачей больницы (только админ больницы)."""
    user = request.user
    if user.role != 'hospital_admin' or not user.hospital:
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        # Все кейсы, где участвуют врачи этой больницы
        hospital_cases = Case.objects.filter(doctors__hospital=user.hospital).order_by().distinct()
        case_ids = list(hospital_cases.values_list('id', flat=True))
        MessageReaction.objects.filter(message__case_id__in=case_ids).delete()
        CaseMessage.objects.filter(case_id__in=case_ids).delete()
        deleted_count = len(case_ids)
        Case.objects.filter(id__in=case_ids).delete()
        messages.success(request, f'Удалено консилиумов больницы: {deleted_count}.')
        return redirect('accounts:cabinet')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')


@login_required
def delete_all_patients_view(request):
    """Удалить всех пациентов (только суперАдмин)."""
    user = request.user
    if user.role != 'superadmin':
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        # Каскадно удалятся их кейсы, сообщения и реакции
        Patient.objects.all().delete()
        messages.success(request, 'Все пациенты удалены.')
        return redirect('accounts:cabinet')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')


@login_required
def delete_all_doctors_except_admin_view(request):
    """Удалить всех врачей (role=doctor), кроме суперпользователей и admin (только суперАдмин)."""
    user = request.user
    if user.role != 'superadmin':
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        qs = User.objects.filter(role='doctor', is_superuser=False)
        deleted_count = qs.count()
        qs.delete()
        messages.success(request, f'Удалено врачей: {deleted_count}.')
        return redirect('accounts:cabinet')
    
    messages.error(request, 'Метод не поддерживается.')
    return redirect('accounts:cabinet')
# API Views
class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        user_data = UserSerializer(user).data
        return Response({
            'user': user_data,
            'token': token.key,
            'message': 'Регистрация успешна.'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API endpoint for user login."""
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Create or get token
    token, created = Token.objects.get_or_create(user=user)
    
    user_data = UserSerializer(user).data
    return Response({
        'user': user_data,
        'token': token.key,
        'message': 'Вход выполнен успешно.'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """API endpoint to get current authenticated user."""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


def logout_view(request):
    """Выход из системы."""
    auth_logout(request)
    return redirect('home')


def register_view(request):
    """Регистрация нового пользователя (врача)."""
    if request.user.is_authenticated:
        return redirect('accounts:cabinet')
    
    if request.method == 'POST':
        # Получаем данные из формы
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        registration_key = request.POST.get('registration_key', '').strip().upper()
        role = request.POST.get('role', 'doctor')
        hospital_id = request.POST.get('hospital')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        patronymic = request.POST.get('patronymic', '').strip()
        specialty = request.POST.get('specialty', '').strip()
        
        # Валидация
        errors = {}
        
        if not last_name:
            errors['last_name'] = 'Фамилия обязательна'
        if not first_name:
            errors['first_name'] = 'Имя обязательно'
        if not specialty:
            errors['specialty'] = 'Специализация обязательна'
        
        # Проверка регистрационного ключа
        if not registration_key:
            errors['registration_key'] = 'Регистрационный ключ обязателен'
        else:
            try:
                key_obj = RegistrationKey.objects.get(key=registration_key)
                if key_obj.is_used:
                    errors['registration_key'] = 'Этот ключ уже использован'
            except RegistrationKey.DoesNotExist:
                errors['registration_key'] = 'Неверный регистрационный ключ'
        
        if not email:
            errors['email'] = 'Email обязателен'
        elif User.objects.filter(email=email).exists():
            errors['email'] = 'Пользователь с таким email уже существует'
        
        if not username:
            errors['username'] = 'Имя пользователя обязательно'
        elif User.objects.filter(username=username).exists():
            errors['username'] = 'Пользователь с таким именем уже существует'
        
        if not password:
            errors['password'] = 'Пароль обязателен'
        elif len(password) < 8:
            errors['password'] = 'Пароль должен содержать минимум 8 символов'
        
        if password != password_confirm:
            errors['password_confirm'] = 'Пароли не совпадают'
        
        if errors:
            hospitals = Hospital.objects.all()
            context = {
                'errors': errors,
                'form_data': request.POST,
                'hospitals': hospitals,
            }
            return render(request, 'accounts/register.html', context)
        
        # Создаем пользователя
        try:
            hospital = Hospital.objects.get(id=hospital_id) if hospital_id else None
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                role=role,
                hospital=hospital,
                first_name=first_name,
                last_name=last_name,
                patronymic=patronymic if patronymic else None,
                specialty=specialty
            )
            
            # Помечаем ключ как использованный
            key_obj = RegistrationKey.objects.get(key=registration_key)
            key_obj.use(user)
            
            # Автоматически входим пользователя
            auth_login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('accounts:cabinet')
        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            hospitals = Hospital.objects.all()
            context = {
                'errors': {'general': 'Ошибка при регистрации. Попробуйте еще раз.'},
                'form_data': request.POST,
                'hospitals': hospitals,
            }
            return render(request, 'accounts/register.html', context)
    
    # GET запрос - показываем форму
    hospitals = Hospital.objects.all()
    context = {
        'hospitals': hospitals,
    }
    return render(request, 'accounts/register.html', context)


@login_required
def generate_registration_keys_view(request):
    """Генерация регистрационных ключей (для администраторов)."""
    user = request.user
    if user.role not in ['superadmin', 'hospital_admin']:
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    count = int(request.GET.get('count', 5))
    if count < 1 or count > 20:
        count = 5
    
    created_keys = []
    for _ in range(count):
        key_obj = RegistrationKey.create_key(created_by=user)
        created_keys.append(key_obj.key)
    
    messages.success(request, f'Создано {count} регистрационных ключей: {", ".join(created_keys)}')
    return redirect('accounts:registration_keys')


@login_required
def registration_keys_view(request):
    """Страница управления регистрационными ключами."""
    user = request.user
    if user.role not in ['superadmin', 'hospital_admin']:
        messages.error(request, 'Недостаточно прав.')
        return redirect('accounts:cabinet')
    
    # Получаем ключи в зависимости от роли
    if user.role == 'superadmin':
        keys = RegistrationKey.objects.all().select_related('created_by', 'used_by')
    else:  # hospital_admin
        keys = RegistrationKey.objects.filter(created_by=user).select_related('created_by', 'used_by')
    
    # Статистика
    total_keys = keys.count()
    active_keys = keys.filter(is_used=False).count()
    used_keys = keys.filter(is_used=True).count()
    
    context = {
        'keys': keys,
        'total_keys': total_keys,
        'active_keys': active_keys,
        'used_keys': used_keys,
    }
    return render(request, 'accounts/registration_keys.html', context)
