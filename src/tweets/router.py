"""Tweets router file. Used to define tweets routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy import and_, any_, delete, distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from config import logger
from medias.models import TweetMedia
from python_advanced_diploma.src.database import get_async_session
from routers_utils import delete_all_tweet_medias, get_user_id_by_api_key
from tweets.models import Like, Tweet
from tweets.schemas import TweetIn, TweetOut
from users.models import User

router = APIRouter(prefix="/api/tweets", tags=["Tweet"])


@router.post("", response_model=None)
async def add_new_tweet(
    new_tweet: TweetIn,
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | int]:
    """
    Эндпоинт для создания нового твита.

    :param new_tweet: новый твит
    :param api_key: api_key пользователя
    :param session: асинхронная сессия
    :return: ID нового твита
    """
    content = new_tweet.tweet_data
    tweet_media_ids = new_tweet.tweet_media_ids
    logger.info(
        "User with api key: {api_key} try to add new tweet ".format(
            api_key=api_key,
        )
        + "with content: {content} and media ID's: {tweet_media_ids}".format(
            content=content,
            tweet_media_ids=tweet_media_ids,
        ),
    )
    author_id = await get_user_id_by_api_key(api_key, session)
    tweet = Tweet(
        content=content,
        author_id=author_id,
        tweet_media_ids=tweet_media_ids,
    )
    session.add(tweet)
    await session.commit()
    logger.info(
        "New tweet with ID: {tweet_id} was added by user with ID: ".format(
            tweet_id=tweet.id,
        )
        + "{author_id}".format(
            author_id=author_id,
        ),
    )
    return {
        "result": True,
        "tweet_id": tweet.id,
    }


@router.delete("/{id}")
async def delete_tweet(
    id: int,
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool]:
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
        )
        + "{id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    stmt = (
        delete(Tweet).
        filter(and_(Tweet.id == id, Tweet.author_id == current_user_id)).
        returning(Tweet.tweet_media_ids)
    )
    tweet_delete_result = await session.execute(stmt)
    media_ids = tweet_delete_result.fetchone()[0]
    if media_ids:
        await delete_all_tweet_medias(media_ids, session)
    await session.commit()
    logger.info(
        "Tweet with ID: {id} was deleted by user with ID: ".format(
            id=id,
        )
        + "{current_user_id}".format(
            current_user_id=current_user_id,
        ),
    )
    return {
        "result": True,
    }


@router.post("/{id}/likes")
async def like_tweet(
    id: int,
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | str]:
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
    if tweet.author_id == current_user_id:
        logger.warning(
            "User with ID: {current_user_id}".format(
                current_user_id=current_user_id,
            )
            + "try to like own tweet with ID: {id}".format(
                id=id,
            ),
        )
        return {
            "result": False,
            "error_type": "ValueError",
            "error_message": "You can't like own tweet",
        }
    like = Like(
        user_id=current_user_id,
        tweet_id=id,
    )
    session.add(like)
    await session.commit()
    logger.info(
        "Tweet with ID: {id} was liked by user with ID: ".format(
            id=id,
        )
        + "{current_user_id}".format(
            current_user_id=current_user_id,
        ),
    )
    return {
        "result": True,
    }


@router.delete("/{id}/likes")
async def dislike_tweet(
    id: int,
    api_key: Annotated[str | None, Header()],
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool]:
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
        )
        + "{id}".format(
            id=id,
        ),
    )
    current_user_id = await get_user_id_by_api_key(api_key, session)
    stmt = delete(Like).filter(
        and_(Like.user_id == current_user_id, Like.tweet_id == id),
    )
    await session.execute(stmt)
    await session.commit()
    logger.info(
        "Tweet with ID: {id} was disliked by user with id: ".format(
            id=id,
        )
        + "{current_user_id}".format(
            current_user_id=current_user_id,
        ),
    )
    return {
        "result": True,
    }


@router.get("")
async def get_tweets(
    api_key: Annotated[str | None, Header()],
    limit: int = None,
    offset: int = None,
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, bool | list[TweetOut]]:
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
        )
        + "{limit} and offset: {offset}".format(
            limit=limit,
            offset=offset,
        ),
    )
    if offset and limit:
        offset = (offset - 1) * limit
    query = (
        select(Tweet, func.array_agg(distinct(TweetMedia.image))).
        options(selectinload(Tweet.author).load_only(User.name)).
        options(selectinload(Tweet.put_like_users).load_only(User.name)).
        join(
            TweetMedia,
            TweetMedia.id == any_(Tweet.tweet_media_ids),
            isouter=True,
        ).
        join(Like, isouter=True).
        group_by(Tweet.id).
        order_by(func.count(Tweet.likes).desc(), Tweet.id).
        offset(offset).
        limit(limit)
    )
    tweets_select_result = await session.execute(query)
    tweets = tweets_select_result.all()
    validated_tweets = []
    for tweet in tweets:
        validated_tweet = TweetOut.model_validate(
            tweet[0], from_attributes=True,
        )
        if tweet[1]:
            attachments = []
            for tweet_image in tweet[1]:
                attachments.append(tweet_image)
            validated_tweet.attachments = attachments
        else:
            validated_tweet.attachments = []
        validated_tweets.append(validated_tweet)
    return {
        "result": True,
        "tweets": validated_tweets,
    }
