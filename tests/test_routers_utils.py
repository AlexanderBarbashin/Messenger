"""Test routers utils file. Used to test routers utils."""

import random
from string import ascii_letters

import pytest
from sqlalchemy.exc import NoResultFound

from python_advanced_diploma.src.routers_utils import get_user_id_by_api_key
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_get_user_id_by_api_key(user: User) -> None:
    """
    Тест утилиты для получения ID пользователя по его api key.

    :param user: Пользователь
    """
    user_id = await get_user_id_by_api_key(
        user.user_api_key, test_async_session,
    )
    expected_user_id = user.id
    assert user_id == expected_user_id


async def test_get_user_id_by_non_exists_api_key() -> None:
    """
    Тест утилиты для получения ID пользователя по его api key.

    С передачей несуществующего api key.
    """
    api_key = "".join(random.choices(ascii_letters, k=5))  # noqa: S311
    with pytest.raises(NoResultFound):
        await get_user_id_by_api_key(api_key, test_async_session)
