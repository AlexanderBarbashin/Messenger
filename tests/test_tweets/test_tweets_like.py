"""Test like tweet router file. Used to test like tweet route."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from starlette import status

from python_advanced_diploma.src.tweets.tweets_models import Like, Tweet
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_like_tweet(
    ac: AsyncClient,
    user: User,
    tweet_to_like: Tweet,
) -> None:
    """
    Тест эндпоинта для установки отметки 'Нравится' на твит.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweet_to_like: Твит для установки отметки 'Нравится'
    """
    response = await ac.post(
        "/api/tweets/{tweet_to_like_id}/likes".format(
            tweet_to_like_id=tweet_to_like.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Like).filter_by(user_id=user.id, tweet_id=tweet_to_like.id)
    async with test_async_session as session:
        select_like_result = await session.execute(query)
    like = select_like_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"result": True}
    assert like is not None


async def test_like_own_tweet(
    ac: AsyncClient,
    user: User,
    own_tweet_to_like: Tweet,
) -> None:
    """
    Тест эндпоинта для установки отметки 'Нравится' на собственный твит.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param own_tweet_to_like: Собственный твит для установки отметки 'Нравится'
    """
    response = await ac.post(
        "/api/tweets/{own_tweet_to_like_id}/likes".format(
            own_tweet_to_like_id=own_tweet_to_like.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Like).filter_by(
        user_id=user.id,
        tweet_id=own_tweet_to_like.id,
    )
    async with test_async_session as session:
        select_like_own_tweet_result = await session.execute(query)
    like = select_like_own_tweet_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not response.json()["result"]
    assert like is None


async def test_like_tweet_with_non_valid_tweet_id(
    ac: AsyncClient,
    user: User,
) -> None:
    """
    Тест эндпоинта для установки отметки 'Нравится'.

    С некорректным значением ID твита.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.post(
        "/api/tweets/tweet_to_like.id/likes",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_like_non_exist_tweet(
    ac: AsyncClient,
    user: User,
) -> None:
    """
    Тест эндпоинта для установки отметки 'Нравится' на твит.

    С передачей несуществующего ID твита.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    non_exist_tweet_id = 666
    response = await ac.post(
        "/api/tweets/{non_exist_tweet_id}/likes".format(
            non_exist_tweet_id=non_exist_tweet_id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Like).filter_by(
        user_id=user.id,
        tweet_id=non_exist_tweet_id,
    )
    async with test_async_session as session:
        select_like_non_exist_tweet_result = await session.execute(query)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
    with pytest.raises(NoResultFound):
        select_like_non_exist_tweet_result.scalars().one()


async def test_like_tweet_already_exists(
    ac: AsyncClient,
    user: User,
    tweet_to_test_exist_like: Tweet,
    exist_like_to_test: Like,
) -> None:
    """
    Тест эндпоинта для установки отметки 'Нравится' на твит.

    С передачей ID твита, на который пользователь уже установил отметку
    'Нравится'.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweet_to_test_exist_like: Твит с установленной отметкой 'Нравится'
    :param exist_like_to_test: Существующий лайк
    """
    response = await ac.post(
        "/api/tweets/{tweet_to_test_exist_like_id}/likes".format(
            tweet_to_test_exist_like_id=tweet_to_test_exist_like.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not response.json()["result"]
