"""Medias router file. Used to define medias routes."""

from typing import Annotated

import filetype  # type: ignore
from fastapi import APIRouter, Depends, Header, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from python_advanced_diploma.src.config import logger
from python_advanced_diploma.src.database import get_async_session
from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.medias.medias_router_utils import (
    save_image_to_disk,
)
from python_advanced_diploma.src.medias.medias_schemas import TweetMediaOut
from python_advanced_diploma.src.responses import validation_error_response
from python_advanced_diploma.src.schemas import ErrorMessage

router = APIRouter(prefix="/api/medias", tags=["Media"])


@router.post(
    "",
    response_model=TweetMediaOut,
    responses={
        415: {"model": ErrorMessage, "description": "Type Error"},
        422: validation_error_response,
    },
    status_code=status.HTTP_201_CREATED,
)
async def add_new_media(
    api_key: Annotated[str, Header()],
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    Эндпоинт для загрузки файлов из твита.

    :param api_key: api_key пользователя
    :param file: файл
    :param session: асинхронная сессия
    :return: ID нового файла
    """
    logger.info(
        "User with api key: "
        "{api_key} try to add image with name: {filename}".format(
            api_key=api_key,
            filename=file.filename,
        ),
    )
    img = await file.read()
    if filetype.is_image(img):
        image_path = await save_image_to_disk(api_key, file.filename, img)
        tweet_media = TweetMedia(image=image_path)
        session.add(tweet_media)
        await session.commit()
        logger.info(
            "New media with ID: {tweet_media_id} was added".format(
                tweet_media_id=tweet_media.id,
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"result": True, "media_id": tweet_media.id},
        )
    logger.warning(
        "User with api key: {api_key} try to add non image file with filename:"
        " {filename}".format(
            api_key=api_key,
            filename=file.filename,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        content={
            "result": False,
            "error_type": "TypeError",
            "error_message": "In tweet media possible upload only images",
        },
    )
