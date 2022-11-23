from http import HTTPStatus
from starlette.testclient import TestClient

from service.settings import ServiceConfig


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK
