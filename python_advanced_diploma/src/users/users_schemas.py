"""Users schemas file. Used to define schemas to users routes."""
from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    """Базовый пользователь. Родитель: BaseModel."""

    id: int = Field(..., gt=0)
    name: str


class UserOut(BaseUser):
    """Исходящий пользователь. Родитель: BaseModel."""

    followers: list[BaseUser]
    following: list[BaseUser]


class UsersOut(BaseModel):
    """Исходящие пользователи. Родитель: BaseModel."""

    request_result: bool = Field(..., serialization_alias="result")
    user: UserOut
