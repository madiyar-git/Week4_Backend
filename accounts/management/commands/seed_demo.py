from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with demo data: 2 users and 5 tasks'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting data seeding...'))
        # * удаление заданий
        # self.stdout.write(self.style.ERROR('Deleting old task...'))
        # Task.objects.all().delete()

        user1, created1 = User.objects.get_or_create(username='user1', email='user1@example.com')
        if created1:
            user1.set_password('devpass123')
            user1.save()

        user2, created2 = User.objects.get_or_create(username='user2', email='user2@example.com')
        if created2:
            user2.set_password('devpass123')
            user2.save()

        for i in range(1, 6):
            Task.objects.create(
                title=f'Demo task No. {i}',
                description=f'Automatically generated description for task {i}',
                owner=user1 if i % 2 == 0 else user2
            )

        self.stdout.write(self.style.SUCCESS('Database successfully populated with demo data (2 users, 5 tasks)!'))