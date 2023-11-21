from typing import List
from http import HTTPStatus
from fastapi import APIRouter, FastAPI, Request
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
import random
from service.api.exceptions import UserNotFoundError
from service.log import app_logger
from service.keysconfig import api_key


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]

ErrorResponseModel = BaseModel.model_construct(detail=Field(...))

common_responses = {
    200: {
        "description": "Success!",
        "model": RecoResponse,
    },
    404: {
        "description": "Your model or user id was not found",
        "model": BaseModel.model_construct(detail=Field(...)),
    },
    401: {
        "description": "Unauthorized access",
        "model": BaseModel.model_construct(detail=Field(...)),
    },
    403: {
        "description": "Unauthorized access",
        "model": BaseModel.model_construct(detail=Field(...)),
    }
}

router = APIRouter()
security = HTTPBearer()

async def verify_token(http_authorization_credentials: HTTPAuthorizationCredentials = Security(security)):
    token = http_authorization_credentials.credentials
    if token != api_key:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token")



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
    dependencies=[Security(verify_token)],
    responses = common_responses 
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")


    

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")
    if model_name != 'random':
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"There is no model named {model_name}")
    if model_name == "random":
        reco = random.sample(range(1, 10), 10)
    else:
        k_recs = request.app.state.k_recs
        reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
