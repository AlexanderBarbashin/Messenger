"""Test get users profile route file. Used to test get users profile route."""

from httpx import AsyncClient
from starlette import status

from python_advanced_diploma.src.users.users_models import User


async def test_get_profile_info(
    ac: AsyncClient,
    user: User,
    another_user: User,
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
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["result"]
    assert response.json().get("user")["id"] == another_user.id


async def test_get_profile_info_with_non_valid_user_id(
    ac: AsyncClient, user: User,
) -> None:
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
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_get_profile_info_with_non_exists_user_id(
    ac: AsyncClient,
    user: User,
) -> None:
    """
    Тест эндпоинта для получения информации о профиле по ID.

    С несуществующим значением ID другого пользователя.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.get(
        "/api/users/555",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
