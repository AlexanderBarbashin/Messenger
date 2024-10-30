"""Test add new tweet route file. Used to test create tweets route."""

import random
from string import ascii_letters

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from starlette import status

from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.tweets.tweets_models import Tweet
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_add_new_tweet(
    ac: AsyncClient,
    user: User,
    tweet_medias: list[TweetMedia],
) -> None:
    """
    Тест эндпоинта для добавления нового твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweet_medias: список твит медиа
    """
    response = await ac.post(
        "/api/tweets",
        json={
            "tweet_data": "Some test tweet data",
            "tweet_media_ids":
                [tweet_media.id for tweet_media in tweet_medias],
        },
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Tweet).filter_by(content="Some test tweet data")
    async with test_async_session as session:
        select_tweet_result = await session.execute(query)
    new_tweet = select_tweet_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_201_CREATED
    assert new_tweet is not None
    assert response.json() == {
        "result": True,
        "tweet_id": new_tweet.id,
    }


async def test_add_new_tweet_by_non_exists_user(ac: AsyncClient) -> None:
    """
    Тест эндпоинта для добавления нового твита несуществующим пользователем.

    :param ac: Асинхронный клиент
    """
    new_tweet_content = "Some test tweet data by non exist user"
    response = await ac.post(
        "/api/tweets",
        json={"tweet_data": new_tweet_content, "tweet_media_ids": []},
        headers={
            "Api-Key": "".join(
                random.choices(ascii_letters, k=5),  # noqa: S311
            ),
        },
    )
    query = select(Tweet).filter_by(content=new_tweet_content)
    async with test_async_session as session:
        select_tweet_result = await session.execute(query)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
    with pytest.raises(NoResultFound):
        select_tweet_result.scalars().one()


async def test_add_new_tweet_with_non_valid_body(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для добавления нового твита.

    С некорректным значением элемента списка ID медиа.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    new_tweet_content = "Some test tweet data with non valid body"
    response = await ac.post(
        "/api/tweets",
        json={
            "tweet_data": new_tweet_content,
            "tweet_media_ids": ["some text"],
        },
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Tweet).filter_by(content=new_tweet_content)
    async with test_async_session as session:
        select_tweet_result = await session.execute(query)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]
    with pytest.raises(NoResultFound):
        select_tweet_result.scalars().one()


async def test_add_new_tweet_with_non_exist_media(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для добавления нового твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    new_tweet_content = "Some test tweet data with non exist media"
    response = await ac.post(
        "/api/tweets",
        json={"tweet_data": new_tweet_content, "tweet_media_ids": [100]},
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Tweet).filter_by(content=new_tweet_content)
    async with test_async_session as session:
        select_tweet_result = await session.execute(query)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
    with pytest.raises(NoResultFound):
        select_tweet_result.scalars().one()
