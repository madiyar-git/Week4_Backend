# Отчёт: Перевод фоновых задач на Celery + Redis и оптимизация Latency

## 1. Выполненные работы

- Вынесены синхронные блокирующие операции (`send_welcome_email`, `send_task_created_notification`) из HTTP-цикла
  request/response в фоновые задачи Celery.
- Организована безопасная загрузка объектов в воркере с обработкой `ObjectDoesNotExist` (логирование и выгрузка без
  падения процесса).
- Заменен вызов `print` на модуль `logging`.
  > **Почему `print` бесполезен в фоновых задачах:**
  > В фоновых процессах Celery (в Docker-контейнерах или системных демонах) поток `stdout` перенаправляется или
  глушится. Сообщения из `print` не попадают в единую систему сбора логов, их невозможно ротировать и отслеживать в
  реальном времени.

---

## 2. Эксперимент с сериализацией Django Models

При попытке передать экземпляр модели `User` напрямую в асинхронную задачу:

```python
# НЕПРАВИЛЬНО:
send_welcome_email.delay(user)
```

### Зафиксированная ошибка:

```text
kombu.exceptions.EncodeError: Object of type User is not JSON serializable
# Или TypeError: Object of type User is not JSON serializable
```

### Причина и правило:

1. **JSON-сериализация:** Celery кодирует аргументы задач в JSON. Сложные объекты Python (модели ORM, datetime, сокеты)
   не могут быть автоматически преобразованы в JSON.
2. **Race Condition & Freshness:** Передача `user.id` (примитива `int`) гарантирует, что когда воркер подхватит задачу
   из очереди, он запросит актуальное состояние объекта из базы данных, избегая работы с устаревшим или неполным
   объектом.

---

## 3. Замеры производительности (`curl`)

Замеры времени отклика API на эндпоинтах создания сущностей (`POST /api/tasks/`):

| Сценарий                          |  HTTP Статус  | Время ответа (Total Time) | Поведение системы                                       |
|:----------------------------------|:-------------:|:-------------------------:|:--------------------------------------------------------|
| **1. Синхронный вызов**           | `201 Created` |         `~0.600s`         | HTTP-поток заблокирован до окончания отправки/задержки  |
| **2. Асинхронный вызов (Celery)** | `201 Created` |         `~0.074s`         | API отвечает моментально, задача ушла воркеру           |
| **3. Остановка Celery Worker**    | `201 Created` |         `~0.074s`         | Задача безопасно садится в Redis и ждет запуска воркера |
| **4. Сбой Redis (без таймаутов)** | `201 Created` |         `~95.48s`         | Зависание TCP-сокета ОС в ожидании ответа Docker-сети   |
| **5. Сбой Redis (с таймаутами)**  | `201 Created` |         `~0.581s`         | Перехват `try/except`, сбой залогирован, API не упал    |

---

## 4. Защита от сбоев инфраструктуры (Resilience)

Для предотвращения зависания запросов при абсолютной недоступности брокера Redis применены следующие настройки:

1. **Параметры сокета в `settings.py`:**
   ```python
   # Форсирование сокетных таймаутов на уровне redis-py
   _broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis_broker:6379/0")
   if "?" not in _broker_url:
       CELERY_BROKER_URL = f"{_broker_url}?socket_timeout=1.0&socket_connect_timeout=1.0&retry_on_timeout=false"
   
   CELERY_TASK_PUBLISH_RETRY = False
   CELERY_BROKER_CONNECTION_TIMEOUT = 1.0
   CELERY_BROKER_CONNECTION_MAX_RETRIES = 1
   ```

2. **Безопасный вызов во ViewSet:**
   ```python
   try:
       send_task_created_notification.apply_async(args=[task.id], retry=False)
   except Exception as exc:
       logger.error("Не удалось отправить задачу в Celery для task_id=%s: %s", task.id, exc)
   ```

# Celery: Надежность асинхронных задач

## 1. Декларативный Auto-Retry & Exponential Backoff

Для обработки временных сбоев (сетевые таймауты, 5xx ошибки внешних сервисов) используется декларативный повтор вместо
ручного вызова `self.retry()`.

* **`autoretry_for`**: список исключений, при которых Celery автоматически перезапустит задачу (например,
  `requests.exceptions.RequestException`).
* **`max_retries`**: максимальное количество повторов (по умолчанию 3).
* **`retry_backoff`**: включает экспоненциальный рост задержки между попытками ($1s \to 2s \to 4s \to 8s \dots$).
* **`retry_backoff_max`**: верхний предел задержки в секундах.
* **`retry_jitter=True`**: добавляет случайный разброс во время задержки (jitter). Защищает сервисы от эффекта *
  *Thundering Herd** (когда множество упавших задач одновременно атакуют внешний API после восстановления).

---

## 2. Ограничения времени выполнения (Time Limits)

Каждая фоновая задача должна иметь лимиты по времени, чтобы зависшие HTTP-запросы не блокировали воркеры навсегда.

* **`soft_time_limit`** (мягкий лимит): генерирует исключение `SoftTimeLimitExceeded` внутри задачи. Позволяет корректно
  завершить работу, закрыть соединения и залогировать ошибку.
* **`time_limit`** (жесткий лимит): отправляет сигнал `SIGKILL` процессу воркера на уровне ОС. Задача принудительно
  завершается.

---

## 3. Гарантия идемпотентности через Redis Cache

Поскольку брокеры сообщений (RabbitMQ, Redis) гарантируют доставку **at-least-once** (как минимум один раз), задача
может выполниться повторно. Для предотвращения дублирования действий (повторная отправка писем, списание средств)
используется паттерн идемпотентности через Redis Cache.

1. Перед выполнением основной бизнес-логики проверяется наличие ключа в кэше: `cache.get(f"key:{entity_id}")`.
2. Если ключ существует — задача мгновенно завершается (`Skipping`).
3. При успешном выполнении ключ устанавливается с TTL: `cache.set(key, True, timeout=86400)`.
4. В случае сетевой ошибки ключ сбрасывается (`cache.delete`), чтобы следующий автоматический ретрай мог выполнить
   задачу.

---

## 4. Эталонный паттерн задачи

```python
import logging
import requests
from django.core.cache import cache
from django.contrib.auth import get_user_model
from celery import shared_task
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(
  bind=True, autoretry_for=(RequestException,), retry_backoff=True, retry_backoff_max=600, retry_jitter=True,
  max_retries=3, soft_time_limit=10, time_limit=15, )
def send_welcome_email_idempotent( self, user_id: int ) -> bool:
  request_id = self.request.id
  attempt = self.request.retries + 1
  cache_key = f"welcome_email_sent:{user_id}"
  
  # 1. Проверка идемпотентности
  if cache.get(cache_key):
    logger.info("Task [%s]: Email already sent to User id=%s. Skipping.", request_id, user_id)
    return True
  
  try:
    user = User.objects.get(pk=user_id)
  except User.DoesNotExist:
    logger.warning("Task [%s]: User id=%s not found.", request_id, user_id)
    return False
  
  logger.info("Task [%s] (Attempt %s/3): Sending welcome email to User id=%s...", request_id, attempt, user_id)
  
  try:
    # Имитация отправки / вызова внешней системы
    cache.set(cache_key, True, timeout=86400)
    logger.info("Task [%s]: Email successfully sent to User id=%s", request_id, user_id)
    return True
  
  except Exception as exc:
    # При ошибке сбрасываем ключ, чтобы ретрай отработал
    cache.delete(cache_key)
    raise exc
```