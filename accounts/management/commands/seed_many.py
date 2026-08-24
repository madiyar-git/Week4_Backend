import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds the database with 100 users and 500 tasks per user (50k total)"

    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")
        users = []
        for i in range(1, 101):
            username = f"perf_user_{i}"
            user, created = User.objects.get_or_create(
                username=username, defaults={"email": f"{username}@example.com"}
            )
            if created:
                user.set_password("secure_pass_123")
                user.save()
            users.append(user)
        self.stdout.write(f"Successfully synchronized {len(users)} users.")
        tasks_to_create = []
        for user in users:
            for j in range(1, 501):
                tasks_to_create.append(
                    Task(
                        title=f"Performance Test Task #{j}",
                        description=f"Automated benchmarking task generated for user {user.username}.",
                        completed=random.choice([True, False]),
                        owner=user,
                    )
                )
        self.stdout.write(
            f"Generated {len(tasks_to_create)} objects in memory. Executing bulk_create..."
        )
        Task.objects.bulk_create(tasks_to_create, batch_size=1000)
        self.stdout.write(
            self.style.SUCCESS(
                "Success! Database successfully seeded with 50,000 tasks"
            )
        )
