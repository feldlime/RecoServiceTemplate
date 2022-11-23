from typing import List

from fastapi import APIRouter, FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from service.api.exceptions import UserNotFoundError, ModelNotFoundError
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()
auth_scheme = HTTPBearer(auto_error=False)


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
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> RecoResponse:

    if token:
        token_api = token.credentials

        if token_api != "api":
            raise HTTPException(
                status_code=401,
                detail="wrong api key",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(

            status_code=401,
            detail="wrong api key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")
    model_names = ["test_model"]

    if user_id > 10 ** 9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name not in model_names:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
