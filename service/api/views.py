from typing import Any, Dict, List

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel

from service.api.exceptions import (
    BearerAccessTokenError,
    ModelNotFoundError,
    UserNotFoundError,
)
from service.api.responses import (
    AuthorizationResponse,
    ForbiddenResponse,
    NotFoundError,
)
from service.configuration import (
    ANN_PATHS,
    FEATURES_FOR_COLD,
    ITEM_MAPPING,
    LIGHT_FM,
    OFFLINE_KNN_MODEL_PATH,
    ONLINE_KNN_MODEL_PATH,
    POPULAR_IN_CATEGORY,
    POPULAR_MODEL_RECS,
    POPULAR_MODEL_USERS,
    UNIQUE_FEATURES,
    USER_MAPPING,
)
from service.log import app_logger
from service.reco_models import (
    ANNLightFM,
    OfflineKnnModel,
    OnlineFM,
    OnlineKnnModel,
    PopularInCategory,
    SimplePopularModel,
)

baseline_model = PopularInCategory(POPULAR_IN_CATEGORY)
popular_model = SimplePopularModel(
    POPULAR_MODEL_USERS,
    POPULAR_MODEL_RECS,
)
offline_knn_model = OfflineKnnModel(OFFLINE_KNN_MODEL_PATH)
online_knn_model = OnlineKnnModel(ONLINE_KNN_MODEL_PATH)
# Use LightFM model to predict recos for cold with features,
# popular for others
online_fm_part_popular = OnlineFM(
    name=LIGHT_FM,
    USER_MAPPING=USER_MAPPING,
    ITEM_MAPPING=ITEM_MAPPING,
    FEATURES_FOR_COLD=FEATURES_FOR_COLD,
    UNIQUE_FEATURES=UNIQUE_FEATURES,
)
#  Use popular model to predict recos for all cold
online_fm_all_popular = OnlineFM(
    name=LIGHT_FM,
    cold_with_fm=False,
    USER_MAPPING=USER_MAPPING,
    ITEM_MAPPING=ITEM_MAPPING,
    FEATURES_FOR_COLD=FEATURES_FOR_COLD,
    UNIQUE_FEATURES=UNIQUE_FEATURES,
)
ann_lightfm = ANNLightFM(ANN_PATHS, popular_model)


class RecoResponse(BaseModel):
    user_id: int
    items: List[int]


bearer_scheme = HTTPBearer()

router = APIRouter()

responses: Dict[str, Any] = {
    "401": AuthorizationResponse().get_response(),
    "403": ForbiddenResponse().get_response(),
    "404": NotFoundError().get_response(),
}


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
    responses=responses,  # type: ignore
)
async def get_reco(
    request: Request,
    model_name: str,
    user_id: int,
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> RecoResponse:
    app_logger.info(f"Request for model: {model_name}, user_id: {user_id}")

    if token.credentials != "Team_5":
        raise BearerAccessTokenError()
    if user_id > 10**9:
        raise UserNotFoundError(error_message=f"User {user_id} not found")

    k_recs = request.app.state.k_recs

    reco = None
    model_names = ["test_model", "baseline", "knn", "online_knn", "light_fm_1", "light_fm_2", "ann_lightfm"]
    if model_name == "test_model":
        reco = list(range(k_recs))
    if model_name == "baseline":
        reco = baseline_model.predict(user_id, k_recs)
    if model_name in ("knn", "online_knn"):
        reco = offline_knn_model.predict(user_id) if model_name == "knn" else online_knn_model.predict(user_id)
    if model_name in ("light_fm_1", "light_fm_2"):
        reco = (
            online_fm_all_popular.predict(user_id, k_recs)
            if model_name == "light_fm_1"
            else online_fm_part_popular.predict(user_id, k_recs)
        )
    if model_name == "ann_lightfm":
        reco = ann_lightfm.predict(user_id)

    if model_name not in model_names:
        raise ModelNotFoundError(error_message=f"Model {model_name} not found")
    if not reco:
        reco = popular_model.predict(user_id, k_recs)
    return RecoResponse(user_id=user_id, items=reco)


def add_views(app: FastAPI) -> None:
    app.include_router(router)
