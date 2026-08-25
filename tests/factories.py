import factory
from django.contrib.auth import get_user_model

from tasks.models import Task

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@gmail.com")


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("text")
    owner = factory.SubFactory(UserFactory)
