import random
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, FastAPI, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from service.api.exceptions import UserNotFoundError
from service.log import app_logger

MODEL_PATH = "recmodels/baseknn.pkl"
userknn = load_model(MODEL_PATH)


class NotFoundModel(BaseModel):
    detail: str


class UnauthorizedModel(BaseModel):
    detail: str


class InternalServerErrorModel(BaseModel):
    detail: str


security = HTTPBearer()
API_KEY = "i_love_recsys"
VALID_MODELS = ['some_model', 'best_random', 'knn']


async def verify_token(
    http_authorization_credentials: HTTPAuthorizationCredentials = Security(
        security)):
    token = http_authorization_credentials.credentials
    if token != API_KEY:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Invalid or missing token")


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
    responses={
        200: {
            "description": "Successful health response",
        },
        500: {
            "description": "Internal server error",
            "model": InternalServerErrorModel,
        }
    }
)
async def health() -> str:
    return "I am alive"


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    dependencies=[Security(verify_token)],
    responses={
        200: {
            "description": "Successful response with recommendations",
            "model": RecoResponse,
        },
        404: {
            "description": "Model not found or user not found",
            "model": NotFoundModel,
        },
        401: {
            "description": "Unauthorized access",
            "model": UnauthorizedModel,
        },
        500: {
            "description": "Internal server error",
            "model": InternalServerErrorModel,
        }
    }
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
) -> RecoResponse:
    app_logger.info(f"Запрос на модель: {model_name}, user_id: {user_id}")

    if model_name not in VALID_MODELS and model_name != "best_random":
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Модель {model_name} не найдена"
        )

    if user_id > 10 ** 9:
        raise UserNotFoundError(
            error_message=f"Пользователь {user_id} не найден"
        )

    reco = []

    if model_name == "best_random":
        reco = random.sample(range(0, 10), 10)
    elif model_name == 'knn':
        reco = predict(userknn, user_id, N_recs=10)['item_id'].tolist()
    else:
        k_recs = request.app.state.k_recs
        reco = list(range(k_recs))

    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
