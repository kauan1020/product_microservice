import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus
from unittest.mock import patch

from tech.api.app import app


class TestApp:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_read_root(self, client):
        response = client.get("/")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "Tech Challenge FIAP - Kauan Silva!      Products Microservice"}
