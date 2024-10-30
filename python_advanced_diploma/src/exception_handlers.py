"""Exception handlers file. Used to handle raises exceptions."""
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, NoResultFound
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from python_advanced_diploma.src.config import logger


def add_no_result_found_exception_handler(app: FastAPI) -> None:
    """
    Функция для добавления обработчика исключения 'NoResultFound' в приложение.

    :param app: приложение
    """
    @app.exception_handler(NoResultFound)
    async def no_result_found_exception_handler(
        request: Request, exc: NoResultFound,
    ) -> Response:
        """
        Обработчик исключения 'NoResultFound'.

        :param request: HTTP запрос
        :param exc: исключение
        :return: HTTP ответ
        """
        user_api_key = request.headers.get("api-key")
        requested_url = request.url
        request_method = request.method
        path_params = request.path_params
        error_message = (
            "NoResultFound exception raised when trying to "
            "execute request to URL: '{requested_url}' by method "
            "'{request_method}' with api-key: '{user_api_key}' "
            "and path parameters: '{path_params}'"
        ).format(
            user_api_key=user_api_key,
            requested_url=requested_url,
            request_method=request_method,
            path_params=path_params,
        )
        logger.error(error_message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": False,
                "error_type": "NoResultFound",
                "error_message": error_message,
            },
        )


def add_attribute_error_exception_handler(app: FastAPI) -> None:
    """
    Функция для добавления обработчика исключения 'AttributeError'.

    Добавляет обработчик исключения 'AttributeError' в приложение.
    :param app: приложение
    """
    @app.exception_handler(AttributeError)
    async def attribute_error_exception_handler(
        request: Request, exc: AttributeError,
    ) -> Response:
        """
        Обработчик исключения 'AttributeError'.

        :param request: HTTP запрос
        :param exc: исключение
        :return: HTTP ответ
        """
        user_api_key = request.headers.get("api-key")
        requested_url = request.url
        request_method = request.method
        path_params = request.path_params
        error_message = (
            "AttributeError exception raise when trying to execute "
            "request to URL: '{requested_url}' by method "
            "'{request_method} with api-key: '{user_api_key}' "
            "and path parameters: '{path_params}'"
        ).format(
            user_api_key=user_api_key,
            requested_url=requested_url,
            request_method=request_method,
            path_params=path_params,
        )
        logger.error(error_message)
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": False,
                "error_type": "AttributeError",
                "error_message": error_message,
            },
        )


def add_integrity_error_exception_handler(app: FastAPI) -> None:
    """
    Функция для добавления обработчика исключения 'IntegrityError'.

    Добавляет обработчик исключения 'IntegrityError' в приложение.
    :param app: приложение
    """
    @app.exception_handler(IntegrityError)
    async def integrity_error_exception_handler(
        request: Request, exc: IntegrityError,
    ) -> Response:
        """
        Обработчик исключения 'IntegrityError'.

        :param request: HTTP запрос
        :param exc: исключение
        :return: HTTP ответ
        """
        logger.error(exc.args[0])
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": False,
                "error_type": "IntegrityError",
                "error_message": exc.args[0],
            },
        )


def override_validation_exception_handler(app: FastAPI) -> None:
    """
    Функция для перезаписи обработчика исключения 'RequestValidationError'.

    Перезаписывает обработчик исключения 'RequestValidationError' в
    приложении.
    :param app: приложение
    """
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError,
    ) -> Response:
        """
        Обработчик исключения 'RequestValidationError'.

        :param request: HTTP запрос
        :param exc: исключение
        :return: HTTP ответ
        """
        user_api_key = request.headers.get("api-key")
        path_params = request.path_params
        request_body_bytes = await request.body()
        request_body = request_body_bytes.decode()
        error_message = (
            "{errors} occurred when trying to execute request to URL:"
            " '{requested_url}' by method '{request_method} with "
            "api-key: '{user_api_key}', path parameters: "
            "'{path_params}' and request_body: '{request_body}'"
        ).format(
            errors=exc.errors(),
            user_api_key=user_api_key,
            requested_url=request.url,
            request_method=request.method,
            path_params=path_params,
            request_body=request_body,
        )
        logger.error(error_message)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "result": False,
                "error_type": "RequestValidationError",
                "error_message": exc.errors(),
            },
        )
