# 🚀 Task Management Application

Полнофункциональное веб-приложение для управления задачами с **Kanban-доской**, фильтрацией по тегам и категориям, *
*JWT-аутентификацией** и аналитикой.

---

## 🛠 Стек технологий

* **Backend:** Python 3.11+, Django, Django REST Framework (DRF), SimpleJWT
* **Frontend:** Vue 3, Vite, TypeScript, Pinia, Vue Router
* **База данных:** PostgreSQL 16
* **Инфраструктура:** Docker, Docker Compose, Makefile

---

## 📋 Требования

Устанавливать Python, Node.js или PostgreSQL локально **не требуется** — все сервисы запускаются внутри
Docker-контейнеров.

Перед началом работы необходимо установить:

1. [Git](https://git-scm.com/)
2. [Docker Desktop](https://www.docker.com/products/docker-desktop/)

> **Важно:** перед запуском проекта убедитесь, что Docker Desktop запущен.

---

## ⚡️ Быстрый запуск

### 1. Клонирование репозитория

Откройте терминал (Git Bash, PowerShell или Терминал macOS) и выполните:

```bash
git clone <URL_РЕПОЗИТОРИЯ>
cd <ИМЯ_ПАПКИ_ПРОЕКТА>
```

### 2. Создание файла `.env`

Скопируйте готовый шаблон переменных окружения:

```bash
cp .env.example .env
```

> 💡 Настройки по умолчанию в `.env` уже подготовлены для локального запуска.

### 3. Запуск контейнеров

Запустите сборку и все необходимые сервисы:

```bash
make up
```

Если команда `make` недоступна, используйте:

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

Следуйте инструкциям в терминале и укажите логин, email и пароль.

При необходимости можно заполнить базу демонстрационными данными:

```bash
docker compose exec web python manage.py seed_demo
```

🎉 **Готово! Проект запущен и готов к работе.**

---

## 🌐 Доступ к приложению

После запуска сервисы доступны по следующим адресам:

| Сервис              | URL                                                                |
|---------------------|--------------------------------------------------------------------|
| 🖥 **Frontend**     | [http://localhost:5173](http://localhost:5173)                     |
| ⚙️ **Backend API**  | [http://localhost:8000/api/](http://localhost:8000/api/)           |
| 📚 **Swagger UI**   | [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) |
| 🔐 **Django Admin** | [http://localhost:8000/admin/](http://localhost:8000/admin/)       |

---

## 🛠 Основные команды

При наличии `make` можно использовать следующие команды:

| Команда          | Описание                                         | Эквивалент без Make                                        |
|------------------|--------------------------------------------------|------------------------------------------------------------|
| `make up`        | Запускает все сервисы в фоне                     | `docker compose up -d`                                     |
| `make down`      | Останавливает и удаляет контейнеры               | `docker compose down`                                      |
| `make restart`   | Перезапускает контейнеры                         | `docker compose restart`                                   |
| `make logs`      | Показывает логи всех сервисов в реальном времени | `docker compose logs -f`                                   |
| `make migrate`   | Применяет миграции базы данных                   | `docker compose exec web python manage.py migrate`         |
| `make superuser` | Создаёт администратора                           | `docker compose exec web python manage.py createsuperuser` |
| `make ps`        | Показывает статус контейнеров                    | `docker compose ps`                                        |

---

## 📡 API

Полная интерактивная документация API доступна через **Swagger UI**:

[http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)

### 🔑 Аутентификация

| Метод  | Endpoint              | Описание                                                 |
|--------|-----------------------|----------------------------------------------------------|
| `POST` | `/api/register/`      | Регистрация нового пользователя                          |
| `POST` | `/api/token/`         | Авторизация и получение JWT `access` и `refresh` токенов |
| `POST` | `/api/token/refresh/` | Обновление `access`-токена                               |

### 📝 Задачи

Для работы с задачами требуется JWT-аутентификация:

```http
Authorization: Bearer <token>
```

| Метод    | Endpoint            | Описание                                    |
|----------|---------------------|---------------------------------------------|
| `GET`    | `/api/tasks/`       | Получить список задач текущего пользователя |
| `POST`   | `/api/tasks/`       | Создать новую задачу                        |
| `GET`    | `/api/tasks/<id>/`  | Получить информацию о задаче                |
| `PATCH`  | `/api/tasks/<id>/`  | Обновить задачу                             |
| `DELETE` | `/api/tasks/<id>/`  | Удалить задачу                              |
| `GET`    | `/api/tasks/stats/` | Получить статистику по задачам              |

Через `PATCH` можно, например, изменить:

* статус выполнения;
* приоритет;
* заголовок задачи.

---

## ❓ Troubleshooting

### 1. `ports are allocated` / `port is already allocated`

**Проблема:** порт `8000` или `5432` уже используется другой программой, например локальным PostgreSQL.

**Решение:** остановите конфликтующий сервис или освободите порт.

#### Windows PowerShell

```powershell
Stop-Service postgresql*
```

#### Linux / macOS

```bash
sudo service postgresql stop
```

После освобождения портов снова запустите проект:

```bash
make up
```

---

### 2. `FATAL: role "-d" does not exist`

**Проблема:** файл `.env` отсутствует или повреждён. В результате Docker получает некорректные значения переменных
окружения.

**Решение:** пересоздайте `.env` из шаблона:

```bash
cp .env.example .env
```

Затем перезапустите контейнеры:

```bash
make restart
```

При необходимости можно выполнить полный перезапуск:

```bash
docker compose down
docker compose up -d --build
```

---

### 3. `make` не распознаётся в Windows

**Проблема:** утилита `make` обычно не входит в стандартную установку Windows.

**Решение:** используйте один из вариантов:

* запустите команды через **Git Bash**;
* установите `make`;
* используйте эквивалентные команды `docker compose`.

Например:

```bash
make up
```

можно заменить на:

```bash
docker compose up -d
```

---

### 4. Frontend не может подключиться к Backend

Если в браузере появляются ошибки вроде:

```text
net::ERR_CERT_AUTHORITY_INVALID
```

или ошибки CORS, проверьте настройки `.env`.

Убедитесь, что используются `http://`, а не `https://`:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4173
```

После изменения `.env` перезапустите контейнеры:

```bash
make restart
```

---

## 📁 Структура проекта

```text
.
├── backend/               # Исходный код Django REST Framework
│   ├── apps/              # Модули приложения (tasks, users, categories)
│   ├── config/            # Конфигурация Django (settings, urls)
│   ├── Dockerfile         # Dockerfile backend-сервиса
│   └── manage.py
│
├── frontend/              # Исходный код Vue 3 + Vite
│   ├── src/               # Компоненты, Pinia stores, роутер
│   └── Dockerfile         # Dockerfile frontend-сервиса
│
├── .env.example           # Шаблон переменных окружения
├── docker-compose.yml     # Конфигурация Docker Compose
├── Makefile               # Команды автоматизации
└── README.md              # Документация проекта
```

---

## 🐳 Архитектура

Проект состоит из трёх основных сервисов:

```text
┌─────────────────────┐
│      Frontend       │
│   Vue 3 + Vite      │
│   localhost:5173    │
└──────────┬──────────┘
           │
           │ HTTP / REST API
           ▼
┌─────────────────────┐
│       Backend       │
│ Django + DRF + JWT  │
│   localhost:8000    │
└──────────┬──────────┘
           │
           │ PostgreSQL
           ▼
┌─────────────────────┐
│      Database       │
│    PostgreSQL 16    │
│      port 5432      │
└─────────────────────┘
```

---

## 🔐 Аутентификация

Для авторизации используется **JWT (JSON Web Token)**.

Процесс авторизации:

1. Пользователь регистрируется через `/api/register/`.
2. Пользователь отправляет логин и пароль на `/api/token/`.
3. Backend возвращает `access` и `refresh` токены.
4. `access`-токен используется для авторизованных запросов.
5. При истечении срока действия `access`-токена используется `/api/token/refresh/`.

Пример заголовка авторизованного запроса:

```http
Authorization: Bearer <access_token>
```

---

## 📊 Основные возможности

* ✅ Регистрация и авторизация пользователей
* ✅ JWT-аутентификация
* ✅ Создание, редактирование и удаление задач
* ✅ Kanban-доска
* ✅ Управление статусами задач
* ✅ Приоритеты задач
* ✅ Фильтрация по тегам и категориям
* ✅ Статистика и аналитика
* ✅ REST API
* ✅ Swagger-документация
* ✅ Django Admin
* ✅ PostgreSQL
* ✅ Docker-контейнеризация
* ✅ Vue 3 + TypeScript
* ✅ Pinia для управления состоянием

---

## 🚀 Production

Текущая конфигурация предназначена прежде всего для **локальной разработки и демонстрации проекта**.

Перед использованием в production необходимо отдельно настроить:

* `DEBUG=False`;
* безопасные секретные ключи;
* production-переменные окружения;
* HTTPS;
* CORS;
* CSRF;
* настройки PostgreSQL;
* reverse proxy;
* production-сборку frontend;
* хранение секретов;
* резервное копирование базы данных;
* мониторинг и логирование.

---
