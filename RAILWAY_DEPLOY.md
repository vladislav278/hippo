# Инструкция по деплою на Railway

## Шаг 1: Подготовка проекта

Проект уже настроен для Railway. Убедитесь, что все файлы закоммичены:

```bash
git add .
git commit -m "Configure for Railway deployment"
git push
```

## Шаг 2: Создание проекта на Railway

1. Зайдите на https://railway.app
2. Войдите через GitHub
3. Нажмите "New Project"
4. Выберите "Deploy from GitHub repo"
5. Выберите ваш репозиторий `tretie_mnenie`

## Шаг 3: Добавление PostgreSQL базы данных

1. В вашем проекте на Railway нажмите "+ New"
2. Выберите "Database" → "Add PostgreSQL"
3. Railway автоматически создаст базу данных

## Шаг 4: Настройка переменных окружения

В настройках вашего сервиса (не базы данных) добавьте переменные окружения:

1. Перейдите в Settings → Variables
2. Добавьте следующие переменные:

### Обязательные переменные:

- `SECRET_KEY` - сгенерируйте новый секретный ключ:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- `DEBUG` - установите `False` для production

- `ALLOWED_HOSTS` - укажите домен Railway (например: `your-app.railway.app`) или `*` для начала

### Автоматические переменные (Railway создаст их автоматически):

- `DATABASE_URL` - Railway автоматически создаст эту переменную при подключении PostgreSQL
  - Нужно подключить базу данных к сервису:
    - В настройках вашего сервиса → Variables
    - Нажмите "Add Reference"
    - Выберите вашу PostgreSQL базу данных
    - Выберите `DATABASE_URL`

## Шаг 5: Настройка деплоя

Railway автоматически определит, что это Django проект, благодаря:
- `Procfile`
- `requirements.txt`
- `railway.json`

## Шаг 6: Применение миграций

После первого деплоя нужно применить миграции:

1. В Railway откройте ваш сервис
2. Перейдите в раздел "Deployments"
3. Откройте последний деплой
4. В разделе "Logs" вы увидите, что миграции применяются автоматически (благодаря `railway.json`)

Или вручную через Railway CLI:
```bash
railway run python manage.py migrate
```

## Шаг 7: Создание суперпользователя

После деплоя создайте суперпользователя:

1. В Railway откройте ваш сервис
2. Перейдите в "Deployments" → последний деплой
3. Откройте консоль (Terminal)
4. Выполните:
```bash
cd core
python manage.py createsuperuser
```

Или через Railway CLI:
```bash
railway run python manage.py createsuperuser
```

## Шаг 8: Проверка работы

После деплоя Railway предоставит вам URL вида: `https://your-app.railway.app`

Проверьте:
- Главная страница: `https://your-app.railway.app/`
- API: `https://your-app.railway.app/api/accounts/register/`
- Админка: `https://your-app.railway.app/admin/`

## Полезные команды Railway CLI

Установите Railway CLI:
```bash
npm i -g @railway/cli
```

Войдите:
```bash
railway login
```

Подключитесь к проекту:
```bash
railway link
```

Просмотр логов:
```bash
railway logs
```

Запуск команд:
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

## Решение проблем

### Ошибка подключения к базе данных
- Убедитесь, что PostgreSQL база данных подключена к сервису
- Проверьте, что переменная `DATABASE_URL` доступна

### Ошибка статических файлов
- WhiteNoise уже настроен в `settings.py`
- Убедитесь, что `STATIC_ROOT` настроен правильно

### Ошибка миграций
- Выполните миграции вручную через Railway CLI или консоль

### DEBUG=True в production
- Установите `DEBUG=False` в переменных окружения Railway

## Обновление проекта

После изменений в коде:

```bash
git add .
git commit -m "Описание изменений"
git push
```

Railway автоматически задеплоит изменения!

