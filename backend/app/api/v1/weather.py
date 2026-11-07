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


@router.get("/homepage")
async def get_weather_homepage() -> dict[str, str]:
    """Lightweight summary endpoint formatted for Homepage dashboard customapi widgets."""
    try:
        data = await collector.get_weather()
        result: dict[str, str] = {}
        for r in data.regions:
            max_gust = max((s.summit_current.wind_gust for s in r.sub_regions), default=0.0)
            summary = f"{r.overall_hazard.value} ({round(max_gust)}mph)"
            if r.id == "lake-district":
                result["lakes"] = summary
            elif r.id == "wales":
                result["wales"] = summary
            elif r.id == "peak-district":
                result["peak"] = summary
            result[r.id.replace("-", "_")] = summary
        result["status"] = "success"
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to retrieve homepage weather data: {exc}",
        ) from exc
