from http import HTTPStatus
from typing import List

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse

from service.log import app_logger
from service.response import create_response


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def ping() -> JSONResponse:
    return create_response(message="I am alive :)", status_code=HTTPStatus.OK)


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Health"],
    response_model=RecoResponse,
)
async def get_reco(model_name: str, user_id: str) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")
    reco = list(range(10))
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
