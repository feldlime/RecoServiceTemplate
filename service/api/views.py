from typing import List

from fastapi import APIRouter, FastAPI, Request, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

from service.api.exceptions import UserNotFoundError, ModelNotFoundError
from service.log import app_logger


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]

class NotFoundError(BaseModel):
    error_key: str
    error_message: str
    error_loc: Optional[Sequence[str]]        

router = APIRouter()
SEC_TOKEN = "12345678"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")

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
    responses={404: {"model": NotFoundError, "user": NotFoundError}}
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: str = Depends(oauth2_scheme)
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if token != SEC_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Basic"},
        )

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    if model_name != 'model_1':
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
