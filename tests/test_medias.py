"""Test medias file. Used to test medias routes."""

import shutil

import aiofiles
from httpx import AsyncClient
from sqlalchemy import select

from medias.models import TweetMedia
from python_advanced_diploma.tests.conftest import (
    SUCCESS_STATUS_CODE,
    VALIDATION_ERROR_STATUS_CODE,
    test_async_session,
)
from users.models import User


async def test_add_new_media(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для добавления нового твит медиа.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    test_image_to_add = "test_image.jpeg"
    async with aiofiles.open(test_image_to_add, "rb") as image_file:
        image = await image_file.read()
    response = await ac.post(
        "/api/medias",
        files={"file": (test_image_to_add, image)},
        headers={"Api-Key": user.user_api_key},
    )
    expected_response = {"result": True, "media_id": 1}
    query = select(TweetMedia).filter(
        TweetMedia.image.contains(test_image_to_add),
    )
    select_media_result = await test_async_session.execute(query)
    new_tweet_media = select_media_result.scalars().one()
    assert response.status_code == SUCCESS_STATUS_CODE
    assert response.json() == expected_response
    assert new_tweet_media.id == 1
    shutil.rmtree(
        "static/images/{user_api_key}".format(
            user_api_key=user.user_api_key,
        ),
    )


async def test_add_new_media_failed(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для добавления нового твит медиа без отправки файла.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.post(
        "/api/medias", headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == VALIDATION_ERROR_STATUS_CODE
