"""Test tweets file. Used to test tweets routes."""

from httpx import AsyncClient
from sqlalchemy import func, select

from python_advanced_diploma.tests.conftest import (
    SUCCESS_STATUS_CODE,
    VALIDATION_ERROR_STATUS_CODE,
    test_async_session,
)
from tweets.models import Like, Tweet
from users.models import User


async def test_add_new_tweet(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для добавления нового твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    new_tweet_content = "Some test tweet data"
    response = await ac.post(
        "/api/tweets",
        json={"tweet_data": new_tweet_content, "tweet_media_ids": []},
        headers={"Api-Key": user.user_api_key},
    )
    expected_response = {
        "result": True,
        "tweet_id": 1,
    }
    query = select(Tweet).filter_by(content=new_tweet_content)
    async with test_async_session as session:
        select_tweet_result = await session.execute(query)
    new_tweet = select_tweet_result.scalars().one()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert new_tweet.id == 1
    # await test_async_session.close()


async def test_add_new_tweet_failed(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для добавления нового твита.

    С некорректным значением элемента списка ID медиа.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.post(
        "/api/tweets",
        json={
            "tweet_data": "Some test tweet data",
            "tweet_media_ids": ["some text"],
        },
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


async def test_delete_tweet(
    ac: AsyncClient, user: User, tweet_to_delete: Tweet,
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
    expected_response = {
        "result": True,
    }
    query = select(Tweet).filter_by(id=tweet_to_delete.id)
    async with test_async_session as session:
        select_tweet_to_delete_result = await session.execute(query)
    deleted_tweet = select_tweet_to_delete_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert deleted_tweet is None


async def test_delete_tweet_failed(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для удаления твита с некорректным значением ID твита.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.delete(
        "/api/tweets/some_id", headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


async def test_like_tweet(
    ac: AsyncClient, user: User, tweet_to_like: Tweet,
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
    expected_response = {
        "result": True,
    }
    query = select(Like).filter_by(user_id=user.id, tweet_id=tweet_to_like.id)
    async with test_async_session as session:
        select_like_result = await session.execute(query)
    like = select_like_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert like is not None


async def test_like_own_tweet(
    ac: AsyncClient, user: User, own_tweet_to_like: Tweet,
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
    expected_response = {
        "result": False,
        "error_type": "ValueError",
        "error_message": "You can't like own tweet",
    }
    query = select(Like).filter_by(
        user_id=user.id, tweet_id=own_tweet_to_like.id,
    )
    async with test_async_session as session:
        select_like_own_tweet_result = await session.execute(query)
    like = select_like_own_tweet_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert like is None


async def test_like_tweet_failed(ac: AsyncClient, user: User) -> None:
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
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


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
    expected_response = {
        "result": True,
    }
    query = select(Like).filter_by(
        user_id=user.id,
        tweet_id=tweet_to_delete_like.id,
    )
    async with test_async_session as session:
        select_like_to_delete_result = await session.execute(query)
    like = select_like_to_delete_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert like is None


async def test_dislike_tweet_failed(ac: AsyncClient, user: User) -> None:
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
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


async def test_get_tweets(
    ac: AsyncClient, user: User, tweets: tuple[Tweet],
) -> None:
    """
    Тест эндпоинта для получения ленты твитов.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param tweets: Кортеж твитов
    """
    response = await ac.get(
        "/api/tweets", headers={"Api-Key": user.user_api_key},
    )
    query = (
        select(Tweet.id).
        join(Like, isouter=True).
        group_by(Tweet.id).
        order_by(func.count(Tweet.likes).desc(), Tweet.id)
    )
    async with test_async_session as session:
        select_tweets_result = await session.execute(query)
    db_tweets = select_tweets_result.scalars().all()
    response_tweets = [
        tweet.get("id") for tweet in response.json().get("tweets")
    ]
    assert response.status_code == SUCCESS_STATUS_CODE
    assert db_tweets == response_tweets


async def test_get_tweets_failed(ac: AsyncClient) -> None:
    """
    Тест эндпоинта для получения ленты твитов без api key пользователя.

    :param ac: Асинхронный клиент
    """
    response = await ac.get(
        "/api/tweets",
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE
