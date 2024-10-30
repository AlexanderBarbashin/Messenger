"""Medias models file. Used to create medias models."""
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from python_advanced_diploma.src.database import Base


class TweetMedia(Base):
    """Медиа твита. Родитель: Base."""

    __tablename__ = "tweet_media"
    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str]
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweet.id", ondelete="CASCADE"),
        nullable=True,
    )
