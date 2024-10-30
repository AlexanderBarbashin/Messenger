"""Test tweets routers utils file. Used to test tweets routers utils."""

from python_advanced_diploma.src.tweets.tweets_router_utils import (
    create_new_tweet,
)
from python_advanced_diploma.src.tweets.tweets_schemas import TweetIn
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_create_new_tweet(user: User) -> None:
    """
    Тест утилиты для создания экземпляра класса 'Tweet'.

    :param user: Пользователь
    """
    new_tweet = TweetIn(
        tweet_data="Content to test create new tweet util",
        tweet_media_ids=[],
    )
    tweet = await create_new_tweet(user.id, test_async_session, new_tweet)
    assert tweet
    assert tweet.content == "Content to test create new tweet util"
    assert tweet.author_id == user.id
