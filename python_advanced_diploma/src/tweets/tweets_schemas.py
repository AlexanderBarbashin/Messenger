"""Tweets schemas file. Used to define schemas to tweets routes."""
from pydantic import BaseModel, Field, conint, model_serializer

from python_advanced_diploma.src.schemas import SuccessMessage
from python_advanced_diploma.src.users.users_schemas import BaseUser


class TweetIn(BaseModel):
    """Входящий твит. Родитель: BaseModel."""

    tweet_data: str
    tweet_media_ids: list[conint(gt=0)]  # type: ignore


class TweetCreated(SuccessMessage):
    """Результат создания твита. Родитель: SuccessMessage."""

    tweet_id: int = Field(..., gt=0)


class LikeOut(BaseModel):
    """Исходящий лайк. Родитель: BaseModel."""

    id: int = Field(..., serialization_alias="user_id", gt=0)
    name: str


class TweetImage(BaseModel):
    """Изображение твита. Родитель: BaseModel."""

    image: str

    @model_serializer
    def serialize_model(self) -> str:
        """
        Метод для сериализации модели изображения твита.

        :return: изображение твита
        """
        return self.image


class TweetOut(BaseModel):
    """Исходящий твит. Родитель: BaseModel."""

    id: int = Field(..., gt=0)
    content: str
    tweet_medias: list[TweetImage] = Field(
        ...,
        serialization_alias="attachments",
    )
    author: BaseUser
    put_like_users: list[LikeOut] = Field(..., serialization_alias="likes")


class TweetsOut(SuccessMessage):
    """Лента с твитами. Родитель: SuccessMessage."""

    tweets: list[TweetOut]
