"""Test get tweets route file. Used to test get tweets route."""

from httpx import AsyncClient
from sqlalchemy import func, select
from starlette import status

from python_advanced_diploma.src.tweets.tweets_models import Like, Tweet
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_get_tweets(
    ac: AsyncClient,
    user: User,
    tweets: tuple[Tweet],
) -> None:
    """
    Тест эндпоинта для получения ленты твитов.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweets: Кортеж твитов
    """
    response = await ac.get(
        "/api/tweets",
        headers={"Api-Key": user.user_api_key},
    )
    query = (
        select(Tweet.id).
        join(Like, isouter=True).
        group_by(Tweet.id).
        order_by(func.count(Tweet.likes).desc(), Tweet.id)
    )
    async with test_async_session as session:
        select_tweets_result = await session.execute(query)
    response_tweets = [
        tweet.get("id") for tweet in response.json().get("tweets")
    ]
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["result"]
    assert select_tweets_result.scalars().all() == response_tweets


async def test_get_tweets_without_user_api_key(ac: AsyncClient) -> None:
    """
    Тест эндпоинта для получения ленты твитов без api key пользователя.

    :param ac: Асинхронный клиент
    """
    response = await ac.get(
        "/api/tweets",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_get_tweets_with_non_valid_params(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для получения ленты твитов.

    С некорректными значениями лимита и сдвига
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.get(
        "/api/tweets?limit=-1&offset=-1",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]
