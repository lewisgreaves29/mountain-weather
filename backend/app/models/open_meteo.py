from pydantic import BaseModel, Field


class OpenMeteoHourly(BaseModel):
    time: list[str] = Field(default_factory=list)
    temperature_2m: list[float | None] = Field(default_factory=list)
    apparent_temperature: list[float | None] = Field(default_factory=list)
    precipitation_probability: list[float | None] = Field(default_factory=list)
    precipitation: list[float | None] = Field(default_factory=list)
    wind_speed_10m: list[float | None] = Field(default_factory=list)
    wind_gusts_10m: list[float | None] = Field(default_factory=list)
    wind_direction_10m: list[float | None] = Field(default_factory=list)
    cloud_cover: list[float | None] = Field(default_factory=list)
    cloud_cover_low: list[float | None] = Field(default_factory=list)
    freezing_level_height: list[float | None] = Field(default_factory=list)
    dew_point_2m: list[float | None] = Field(default_factory=list)
    cloud_base_height: list[float | None] | None = None


class OpenMeteoResponse(BaseModel):
    latitude: float
    longitude: float
    elevation: float
    utc_offset_seconds: int = 0
    timezone: str | None = None
    hourly: OpenMeteoHourly = Field(default_factory=OpenMeteoHourly)
