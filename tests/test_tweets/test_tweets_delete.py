"""Test delete tweets route file. Used to test delete tweets route."""

from httpx import AsyncClient
from sqlalchemy import select
from starlette import status

from python_advanced_diploma.src.tweets.tweets_models import Tweet
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_delete_tweet(
    ac: AsyncClient,
    user: User,
    tweet_to_delete: Tweet,
) -> None:
    """
    Тест эндпоинта для удаления твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweet_to_delete: Твит для удаления
    """
    response = await ac.delete(
        "/api/tweets/{tweet_to_delete_id}".format(
            tweet_to_delete_id=tweet_to_delete.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Tweet).filter_by(id=tweet_to_delete.id)
    async with test_async_session as session:
        select_tweet_to_delete_result = await session.execute(query)
    deleted_tweet = select_tweet_to_delete_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": True}
    assert deleted_tweet is None


async def test_delete_non_exist_tweet(
    ac: AsyncClient,
    user: User,
) -> None:
    """
    Тест эндпоинта для удаления твита с передачей несуществующего ID твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.delete(
        "/api/tweets/666",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]


async def test_delete_foreign_tweet(
    ac: AsyncClient,
    user: User,
    tweet_to_like: Tweet,
) -> None:
    """
    Тест эндпоинта для удаления чужого твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweet_to_like: чужой твит
    """
    response = await ac.delete(
        "/api/tweets/{foreign_tweet_id}".format(
            foreign_tweet_id=tweet_to_like.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]


async def test_delete_tweet_with_non_valid_tweet_id(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для удаления твита с некорректным значением ID твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.delete(
        "/api/tweets/some_id",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]
