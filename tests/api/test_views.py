from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_with_uncorrect_token(
    client: TestClient,
) -> None:
    auth_token = "uncorrect_token"
    headers = {"Authorization": "Bearer " + auth_token}
    user_id = 123
    path = GET_RECO_PATH.format(
        model_name="random_number_model", user_id=user_id
    )
    with client:
        response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert (
        response.json()["errors"][0]["error_key"] == "not_correct_bearer_token"
    )


def test_get_reco_without_token(
    client: TestClient,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(
        model_name="random_number_model", user_id=user_id
    )
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_key"] == "http_exception"


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    auth_token = service_config.admin_token
    headers = {"Authorization": "Bearer " + auth_token}
    user_id = 123
    path = GET_RECO_PATH.format(
        model_name="random_number_model", user_id=user_id
    )
    with client:
        response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert len(response_json["items"]) == len(set(response_json["items"]))
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_get_reco_for_unknown_model(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    auth_token = service_config.admin_token
    headers = {"Authorization": "Bearer " + auth_token}
    user_id = 123
    path = GET_RECO_PATH.format(model_name="unknown_model", user_id=user_id)
    with client:
        response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_for_unknown_user(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    auth_token = service_config.admin_token
    headers = {"Authorization": "Bearer " + auth_token}
    user_id = 10**10
    path = GET_RECO_PATH.format(
        model_name="random_number_model", user_id=user_id
    )
    with client:
        response = client.get(path, headers=headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"
