from typing import List, Optional
from pydantic import BaseModel, Field


class OpenMeteoHourly(BaseModel):
    time: List[str] = Field(default_factory=list)
    temperature_2m: List[Optional[float]] = Field(default_factory=list)
    apparent_temperature: List[Optional[float]] = Field(default_factory=list)
    precipitation_probability: List[Optional[float]] = Field(default_factory=list)
    precipitation: List[Optional[float]] = Field(default_factory=list)
    wind_speed_10m: List[Optional[float]] = Field(default_factory=list)
    wind_gusts_10m: List[Optional[float]] = Field(default_factory=list)
    wind_direction_10m: List[Optional[float]] = Field(default_factory=list)
    cloud_cover: List[Optional[float]] = Field(default_factory=list)
    cloud_cover_low: List[Optional[float]] = Field(default_factory=list)
    freezing_level_height: List[Optional[float]] = Field(default_factory=list)
    dew_point_2m: List[Optional[float]] = Field(default_factory=list)
    cloud_base_height: Optional[List[Optional[float]]] = None


class OpenMeteoResponse(BaseModel):
    latitude: float
    longitude: float
    elevation: float
    utc_offset_seconds: int = 0
    timezone: Optional[str] = None
    hourly: OpenMeteoHourly = Field(default_factory=OpenMeteoHourly)
