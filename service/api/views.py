from typing import List

from fastapi import APIRouter, FastAPI, Header, Request
from pydantic import BaseModel

from service.api.exceptions import InvalidAuthorization, ModelNotFoundError, UserNotFoundError
from service.api.recsys.user_based_recsys import get_reccomendation
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


def check_access(authorization):
    if authorization is None:
        raise InvalidAuthorization(error_message=f"No token")
    token = authorization.split(" ")[-1]
    SECRET_KEY = "mYOHbHbOwViaarXnJGlAihcJhIjjQDUQ"
    if token != SECRET_KEY:
        raise InvalidAuthorization(error_message=f"Invalid token {token}")


@router.get(
    path="/health",
    tags=["Health"],
)
async def health(authorization: str = Header(None)) -> str:
    check_access(authorization)
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
)
async def get_reco(request: Request, model_name: str, user_id: int, authorization: str = Header(None)) -> RecoResponse:
    check_access(authorization)
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")
    if model_name != "user_based":
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")
    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    # reco = get_reccomendation(user_id, request.app.state.k_recs)
    reco = list(range(1, 11))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
