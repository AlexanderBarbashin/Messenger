"""Test users file. Used to test users routes."""

from httpx import AsyncClient
from sqlalchemy import select

from python_advanced_diploma.tests.conftest import (
    SUCCESS_STATUS_CODE,
    VALIDATION_ERROR_STATUS_CODE,
    test_async_session,
)
from users.models import Follow, User


async def test_follow_user(
    ac: AsyncClient, user: User, another_user: User,
) -> None:
    """
    Тест эндпоинта для подписки на другого пользователя.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param another_user: Другой пользователь
    """
    response = await ac.post(
        "/api/users/{another_user_id}/follow".format(
            another_user_id=another_user.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    expected_response = {
        "result": True,
    }
    query = select(Follow).filter_by(
        following_user_id=another_user.id, followed_user_id=user.id,
    )
    async with test_async_session as session:
        select_follow_result = await session.execute(query)
    follow = select_follow_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert follow is not None


async def test_follow_user_self(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для подписки на другого пользователя.

    Тестирование попытки подписки на себя.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.post(
        "/api/users/{user_id}/follow".format(
            user_id=user.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    expected_response = {
        "result": False,
        "error_type": "ValueError",
        "error_message": "You can't follow yourself",
    }
    query = select(Follow).filter_by(
        following_user_id=user.id, followed_user_id=user.id,
    )
    async with test_async_session as session:
        select_follow_self_result = await session.execute(query)
    follow = select_follow_self_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert follow is None


async def test_follow_user_failed(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для подписки на другого пользователя.

    Тестирование с некорректным значением ID другого пользователя.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.post(
        "/api/users/another_user.id/follow",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


async def test_cancel_follow_user(
    ac: AsyncClient, user: User, another_user: User, follow_to_delete: Follow,
) -> None:
    """
    Тест эндпоинта для отмены подписки на другого пользователя.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param another_user: Другой пользователь
    :param follow_to_delete: Подписка для удаления
    """
    response = await ac.delete(
        "/api/users/{user_id}/follow".format(user_id=user.id),
        headers={"Api-Key": another_user.user_api_key},
    )
    expected_response = {
        "result": True,
    }
    query = select(Follow).filter_by(
        following_user_id=user.id, followed_user_id=another_user.id,
    )
    async with test_async_session as session:
        select_follow_user_result = await session.execute(query)
    follow = select_follow_user_result.scalars().one_or_none()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert follow is None


async def test_cancel_follow_user_failed(
    ac: AsyncClient, another_user: User,
) -> None:
    """
    Тест эндпоинта для отмены подписки на другого пользователя.

    С некорректным значением ID другого пользователя.
    :param ac: Асинхронный клиент
    :param another_user: Другой пользователь
    """
    response = await ac.delete(
        "/api/users/user.id/follow",
        headers={"Api-Key": another_user.user_api_key},
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


async def test_get_own_profile_info(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для получения информации о собственном профиле.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.get(
        "/api/users/me",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json().get("user")["id"] == user.id


async def test_get_own_profile_info_failed(ac: AsyncClient) -> None:
    """
    Тест эндпоинта для получения информации о собственном профиле.

    Без api key пользователя.
    :param ac: Асинхронный клиент
    """
    response = await ac.get(
        "/api/users/me",
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE


async def test_get_profile_info(
    ac: AsyncClient, user: User, another_user: User,
) -> None:
    """
    Тест эндпоинта для получения информации о профиле по ID.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param another_user: Другой пользователь
    """
    response = await ac.get(
        "/api/users/{another_user_id}".format(
            another_user_id=another_user.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json().get("user")["id"] == another_user.id


async def test_get_profile_info_failed(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для получения информации о профиле по ID.

    С некорректным значением ID.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.get(
        "/api/users/another_user.id",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE
