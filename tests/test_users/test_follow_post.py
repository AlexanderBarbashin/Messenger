"""Test post follow users route file. Used to test post follow users route."""

from httpx import AsyncClient
from sqlalchemy import select
from starlette import status

from python_advanced_diploma.src.users.users_models import Follow, User
from tests.conftest import test_async_session


async def test_follow_user(
    ac: AsyncClient,
    user: User,
    another_user: User,
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
    query = select(Follow).filter_by(
        following_user_id=another_user.id,
        followed_user_id=user.id,
    )
    async with test_async_session as session:
        select_follow_result = await session.execute(query)
    follow = select_follow_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"result": True}
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
    query = select(Follow).filter_by(
        following_user_id=user.id,
        followed_user_id=user.id,
    )
    async with test_async_session as session:
        select_follow_self_result = await session.execute(query)
    follow = select_follow_self_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not response.json()["result"]
    assert follow is None


async def test_follow_user_with_non_valid_user_id(
    ac: AsyncClient, user: User,
) -> None:
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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_follow_non_exist_user(
    ac: AsyncClient,
    user: User,
) -> None:
    """
    Тест эндпоинта для подписки на другого пользователя.

    С передачей ID несуществующего пользователя
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    non_exist_user_id = 1234
    response = await ac.post(
        "/api/users/{non_exist_user_id}/follow".format(
            non_exist_user_id=non_exist_user_id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    query = select(Follow).filter_by(
        following_user_id=non_exist_user_id,
        followed_user_id=user.id,
    )
    async with test_async_session as session:
        select_follow_result = await session.execute(query)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not response.json()["result"]
    assert select_follow_result.scalars().one_or_none() is None


async def test_follow_user_already_exists(
    ac: AsyncClient,
    user: User,
    user_to_follow: User,
    follow_to_test: Follow,
) -> None:
    """
    Тест эндпоинта для подписки на другого пользователя.

    С передачей ID пользователя, на которого уже подписан пользователь.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    :param user_to_follow: Пользователь для тестирования подписки
    :param follow_to_test: Существующая подписка для тестирования
    """
    response = await ac.post(
        "/api/users/{user_to_follow_id}/follow".format(
            user_to_follow_id=user_to_follow.id,
        ),
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not response.json()["result"]
