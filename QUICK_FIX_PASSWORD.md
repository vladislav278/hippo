# Быстрое решение: Установка пароля через веб-консоль Railway

## Самый простой способ:

1. Откройте https://railway.app
2. Войдите в ваш проект
3. Откройте ваш **сервис** (не базу данных)
4. Перейдите в раздел **"Deployments"**
5. Найдите последний деплой и нажмите на него
6. Найдите кнопку **"View Logs"** или **"Terminal"** / **"Console"**
7. В открывшейся консоли выполните:

```bash
cd core
python manage.py set_admin_password icq38307288@gmail.com Admin123!@#
```

Или через shell:

```bash
cd core
python manage.py shell
```

Затем в Python shell:
```python
from accounts.models import User
user = User.objects.get(email='icq38307288@gmail.com')
user.set_password('Admin123!@#')
user.save()
print('Пароль изменен!')
exit()
```

---

## Альтернатива: Через Railway CLI (правильный синтаксис)

Если Railway CLI установлен, попробуйте:

```bash
railway run --service <название-сервиса> python core/manage.py set_admin_password icq38307288@gmail.com "Admin123!@#"
```

Или с указанием рабочей директории:

```bash
railway run --service <название-сервиса> sh -c "cd core && python manage.py set_admin_password icq38307288@gmail.com 'Admin123!@#'"
```

Чтобы узнать название сервиса:
```bash
railway status
```

---

## Если пользователя нет - создайте нового:

```bash
cd core
python manage.py createsuperuser
```

Введите:
- Email: `icq38307288@gmail.com`
- Username: `admin` (или любой другой)
- Password: `Admin123!@#`
- Password (again): `Admin123!@#`

