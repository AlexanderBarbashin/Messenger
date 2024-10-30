"""App schemas file. Used to define schemas to all app routes."""
from typing import Dict

from pydantic import BaseModel


class SuccessMessage(BaseModel):
    """Сообщение об успешном выполнении запроса. Родитель: BaseModel."""

    result: bool = True


class ErrorMessage(BaseModel):
    """Сообщение об ошибке. Родитель: BaseModel."""

    result: bool = False
    error_type: str
    error_message: str | Dict


class ValidationErrorMessage(ErrorMessage):
    """Сообщение об ошибке валидации. Родитель: ErrorMessage."""

    error_message: dict = {
        "detail": [
            {
                "loc": [
                    "string",
                    0,
                ],
                "msg": "string",
                "type": "string",
            },
        ],
    }
