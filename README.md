[![CI Pipeline](https://github.com/madiyar-git/Week4_Backend/actions/workflows/ci.yml/badge.svg)](https://github.com/madiyar-git/Week4_Backend/actions/workflows/ci.yml)

# 🚀 Task Management Application

Полнофункциональное веб-приложение для управления задачами с **Kanban-доской**, фильтрацией по тегам и категориям, *
*JWT-аутентификацией**, фоновой обработкой задач и аналитикой.

---

# Стек технологий

* **Backend:** Python 3.11+, Django, Django REST Framework (DRF), SimpleJWT
* **Frontend:** Vue 3, Vite, TypeScript, Pinia, Vue Router
* **Асинхронные задачи и очередь:** Celery, Celery Beat, Redis, Flower
* **База данных:** PostgreSQL 16
* **Инфраструктура:** Docker, Docker Compose, Makefile

---

# Локальный запуск проекта

Устанавливать Python, Node.js, PostgreSQL или Redis локально **не требуется** — все сервисы запускаются внутри
Docker-контейнеров.

```bash
python -m venv venv
```

### Активация для Windows

```bash
venv\Scripts\activate
```

```bash
source venv/bin/activate
```

---

## 2. Установка зависимостей

```bash
cp .env.example .env
```

> 💡 Настройки по умолчанию в `.env` уже подготовлены для локального запуска всех сервисов, включая Redis, Celery и
> Flower.

### 3. Запуск контейнеров

Запустите сборку и все сервисы (Web, Frontend, Database, Redis, Worker, Beat, Flower):

```bash
make up
```

Если утилита `make` недоступна, используйте:

```bash
docker compose up -d --build
```

### 4. Подготовка базы данных

Примените миграции:

```bash
make migrate
```

Создайте администратора:

```bash
make superuser
```

Заполните базу демонстрационными данными (по желанию):

```bash
docker compose exec web python manage.py seed_demo
```

🎉 **Готово! Проект запущен и готов к работе.**

---

## 🌐 Доступ к приложению

После запуска сервисы доступны по следующим адресам:

| Сервис                 | URL                                                                | Доступы по умолчанию               |
|:-----------------------|:-------------------------------------------------------------------|:-----------------------------------|
| 🖥 **Frontend**        | [http://localhost:5173](http://localhost:5173)                     | —                                  |
| ⚙️ **Backend API**     | [http://localhost:8000/api/](http://localhost:8000/api/)           | —                                  |
| 📚 **Swagger UI**      | [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) | —                                  |
| 🔐 **Django Admin**    | [http://localhost:8000/admin/](http://localhost:8000/admin/)       | Данные `superuser`                 |
| 🌸 **Flower (Celery)** | [http://localhost:5555](http://localhost:5555)                     | Login: `admin` / Pass: `adminpass` |

---

## 🛠 Основные команды

| Команда          | Описание                               | Эквивалент без Make                                        |
|:-----------------|:---------------------------------------|:-----------------------------------------------------------|
| `make up`        | Запускает все сервисы в фоне           | `docker compose up -d`                                     |
| `make down`      | Останавливает и удаляет контейнеры     | `docker compose down`                                      |
| `make restart`   | Перезапускает контейнеры               | `docker compose restart`                                   |
| `make logs`      | Логи всех сервисов в реальном времени  | `docker compose logs -f`                                   |
| `make migrate`   | Применяет миграции базы данных         | `docker compose exec web python manage.py migrate`         |
| `make superuser` | Создаёт администратора                 | `docker compose exec web python manage.py createsuperuser` |
| `make test`      | Запускает юнит- и интеграционные тесты | `docker compose exec web pytest`                           |
| `make ps`        | Показывает статус всех контейнеров     | `docker compose ps`                                        |

---

## 🐳 Архитектура

Проект состоит из следующей инфраструктуры контейнеров:

```text
┌─────────────────────┐      HTTP / REST     ┌─────────────────────┐
│      Frontend       │ ───────────────────► │       Backend       │
│    Vue 3 + Vite     │                      │ Django + DRF + JWT  │
│   localhost:5173    │                      │   localhost:8000    │
└─────────────────────┘                      └──────────┬──────────┘
                                                        │
                      ┌─────────────────────────────────┼─────────────────────────────────┐
                      ▼                                 ▼                                 ▼
           ┌─────────────────────┐           ┌─────────────────────┐           ┌─────────────────────┐
           │      Database       │           │    Redis Broker     │           │    Celery Worker    │
           │    PostgreSQL 16    │           │    In-Memory DB     │ ◄───────► │   Background Tasks  │
           │      port 5432      │           │      port 6379      │           └─────────────────────┘
           └─────────────────────┘           └──────────┬──────────┘                      ▲
                                                        │                                 │
                                                        ▼                                 │
                                             ┌─────────────────────┐                      │
                                             │     Celery Beat     │ ─────────────────────┘
                                             │ Periodic Scheduler  │
                                             └─────────────────────┘
                                                        │
                                                        ▼
                                             ┌─────────────────────┐
                                             │    Flower Monitor   │
                                             │   localhost:5555    │
                                             └─────────────────────┘
```

---

## ⚙️ Фоновые и периодические задачи (Celery + Redis + Flower)

Для обработки длительных операций (отправка email, уведомления по webhook, внешние API) и периодических скриптов очистки
используются **Celery**, **Celery Beat** и **Redis**.

### 1. Сервисы фоновой обработки

* **`redis`**: Брокер сообщений и бэкенд результатов.
* **`celery_worker`**: Исполнитель фоновых задач.
* **`celery_beat`**: Планировщик периодических задач (cron).
* **`flower`**: Веб-панель для мониторинга очередей и производительности воркеров.

### 2. Просмотр логов фоновых сервисов

```bash
# Логи исполняющего воркера Celery
docker compose logs -f celery_worker

# Логи планировщика периодических задач (Beat)
docker compose logs -f celery_beat

# Логи панели мониторинга Flower
docker compose logs -f flower

# Логи брокера Redis
docker compose logs -f redis
```

### 3. Расписание периодических задач

| Задача                  | Расписание     | Описание                             |
|:------------------------|:---------------|:-------------------------------------|
| `cleanup_expired_tasks` | Каждые 5 минут | Очистка устаревших завершенных задач |

### 4. Тестирование Celery-задач

Тесты Celery-задач выполняются изолированно (с использованием `unittest.mock` и кэша):

```bash
docker compose exec web pytest tests/unit/test_celery_tasks.py
```

---

## 📡 API & Аутентификация

Полная интерактивная документация доступна в **Swagger UI
**: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

Для авторизации используется **JWT (JSON Web Token)**. Передавайте полученный `access`-токен в заголовке запроса:

```http
Authorization: Bearer <access_token>
```

### 🔑 Основные Endpoints

| Метод                      | Endpoint              | Описание                                         |
|:---------------------------|:----------------------|:-------------------------------------------------|
| `POST`                     | `/api/register/`      | Регистрация пользователя                         |
| `POST`                     | `/api/token/`         | Получение JWT токенов (`access` и `refresh`)     |
| `POST`                     | `/api/token/refresh/` | Обновление `access`-токена                       |
| `GET` / `POST`             | `/api/tasks/`         | Получение списка и создание задач                |
| `GET` / `PATCH` / `DELETE` | `/api/tasks/<id>/`    | Просмотр, частичное обновление и удаление задачи |
| `GET`                      | `/api/tasks/stats/`   | Статистика по задачам пользователя               |

---

## ❓ Troubleshooting

### 1. `ports are allocated` / `port is already allocated`

**Проблема:** Порт `8000`, `5432` или `6379` занят другой локальной службой.
**Решение:** Остановите системный PostgreSQL/Redis или свободный сервис:

* **Windows (PowerShell):** `Stop-Service postgresql*`
* **Linux/macOS:** `sudo service postgresql stop`

### 2. `FATAL: role "-d" does not exist`

**Проблема:** Отсутствует файл `.env`.
**Решение:** Пересоздайте `.env` из шаблона:

```bash
cp .env.example .env
make restart
```

### 3. Frontend не подключается к Backend (CORS / SSL Error)

Убедитесь, что в файле `.env` используется протокол `http://`, а не `https://`:

---

---

### Обновление access-токена

```text
.
├── backend/               # Исходный код Django REST Framework
│   ├── apps/              # Модули приложения (tasks, users, categories)
│   ├── config/            # Настройки Django, Celery, URLs
│   ├── tests/             # Модульные и интеграционные тесты
│   ├── Dockerfile         # Dockerfile backend-сервиса
│   └── manage.py
│
├── frontend/              # Исходный код Vue 3 + Vite
│   ├── src/               # Компоненты, Pinia stores, Vue Router
│   └── Dockerfile         # Dockerfile frontend-сервиса
│
├── notes/                 # Архитектурная документация и отчеты (async, ssr)
│   └── async-and-ssr.md
├── .env.example           # Шаблон переменных окружения
├── docker-compose.yml     # Оркестрация контейнеров
├── Makefile               # Команды автоматизации
└── README.md              # Документация проекта
```

Получение нового access-токена с помощью refresh-токена.

## 🚀 Production

Текущий сетап предназначен для локальной разработки и демонстрации. Для деплоя в Production дополнительно требуется:

* `DEBUG=False` и генерация стойких секретных ключей;
* Настройка SSL/TLS (HTTPS) и защита портов базы данных и Redis;
* Интеграция Sentry для отслеживания ошибок бэкенда и Celery;
* Настройка Dead-Letter Queue (DLQ) для непредвиденных сбоев фоновых задач.
