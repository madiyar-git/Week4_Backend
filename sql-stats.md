## Input ORM:

``` commandline
from django.db import models
from tasks.models import Task

stats_query = Task.objects.filter(owner_id=2).values('owner_id').annotate(
    total_tasks=models.Count('id'),
    completed_tasks=models.Count('id', filter=models.Q(completed=True)),
    active_tasks=models.Count('id', filter=models.Q(completed=False))
).query

print(stats_query)
```

## Output ORM:

```commandline
SELECT "tasks_task"."owner_id" AS "owner_id",
    COUNT("tasks_task"."id") AS "total_tasks",
    COUNT("tasks_task"."id") FILTER (WHERE "tasks_task"."completed") AS "completed_tasks",
    COUNT("tasks_task"."id") FILTER (WHERE NOT "tasks_task"."completed") AS "active_tasks" 
FROM "tasks_task"
WHERE "tasks_task"."owner_id" = 2
GROUP BY 1

```
