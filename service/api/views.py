from typing import List

from fastapi import APIRouter, FastAPI, Request
from pydantic import BaseModel

from service.api.exceptions import (
    ModelNotFoundError,
    NotCorrectBearerTokenError,
    UserNotFoundError,
)
from service.log import app_logger

from .auth import BEARER_TOKEN_DEPS
from .models import MODELS


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


RECO_EXAMPLE_404 = {
    "errors": [
        {
            "error_key": "model_not_found",
            "error_message": "Model unknown_model not found",
            "error_loc": None,
        },
        {
            "error_key": "user_not_found",
            "error_message": "User 10000000000 not found",
            "error_loc": None,
        },
    ]
}


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={
        404: {
            "description": "Not found user or model",
            "content": {"application/json": {"example": RECO_EXAMPLE_404}},
        }
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: str = BEARER_TOKEN_DEPS,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    print(token, request.app.state.admin_token)
    if token != request.app.state.admin_token:
        raise NotCorrectBearerTokenError()

    if model_name not in MODELS:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    model = MODELS[model_name]()
    reco = model.predict(user_id=user_id, k_recs=k_recs)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
