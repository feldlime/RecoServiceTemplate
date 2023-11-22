from http import HTTPStatus

from starlette.testclient import TestClient
from service.keysconfig import api_key
from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"
HEADERS = {f"Your key is {api_key}"}

def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    
    response = client.get(path, headers=HEADERS)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(
    client: TestClient,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    response = client.get(path, headers=HEADERS)
    assert response.status_code == HTTPStatus.NOT_FOUND #404
    assert response.json()["errors"][0]["error_key"] == "user_not_found"

def test_get_reco_invalid_model(client: TestClient) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name='dsa', user_id=user_id)
    response = client.get(path, headers=HEADERS)
    assert response.status_code == HTTPStatus.NOT_FOUND #404


def test_get_reco_unauthorized(client: TestClient) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    response = client.get(path)
    assert response.status_code == HTTPStatus.FORBIDDEN #403
    assert response.json()["errors"][0]["error_key"] == "user_not_authorized"
 

def test_get_reco_authorized(client: TestClient) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    response = client.get(path, headers=HEADERS)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id


