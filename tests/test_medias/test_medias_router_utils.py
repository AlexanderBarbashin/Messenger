"""Test medias routers utils file. Used to test media routers utils."""
import os
import shutil

import aiofiles

from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.medias.medias_router_utils import (
    delete_all_tweet_medias,
    save_image_to_disk,
)


async def test_delete_all_tweet_medias(tweet_medias: list[TweetMedia]) -> None:
    """
    Тест утилиты для удаления твит медиа.

    :param tweet_medias: Твит медиа
    """
    await delete_all_tweet_medias(tweet_medias)
    for tweet_media_image in tweet_medias:
        assert not os.path.isfile(tweet_media_image.image)


async def test_save_image_to_disk() -> None:
    """Тест утилиты для сохранения изображений на диск."""
    async with aiofiles.open(
        "../../tests/images_for_tests/test_image.jpeg", "rb",
    ) as image_file:
        image = await image_file.read()
    test_image_path = await save_image_to_disk(
        "api_key_for_test_util",
        "filename_for_test_util",
        image,
    )
    assert os.path.isfile(test_image_path)
    shutil.rmtree("../../images/api_key_for_test_util")
