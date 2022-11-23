from typing import List

from fastapi import APIRouter, FastAPI, Request, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from service.api.exceptions import UserNotFoundError
from service.log import app_logger
from service.models import UserInDB
from service.utils import fake_users_db, fake_hash_password, MODEL_NAMES


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


router = APIRouter()

AUTH_TOKEN = "qwerty123"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.get(
    path="/health",
    tags=["Health"],
    responses={401: {"description": "Incorrect authorization token"}},
)
async def health(
    token: str = Depends(oauth2_scheme)) -> str:
    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Basic"},
        )

    return JSONResponse(
        content={'health': '36.6'},
        status_code=status.HTTP_200_OK
    )


@router.get(
    path="/reco/{model_name}/{user_id}",
    tags=["Recommendations"],
    response_model=RecoResponse,
    responses={404: {"description": "Incorrect user_id or model_name"},
               401: {"description": "Incorrect authorization token"}},
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: str = Depends(oauth2_scheme)
) -> RecoResponse:

    if token != AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Basic"},
        )

    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    # Write your code here

    if model_name not in MODEL_NAMES:
        raise HTTPException(status_code=404, detail="Model not found")

    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs
    reco = list(range(k_recs))
    return RecoResponse(user_id=user_id, items=reco)


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


def add_views(app: FastAPI) -> None:
    app.include_router(router)
