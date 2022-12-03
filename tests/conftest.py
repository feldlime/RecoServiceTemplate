import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from creds import token
from service.api.app import create_app
from service.settings import (
    ServiceConfig,
    get_config,
)


@pytest.fixture
def service_config() -> ServiceConfig:
    return get_config()


@pytest.fixture
def app(
    service_config: ServiceConfig,
) -> FastAPI:
    app = create_app(service_config)
    return app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    client = TestClient(app=app)
    client.headers.setdefault("Authorization", token)
    return client
