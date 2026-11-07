from fastapi import APIRouter, HTTPException, Query

from backend.app.models.domain import WeatherResponse
from backend.app.services.collector import collector

router = APIRouter(prefix="/weather", tags=["weather"])


@router.get("", response_model=WeatherResponse)
async def get_weather(force_refresh: bool = Query(False)) -> WeatherResponse:
    """Returns high-resolution UK Met Office mountain weather forecasts and summit ridge hazard assessments."""
    try:
        return await collector.get_weather(force_refresh=force_refresh)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve mountain weather data: {exc}",
        ) from exc
