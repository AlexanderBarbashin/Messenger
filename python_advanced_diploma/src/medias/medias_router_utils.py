"""Medias router utils file. Use to create util functions."""
import asyncio
from datetime import datetime

import aiofiles
from aiofiles.os import makedirs, remove

from python_advanced_diploma.src.medias.medias_models import TweetMedia


async def save_image_to_disk(
    api_key: str | None, filename: str | None, img: bytes,
) -> str:
    """
    Функция для сохранения изображения на диск.

    :param api_key: api_key пользователя
    :param filename: имя файла
    :param img: изображение
    :return: путь к изображению на диске
    """
    image_path = "../../images/{api_key}/{now}_{filename}".format(
        api_key=api_key,
        now=datetime.now(),
        filename=filename,
    )
    await makedirs(
        "../../images/{api_key}".format(api_key=api_key),
        exist_ok=True,
    )
    async with aiofiles.open(image_path, "wb") as image_file:
        await image_file.write(img)
    return image_path


async def delete_media(media_image: str) -> None:
    """
    Функция для удаления твит медиа.

    :param media_image: изображение
    """
    await remove(media_image)


async def delete_all_tweet_medias(tweet_medias: list[TweetMedia]) -> None:
    """
    Функция для удаления всех твит медиа твита.

    :param tweet_medias: list[TweetMedia]
    """
    tweet_images = [tweet_media.image for tweet_media in tweet_medias]
    tasks = [delete_media(media_image) for media_image in tweet_images]
    await asyncio.gather(*tasks)
