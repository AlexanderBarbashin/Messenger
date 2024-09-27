"""Project routers utils file. Use to create util functions."""

import asyncio

from aiofiles.os import remove
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from medias.models import TweetMedia
from users.models import User


async def get_user_id_by_api_key(api_key: str, session: AsyncSession) -> int:
    """
    Функция для получения ID записи пользователя из БД.

    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: ID пользователя
    """
    query = select(User).filter_by(user_api_key=api_key)
    query_result = await session.execute(query)
    return query_result.scalars().one().id


async def delete_media(media_id: int, session: AsyncSession) -> None:
    """
    Функция для удаления твит медиа по ID.

    :param media_id: ID
    :param session: асинхронная сессия
    """
    stmt = (
        delete(TweetMedia).filter_by(id=media_id).returning(TweetMedia.image)
    )
    stmt_result = await session.execute(stmt)
    image_to_delete = stmt_result.fetchone()[0]
    await remove(image_to_delete)


async def delete_all_tweet_medias(
    media_ids: list[int], session: AsyncSession,
) -> None:
    """
    Функция для удаления твит медиа.

    :param media_ids: list[ID]
    :param session: асинхронная сессия
    """
    tasks = [delete_media(media_id, session) for media_id in media_ids]
    await asyncio.gather(*tasks)
