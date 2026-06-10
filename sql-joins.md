# Тема: Ручное соединение Many-to-Many таблиц (Task and Tag)

Для извлечения связей между задачами и тегами используется соединение через промежуточную таблицу `tasks_task_tags`.

## SQL Запрос

```sql
SELECT 
    tasks_task.id AS task_id,
    tasks_task.title AS task_title,
    tasks_tag.name AS tag_name,
    tasks_tag.color AS tag_color
FROM tasks_task
INNER JOIN tasks_task_tags ON tasks_task.id = tasks_task_tags.task_id
INNER JOIN tasks_tag ON tasks_task_tags.tag_id = tasks_tag.id;