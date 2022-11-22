from typing import List

from fastapi import APIRouter, FastAPI, HTTPException, Request
from pydantic import BaseModel

from service.api.exceptions import NeedToken, TokenNotFound, UserNotFoundError
from service.log import app_logger

TOKEN_OUR = "Phoenix"


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
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # Write your code here

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    try:
        headers = dict(request.headers)
        token = headers["authorization"].split()[1]
    except:
        raise NeedToken(error_message="for this request need token")
    if token != TOKEN_OUR:
        raise TokenNotFound(error_message=f"token {token} is not our")

    k_recs = request.app.state.k_recs
    # reco = list(range(k_recs))

    if model_name == "our_model":
        reco = list(range(k_recs))
    else:
        raise HTTPException(status_code=404, detail="not found model")
        # reco = list(range(k_recs))[::-1 ]
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)

