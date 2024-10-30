"""
Test follow users delete route file.

Used to test delete users follow route.
"""

from httpx import AsyncClient
from sqlalchemy import select
from starlette import status

from python_advanced_diploma.src.users.users_models import Follow, User
from tests.conftest import test_async_session


async def test_cancel_follow_user(
    ac: AsyncClient,
    user: User,
    another_user: User,
    follow_to_delete: Follow,
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
    query = select(Follow).filter_by(
        following_user_id=user.id,
        followed_user_id=another_user.id,
    )
    async with test_async_session as session:
        select_follow_user_result = await session.execute(query)
    follow = select_follow_user_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"result": True}
    assert follow is None


async def test_cancel_follow_non_valid_user(
    ac: AsyncClient,
    another_user: User,
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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_cancel_follow_user_non_exists(
    ac: AsyncClient,
    user: User,
) -> None:
    """
    Тест эндпоинта для отмены подписки на другого пользователя.

    С передачей ID другого пользователя, на которого пользователь не подписан.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.delete(
        "/api/users/1234/follow",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
