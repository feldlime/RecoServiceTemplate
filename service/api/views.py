from typing import List

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel

from service.api.exceptions import (
    BearerAccessTokenError,
    ModelNotFoundError,
    UserNotFoundError,
)
from service.log import app_logger
from service.models import Error, ErrorResponse


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


bearer_scheme = HTTPBearer()

router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


# Null values are ignored by OpenAPI.
# Problem: https://github.com/tiangolo/fastapi/issues/5559
responses = {
    401: {
        "model": ErrorResponse,
        "description": "Error: Unauthorized",
        "content": {
            "application/json": {
                "example": ErrorResponse(
                    errors=[
                        Error(
                            error_key="incorrect_bearer_key",
                            error_message=(
                                "Authorization failure due to incorrect token"
                            ),
                            error_loc=None,
                        )
                    ]
                )
            }
        },
    },
    403: {
        "model": ErrorResponse,
        "description": "Error: Forbidden",
        "content": {
            "application/json": {
                "example": ErrorResponse(
                    errors=[
                        Error(
                            error_key="http_exception",
                            error_message="Not authenticated",
                            error_loc=None,
                        )
                    ]
                )
            }
        },
    },
    404: {
        "model": ErrorResponse,
        "description": "Error: Not Found",
        "content": {
            "application/json": {
                "examples": {
                    "example_1": {
                        "summary": "Model error",
                        "value": ErrorResponse(
                            errors=[
                                Error(
                                    error_key="model_not_found",
                                    error_message="Model is unknown",
                                    error_loc=None,
                                )
                            ]
                        ),
                    },
                    "example_2": {
                        "summary": "User error",
                        "value": ErrorResponse(
                            errors=[
                                Error(
                                    error_key="user_not_found",
                                    error_message="User is unknown",
                                    error_loc=None,
                                )
                            ]
                        ),
                    },
                }
            },
        },
    },
}


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses=responses,  # type: ignore
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # Write your code here

    # TODO() 1. Добавить описание возможных ответов (401, 403,, 404) в сваггер
    # TODO() 2. Покрыть тестами 401 ошибку аутентификации
    #  и 404 ошибку отсутствия модели
    if token.credentials != "Team_5":
        raise BearerAccessTokenError()
    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    if model_name != "test_model":
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
