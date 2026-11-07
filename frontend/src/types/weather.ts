export type HazardLevel = 'GREEN' | 'AMBER' | 'RED'

export interface LocationPoint {
  name: string
  lat: number
  lon: number
  elevation: number
}

export interface WeatherMetricPoint {
  temperature: number
  apparent_temperature: number
  wind_speed: number
  wind_gust: number
  wind_direction: number
  precipitation_probability: number
  precipitation: number
  cloud_cover: number
  cloud_cover_low: number
  freezing_level_height?: number | null
  estimated_cloud_base?: number | null
}

export interface HourlyForecastPoint {
  time: string
  summit_temp: number
  valley_temp: number
  summit_wind_speed: number
  summit_wind_gust: number
  precipitation_probability: number
  precipitation: number
  freezing_level?: number | null
  hazard_level: HazardLevel
}

export interface HazardAssessment {
  level: HazardLevel
  reasons: string[]
  wind_hazard: boolean
  icing_hazard: boolean
  visibility_hazard: boolean
  chill_hazard: boolean
}

export interface DailyForecastPoint {
  date: string
  day_name: string
  summit_min_temp: number
  summit_max_temp: number
  valley_min_temp: number
  valley_max_temp: number
  summit_max_wind_speed: number
  summit_max_wind_gust: number
  max_precipitation_probability: number
  total_precipitation: number
  min_freezing_level?: number | null
  hazard: HazardAssessment
}

export interface SubRegionWeather {
  id: string
  name: string
  target_fells: string
  valley: LocationPoint
  summit: LocationPoint
  valley_current: WeatherMetricPoint
  summit_current: WeatherMetricPoint
  temp_delta: number
  hazard: HazardAssessment
  daily_forecast: DailyForecastPoint[]
  hourly_forecast: HourlyForecastPoint[]
}

export interface RegionWeather {
  id: string
  name: string
  layout: 'detailed' | 'compact'
  overall_hazard: HazardLevel
  sub_regions: SubRegionWeather[]
}

export interface WeatherResponse {
  generated_at: string
  cached: boolean
  model: string
  regions: RegionWeather[]
}
