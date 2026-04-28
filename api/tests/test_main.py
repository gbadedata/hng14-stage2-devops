import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("redis.Redis") as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        from importlib import reload
        import api.main as main_module
        reload(main_module)
        yield TestClient(main_module.app), mock_instance


def test_health_endpoint():
    with patch("redis.Redis"):
        from importlib import reload
        import sys
        if "api.main" in sys.modules:
            del sys.modules["api.main"]
        import api.main as m
        c = TestClient(m.app)
        response = c.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_create_job_returns_job_id():
    with patch("redis.Redis") as mock_redis:
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        import sys
        if "api.main" in sys.modules:
            del sys.modules["api.main"]
        import api.main as m
        c = TestClient(m.app)
        response = c.post("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert len(data["job_id"]) == 36  # UUID format


def test_get_job_not_found():
    with patch("redis.Redis") as mock_redis:
        mock_instance = MagicMock()
        mock_instance.hget.return_value = None
        mock_redis.return_value = mock_instance
        import sys
        if "api.main" in sys.modules:
            del sys.modules["api.main"]
        import api.main as m
        c = TestClient(m.app)
        response = c.get("/jobs/nonexistent-id")
        assert response.status_code == 404


def test_get_job_returns_status():
    with patch("redis.Redis") as mock_redis:
        mock_instance = MagicMock()
        mock_instance.hget.return_value = b"completed"
        mock_redis.return_value = mock_instance
        import sys
        if "api.main" in sys.modules:
            del sys.modules["api.main"]
        import api.main as m
        c = TestClient(m.app)
        response = c.get("/jobs/some-valid-id")
        assert response.status_code == 200
        assert response.json()["status"] == "completed"
