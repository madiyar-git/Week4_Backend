## Запуск проекта (How to Run)

### 1. Настройка окружения

Перед запуском бэкенда необходимо настроить переменные окружения. Скопируй шаблон `.env.example` в новый файл `.env` и
заполни значения локальными данными:

```bash
cp .env.example .env
```

## Установка PostgreSQL

### 1. Запуск БД в Docker

```
docker run --name pg-internship -e POSTGRES_PASSWORD=<password> -e POSTGRES_USER=internship -e POSTGRES_DB=internship_dev -p 5433:5432 -d postgres:16
```

### 2. Миграции и создание админа

```
python manage.py migrate
python manage.py createsuperuser
```

### 3. Наполнение демо-данными

```
python manage.py seed_demo
```

## Django + PostgreSQL в Docker

### Требования:

* Docker, Docker compose
* Утилита `make`(Для linux/ macOS или Git Bash для Windows)

## Запуск:

### 1. Создать .env файл:

### Cкопировать настройки по умолчанию:

```bash
cp .env.example .env
```

### 1. Запуск контейнера:

```bash
make up
```

### 2. Миграция для БД:

```bash
make migrate
```

### 3. Создание суперюзера:

```bash
make superuser
```