"""Users router file. Used to define users routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.params import Path
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload
from starlette.responses import JSONResponse

from python_advanced_diploma.src.config import logger
from python_advanced_diploma.src.database import get_async_session
from python_advanced_diploma.src.responses import (
    bad_request_error_response,
    not_found_error_response,
    validation_error_response,
)
from python_advanced_diploma.src.routers_utils import get_user_id_by_api_key
from python_advanced_diploma.src.schemas import SuccessMessage
from python_advanced_diploma.src.users.users_models import Follow, User
from python_advanced_diploma.src.users.users_schemas import UsersOut

router = APIRouter(prefix="/api/users", tags=["User"])


@router.post(
    "/{id}/follow",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessMessage,
    responses={
        400: bad_request_error_response,
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def follow_user(
    id: Annotated[int, Path(gt=0)],
    api_key: Annotated[str, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> Response:
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
        ) + " try to following user with ID: {id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    if id == current_user_id:
        logger.warning(
            "User with ID: {current_user_id} ".format(
                current_user_id=current_user_id,
            ) + "try to following self",
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": False,
                "error_type": "ValueError",
                "error_message": "You can't follow yourself",
            },
        )
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
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"result": True},
    )


@router.delete(
    "/{id}/follow",
    response_model=SuccessMessage,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def cancel_follow_user(
    id: Annotated[int, Path(gt=0)],
    api_key: Annotated[str, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> Response:
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
        ) + " try to stop following user with ID: {id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    stmt = (
        delete(Follow).
        filter(
            and_(
                Follow.following_user_id == id,
                Follow.followed_user_id == current_user_id,
            ),
        ).
        returning(Follow)
    )
    follow_delete_result = await session.execute(stmt)
    deleted_follow = follow_delete_result.fetchone()
    if deleted_follow:
        await session.commit()
        logger.info(
            "User with ID: {current_user_id}".format(
                current_user_id=current_user_id,
            ) + " stop following user with ID: {id}".format(
                id=id,
            ),
        )
        return JSONResponse(content={"result": True})
    logger.warning(
        "User with ID: {id} wasn't followed by user with ID: "
        "{current_user_id}".format(
            id=id,
            current_user_id=current_user_id,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "result": False,
            "error_type": "NoResultFound",
            "error_message": "Follow not found",
        },
    )


@router.get(
    "/me",
    response_model=UsersOut,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def get_own_profile_info(
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | User]:
    """
    Эндпоинт для получения информации о своём профиле.

    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key}".format(
            api_key=api_key,
        ) + " try to get own profile info",
    )
    query = (
        select(User).options(load_only(User.name)).
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


@router.get(
    "/{id}",
    response_model=UsersOut,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def get_profile_info(
    id: Annotated[int, Path(gt=0)],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | User]:
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
        select(User).options(load_only(User.name)).
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
