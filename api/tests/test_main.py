import pytest
from unittest.mock import MagicMock, patch

with patch("redis.Redis") as _mock:
    _mock.return_value = MagicMock()
    from main import app

from fastapi.testclient import TestClient

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_job_returns_job_id():
    with patch("main.r") as mock_r:
        mock_r.lpush = MagicMock()
        mock_r.hset = MagicMock()
        response = client.post("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert len(data["job_id"]) == 36


def test_get_job_not_found():
    with patch("main.r") as mock_r:
        mock_r.hget.return_value = None
        response = client.get("/jobs/nonexistent-id")
        assert response.status_code == 404


def test_get_job_returns_status():
    with patch("main.r") as mock_r:
        mock_r.hget.return_value = b"completed"
        response = client.get("/jobs/some-valid-id")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
