"""Tweets router utils file. Use to create util functions."""
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from python_advanced_diploma.src.medias.medias_models import TweetMedia
from python_advanced_diploma.src.tweets.tweets_models import Tweet
from python_advanced_diploma.src.tweets.tweets_schemas import TweetIn


async def create_new_tweet(
    current_user_id: int,
    session: AsyncSession,
    new_tweet: TweetIn,
) -> Tweet | None:
    """
    Функция для создания экземпляра класса 'Tweet'.

    :param current_user_id: ID текущего пользователя
    :param session: Асинхронная сессия
    :param new_tweet: новый твит
    :return: экземпляр класса 'Tweet' | None
    """
    tweet = Tweet(
        content=new_tweet.tweet_data,
        author_id=current_user_id,
    )
    session.add(tweet)
    await session.flush()
    medias_update_stmt = (
        update(TweetMedia).
        where(TweetMedia.id.in_(new_tweet.tweet_media_ids)).
        values(tweet_id=tweet.id)
    ).returning(TweetMedia)
    medias_update_result = await session.execute(medias_update_stmt)
    medias_update = medias_update_result.scalars().all()
    if len(new_tweet.tweet_media_ids) == len(medias_update):
        await session.commit()
        return tweet
    return None
