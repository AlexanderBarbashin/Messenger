"""Tweets models file. Used to create tweets models."""

from sqlalchemy import ARRAY, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from python_advanced_diploma.src.database import Base
from users.models import User


class Like(Base):
    """Лайк. Родитель: Base."""

    __tablename__ = "like"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweet.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Tweet(Base):
    """Твит. Родитель: Base."""

    __tablename__ = "tweet"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    author_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="RESTRICT"),
    )
    tweet_media_ids = Column(ARRAY(Integer), nullable=True)
    author: Mapped["User"] = relationship()
    put_like_users: Mapped[list["User"]] = relationship(secondary="like")
    likes: Mapped[list["Like"]] = relationship(primaryjoin=(Like.tweet_id == id))
