"""Test get self profile route file. Used to test get self profile route."""

import random
from string import ascii_letters

from httpx import AsyncClient
from starlette import status

from python_advanced_diploma.src.users.users_models import User


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
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["result"]
    assert response.json().get("user")["id"] == user.id


async def test_get_own_profile_info_without_api_key(
    ac: AsyncClient,
) -> None:
    """
    Тест эндпоинта для получения информации о собственном профиле.

    Без api key пользователя.
    :param ac: Асинхронный клиент
    """
    response = await ac.get(
        "/api/users/me",
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert not response.json()["result"]


async def test_get_own_non_exists_profile(
    ac: AsyncClient,
) -> None:
    """
    Тест эндпоинта для получения информации о собственном профиле.

    С несуществующим значением api key пользователя.
    :param ac: Асинхронный клиент
    """
    response = await ac.get(
        "/api/users/me",
        headers={"Api-Key": "".join(
            random.choices(ascii_letters, k=5),  # noqa: S311
        )},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not response.json()["result"]
