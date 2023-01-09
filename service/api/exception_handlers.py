from typing import Union

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from service.log import app_logger
from service.models import Error
from service.response import create_response, server_error

from .exceptions import AppException


async def default_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    app_logger.error(str(exc))
    error = Error(error_key="server_error", error_message=str(exc))
    return server_error([error])


async def http_error_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    app_logger.error(str(exc))
    error = Error(error_key="http_exception", error_message=exc.detail)
    return create_response(status_code=exc.status_code, errors=[error])


async def validation_error_handler(
    request: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    errors = [
        Error(
            error_key=err.get("type"),
            error_message=err.get("msg"),
            error_loc=err.get("loc"),
        )
        for err in exc.errors()
    ]
    app_logger.error(str(errors))
    return create_response(status.HTTP_422_UNPROCESSABLE_ENTITY, errors=errors)


async def app_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    errors = [
        Error(
            error_key=exc.error_key,
            error_message=exc.error_message,
            error_loc=exc.error_loc,
        )
    ]
    app_logger.error(str(errors))
    return create_response(exc.status_code, errors=errors)


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, default_error_handler)
