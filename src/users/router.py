"""Users router file. Used to define users routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import logger
from python_advanced_diploma.src.database import get_async_session
from routers_utils import get_user_id_by_api_key
from users.models import Follow, User
from users.schemas import UserOut, UsersOut

router = APIRouter(prefix="/api/users", tags=["User"])


@router.post("/{id}/follow")
async def follow_user(
    id: int,
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | str]:
    """
    Эндпоинт для подписки на другого пользователя.

    :param id: ID другого пользователя
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key}".format(
            api_key=api_key,
        )
        + " try to following user with ID: {id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    if id == current_user_id:
        logger.warning(
            "User with ID: {current_user_id} ".format(
                current_user_id=current_user_id,
            )
            + "try to following self",
        )
        return {
            "result": False,
            "error_type": "ValueError",
            "error_message": "You can't follow yourself",
        }
    follow = Follow(
        following_user_id=id,
        followed_user_id=current_user_id,
    )
    session.add(follow)
    await session.commit()
    logger.info(
        "User with ID: {current_user_id} following user with ID: {id}".format(
            current_user_id=current_user_id,
            id=id,
        ),
    )
    return {"result": True}


@router.delete("/{id}/follow")
async def cancel_follow_user(
    id: int,
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool]:
    """
    Эндпоинт для отписки от другого пользователя.

    :param id: ID другого пользователя
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key}".format(
            api_key=api_key,
        )
        + " try to stop following user with ID: {id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    stmt = delete(Follow).filter(
        and_(
            Follow.following_user_id == id,
            Follow.followed_user_id == current_user_id,
        ),
    )
    await session.execute(stmt)
    await session.commit()
    logger.info(
        "User with ID: {current_user_id}".format(
            current_user_id=current_user_id,
        )
        + " stop following user with ID: {id}".format(
            id=id,
        ),
    )
    return {"result": True}


@router.get("/me", response_model=UsersOut)
async def get_own_profile_info(
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | UserOut]:
    """
    Эндпоинт для получения информации о своём профиле.

    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key}".format(
            api_key=api_key,
        )
        + " try to get own profile info",
    )
    query = (
        select(User).
        filter_by(user_api_key=api_key).
        options(selectinload(User.followers).load_only(User.name)).
        options(selectinload(User.following).load_only(User.name))
    )
    select_user_own_info_result = await session.execute(query)
    current_user = select_user_own_info_result.scalars().one()
    logger.info(
        "User with ID: {current_user_id} get own profile info".format(
            current_user_id=current_user.id,
        ),
    )
    return {
        "request_result": True,
        "user": current_user,
    }


@router.get("/{id}", response_model=UsersOut)
async def get_profile_info(
    id: int, session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | UserOut]:
    """
    Эндпоинт для получения информации о произвольном профиле по его ID.

    :param id: ID произвольного пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User try to get profile with ID: {id} info".format(
            id=id,
        ),
    )
    query = (
        select(User).
        filter_by(id=id).
        options(selectinload(User.followers).load_only(User.name)).
        options(selectinload(User.following).load_only(User.name))
    )
    select_user_info_result = await session.execute(query)
    user = select_user_info_result.scalars().one()
    logger.info(
        "User get profile with ID: {id} info".format(
            id=id,
        ),
    )
    return {
        "request_result": True,
        "user": user,
    }
