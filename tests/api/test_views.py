from http import HTTPStatus

from decouple import config

# from requests.structures import CaseInsensitiveDict
from starlette.testclient import TestClient

from service.api.auth.auth_handler import signJWT
from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"
JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

auth_token = signJWT()
correct_headers = {"Authorization": f"Bearer {auth_token['access_token']}"}


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
    path = GET_RECO_PATH.format(model_name="random", user_id=user_id)
    with client:
        response = client.get(path, headers=correct_headers)
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
    with client:
        response = client.get(path, headers=correct_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "user_not_found"


def test_get_reco_for_unknown_model(
    client: TestClient,
) -> None:
    user_id = 123
    model_name = "unknown"
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    with client:
        response = client.get(path, headers=correct_headers)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["errors"][0]["error_key"] == "model_not_found"


def test_get_reco_unauthorized_invalid_authentication_scheme(
    client: TestClient,
) -> None:
    user_id = 123
    model_name = "random"
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    bad_headers = {"Authorization": f"X-token {auth_token}"}
    with client:
        response = client.get(path, headers=bad_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["errors"][0]["error_key"] == "http_exception"
    assert response.json()["errors"][0]["error_message"] == "Invalid authentication credentials"


def test_get_reco_unauthorized_invalid_token(
    client: TestClient,
) -> None:
    user_id = 123
    model_name = "random"
    auth_token = "wrong_auth_token"
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    bad_token_headers = {"Authorization": f"Bearer {auth_token}"}
    with client:
        response = client.get(path, headers=bad_token_headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json()["errors"][0]["error_key"] == "http_exception"
    assert response.json()["errors"][0]["error_message"] == "Invalid token or expired token."


def test_get_reco_unauthorized_invalid_authorization_code(
    client: TestClient,
) -> None:
    user_id = 123
    model_name = "random"
    path = GET_RECO_PATH.format(model_name=model_name, user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json()["errors"][0]["error_key"] == "http_exception"
    assert response.json()["errors"][0]["error_message"] == "Not authenticated"
