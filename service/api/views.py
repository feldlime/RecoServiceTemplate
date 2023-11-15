from typing import List

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError, WrongTokenError
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={
        401: {
            "description": "Wrong token",
            "content": {
                "application/json": {
                    "example": {"error_key": "wrong_token", "error_message": "Token is wrong", "error_loc": "null"}
                }
            },
        },
        404: {
            "description": "User or model not found",
            "content": {
                "application/json": {
                    "example": [
                        {"error_key": "model_not_found", "error_message": "Model not found", "error_loc": "null"},
                        {"error_key": "user_not_found", "error_message": "User is unknown", "error_loc": "null"},
                    ]
                }
            },
        },
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    k_recs = request.app.state.k_recs
    models = request.app.state.models
    auth_token = request.headers.get("authorization").split()[1]

    if auth_token != request.app.state.orig_token:
        raise WrongTokenError()

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name not in request.app.state.models:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    reco = models[model_name].get_reco(user_id, k_recs)

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
