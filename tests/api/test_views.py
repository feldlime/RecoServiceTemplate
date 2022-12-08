import os
from http import HTTPStatus

from requests.structures import CaseInsensitiveDict
from starlette.testclient import TestClient

from service.settings import ServiceConfig


GET_RECO_PATH = "/reco/{model_name}/{user_id}"
ACCESS_TOKEN = os.getenv("ACCESS_KEY", "12345678")


def test_health(
    client: TestClient,
) -> None:
    client.headers = CaseInsensitiveDict(
        {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="random", user_id=user_id)
    client.headers = CaseInsensitiveDict(
        {"Authorization": f"Bearer {ACCESS_TOKEN}"}
     )
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="random", user_id=user_id)
    client.headers = CaseInsensitiveDict(
        {"Authorization": f"Bearer {ACCESS_TOKEN}"}
     )
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
 ) -> None:
    user_id = 1
    path = GET_RECO_PATH.format(model_name="imagine_model", user_id=user_id)
    client.headers = CaseInsensitiveDict(
        {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    )
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_unauthorized(
    client: TestClient,
) -> None:
    user_id = 1
    path = GET_RECO_PATH.format(model_name="imagine_model", user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_key"] == "authorization_error"
