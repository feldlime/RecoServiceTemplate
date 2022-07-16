from http import HTTPStatus
from typing import List

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse

from service.api.exceptions import UserNotFoundException
from service.response import create_response


class RecoResponse(BaseModel):
    items: List[str]


router = APIRouter()


@router.get(
    path="/health",
    tags=["Health"],
)
async def ping() -> JSONResponse:
    return create_response(message="I am alive :)", status_code=HTTPStatus.OK)


@router.get(
    path="/reco/{user_id}",
    tags=["Health"],
    response_model=RecoResponse,
)
async def get_reco(user_id: str) -> RecoResponse:
    # Write your code here

    if len(user_id) > 3:  # stub check
        raise UserNotFoundException(error_message=f"User {user_id} not found")

    reco = [user_id + "a", user_id + "b"]  # stub reco

    return RecoResponse(items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
