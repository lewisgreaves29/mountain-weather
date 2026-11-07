from pathlib import Path
import httpx
import pytest
import respx
from backend.app.services.collector import OPEN_METEO_BASE_URL, WeatherCollector


@pytest.fixture
def mock_open_meteo_payload():
    return {
        "latitude": 54.6,
        "longitude": -3.1,
        "elevation": 931.0,
        "hourly": {
            "time": ["2026-11-07T12:00", "2026-11-07T13:00"],
            "temperature_2m": [4.5, 4.0],
            "apparent_temperature": [0.5, -0.2],
            "precipitation_probability": [20.0, 35.0],
            "precipitation": [0.0, 0.2],
            "wind_speed_10m": [22.0, 24.0],
            "wind_gusts_10m": [32.0, 35.0],
            "wind_direction_10m": [260.0, 270.0],
            "cloud_cover": [80.0, 90.0],
            "cloud_cover_low": [60.0, 70.0],
            "freezing_level_height": [1200.0, 1150.0],
            "dew_point_2m": [1.0, 1.2],
        },
    }


@pytest.mark.asyncio
async def test_collector_query_parameters(mock_open_meteo_payload):
    """Assert queries include models=ukmo_seamless, elevation=<AMSL>, and appropriate hourly variables."""
    collector = WeatherCollector(locations_file=Path("config/locations.yaml"))

    with respx.mock(base_url="https://api.open-meteo.com") as respx_mock:
        route = respx_mock.get("/v1/forecast").respond(
            status_code=200,
            json=mock_open_meteo_payload,
        )

        async with httpx.AsyncClient() as client:
            resp = await collector.fetch_open_meteo(
                lat=54.651,
                lon=-3.148,
                elevation=931.0,
                client=client,
            )

        assert route.called
        last_request = route.calls.last.request
        query = dict(last_request.url.params)

        assert query["models"] == "ukmo_seamless"
        assert float(query["elevation"]) == 931.0
        assert query["wind_speed_unit"] == "mph"
        assert query["temperature_unit"] == "celsius"
        assert "temperature_2m" in query["hourly"]
        assert "freezing_level_height" in query["hourly"]
        assert resp.elevation == 931.0


@pytest.mark.asyncio
async def test_collector_collect_all_and_cache_preservation(mock_open_meteo_payload):
    """Assert successful collection and that upstream HTTP 500 or timeout preserves the last known valid cache."""
    collector = WeatherCollector(locations_file=Path("config/locations.yaml"))

    with respx.mock(base_url="https://api.open-meteo.com") as respx_mock:
        # 1. Success response for initial collection
        respx_mock.get("/v1/forecast").respond(
            status_code=200,
            json=mock_open_meteo_payload,
        )

        result = await collector.collect_all()
        assert len(result.regions) > 0
        assert collector.is_ready is True
        assert result.cached is False

        # 2. Simulate upstream HTTP 500 failure
        respx_mock.reset()
        respx_mock.get("/v1/forecast").respond(status_code=500)

        # get_weather with force_refresh should gracefully fall back to existing cache
        stale_result = await collector.get_weather(force_refresh=True)
        assert stale_result is not None
        assert stale_result.cached is True
        assert len(stale_result.regions) == len(result.regions)


@pytest.mark.asyncio
async def test_collector_raises_when_no_cache_on_upstream_error():
    """Assert that when no cache exists yet, an upstream failure raises an exception."""
    collector = WeatherCollector(locations_file=Path("config/locations.yaml"))

    with respx.mock(base_url="https://api.open-meteo.com") as respx_mock:
        respx_mock.get("/v1/forecast").respond(status_code=500)

        with pytest.raises(httpx.HTTPStatusError):
            await collector.get_weather(force_refresh=True)
