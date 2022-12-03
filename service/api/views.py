import logging
from typing import List

import numpy as np
from fastapi import (
    APIRouter,
    Depends,
    FastAPI,
    Request,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from pydantic import BaseModel

from creds import token
from recommendations.estimator import Estimator
from recommendations.model_utils import load_model
from service.api.exceptions import (
    NotAuthUser,
    UserNotFoundError,
    WrongModelName,
)

router = APIRouter()
security = HTTPBearer()

log = logging.getLogger(__name__)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


def authorize(
    credentials: HTTPAuthorizationCredentials = Depends(security),  # noqa: B008
):
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
    dependencies=[Depends(authorize)],
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    log.info(f"Request for model: {model_name}, user_id: {user_id}")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    try:
        model: Estimator = load_model(model_name)
    except ValueError:
        raise WrongModelName(error_message=f"Model {model_name} doesn't exist")

    k_recs = request.app.state.k_recs
    recommendations: np.ndarray = model.recommend([user_id], k_recs)
    return RecoResponse(user_id=user_id, items=recommendations.tolist())


def add_views(app: FastAPI) -> None:
    app.include_router(router)
