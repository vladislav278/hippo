# Установка пароля администратора на Railway

## Способ 1: Через веб-консоль Railway (без CLI)

1. Откройте ваш проект на Railway: https://railway.app
2. Откройте ваш сервис (не базу данных)
3. Перейдите в раздел **"Deployments"**
4. Откройте последний деплой
5. Нажмите на вкладку **"View Logs"** или найдите кнопку **"Terminal"** / **"Console"**
6. В открывшейся консоли выполните:

```bash
cd core
python manage.py set_admin_password icq38307288@gmail.com Admin123!@#
```

Или через Django shell:

```bash
cd core
python manage.py shell
```

Затем в shell выполните:
```python
from accounts.models import User
user = User.objects.get(email='icq38307288@gmail.com')
user.set_password('Admin123!@#')
user.save()
print('Пароль успешно изменен!')
exit()
```

---

## Способ 2: Установка Railway CLI (для будущего использования)

### Windows (через npm):

1. Установите Node.js с сайта: https://nodejs.org/
2. После установки откройте PowerShell или Command Prompt
3. Выполните:
```bash
npm install -g @railway/cli
```

### Windows (через установщик):

1. Скачайте установщик Railway CLI для Windows:
   - Перейдите на: https://github.com/railwayapp/cli/releases
   - Скачайте последнюю версию для Windows (`.exe` файл)
2. Запустите установщик

### После установки Railway CLI:

1. Войдите в Railway:
```bash
railway login
```

2. Подключитесь к проекту:
```bash
cd C:\Users\icq38\Desktop\HACKATON\Tretie_mnenie_verion\tretie_mnenie
railway link
```
Выберите ваш проект из списка

3. Установите пароль администратора:
```bash
railway run python manage.py set_admin_password icq38307288@gmail.com Admin123!@#
```

Или через shell:
```bash
railway run python manage.py shell
```
Затем в shell:
```python
from accounts.models import User
user = User.objects.get(email='icq38307288@gmail.com')
user.set_password('Admin123!@#')
user.save()
exit()
```

---

## Способ 3: Создать нового суперпользователя

Если пользователя нет в базе на Railway:

```bash
cd core
python manage.py createsuperuser
```

Введите:
- Email: `icq38307288@gmail.com`
- Username: `admin`
- Password: `Admin123!@#`
- Password (again): `Admin123!@#`

---

## Проверка

После установки пароля попробуйте войти в админку:
- URL: `https://web-production-5dc97.up.railway.app/admin/`
- Email: `icq38307288@gmail.com`
- Password: `Admin123!@#`

