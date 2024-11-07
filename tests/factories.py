"""Factories file. Used to define models factories."""
import factory
from factory.fuzzy import FuzzyText

from python_advanced_diploma.src.tweets.tweets_models import Tweet
from python_advanced_diploma.src.users.users_models import User


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика пользователей. Родитель: SQLAlchemyModelFactory."""

    name: factory.Faker = factory.Faker("first_name")
    user_api_key = FuzzyText()

    class Meta:
        """Мета класс фабрики пользователей."""

        model = User


class TweetFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Фабрика твитов. Родитель: SQLAlchemyModelFactory."""

    content: factory.Faker = factory.Faker("word")
    author: factory.SubFactory = factory.SubFactory(UserFactory)

    class Meta:
        """Мета класс фабрики твитов."""

        model = Tweet
