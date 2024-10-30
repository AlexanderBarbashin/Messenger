"""Tweet media schemas file. Used to define schemas to tweet media routes."""
from pydantic import BaseModel, Field


class TweetMediaOut(BaseModel):
    """Результат создания твит медиа. Родитель: BaseModel."""

    result: bool
    tweet_id: int = Field(..., gt=0)
