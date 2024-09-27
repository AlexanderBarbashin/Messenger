"""Tweets schemas file. Used to define schemas to tweets routes."""
from pydantic import BaseModel, Field

from users.schemas import BaseUser


class TweetIn(BaseModel):
    """Входящий твит. Родитель: BaseModel."""

    tweet_data: str
    tweet_media_ids: list[int]


class LikeOut(BaseModel):
    """Исходящий лайк. Родитель: BaseModel."""

    id: int = Field(..., serialization_alias="user_id")
    name: str


class TweetOut(BaseModel):
    """Исходящий твит. Родитель: BaseModel."""

    id: int
    content: str
    attachments: list[str] = []
    author: BaseUser
    put_like_users: list[LikeOut] = Field(..., serialization_alias="likes")
