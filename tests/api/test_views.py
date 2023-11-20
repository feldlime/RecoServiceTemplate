from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


API_KEY = "i_love_recsys"


def test_get_reco_success(client: TestClient, service_config: ServiceConfig) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_user(client: TestClient) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_unauthorized(client: TestClient) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    response = client.get(path)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_reco_authorized(client: TestClient) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id


def test_get_reco_invalid_model(client: TestClient) -> None:
    user_id = 123
    invalid_model_name = "invalid_model"
    path = GET_RECO_PATH.format(model_name=invalid_model_name, user_id=user_id)
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
