# Task Manager API (Backend)

Бэкенд-часть приложения для управления задачами.
Реализует REST API, ролевую модель доступа (каждый пользователь видит только свои данные) и безопасную авторизацию на базе JWT.

---

# Стек технологий

* **Язык:** Python 3.11+
* **Фреймворк:** Django, Django REST Framework (DRF)
* **Авторизация:** Django SimpleJWT (JWT — JSON Web Tokens)
* **База данных:** SQLite (для локальной разработки)
* **Гигиена кода:** python-dotenv (изоляция секретов и переменных окружения)

---

# Локальный запуск проекта

## 1. Создание виртуального окружения

```bash
python -m venv venv
```

### Активация для Windows

```bash
venv\Scripts\activate
```

### Активация для macOS / Linux

```bash
source venv/bin/activate
```

---

## 2. Установка зависимостей

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
python manage.py seed_demo
```
pip install -r requirements.txt
```

---

## 3. Настройка переменных окружения

Скопируйте шаблон конфигурации:

```bash
cp .env.example .env
```

После этого откройте файл `.env` и проверьте локальные параметры:

* `CORS_ALLOWED_ORIGINS`
* порты приложения
* настройки базы данных (при необходимости)

---

## 4. Применение миграций

```bash
python manage.py migrate
```

---

## 5. Создание суперпользователя

```bash
python manage.py createsuperuser
```

---

## 6. Запуск сервера

```bash
python manage.py runserver
```

После запуска API будет доступно по адресу:

```text
http://127.0.0.1:8000/
```

---

# API Эндпоинты

## Аутентификация

### Регистрация

```http
POST /api/register/
```

Создание нового аккаунта пользователя.

---

### Авторизация

```http
POST /api/token/
```

Получение `access` и `refresh` JWT-токенов.

---

### Обновление access-токена

```http
POST /api/token/refresh/
```

Получение нового access-токена с помощью refresh-токена.

---

# Управление задачами

> Все эндпоинты ниже доступны только авторизованным пользователям.

---

### Получить список задач

```http
GET /api/tasks/
```

Возвращает список задач текущего пользователя.
Сортировка: новые задачи отображаются сверху.

---

### Создать задачу

```http
POST /api/tasks/
```

---

### Получить задачу по ID

```http
GET /api/tasks/<id>/
```

---

### Частичное обновление задачи

```http
PATCH /api/tasks/<id>/
```

Примеры:

* изменение статуса `completed`
* изменение приоритета
* обновление заголовка или описания

---

## 🧪 Запуск тестов

* **Backend (в Docker):** `make test`
