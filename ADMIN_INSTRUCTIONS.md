# Инструкция по работе с админом Django

## Как посмотреть существующих пользователей

### Через Django shell (если виртуальное окружение активировано):
```bash
cd core
python manage.py shell
```

Затем в shell:
```python
from accounts.models import User
users = User.objects.all()
for u in users:
    print(f"Email: {u.email}, Username: {u.username}, Role: {u.role}, Is Superuser: {u.is_superuser}")
```

### Через Django admin:
1. Запустите сервер: `python manage.py runserver`
2. Откройте http://127.0.0.1:8000/admin/
3. Войдите с учетными данными суперпользователя

---

## Как создать нового суперпользователя

```bash
cd core
python manage.py createsuperuser
```

Вам будет предложено ввести:
- Email (используется как username)
- Username (опционально)
- Password (введите дважды)

---

## Как сбросить пароль существующего пользователя

### Способ 1: Через Django shell
```bash
cd core
python manage.py shell
```

Затем:
```python
from accounts.models import User
user = User.objects.get(email='ваш@email.com')
user.set_password('новый_пароль')
user.save()
print("Пароль изменен!")
```

### Способ 2: Через команду changepassword
```bash
cd core
python manage.py changepassword ваш@email.com
```

---

## Как посмотреть всех пользователей через команду

Создайте временный скрипт `show_users.py` в папке `core`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User

print("=== ВСЕ ПОЛЬЗОВАТЕЛИ ===")
users = User.objects.all()
if users:
    for u in users:
        print(f"\nEmail: {u.email}")
        print(f"Username: {u.username}")
        print(f"Role: {u.role}")
        print(f"Is Staff: {u.is_staff}")
        print(f"Is Superuser: {u.is_superuser}")
        print("-" * 40)
else:
    print("Пользователей нет в базе")
```

Затем запустите:
```bash
cd core
python show_users.py
```

---

## Важно!

**Пароли в Django нельзя просто "посмотреть"** - они хранятся в хешированном виде для безопасности.

Если вы забыли пароль:
- Используйте `changepassword` для сброса
- Или создайте нового суперпользователя

