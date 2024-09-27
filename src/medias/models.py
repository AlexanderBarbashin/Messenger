"""Medias models file. Used to create medias models."""
from sqlalchemy.orm import Mapped, mapped_column

from python_advanced_diploma.src.database import Base


class TweetMedia(Base):
    """Медиа твита. Родитель: Base."""

    __tablename__ = "tweet_media"
    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str]
