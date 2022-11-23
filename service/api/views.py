import os
from typing import List

from fastapi import APIRouter, FastAPI, Request, Depends
from pydantic import BaseModel
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.model_zero import Model
from models.model_utils import load_model
from service.api.exceptions import UserNotFoundError, WrongModelName, NotAuthUser
from service.log import app_logger
from creds import token

router = APIRouter()
security = HTTPBearer()
# load model
model: Model = load_model(os.getenv("MODEL_NAME", "model_0"))


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


def authorize(credentials: HTTPAuthorizationCredentials = Depends(security)):
    submitted_token: str = credentials.credentials
    is_token_ok = submitted_token == token.split()[-1]

    if not is_token_ok:
        raise NotAuthUser(error_message=f"Wrong token: {submitted_token}")


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
    dependencies=[Depends(authorize)]
)
async def get_reco(
        request: Request,
        model_name: str,
        user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name != model.name:
        raise WrongModelName(error_message=f"Model {model_name} doesn't exist")

    k_recs = request.app.state.k_recs
    predicts = model.predict(k_recs)
    return RecoResponse(user_id=user_id, items=predicts)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
