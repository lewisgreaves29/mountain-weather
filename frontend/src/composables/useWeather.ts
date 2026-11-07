import { ref, computed } from 'vue'
import type { WeatherResponse, RegionWeather } from '../types/weather'

export function useWeather() {
  const weatherData = ref<WeatherResponse | null>(null)
  const selectedRegionId = ref<string>('')
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)
  const isRefreshing = ref<boolean>(false)

  const selectedRegion = computed<RegionWeather | null>(() => {
    if (!weatherData.value || !weatherData.value.regions.length) return null
    if (!selectedRegionId.value) return weatherData.value.regions[0]
    return (
      weatherData.value.regions.find(r => r.id === selectedRegionId.value) ||
      weatherData.value.regions[0]
    )
  })

  async function fetchWeather(forceRefresh: boolean = false) {
    if (forceRefresh) {
      isRefreshing.value = true
    } else if (!weatherData.value) {
      isLoading.value = true
    }
    error.value = null

    try {
      const url = forceRefresh ? '/api/v1/weather?force_refresh=true' : '/api/v1/weather'
      const res = await fetch(url)
      if (!res.ok) {
        throw new Error(`Weather service returned ${res.status}: ${res.statusText}`)
      }
      const data: WeatherResponse = await res.json()
      weatherData.value = data

      if (!selectedRegionId.value && data.regions.length > 0) {
        selectedRegionId.value = data.regions[0].id
      }
    } catch (err: any) {
      error.value = err.message || 'Failed to fetch mountain weather telemetry'
    } finally {
      isLoading.value = false
      isRefreshing.value = false
    }
  }

  function selectRegion(id: string) {
    selectedRegionId.value = id
  }

  return {
    weatherData,
    selectedRegionId,
    selectedRegion,
    isLoading,
    isRefreshing,
    error,
    fetchWeather,
    selectRegion
  }
}
