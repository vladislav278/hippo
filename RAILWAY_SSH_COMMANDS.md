# Команды для работы через Railway SSH

## Проблема: Django не найден

Если получаете ошибку `ModuleNotFoundError: No module named 'django'`, попробуйте:

### 1. Проверить, где установлен Python и зависимости:

```bash
# Проверить версию Python
which python
which python3

# Проверить установленные пакеты
pip list | grep -i django
pip3 list | grep -i django

# Проверить переменные окружения
echo $PYTHONPATH
echo $VIRTUAL_ENV
```

### 2. Попробовать разные варианты Python:

```bash
cd /app/core

# Вариант 1
python3 manage.py set_admin_password icq38307288@gmail.com 'Admin123!@#'

# Вариант 2 (если есть виртуальное окружение)
source venv/bin/activate
python manage.py set_admin_password icq38307288@gmail.com 'Admin123!@#'

# Вариант 3 (через pip установленный Django)
python -m django set_admin_password icq38307288@gmail.com 'Admin123!@#'
```

### 3. Использовать Django shell напрямую:

```bash
cd /app/core

# Найти где установлен Django
python3 -c "import django; print(django.__file__)"

# Если Django найден, используйте shell
python3 manage.py shell
```

Затем в shell:
```python
from accounts.models import User
user = User.objects.get(email='icq38307288@gmail.com')
user.set_password('Admin123!@#')
user.save()
print('Пароль успешно изменен!')
exit()
```

### 4. Проверить структуру проекта:

```bash
# Посмотреть где мы находимся
pwd
ls -la

# Проверить requirements.txt
cat ../requirements.txt

# Установить зависимости вручную (если нужно)
pip install -r ../requirements.txt
```

### 5. Альтернатива - использовать переменные окружения для автоматической установки:

Вместо ручной установки пароля, добавьте в Railway Variables:
- `ADMIN_EMAIL` = `icq38307288@gmail.com`
- `ADMIN_PASSWORD` = `Admin123!@#`

И пароль установится автоматически при следующем деплое через `setup_admin.py`

