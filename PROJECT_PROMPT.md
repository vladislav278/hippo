# ПРОМПТ ДЛЯ AI-АССИСТЕНТА: Проект "Третье мнение"

## КОНТЕКСТ ПРОЕКТА

Вы работаете с Django backend проектом **"Третье мнение"** (tretie_mnenie) - платформой для консилиумов врачей.

**Основная идея:** Для каждого пациента/клинической ситуации создается отдельный "консилиум" (обсуждение случая). Врачи могут регистрироваться, принадлежать к больнице, создавать консилиумы, приглашать других врачей и обсуждать случаи в чате с возможностью запроса AI-резюме/дифференциальной диагностики.

**Текущий фокус:** BACKEND - модели данных, API endpoints, базовая аутентификация/регистрация. Frontend минимальный (DRF browsable API, базовые HTML заглушки).

---

## СТРУКТУРА ПРОЕКТА

```
tretie_mnenie/
├── core/                          # Основная директория Django проекта
│   ├── manage.py                  # Django management script
│   ├── core/                      # Внутренний модуль настроек Django
│   │   ├── settings.py           # Настройки проекта (PostgreSQL/SQLite)
│   │   ├── urls.py               # Главный URL router
│   │   ├── views.py              # Главная страница API
│   │   ├── wsgi.py               # WSGI конфигурация
│   │   └── asgi.py               # ASGI конфигурация
│   ├── accounts/                 # Приложение для пользователей и аутентификации
│   │   ├── models.py            # Custom User model
│   │   ├── serializers.py       # Сериализаторы для User
│   │   ├── views.py             # API views (register, login, me)
│   │   ├── urls.py              # URL routing для accounts
│   │   └── admin.py             # Django admin для User
│   ├── hospitals/               # Приложение для больниц
│   │   ├── models.py            # Hospital model
│   │   ├── serializers.py       # Сериализаторы для Hospital
│   │   ├── views.py             # API views (list, create)
│   │   ├── urls.py              # URL routing для hospitals
│   │   └── admin.py             # Django admin для Hospital
│   └── patients/                # Приложение для пациентов и медицинских карточек
│       ├── models.py            # Patient, MedicalRecord, PatientDoctorRelation
│       ├── serializers.py       # Сериализаторы для пациентов и карточек
│       ├── views.py             # API views (кабинет врача, CRUD пациентов/карточек)
│       ├── urls.py              # URL routing для patients
│       └── admin.py             # Django admin для пациентов
├── requirements.txt              # Python зависимости
├── Procfile                      # Конфигурация для Railway
├── railway.json                  # Настройки деплоя на Railway
├── .gitignore                    # Git ignore правила
├── README.md                     # Документация проекта
└── RAILWAY_DEPLOY.md             # Инструкция по деплою

ВАЖНО: manage.py находится ВНУТРИ папки "core", поэтому все Django команды выполняются из:
cd core && python manage.py ...
```

---

## ТЕХНОЛОГИЧЕСКИЙ СТЕК

- **Python 3.x** (Windows)
- **Django 5.x**
- **Django REST Framework** (DRF)
- **PostgreSQL** (для production на Railway) / **SQLite** (для локальной разработки)
- **Token Authentication** (DRF authtoken)
- **WhiteNoise** (для статических файлов на Railway)
- **Gunicorn** (веб-сервер для production)

---

## МОДЕЛИ ДАННЫХ

### 1. User (accounts.User) - Кастомная модель пользователя

**Основа:** `AbstractUser` с email как основным идентификатором

**Поля:**
- `email` - EmailField (unique, USERNAME_FIELD)
- `username` - для совместимости
- `role` - CharField с choices: 'superadmin', 'hospital_admin', 'doctor' (по умолчанию 'doctor')
- `hospital` - ForeignKey к Hospital (nullable, для superadmin может быть None)
- Стандартные Django поля: password, is_active, date_joined и т.д.

**AUTH_USER_MODEL:** `'accounts.User'` (настроено в settings.py)

### 2. Hospital (hospitals.Hospital)

**Поля:**
- `name` - CharField (название больницы)
- `city` - CharField (опционально)
- `address` - TextField (опционально)
- `created_at`, `updated_at` - автоматические timestamps

### 3. Patient (patients.Patient)

**Поля:**
- `first_name`, `last_name`, `middle_name` - ФИО
- `date_of_birth` - DateField
- `gender` - CharField с choices: 'M', 'F', 'O'
- `phone`, `email`, `address` - контакты (опционально)
- `hospital` - ForeignKey к Hospital (опционально)
- `created_at`, `updated_at` - timestamps

**Методы:**
- `full_name` - property, возвращает полное имя

### 4. MedicalRecord (patients.MedicalRecord) - Медицинская карточка

**Поля:**
- `patient` - ForeignKey к Patient
- `doctor` - ForeignKey к User (автоматически устанавливается при создании)
- `chief_complaint` - TextField (жалобы)
- `diagnosis` - CharField (диагноз, опционально)
- `anamnesis` - TextField (анамнез, опционально)
- `allergies` - TextField (аллергии, опционально)
- `chronic_diseases` - TextField (хронические заболевания, опционально)
- `current_medications` - TextField (текущие препараты, опционально)
- `notes` - TextField (примечания, опционально)
- `visit_date` - DateField (дата визита)
- `created_at`, `updated_at` - timestamps

### 5. PatientDoctorRelation (patients.PatientDoctorRelation) - Связь врач-пациент

**Назначение:** Отслеживает, какой врач лечит какого пациента

**Поля:**
- `patient` - ForeignKey к Patient
- `doctor` - ForeignKey к User
- `assigned_date` - DateField (автоматически при создании)
- `is_active` - BooleanField (активна ли связь)
- `notes` - TextField (опционально)

**Unique together:** ['patient', 'doctor']

**Автоматическое создание:** При создании пациента через API автоматически создается связь с текущим врачом.

---

## API ENDPOINTS

### Аутентификация (`/api/accounts/`)

1. **POST /api/accounts/register/** - Регистрация
   - Принимает: email, username, password, password_confirm, role (опционально), hospital (опционально)
   - Возвращает: user data + token
   - Публичный endpoint (AllowAny)

2. **POST /api/accounts/login/** - Вход
   - Принимает: email, password
   - Возвращает: user data + token
   - Публичный endpoint (AllowAny)

3. **GET /api/accounts/me/** - Текущий пользователь
   - Возвращает: данные текущего авторизованного пользователя
   - Требует аутентификации

### Больницы (`/api/hospitals/`)

4. **GET /api/hospitals/** - Список больниц
   - Возвращает: список всех больниц
   - Публичный endpoint (AllowAny)
   - Пагинация: 20 элементов на страницу

5. **POST /api/hospitals/** - Создать больницу
   - Принимает: name, city (опционально), address (опционально)
   - Требует аутентификации

### Пациенты и медицинские карточки (`/api/patients/`)

6. **GET /api/patients/cabinet/** - Кабинет врача
   - Возвращает: статистику (количество пациентов, карточек), последние 5 пациентов, последние 5 карточек
   - Требует аутентификации
   - Врач видит только своих пациентов, админ больницы - всех пациентов своей больницы

7. **GET /api/patients/patients/** - Список пациентов
   - Возвращает: список пациентов врача
   - Поиск: `?search=query` (по имени, фамилии, телефону, email)
   - Сортировка: `?ordering=last_name` или `?ordering=-created_at`
   - Требует аутентификации

8. **POST /api/patients/patients/** - Создать пациента
   - Принимает: все поля Patient
   - Автоматически создает PatientDoctorRelation с текущим врачом
   - Требует аутентификации

9. **GET /api/patients/patients/<id>/** - Детали пациента
   - Возвращает: полную информацию о пациенте + все его медицинские карточки
   - Требует аутентификации

10. **PUT/PATCH /api/patients/patients/<id>/** - Обновить пациента
    - Требует аутентификации

11. **DELETE /api/patients/patients/<id>/** - Удалить пациента
    - Требует аутентификации

12. **GET /api/patients/records/** - Список медицинских карточек
    - Фильтр по пациенту: `?patient=<id>`
    - Сортировка: `?ordering=-visit_date`
    - Требует аутентификации

13. **POST /api/patients/records/** - Создать медицинскую карточку
    - Принимает: все поля MedicalRecord (кроме doctor - устанавливается автоматически)
    - Требует аутентификации

14. **GET /api/patients/records/<id>/** - Детали карточки
    - Требует аутентификации

15. **PUT/PATCH /api/patients/records/<id>/** - Обновить карточку
    - Требует аутентификации

16. **DELETE /api/patients/records/<id>/** - Удалить карточку
    - Требует аутентификации

### Главная страница

17. **GET /** - Информация о всех API endpoints
   - Возвращает JSON с описанием всех доступных endpoints

---

## ПРАВА ДОСТУПА И ФИЛЬТРАЦИЯ

### Врач (role='doctor'):
- Видит только своих пациентов (через PatientDoctorRelation с is_active=True)
- Видит только свои медицинские карточки (где doctor=current_user)
- Может создавать пациентов и карточки

### Администратор больницы (role='hospital_admin'):
- Видит всех пациентов своей больницы (patient.hospital == user.hospital)
- Видит все карточки пациентов своей больницы
- Может создавать пациентов и карточки

### Супер-администратор (role='superadmin'):
- Видит всех пациентов (без фильтрации)
- Видит все карточки (без фильтрации)
- Может создавать пациентов и карточки

---

## НАСТРОЙКИ (settings.py)

### База данных:
- **Автоматическое переключение:** Если есть переменная окружения `DATABASE_URL` - используется PostgreSQL, иначе SQLite
- **PostgreSQL:** Парсится из `DATABASE_URL` (формат Railway: `postgresql://user:password@host:port/dbname`)
- **SQLite:** Используется для локальной разработки (`db.sqlite3`)

### Переменные окружения:
- `SECRET_KEY` - секретный ключ Django (обязательно для production)
- `DEBUG` - режим отладки ('True' или 'False', по умолчанию 'True')
- `ALLOWED_HOSTS` - разрешенные хосты (через запятую, по умолчанию '*')
- `DATABASE_URL` - URL базы данных PostgreSQL (автоматически на Railway)

### Статические файлы:
- `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- Используется WhiteNoise для обслуживания статики на Railway
- `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`

### DRF настройки:
- Аутентификация: SessionAuthentication, TokenAuthentication
- Права по умолчанию: IsAuthenticated
- Пагинация: PageNumberPagination (20 элементов на страницу)

---

## КАК ЗАПУСТИТЬ ПРОЕКТ

### Локальная разработка:

```bash
# 1. Перейти в папку core
cd core

# 2. Создать виртуальное окружение (если еще нет)
python -m venv ../env
# Windows
../env/Scripts/activate
# Linux/Mac
source ../env/bin/activate

# 3. Установить зависимости
pip install -r ../requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Создать суперпользователя
python manage.py createsuperuser

# 6. Запустить сервер
python manage.py runserver
```

Проект будет доступен на http://127.0.0.1:8000/

### На Railway (Production):

1. Подключить репозиторий к Railway
2. Добавить PostgreSQL базу данных
3. Настроить переменные окружения (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL)
4. Railway автоматически задеплоит проект
5. Миграции применяются автоматически (благодаря Procfile)
6. Создать суперпользователя через Railway CLI или консоль

---

## ЧТО РЕАЛИЗОВАНО

✅ Кастомная модель User с email как username
✅ Роли пользователей (superadmin, hospital_admin, doctor)
✅ Связь пользователей с больницами
✅ CRUD для больниц
✅ Регистрация и аутентификация через API (Token-based)
✅ CRUD для пациентов
✅ CRUD для медицинских карточек
✅ Кабинет врача со статистикой
✅ Права доступа (врач видит только своих пациентов)
✅ Поиск и фильтрация пациентов
✅ Автоматическое создание связей врач-пациент
✅ Настройка для PostgreSQL и Railway
✅ Django Admin для всех моделей
✅ Главная страница с документацией API

---

## ЧТО НЕ РЕАЛИЗОВАНО (БУДУЩИЕ ЗАДАЧИ)

❌ **Consilium (Консилиум)** - основная фича проекта:
   - Модель Consilium (клинический случай/обсуждение)
   - Модель ConsiliumParticipant (участники консилиума)
   - Модель ConsiliumTemplate (шаблоны для быстрого создания)
   - API для создания/управления консилиумами
   - Приглашение врачей в консилиум (вручную и через AI)

❌ **Чат в реальном времени:**
   - Django Channels для WebSocket
   - Модель Message (сообщения в консилиуме)
   - Real-time обновления чата

❌ **AI Assistant:**
   - Интеграция с AI API (OpenAI, Anthropic и т.д.)
   - Endpoint для запроса дифференциальной диагностики
   - Endpoint для резюме обсуждения
   - Endpoint для предложений по плану лечения
   - AI-предложения врачей для приглашения в консилиум

❌ **Дополнительные функции:**
   - Профили врачей (специализация, опыт)
   - История консилиумов
   - Уведомления
   - Экспорт данных
   - Загрузка файлов (анализы, снимки)

---

## ВАЖНЫЕ ОСОБЕННОСТИ КОДА

### 1. Структура проекта:
- `manage.py` находится ВНУТРИ папки `core`
- Все Django команды выполняются из `core/` директории
- Приложения: `accounts`, `hospitals`, `patients` находятся на одном уровне с внутренним `core/`

### 2. Аутентификация:
- Используется DRF Token Authentication
- Токен создается автоматически при регистрации и входе
- Токен передается в заголовке: `Authorization: Token <token>`

### 3. Фильтрация данных:
- Врач видит только своих пациентов через `PatientDoctorRelation`
- Админ больницы видит всех пациентов своей больницы
- Фильтрация реализована в методах `get_queryset()` views

### 4. Автоматические связи:
- При создании пациента через API автоматически создается `PatientDoctorRelation`
- При создании медицинской карточки автоматически устанавливается `doctor = request.user`

### 5. Сериализаторы:
- `UserRegistrationSerializer` - валидация паролей, проверка уникальности email
- `LoginSerializer` - валидация credentials
- `PatientWithRecordsSerializer` - пациент со всеми его карточками
- `MedicalRecordDetailSerializer` - карточка с полной информацией о пациенте и враче

---

## СТИЛЬ КОДА И ПРАКТИКИ

- Используются class-based views (generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView)
- Явные импорты
- Документация в docstrings
- Валидация через сериализаторы
- Обработка ошибок через DRF exceptions
- Русские verbose_name для моделей (для админки)
- Английские имена полей и переменных

---

## КОМАНДЫ ДЛЯ РАЗРАБОТКИ

```bash
# Создать миграции
cd core && python manage.py makemigrations

# Применить миграции
cd core && python manage.py migrate

# Создать суперпользователя
cd core && python manage.py createsuperuser

# Запустить сервер
cd core && python manage.py runserver

# Собрать статические файлы (для production)
cd core && python manage.py collectstatic --noinput
```

---

## ФАЙЛЫ КОНФИГУРАЦИИ

- **requirements.txt** - Python зависимости
- **Procfile** - команда запуска для Railway
- **railway.json** - настройки деплоя на Railway
- **.gitignore** - исключает db.sqlite3, __pycache__, env/, и т.д.

---

## ПРИ РАБОТЕ С ПРОЕКТОМ

1. **Всегда работайте из папки `core/`** для Django команд
2. **Не коммитьте `db.sqlite3`** - он в .gitignore
3. **Используйте переменные окружения** для SECRET_KEY в production
4. **Проверяйте права доступа** - врач должен видеть только своих пациентов
5. **При добавлении новых моделей** - создавайте миграции и применяйте их
6. **При изменении User модели** - будьте осторожны, это кастомная модель

---

## СЛЕДУЮЩИЕ ШАГИ ДЛЯ РАЗВИТИЯ

1. Реализовать модель Consilium и связанные модели
2. Добавить Django Channels для real-time чата
3. Интегрировать AI API для диагностики и резюме
4. Добавить систему уведомлений
5. Реализовать загрузку файлов (анализы, снимки)
6. Добавить тесты (pytest или Django TestCase)
7. Оптимизировать запросы (select_related, prefetch_related)
8. Добавить кэширование (Redis)

---

## КОНТАКТЫ И ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

- Проект создан для хакатона
- Владелец проекта - студент-медик, начинающий backend разработчик
- Решения должны быть простыми и понятными, без излишнего усложнения
- Приоритет: работоспособность > идеальная архитектура

---

**Этот промпт содержит всю необходимую информацию для продолжения работы над проектом.**

