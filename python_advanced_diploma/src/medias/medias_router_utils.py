"""Medias router utils file. Use to create util functions."""
import asyncio
from datetime import datetime
from typing import Sequence

import aiofiles
from aiofiles.os import makedirs, remove


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


async def delete_image(tweet_image: str) -> None:
    """
    Функция для удаления изображения твит медиа.

    :param tweet_image: изображение
    """
    await remove(tweet_image)


async def delete_all_tweet_images(tweet_images: Sequence[str]) -> None:
    """
    Функция для удаления всех изображений твит медиа твита.

    :param tweet_images: изображения твита
    """
    tasks = [delete_image(tweet_image) for tweet_image in tweet_images]
    await asyncio.gather(*tasks)
