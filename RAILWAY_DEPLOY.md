# Инструкция по деплою на Railway

## Шаги для деплоя:

1. **Подключите проект к Railway:**
   - Зайдите на [railway.app](https://railway.app)
   - Создайте новый проект
   - Подключите GitHub репозиторий

2. **Добавьте PostgreSQL базу данных:**
   - В Railway Dashboard нажмите "New" → "Database" → "PostgreSQL"
   - Railway автоматически создаст переменную окружения `DATABASE_URL`

3. **Настройте переменные окружения:**
   В Railway Dashboard → Settings → Variables добавьте:
   
   ```
   SECRET_KEY=ваш-секретный-ключ-для-production
   DEBUG=False
   ALLOWED_HOSTS=ваш-домен.railway.app,*.railway.app
   CSRF_TRUSTED_ORIGINS=https://ваш-домен.railway.app,https://*.railway.app
   ADMIN_EMAIL=ваш-email@example.com
   ADMIN_PASSWORD=ваш-пароль
   ADMIN_FIRST_NAME=Имя
   ADMIN_LAST_NAME=Фамилия
   ```
   
   **Важно:** Замените `ваш-домен.railway.app` на реальный домен вашего Railway приложения (например, `web-production-5dc97.up.railway.app`).

4. **Сгенерируйте SECRET_KEY:**
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

5. **Деплой:**
   - Railway автоматически определит проект по `Procfile`
   - При каждом push в GitHub будет автоматический деплой
   - Миграции и создание админа выполнятся автоматически

## Локальная разработка:

Проект продолжит работать локально с SQLite:
```bash
cd backend
python manage.py runserver
```

## Проверка:

После деплоя проверьте:
- ✅ Сайт открывается
- ✅ Админ панель доступна по `/admin/`
- ✅ Статические файлы загружаются
- ✅ База данных работает

