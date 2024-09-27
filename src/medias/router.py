"""Medias router file. Used to define medias routes."""

from datetime import datetime
from typing import Annotated

import aiofiles
from aiofiles.os import makedirs
from fastapi import APIRouter, Depends, Header, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from config import logger
from medias.models import TweetMedia
from python_advanced_diploma.src.database import get_async_session

router = APIRouter(prefix="/api/medias", tags=["Media"])


@router.post("", response_model=None)
async def add_new_media(
    api_key: Annotated[str | None, Header()],
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | int]:
    """
    Эндпоинт для загрузки файлов из твита.

    :param api_key: api_key пользователя
    :param upload_file: файл
    :param session: асинхронная сессия
    :return: ID нового файла
    """
    logger.info(
        "User with api key: "
        + "{api_key} try to add image with name: {filename}".format(
            api_key=api_key,
            filename=file.filename,
        ),
    )
    img = await file.read()
    image_path = "static/images/{api_key}/{now}_{filename}".format(
        api_key=api_key,
        now=datetime.now(),
        filename=file.filename,
    )
    await makedirs(
        "static/images/{api_key}".format(api_key=api_key), exist_ok=True,
    )
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(img)
    tweet_media = TweetMedia(image=image_path)
    session.add(tweet_media)
    await session.commit()
    logger.info(
        "New media with ID: {tweet_media_id} was added".format(
            tweet_media_id=tweet_media.id,
        ),
    )
    return {"result": True, "media_id": tweet_media.id}
