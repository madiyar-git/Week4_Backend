# Тема: Ручное соединение Many-to-Many таблиц (Task and Tag)

Для извлечения связей между задачами и тегами используется соединение через промежуточную таблицу `tasks_task_tags`.

## SQL Запрос

```commandline
SELECT 
    tasks_task.id AS task_id,
    tasks_task.title AS task_title,
    tasks_tag.name AS tag_name,
    tasks_tag.color AS tag_color
FROM tasks_task
INNER JOIN tasks_task_tags ON tasks_task.id = tasks_task_tags.task_id
INNER JOIN tasks_tag ON tasks_task_tags.tag_id = tasks_tag.id;
```
## SQL который генерит ORM
#### Input:
```commandline
from django.db import models
from tasks.models import Task

stats_query = Task.objects.filter(owner_id=2).values('owner_id').annotate(
    total_tasks=models.Count('id'),
    completed_tasks=models.Count('id', filter=models.Q(completed=True)),
    active_tasks=models.Count('id', filter=models.Q(completed=False))
).query

print(stats_query)
```

#### Output:
```commandline
    SELECT "tasks_task"."owner_id" AS "owner_id",
        COUNT("tasks_task"."id") AS "total_tasks", 
        COUNT("tasks_task"."id") FILTER (WHERE "tasks_task"."completed") AS "completed_tasks", 
        COUNT("tasks_task"."id") FILTER (WHERE NOT "tasks_task"."completed") AS "active_tasks" 
    FROM "tasks_task" 
    WHERE "tasks_task"."owner_id" = 2 
    GROUP BY 1
```