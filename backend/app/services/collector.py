import asyncio
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import jsonschema
import yaml

from backend.app.config import get_settings
from backend.app.models.domain import (
    HazardLevel,
    HourlyForecastPoint,
    LocationPoint,
    RegionWeather,
    SubRegionWeather,
    WeatherMetricPoint,
    WeatherResponse,
)
from backend.app.models.open_meteo import OpenMeteoResponse
from backend.app.services.hazard_engine import hazard_engine

logger = logging.getLogger(__name__)

OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_HOURLY_VARS = (
    "temperature_2m,apparent_temperature,precipitation_probability,precipitation,"
    "wind_speed_10m,wind_gusts_10m,wind_direction_10m,cloud_cover,cloud_cover_low,"
    "freezing_level_height,dew_point_2m"
)


class WeatherCollector:
    """Collects deterministic UK Met Office weather forecasts via Open-Meteo

    for UK mountain summits and valley baselines, maintaining an async-safe in-memory cache.
    """

    def __init__(self, locations_file: Path | None = None):
        self.settings = get_settings()
        self.locations_file = locations_file or self.settings.locations_file
        self.locations_config: dict[str, Any] = {}
        self._cache: WeatherResponse | None = None
        self._cache_lock = asyncio.Lock()
        self._is_ready = False
        self._load_locations()

    def _load_locations(self) -> None:
        """Loads and validates locations from locations.yaml against locations.schema.json."""
        if not self.locations_file.exists():
            raise FileNotFoundError(f"Locations configuration file not found at: {self.locations_file}")

        schema_file = self.locations_file.parent / "locations.schema.json"
        with open(self.locations_file, encoding="utf-8") as f:
            self.locations_config = yaml.safe_load(f)

        if schema_file.exists():
            with open(schema_file, encoding="utf-8") as sf:
                schema = json.load(sf)
            jsonschema.validate(instance=self.locations_config, schema=schema)
            logger.info("Successfully validated locations against JSON Schema.")
        else:
            logger.warning("No locations.schema.json found at %s; skipping schema validation.", schema_file)

    async def fetch_open_meteo(
        self,
        lat: float,
        lon: float,
        elevation: float,
        client: httpx.AsyncClient | None = None,
    ) -> OpenMeteoResponse:
        """Fetches deterministic UKMO Seamless weather forecast for exact coordinates and elevation."""
        params: dict[str, Any] = {
            "latitude": lat,
            "longitude": lon,
            "elevation": elevation,
            "models": "ukmo_seamless",
            "hourly": DEFAULT_HOURLY_VARS,
            "wind_speed_unit": "mph",
            "temperature_unit": "celsius",
            "timezone": "UTC",
        }

        async def _do_request(c: httpx.AsyncClient) -> httpx.Response:
            resp = await c.get(
                OPEN_METEO_BASE_URL,
                params=params,
                headers={"User-Agent": "UKMountainWeather/1.0 (GreavesLabs Homelab)"},
            )
            resp.raise_for_status()
            return resp

        if client:
            resp = await _do_request(client)
        else:
            async with httpx.AsyncClient(timeout=15.0) as local_client:
                resp = await _do_request(local_client)

        data = resp.json()
        return OpenMeteoResponse.model_validate(data)

    def _find_current_hour_index(self, times: list[str], now_utc: datetime) -> int:
        """Finds the index of the hourly entry closest to current UTC time."""
        if not times:
            return 0
        now_str = now_utc.strftime("%Y-%m-%dT%H:00")
        try:
            return times.index(now_str)
        except ValueError:
            # Fallback to closest match
            closest_idx = 0
            min_diff = float("inf")
            for idx, t_str in enumerate(times):
                try:
                    dt = datetime.fromisoformat(t_str).replace(tzinfo=UTC)
                    diff = abs((dt - now_utc).total_seconds())
                    if diff < min_diff:
                        min_diff = diff
                        closest_idx = idx
                except Exception:
                    continue
            return closest_idx

    def _extract_metric_point(
        self,
        om: OpenMeteoResponse,
        idx: int,
        elevation: float,
    ) -> WeatherMetricPoint:
        h = om.hourly

        def get_val(lst: list[float | None], default: float = 0.0) -> float:
            if 0 <= idx < len(lst) and lst[idx] is not None:
                val = lst[idx]
                return float(val) if val is not None else default
            return default

        def get_opt(lst: list[float | None]) -> float | None:
            if 0 <= idx < len(lst):
                return lst[idx]
            return None

        temp = get_val(h.temperature_2m, 0.0)
        app_temp = get_val(h.apparent_temperature, temp)
        wind_speed = get_val(h.wind_speed_10m, 0.0)
        wind_gust = get_val(h.wind_gusts_10m, wind_speed)
        wind_dir = get_val(h.wind_direction_10m, 0.0)
        precip_prob = get_val(h.precipitation_probability, 0.0)
        precip = get_val(h.precipitation, 0.0)
        cloud_cover = get_val(h.cloud_cover, 0.0)
        cloud_low = get_val(h.cloud_cover_low, 0.0)
        freezing = get_opt(h.freezing_level_height)
        dew_point = get_opt(h.dew_point_2m)

        cloud_base = hazard_engine.calculate_cloud_base(
            elevation=elevation,
            temperature=temp,
            dew_point=dew_point,
        )

        return WeatherMetricPoint(
            temperature=round(temp, 1),
            apparent_temperature=round(app_temp, 1),
            wind_speed=round(wind_speed, 1),
            wind_gust=round(wind_gust, 1),
            wind_direction=round(wind_dir, 1),
            precipitation_probability=round(precip_prob, 0),
            precipitation=round(precip, 2),
            cloud_cover=round(cloud_cover, 0),
            cloud_cover_low=round(cloud_low, 0),
            freezing_level_height=round(freezing, 0) if freezing is not None else None,
            estimated_cloud_base=round(cloud_base, 0) if cloud_base is not None else None,
        )

    async def collect_all(self, client: httpx.AsyncClient | None = None) -> WeatherResponse:
        """Collects weather for all configured regions and evaluates ridge hazards."""
        now_utc = datetime.now(UTC)
        regions_result: list[RegionWeather] = []

        async with httpx.AsyncClient(timeout=20.0) as shared_client:
            http_client = client or shared_client

            for reg_cfg in self.locations_config.get("regions", []):
                sub_regions_weather: list[SubRegionWeather] = []
                region_hazards: list[HazardLevel] = []

                for sub_cfg in reg_cfg.get("sub_regions", []):
                    v_cfg = sub_cfg["valley"]
                    s_cfg = sub_cfg["summit"]

                    valley_loc = LocationPoint(
                        name=v_cfg["name"],
                        lat=v_cfg["lat"],
                        lon=v_cfg["lon"],
                        elevation=v_cfg["elevation"],
                    )
                    summit_loc = LocationPoint(
                        name=s_cfg["name"],
                        lat=s_cfg["lat"],
                        lon=s_cfg["lon"],
                        elevation=s_cfg["elevation"],
                    )

                    # Query Open-Meteo for both Valley and Summit concurrently
                    valley_task = self.fetch_open_meteo(
                        lat=valley_loc.lat,
                        lon=valley_loc.lon,
                        elevation=valley_loc.elevation,
                        client=http_client,
                    )
                    summit_task = self.fetch_open_meteo(
                        lat=summit_loc.lat,
                        lon=summit_loc.lon,
                        elevation=summit_loc.elevation,
                        client=http_client,
                    )

                    valley_om, summit_om = await asyncio.gather(valley_task, summit_task)

                    curr_idx = self._find_current_hour_index(summit_om.hourly.time, now_utc)

                    valley_current = self._extract_metric_point(valley_om, curr_idx, valley_loc.elevation)
                    summit_current = self._extract_metric_point(summit_om, curr_idx, summit_loc.elevation)

                    temp_delta = round(valley_current.temperature - summit_current.temperature, 1)

                    # Evaluate Hazard Engine
                    hazard = hazard_engine.evaluate(
                        summit_elevation=summit_loc.elevation,
                        summit_gust=summit_current.wind_gust,
                        summit_wind_speed=summit_current.wind_speed,
                        summit_temp=summit_current.temperature,
                        summit_apparent_temp=summit_current.apparent_temperature,
                        freezing_level=summit_current.freezing_level_height,
                        precip_probability=summit_current.precipitation_probability,
                        cloud_cover_low=summit_current.cloud_cover_low,
                        cloud_base=summit_current.estimated_cloud_base,
                    )
                    region_hazards.append(hazard.level)

                    # Build next 24 hours forecast
                    hourly_points: list[HourlyForecastPoint] = []
                    total_hours = len(summit_om.hourly.time)
                    for h_idx in range(curr_idx, min(curr_idx + 24, total_hours)):
                        t_str = summit_om.hourly.time[h_idx]
                        v_point = self._extract_metric_point(valley_om, h_idx, valley_loc.elevation)
                        s_point = self._extract_metric_point(summit_om, h_idx, summit_loc.elevation)

                        h_hazard = hazard_engine.evaluate(
                            summit_elevation=summit_loc.elevation,
                            summit_gust=s_point.wind_gust,
                            summit_wind_speed=s_point.wind_speed,
                            summit_temp=s_point.temperature,
                            summit_apparent_temp=s_point.apparent_temperature,
                            freezing_level=s_point.freezing_level_height,
                            precip_probability=s_point.precipitation_probability,
                            cloud_cover_low=s_point.cloud_cover_low,
                            cloud_base=s_point.estimated_cloud_base,
                        )

                        hourly_points.append(
                            HourlyForecastPoint(
                                time=t_str,
                                summit_temp=s_point.temperature,
                                valley_temp=v_point.temperature,
                                summit_wind_speed=s_point.wind_speed,
                                summit_wind_gust=s_point.wind_gust,
                                precipitation_probability=s_point.precipitation_probability,
                                precipitation=s_point.precipitation,
                                freezing_level=s_point.freezing_level_height,
                                hazard_level=h_hazard.level,
                            )
                        )

                    sub_regions_weather.append(
                        SubRegionWeather(
                            id=sub_cfg["id"],
                            name=sub_cfg["name"],
                            target_fells=sub_cfg["target_fells"],
                            valley=valley_loc,
                            summit=summit_loc,
                            valley_current=valley_current,
                            summit_current=summit_current,
                            temp_delta=temp_delta,
                            hazard=hazard,
                            hourly_forecast=hourly_points,
                        )
                    )

                # Determine overall region hazard
                if HazardLevel.RED in region_hazards:
                    reg_overall = HazardLevel.RED
                elif HazardLevel.AMBER in region_hazards:
                    reg_overall = HazardLevel.AMBER
                else:
                    reg_overall = HazardLevel.GREEN

                regions_result.append(
                    RegionWeather(
                        id=reg_cfg["id"],
                        name=reg_cfg["name"],
                        layout=reg_cfg["layout"],
                        overall_hazard=reg_overall,
                        sub_regions=sub_regions_weather,
                    )
                )

        response = WeatherResponse(
            generated_at=now_utc.isoformat(),
            cached=False,
            model="UKMO Seamless 2km",
            regions=regions_result,
        )

        async with self._cache_lock:
            self._cache = response
            self._is_ready = True

        logger.info("Successfully refreshed weather data for %d regions.", len(regions_result))
        return response

    async def get_weather(self, force_refresh: bool = False) -> WeatherResponse:
        """Returns cached weather data, or refreshes if cache is empty or force_refresh is requested."""
        if not force_refresh:
            async with self._cache_lock:
                if self._cache is not None:
                    cached_copy = self._cache.model_copy(update={"cached": True})
                    return cached_copy

        try:
            return await self.collect_all()
        except Exception as exc:
            logger.error("Failed to collect weather data: %s", exc)
            async with self._cache_lock:
                if self._cache is not None:
                    logger.warning("Serving stale cached weather data following upstream error.")
                    return self._cache.model_copy(update={"cached": True})
            raise

    @property
    def is_ready(self) -> bool:
        """Returns True if the initial cache warm-up has completed."""
        return self._is_ready


collector = WeatherCollector()
