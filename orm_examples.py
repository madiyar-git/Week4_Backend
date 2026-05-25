from tasks.models import Task, Category
from django.db.models import Q, Count

# Базовые операции
Task.objects.all()
Task.objects.create(title="ORM задача")
Task.objects.filter(completed=True)
Task.objects.get(id=1)
Task.objects.filter(id=1).update(title="Обновлено")
Task.objects.filter(id=10).delete()

# Агрегации
Task.objects.count()
Task.objects.filter(completed=True).count()
Task.objects.values('priority').annotate(count=Count('id'))

# Q объекты
Task.objects.filter(Q(priority=3) | Q(completed=False))
Task.objects.filter(Q(title__icontains="django") & Q(completed=False))

# Сортировка
Task.objects.order_by('-priority', 'title')