from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(path, headers={'Authorization': f'Bearer {service_config.api_key}'})
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_model(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="UnknownModel", user_id=user_id)
    with client:
        response = client.get(path, headers={'Authorization': f'Bearer {service_config.api_key}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_for_unknown_user(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 10**10
    path = GET_RECO_PATH.format(model_name="some_model", user_id=user_id)
    with client:
        response = client.get(path, headers={'Authorization': f'Bearer {service_config.api_key}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_not_authenticated(
    client: TestClient
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="test_model", user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
