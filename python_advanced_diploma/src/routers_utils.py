"""Project routers utils file. Use to create util functions."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from python_advanced_diploma.src.users.users_models import User


async def get_user_id_by_api_key(api_key: str, session: AsyncSession) -> int:
    """
    Функция для получения ID записи пользователя из БД.

    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: ID пользователя
    """
    query = (
        select(User).
        filter_by(user_api_key=api_key).
        options(load_only(User.id))
    )
    query_result = await session.execute(query)
    return query_result.scalars().one().id
