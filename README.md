# Третье мнение - Платформа для консилиумов врачей

Django REST API проект для платформы консилиумов врачей.

## Структура проекта

```
tretie_mnenie/
├── backend/              # Django проект
│   ├── manage.py
│   ├── core/            # Настройки Django
│   ├── accounts/        # Пользователи и аутентификация
│   ├── hospitals/       # Больницы
│   ├── patients/        # Пациенты и медицинские карточки
│   └── db.sqlite3       # База данных (локальная)
├── env/                 # Виртуальное окружение
└── requirements.txt     # Зависимости
```

## Установка и запуск

### 1. Активировать виртуальное окружение

```bash
# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Применить миграции

```bash
cd backend
python manage.py migrate
```

### 4. Создать суперпользователя

```bash
python manage.py createsuperuser
```

### 5. Запустить сервер

```bash
python manage.py runserver
```

Проект будет доступен на http://127.0.0.1:8000/

## API Endpoints

### Аутентификация
- `POST /api/accounts/register/` - Регистрация
- `POST /api/accounts/login/` - Вход
- `GET /api/accounts/me/` - Текущий пользователь

### Больницы
- `GET /api/hospitals/` - Список больниц
- `POST /api/hospitals/` - Создать больницу

### Пациенты
- `GET /api/patients/cabinet/` - Кабинет врача
- `GET /api/patients/patients/` - Список пациентов
- `POST /api/patients/patients/` - Создать пациента
- `GET /api/patients/patients/<id>/` - Детали пациента
- `GET /api/patients/records/` - Список медицинских карточек
- `POST /api/patients/records/` - Создать карточку

## Аутентификация

Используется Token Authentication. После регистрации или входа вы получите токен, который нужно передавать в заголовке:

```
Authorization: Token <your_token>
```

## Технологии

- Python 3.x
- Django 5.x
- Django REST Framework
- SQLite (для разработки)

