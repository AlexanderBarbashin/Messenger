"""Users models file. Used to create users models."""

from typing import Annotated

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from python_advanced_diploma.src.database import Base

user_id = Annotated[
    int,
    mapped_column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
]


class Follow(Base):
    """Подписка. Родитель: Base."""

    __tablename__ = "follow"
    following_user_id: Mapped[user_id]
    followed_user_id: Mapped[user_id]


class User(Base):
    """Пользователь. Родитель: Base."""

    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    user_api_key: Mapped[str] = mapped_column(unique=True)
    followers: Mapped[list["User"]] = relationship(
        secondary="follow",
        primaryjoin=(Follow.following_user_id == id),
        secondaryjoin=(Follow.followed_user_id == id),
        backref="following",
    )
