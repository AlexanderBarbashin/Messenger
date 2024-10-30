"""Tweets router file. Used to define tweets routes."""

from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, Header, Response, status
from fastapi.params import Path, Query
from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.responses import JSONResponse

from python_advanced_diploma.src.config import logger
from python_advanced_diploma.src.database import get_async_session
from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.medias.medias_router_utils import (
    delete_all_tweet_medias,
)
from python_advanced_diploma.src.responses import (
    bad_request_error_response,
    not_found_error_response,
    validation_error_response,
)
from python_advanced_diploma.src.routers_utils import get_user_id_by_api_key
from python_advanced_diploma.src.schemas import SuccessMessage
from python_advanced_diploma.src.tweets.tweets_models import Like, Tweet
from python_advanced_diploma.src.tweets.tweets_router_utils import (
    create_new_tweet,
)
from python_advanced_diploma.src.tweets.tweets_schemas import (
    TweetCreated,
    TweetIn,
    TweetsOut,
)
from python_advanced_diploma.src.users.users_models import User

router = APIRouter(prefix="/api/tweets", tags=["Tweet"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=TweetCreated,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def add_new_tweet(
    new_tweet: TweetIn,
    api_key: Annotated[str, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    Эндпоинт для создания нового твита.

    :param new_tweet: новый твит
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: ID нового твита
    """
    logger.info(
        "User with api key: {api_key} try to add new tweet ".format(
            api_key=api_key,
        ) + "with content: {content}".format(
            content=new_tweet.tweet_data,
        ) + " and media ID's: {tweet_media_ids}".format(
            tweet_media_ids=new_tweet.tweet_media_ids,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    tweet = await create_new_tweet(current_user_id, session, new_tweet)
    if tweet:
        logger.info(
            "New tweet with ID: {tweet_id} was added by user with ID: ".format(
                tweet_id=tweet.id,
            ) + "{author_id}".format(
                author_id=current_user_id,
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "result": True,
                "tweet_id": tweet.id,
            },
        )
    error_message = (
        "Some of tweet media with ID: {tweet_media_ids} doesn't exist"
    ).format(
        tweet_media_ids=new_tweet.tweet_media_ids,
    )
    logger.error(error_message)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "result": False,
            "error_type": "No Result Found Error",
            "error_message": error_message,
        },
    )


@router.delete(
    "/{id}",
    response_model=SuccessMessage,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def delete_tweet(
    id: Annotated[int, Path(gt=0)],
    api_key: Annotated[str, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    Эндпоинт для удаления твита.

    :param id: ID твита
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key} try to delete tweet with ID: ".format(
            api_key=api_key,
        ) + "{id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    tweet_to_delete_query = (
        select(Tweet).
        options(selectinload(Tweet.tweet_medias).load_only(TweetMedia.image)).
        filter_by(id=id, author_id=current_user_id)
    )
    tweet_to_delete_query_result = await session.execute(tweet_to_delete_query)
    tweet_to_delete = tweet_to_delete_query_result.scalars().one()
    tweet_medias_to_delete = tweet_to_delete.tweet_medias
    if tweet_medias_to_delete:
        await delete_all_tweet_medias(tweet_medias_to_delete)
    await session.delete(tweet_to_delete)
    await session.commit()
    logger.info(
        "Tweet with ID: {id} was deleted by user with ID: ".format(
            id=id,
        ) + "{current_user_id}".format(
            current_user_id=current_user_id,
        ),
    )
    return JSONResponse(
        content={
            "result": True,
        },
    )


@router.post(
    "/{id}/likes",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessMessage,
    responses={
        400: bad_request_error_response,
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def like_tweet(
    id: Annotated[int, Path(gt=0)],
    api_key: Annotated[str, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    Эндпоинт для установки отметки «Нравится» на твит.

    :param id: ID твита
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key} try to like tweet with ID: {id}".format(
            api_key=api_key,
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    tweet = await session.get(Tweet, id)
    if tweet:
        if tweet.author_id == current_user_id:
            logger.warning(
                "User with ID: {current_user_id}".format(
                    current_user_id=current_user_id,
                ) + "try to like own tweet with ID: {id}".format(
                    id=id,
                ),
            )
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "result": False,
                    "error_type": "ValueError",
                    "error_message": "You can't like own tweet",
                },
            )
        like = Like(
            user_id=current_user_id,
            tweet_id=id,
        )
        session.add(like)
        await session.commit()
        logger.info(
            "Tweet with ID: {id} was liked by user with ID: ".format(
                id=id,
            ) + "{current_user_id}".format(
                current_user_id=current_user_id,
            ),
        )
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "result": True,
            },
        )
    logger.error(
        "User with ID: {current_user_id}".format(
            current_user_id=current_user_id,
        ) + "try to like non exists tweet with ID: {id}".format(
            id=id,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "result": False,
            "error_type": "ValueError",
            "error_message": "Tweet with ID: {id} not found".format(id=id),
        },
    )


@router.delete(
    "/{id}/likes",
    response_model=SuccessMessage,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def dislike_tweet(
    id: Annotated[int, Path(gt=0)],
    api_key: Annotated[str, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> Response:
    """
    Эндпоинт для удаления отметки «Нравится» с твита.

    :param id: ID твита
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key} try to dislike tweet with ID: ".format(
            api_key=api_key,
        ) + "{id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    stmt = (
        delete(Like).
        filter(
            and_(Like.user_id == current_user_id, Like.tweet_id == id),
        ).
        returning(Like)
    )
    like_delete_result = await session.execute(stmt)
    deleted_like = like_delete_result.fetchone()
    if deleted_like:
        await session.commit()
        logger.info(
            "Tweet with ID: {id} was disliked by user with id: ".format(
                id=id,
            ) + "{current_user_id}".format(
                current_user_id=current_user_id,
            ),
        )
        return JSONResponse(
            content={
                "result": True,
            },
        )
    logger.warning(
        "Tweet with ID: {id} wasn't liked by author with ID: {author_id}".
        format(
            id=id,
            author_id=current_user_id,
        ),
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "result": False,
            "error_type": "NoResultFound",
            "error_message": "Like not found",
        },
    )


@router.get(
    "",
    response_model=TweetsOut,
    responses={
        404: not_found_error_response,
        422: validation_error_response,
    },
)
async def get_tweets(
    api_key: Annotated[str, Header()],
    limit: Annotated[int | None, Query(ge=0)] = None,
    offset: Annotated[int | None, Query(ge=0)] = None,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | Sequence[Tweet]]:
    """
    Эндпоинт для получения списка твитов.

    :param api_key: api_key пользователя
    :param limit: лимит
    :param offset: сдвиг
    :param session: асинхронная сессия
    :return: response
    """
    logger.info(
        "User with api key: {api_key} try to get tweets with limit: ".format(
            api_key=api_key,
        ) + "{limit} and offset: {offset}".format(
            limit=limit,
            offset=offset,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    if offset and limit:
        offset = (offset - 1) * limit
    query = (
        select(Tweet).
        options(selectinload(Tweet.tweet_medias).load_only(TweetMedia.image)).
        options(selectinload(Tweet.author).load_only(User.name)).
        options(selectinload(Tweet.put_like_users).load_only(User.name)).
        join(Like, isouter=True).
        group_by(Tweet.id).
        order_by(func.count(Tweet.likes).desc(), Tweet.id).
        offset(offset).
        limit(limit)
    )
    tweets_select_result = await session.execute(query)
    tweets = tweets_select_result.scalars().all()
    logger.info(
        "User with ID: {user_id} get tweets with limit: ".format(
            user_id=current_user_id,
        ) + "{limit} and offset: {offset}".format(
            limit=limit,
            offset=offset,
        ),
    )
    return {
        "result": True,
        "tweets": tweets,
    }
