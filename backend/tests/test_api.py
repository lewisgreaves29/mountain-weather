from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import respx
from fastapi.testclient import TestClient

from backend.app.main import app, lifespan
from backend.app.services.collector import collector
from backend.app.services.secrets import validate_secrets


@pytest.fixture
def client():
    return TestClient(app)


def test_healthz_endpoint(client):
    """GET /healthz returns {"status": "ok"}."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readyz_endpoint(client):
    """GET /readyz returns 503 while cache is not populated, and 200 once populated."""
    # Test unready state
    collector._is_ready = False
    response = client.get("/readyz")
    assert response.status_code == 503

    # Test ready state
    collector._is_ready = True
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_weather_endpoint_success(client):
    """GET /api/v1/weather returns validated JSON complying with domain models."""
    sample_payload = {
        "latitude": 54.6,
        "longitude": -3.1,
        "elevation": 931.0,
        "hourly": {
            "time": ["2026-11-07T12:00"],
            "temperature_2m": [4.5],
            "apparent_temperature": [0.5],
            "precipitation_probability": [20.0],
            "precipitation": [0.0],
            "wind_speed_10m": [22.0],
            "wind_gusts_10m": [32.0],
            "wind_direction_10m": [260.0],
            "cloud_cover": [80.0],
            "cloud_cover_low": [60.0],
            "freezing_level_height": [1200.0],
            "dew_point_2m": [1.0],
        },
    }

    with respx.mock(base_url="https://api.open-meteo.com") as respx_mock:
        respx_mock.get("/v1/forecast").respond(status_code=200, json=sample_payload)

        response = client.get("/api/v1/weather?force_refresh=true")
        assert response.status_code == 200
        data = response.json()
        assert "regions" in data
        assert "generated_at" in data
        assert data["model"] == "UKMO Seamless 2km"
        assert len(data["regions"]) > 0


def test_weather_endpoint_failure(client):
    """GET /api/v1/weather returns 503 when collector raises."""
    with patch.object(collector, "get_weather", side_effect=RuntimeError("Upstream network error")):
        response = client.get("/api/v1/weather?force_refresh=true")
        assert response.status_code == 503
        assert "Unable to retrieve mountain weather data" in response.json()["detail"]


def test_spa_serving_fallback_and_files(client, tmp_path):
    """Test serving SPA fallback and static files."""
    # When static dir does not exist or has no dist
    response = client.get("/")
    assert response.status_code == 200
    assert "UK Mountain Weather Dashboard" in response.text

    # When static dir exists with index.html
    static_dir = Path("backend/app/static")
    static_dir.mkdir(parents=True, exist_ok=True)
    index_file = static_dir / "index.html"
    index_file.write_text("<!DOCTYPE html><html><body>Vue App Ready</body></html>", encoding="utf-8")
    test_asset = static_dir / "test.txt"
    test_asset.write_text("hello asset", encoding="utf-8")

    try:
        resp_index = client.get("/")
        assert resp_index.status_code == 200
        assert "Vue App Ready" in resp_index.text

        resp_asset = client.get("/test.txt")
        assert resp_asset.status_code == 200
        assert "hello asset" in resp_asset.text
    finally:
        if test_asset.exists():
            test_asset.unlink()
        if index_file.exists():
            index_file.unlink()


@pytest.mark.asyncio
async def test_app_lifespan():
    """Test lifespan startup and shutdown with scheduler and initial warm up."""
    import asyncio

    with patch.object(collector, "collect_all", new_callable=AsyncMock) as mock_collect:
        async with lifespan(app):
            await asyncio.sleep(0.05)
            assert mock_collect.called


def test_secrets_validation():
    """Verify secrets validation succeeds with valid env and exits when missing."""
    import os

    settings = validate_secrets()
    assert settings.auth_secret_token == "test-token-xyz-12345"

    orig = os.environ.get("AUTH_SECRET_TOKEN")
    try:
        os.environ["AUTH_SECRET_TOKEN"] = ""
        from backend.app.config import get_settings

        get_settings.cache_clear()
        with pytest.raises((SystemExit, RuntimeError)):
            validate_secrets()
    finally:
        if orig:
            os.environ["AUTH_SECRET_TOKEN"] = orig
        get_settings.cache_clear()
