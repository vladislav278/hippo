# Инструкция: Как залить проект на GitHub

## ШАГ 1: Настройте Git (если еще не настроено)

Откройте терминал в папке проекта и выполните:

```bash
git config user.name "Ваше Имя"
git config user.email "ваш@email.com"
```

**Пример:**
```bash
git config user.name "Иван Иванов"
git config user.email "ivan@example.com"
```

---

## ШАГ 2: Сделайте первый коммит

```bash
git commit -m "Initial commit: Django project for medical consultation platform"
```

---

## ШАГ 3: Создайте репозиторий на GitHub

1. Откройте https://github.com в браузере
2. Войдите в свой аккаунт (или зарегистрируйтесь)
3. Нажмите зеленую кнопку **"New"** или **"+"** в правом верхнем углу → **"New repository"**
4. Заполните:
   - **Repository name**: `tretie_mnenie` (или любое другое название)
   - **Description**: "Платформа для консилиумов врачей"
   - **Visibility**: выберите Public или Private
   - **НЕ СТАВЬТЕ ГАЛОЧКИ** на "Add a README file", "Add .gitignore", "Choose a license" (они уже есть)
5. Нажмите **"Create repository"**

---

## ШАГ 4: Подключите проект к GitHub

После создания репозитория GitHub покажет вам инструкции. Выполните эти команды:

**Если вы выбрали HTTPS (рекомендуется):**
```bash
git remote add origin https://github.com/ВАШ_USERNAME/tretie_mnenie.git
git branch -M main
git push -u origin main
```

**Если вы выбрали SSH:**
```bash
git remote add origin git@github.com:ВАШ_USERNAME/tretie_mnenie.git
git branch -M main
git push -u origin main
```

**ВАЖНО:** Замените `ВАШ_USERNAME` на ваш реальный username на GitHub!

---

## ШАГ 5: Введите пароль/токен

При первом push GitHub может попросить:
- **Пароль** (если используете HTTPS) - но GitHub больше не принимает обычные пароли
- **Personal Access Token** - нужно создать на GitHub

### Как создать Personal Access Token:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Выберите срок действия и права (нужно `repo`)
4. Скопируйте токен (показывается только один раз!)
5. Используйте токен вместо пароля при push

---

## Готово! ✅

После выполнения всех шагов ваш проект будет на GitHub по адресу:
`https://github.com/ВАШ_USERNAME/tretie_mnenie`

---

## Если что-то пошло не так:

**Ошибка "remote origin already exists":**
```bash
git remote remove origin
git remote add origin https://github.com/ВАШ_USERNAME/tretie_mnenie.git
```

**Проверить текущий remote:**
```bash
git remote -v
```

**Посмотреть статус:**
```bash
git status
```

