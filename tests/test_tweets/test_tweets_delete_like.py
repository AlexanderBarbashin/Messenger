"""Test dislike tweets route file. Used to test dislike tweets route."""

from httpx import AsyncClient
from sqlalchemy import select
from starlette import status

from python_advanced_diploma.src.tweets.tweets_models import Like, Tweet
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_dislike_tweet(
    ac: AsyncClient,
    user: User,
    tweet_to_delete_like: Tweet,
    like_to_delete: Like,
) -> None:
    """
    Тест эндпоинта для удаления отметки 'Нравится' с твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweet_to_delete_like: Твит для установки отметки 'Нравится'
    :param like_to_delete: Лайк для удаления
    """
    response = await ac.delete(
        "/api/tweets/{tweet_to_like_id}/likes".format(
            tweet_to_like_id=tweet_to_delete_like.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Like).filter_by(
        user_id=user.id,
        tweet_id=tweet_to_delete_like.id,
    )
    async with test_async_session as session:
        select_like_to_delete_result = await session.execute(query)
    like = select_like_to_delete_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": True}
    assert like is None


async def test_dislike_tweet_with_non_valid_tweet_id(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для удаления отметки 'Нравится' с твита.

    С некорректным ID твита.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.delete(
        "/api/tweets/tweet_to_like.id/likes",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_dislike_non_exist_tweet(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для удаления отметки 'Нравится' с твита.

    С передачей несуществующего ID твита.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.delete(
        "/api/tweets/666/likes",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
