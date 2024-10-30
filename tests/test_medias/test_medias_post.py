"""Test medias file. Used to test medias routes."""

import shutil

import aiofiles
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from starlette import status

from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.users.users_models import User
from tests.conftest import test_async_session


async def test_add_new_media(ac: AsyncClient, user: User) -> None:
    """
    Тест эндпоинта для добавления нового твит медиа.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    async with aiofiles.open(
        "../../tests/images_for_tests/test_image.jpeg", "rb",
    ) as image_file:
        image = await image_file.read()
    response = await ac.post(
        "/api/medias",
        files={"file": ("test_image.jpeg", image)},
        headers={"Api-Key": user.user_api_key},
    )
    select_media_result = await test_async_session.execute(
        select(TweetMedia).filter(
            TweetMedia.image.contains("test_image.jpeg"),
        ))
    new_tweet_media = select_media_result.scalars().one_or_none()
    assert response.status_code == status.HTTP_201_CREATED
    assert new_tweet_media is not None
    assert response.json() == {"result": True, "media_id": new_tweet_media.id}
    shutil.rmtree(
        "../../images/{user_api_key}".format(
            user_api_key=user.user_api_key,
        ),
    )


async def test_add_new_media_with_non_image_file(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для добавления нового твит медиа.

    С передачей твит медиа, не являющегося изображением.
    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    async with aiofiles.open(
        "../../tests/images_for_tests/test_file.txt", "rb",
    ) as non_image_file:
        non_image = await non_image_file.read()
    response = await ac.post(
        "/api/medias",
        files={"file": ("test_file.txt", non_image)},
        headers={"Api-Key": user.user_api_key},
    )
    query = select(TweetMedia).filter(
        TweetMedia.image.contains("test_file.txt"),
    )
    select_media_result = await test_async_session.execute(query)
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    assert response.json()["error_message"] == (
        "In tweet media possible upload only images"
    )
    with pytest.raises(NoResultFound):
        select_media_result.scalars().one()


async def test_add_new_media_without_media(
    ac: AsyncClient, user: User,
) -> None:
    """
    Тест эндпоинта для добавления нового твит медиа без отправки файла.

    :param ac: Асинхронный клиент
    :param user: Пользователь
    """
    response = await ac.post(
        "/api/medias",
        headers={"Api-Key": user.user_api_key},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
