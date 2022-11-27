from typing import List

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from service.api.exceptions import ModelNotFoundError, UserNotFoundError
from service.log import app_logger
from service.utils import verify_token


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
token_auth_scheme = HTTPBearer()


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
        404: {"description": "User/model not found"},
        401: {"description": "Not authorized"},
    },
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: str = Depends(token_auth_scheme),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    verify_token(request.app.state.token, token.credentials)

    app_logger.info(f"Valid token for user_id: {user_id}")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name == "rec_model_test":
        k_recs = request.app.state.k_recs
    else:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    return RecoResponse(user_id=user_id, items=list(range(k_recs)))


def add_views(app: FastAPI) -> None:
    app.include_router(router)
