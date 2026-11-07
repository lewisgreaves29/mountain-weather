from enum import Enum

from pydantic import BaseModel, Field


class HazardLevel(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class LocationPoint(BaseModel):
    name: str
    lat: float
    lon: float
    elevation: float  # meters AMSL


class WeatherMetricPoint(BaseModel):
    temperature: float
    apparent_temperature: float
    wind_speed: float  # mph
    wind_gust: float  # mph
    wind_direction: float  # degrees
    precipitation_probability: float  # %
    precipitation: float  # mm
    cloud_cover: float  # %
    cloud_cover_low: float  # %
    freezing_level_height: float | None = None  # meters AMSL
    estimated_cloud_base: float | None = None  # meters AMSL


class HourlyForecastPoint(BaseModel):
    time: str
    summit_temp: float
    valley_temp: float
    summit_wind_speed: float
    summit_wind_gust: float
    precipitation_probability: float
    precipitation: float
    freezing_level: float | None = None
    hazard_level: HazardLevel


class HazardAssessment(BaseModel):
    level: HazardLevel
    reasons: list[str] = Field(default_factory=list)
    wind_hazard: bool = False
    icing_hazard: bool = False
    visibility_hazard: bool = False
    chill_hazard: bool = False


class SubRegionWeather(BaseModel):
    id: str
    name: str
    target_fells: str
    valley: LocationPoint
    summit: LocationPoint
    valley_current: WeatherMetricPoint
    summit_current: WeatherMetricPoint
    temp_delta: float  # valley temp - summit temp (°C)
    hazard: HazardAssessment
    hourly_forecast: list[HourlyForecastPoint] = Field(default_factory=list)


class RegionWeather(BaseModel):
    id: str
    name: str
    layout: str  # "detailed" or "compact"
    overall_hazard: HazardLevel
    sub_regions: list[SubRegionWeather] = Field(default_factory=list)


class WeatherResponse(BaseModel):
    generated_at: str
    cached: bool = False
    model: str = "UKMO Seamless 2km"
    regions: list[RegionWeather] = Field(default_factory=list)
