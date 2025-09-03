# News Portal 🗞️

Django-приложение для полнофункционального новостного портала с системой подписок, email-уведомлениями, мультиязычностью и фоновыми задачами на Celery.

![Django](https://img.shields.io/badge/Django-4.2-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Celery](https://img.shields.io/badge/Celery-5.3-green)
![Redis](https://img.shields.io/badge/Redis-7.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Возможности

-   **Публикация контента**: Новости и статьи с разделением по категориям.
-   **Система подписок**: Пользователи могут подписываться на категории.
-   **Мгновенные уведомления**: Отправка email при публикации новости в категории.
-   **Еженедельные дайджесты**: Автоматическая рассылка подборок за неделю.
-   **Аутентификация**: Регистрация через email и OAuth (Google, Yandex).
-   **Мультиязычность**: Поддержка русского и английского языков (i18n).
-   **Панель администратора**: Расширенное управление контентом и пользователями.
-   **Логирование**: Настройка логов для разных уровней событий.
-   **Кэширование**: Повышение производительности через кэш.
-   **Фоновые задачи**: Выполнение длительных операций через Celery и Redis.

## 🛠 Технологии

-   **Backend**: Django 4.2, Django REST Framework (DRF)
-   **База данных**: SQLite (разработка), PostgreSQL (продакшен)
-   **Асинхронные задачи**: Celery, Redis
-   **Фронтенд**: Bootstrap 5, HTML5, CSS3
-   **Аутентификация**: Django Allauth (Social Auth)
-   **Интернационализация**: Django ModelTranslation
-   **Кэширование**: Django Redis Cache
-   **Логирование**: Встроенное логирование Django (файлы и консоль)
-   **Деплой**: Docker, Gunicorn, Nginx (готово к настройке)

## 📦 Установка и запуск

### Предварительные требования

-   Python 3.9+
-   Redis Server
-   Виртуальное окружение (рекомендуется)

### 1. Клонирование репозитория

```bash
git clone https://github.com/<your-username>/NewsPortal.git
cd NewsPortal
```


###  2. Настройка виртуального окружения и зависимостей
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ИЛИ
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Настройка переменных окружения
1. Создайте файл .env в корне проекта (на основе .env.example):

2. Заполните необходимые переменные:
```bash
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-oauth2-key
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-oauth2-secret
SOCIAL_AUTH_YANDEX_OAUTH2_KEY=your-yandex-oauth2-key
SOCIAL_AUTH_YANDEX_OAUTH2_SECRET=your-yandex-oauth2-secret
```

### 4. Применение миграций и создание суперпользователя
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Запуск Redis
Для Linux/macOS:
```bash
sudo systemctl start redis-server
```

Или:
```bash
redis-server
```

Для Windows:

Скачайте и запустите Redis с официального сайта или используйте WSL.

### 6. Запуск сервера разработки и Celery

#### Откройте три отдельных терминала:

Терминал 1 - Celery Worker:
```bash
celery -A NewsPortal worker -l info -P solo
```
Терминал 2 - Celery Beat (для периодических задач):
```bash
celery -A NewsPortal beat -l info
```
Терминал 3 - Django сервер:
```bash
python manage.py runserver
```

# 📁 Структура проекта
```text
NewsPortal/
├── NewsPortal/           # Настройки проекта (Django)
│   ├── settings.py      # Основные настройки (база, логи, кэш, celery)
│   ├── urls.py          # Корневые URL
│   └── __init__.py
├── portal/              # Основное приложение
│   ├── models.py        # Модели: Post, Category, Author, Comment
│   ├── views.py         # Представления (включая кэширование)
│   ├── admin.py         # Конфигурация админ-панели
│   ├── signals.py       # Сигналы (отправка уведомлений)
│   ├── tasks.py         # Celery задачи (уведомления, дайджесты)
│   ├── templates/       # HTML шаблоны
│   ├── management/      # Кастомные команды
│   └── __init__.py
├── templates/           # Глобальные шаблоны (наследование)
├── static/              # Статические файлы (CSS, JS, изображения)
├── logs/                # Директория для логов (создается автоматически)
├── .env.example         # Пример переменных окружения
├── .gitignore           # Git ignore правила
├── requirements.txt     # Зависимости Python
└── README.md            # Этот файл
```

# ⚙️ Конфигурация

##  Настройка электронной почты
#### Для работы email-уведомлений (регистрация, подписки) настройте в .env:
```ini
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=465
EMAIL_HOST_USER=your-email@yandex.ru
EMAIL_HOST_PASSWORD=your-app-specific-password
EMAIL_USE_SSL=True
DEFAULT_FROM_EMAIL=your-email@yandex.ru
```

#### Для Gmail или других почтовых служб измените EMAIL_HOST и порт.

### Настройка OAuth (Google, Yandex)

#### 1. Получите ключи и секреты для вашего приложения на Google Cloud Console или Yandex OAuth.

#### 2. Добавьте их в файл .env как указано выше.

#### 3. В админ-панели Django добавьте социальные приложения (Sites / Social Applications).

### Логирование
#### Приложение пишет логи в директорию logs/:

#### - general.log - общая информация (уровень INFO)

#### - errors.log - ошибки (уровень ERROR)

#### - security.log - события безопасности

####  Настройки логирования можно изменить в NewsPortal/settings.py.

## 🚀 Деплой на продакшен

### С помощью Docker (рекомендуется)
#### В проекте подготовлены конфиги для деплоя. Для запуска:

#### Настройте docker-compose.prod.yml (если необходимо).

#### Запустите:
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

### На VPS/Хостинг

#### 1. Установите зависимости, настройте базу данных (PostgreSQL).

#### 2. Соберите статику: python manage.py collectstatic --noinput.

#### 3. Настройте веб-сервер (Nginx/Apache) и WSGI (Gunicorn/uWSGI).

#### 4. Настройте демонов для Celery worker и beat (systemd/supervisord).

## 👨‍💻 Разработка

#### Добавление нового перевода
#### Пометить строки для перевода в коде: from django.utils.translation import gettext as _

#### Создать файлы сообщений:
```bash
django-admin makemessages -l en  # для английского
```
#### Отредактировать файлы .po в locale/en/LC_MESSAGES/django.po.

#### Скомпилировать переводы:
```bash
django-admin compilemessages
```
### Создание новых кастомных команд

####  Размещайте команды управления в portal/management/commands/. 
####  Пример: python manage.py delete_news_by_category.

## 🔗 Полезные ссылки

- [Документация Django](https://docs.djangoproject.com/)
- [Документация Celery](https://docs.celeryq.dev/)
- [Документация Redis](https://redis.io/documentation)
- [Документация Django Allauth](https://django-allauth.readthedocs.io/)
