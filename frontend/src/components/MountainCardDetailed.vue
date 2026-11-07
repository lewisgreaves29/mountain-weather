<script setup lang="ts">
import { computed, ref } from 'vue'
import {
  Wind,
  Thermometer,
  CloudRain,
  Eye,
  Snowflake,
  Mountain,
  Calendar
} from 'lucide-vue-next'
import type { SubRegionWeather } from '../types/weather'
import HazardBadge from './HazardBadge.vue'

const props = defineProps<{
  subRegion: SubRegionWeather
}>()

const selectedDayIndex = ref(0)

const activeDay = computed(() => {
  return props.subRegion.daily_forecast?.[selectedDayIndex.value] ?? null
})

const isToday = computed(() => selectedDayIndex.value === 0)

const activeHazard = computed(() => {
  if (isToday.value || !activeDay.value) {
    return props.subRegion.hazard
  }
  return activeDay.value.hazard
})

const computedTempDelta = computed(() => {
  if (isToday.value || !activeDay.value) {
    return (props.subRegion.valley_current.temperature - props.subRegion.summit_current.temperature).toFixed(1)
  }
  return (activeDay.value.valley_max_temp - activeDay.value.summit_max_temp).toFixed(1)
})

const dayHourlyForecast = computed(() => {
  if (!activeDay.value || !props.subRegion.hourly_forecast) {
    return (props.subRegion.hourly_forecast || []).slice(0, 24)
  }
  const dateStr = activeDay.value.date
  const filtered = props.subRegion.hourly_forecast.filter(h => h.time.startsWith(dateStr))
  return filtered.length > 0 ? filtered : props.subRegion.hourly_forecast.slice(0, 24)
})

function formatHour(timeStr: string) {
  try {
    const d = new Date(timeStr)
    return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
  } catch {
    return timeStr.slice(11, 16)
  }
}
</script>

<template>
  <div class="bg-alpine-900/90 border border-alpine-800 rounded-2xl p-6 shadow-xl backdrop-blur-md flex flex-col gap-6">
    <!-- Header: Fell name, targets, and Hazard Badge -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-alpine-800">
      <div>
        <div class="flex items-center gap-2">
          <Mountain class="w-5 h-5 text-emerald-400" />
          <h3 class="text-xl font-bold font-heading text-white tracking-tight">
            {{ subRegion.name }}
          </h3>
        </div>
        <p class="text-xs font-mono text-slate-400 mt-1">
          Targets: <span class="text-slate-300 font-sans">{{ subRegion.target_fells }}</span>
        </p>
      </div>

      <div class="flex items-center gap-3">
        <HazardBadge :status="activeHazard.level" size="lg" />
      </div>
    </div>

    <!-- 7-Day Forecast & Ridge Hazard Outlook Strip -->
    <div v-if="subRegion.daily_forecast && subRegion.daily_forecast.length > 0" class="flex flex-col gap-2">
      <div class="flex items-center justify-between text-xs font-mono text-slate-400">
        <span class="flex items-center gap-1.5 font-bold tracking-wider uppercase text-slate-300">
          <Calendar class="w-3.5 h-3.5 text-emerald-400" />
          7-Day Forecast & Ridge Hazard Outlook
        </span>
        <span class="text-[11px] text-slate-500 hidden sm:inline">Select day to inspect</span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
        <button
          v-for="(day, idx) in subRegion.daily_forecast"
          :key="day.date"
          type="button"
          @click="selectedDayIndex = idx"
          :class="[
            'p-2.5 rounded-xl border flex flex-col items-center justify-between gap-1.5 transition-all text-center cursor-pointer',
            selectedDayIndex === idx
              ? 'bg-alpine-800 border-emerald-500 shadow-lg shadow-emerald-950/50 ring-1 ring-emerald-500'
              : 'bg-alpine-950/60 border-alpine-800/80 hover:bg-alpine-900/60 hover:border-alpine-700'
          ]"
        >
          <!-- Day Name -->
          <span :class="['text-xs font-mono font-bold', selectedDayIndex === idx ? 'text-emerald-300' : 'text-slate-300']">
            {{ day.day_name }}
          </span>

          <!-- Hazard Status Dot & Label -->
          <div class="flex items-center gap-1">
            <span
              :class="[
                'w-2 h-2 rounded-full inline-block',
                day.hazard.level === 'RED'
                  ? 'bg-red-500 animate-pulse'
                  : day.hazard.level === 'AMBER'
                  ? 'bg-amber-400'
                  : 'bg-emerald-400'
              ]"
            />
            <span
              class="text-[10px] font-mono font-semibold uppercase"
              :class="[
                day.hazard.level === 'RED' ? 'text-red-400' : day.hazard.level === 'AMBER' ? 'text-amber-400' : 'text-emerald-400'
              ]"
            >
              {{ day.hazard.level }}
            </span>
          </div>

          <!-- Temp Range -->
          <div class="text-[11px] font-mono text-slate-300">
            <span class="text-sky-300">{{ Math.round(day.summit_min_temp) }}°</span>
            <span class="text-slate-500">/</span>
            <span class="text-white font-bold">{{ Math.round(day.summit_max_temp) }}°</span>
          </div>

          <!-- Max Wind Gust -->
          <div class="text-[10px] font-mono text-slate-400 flex items-center gap-0.5">
            <Wind class="w-2.5 h-2.5 text-sky-400" />
            <span :class="day.summit_max_wind_gust >= 40 ? 'text-red-400 font-bold' : day.summit_max_wind_gust >= 28 ? 'text-amber-300 font-medium' : 'text-slate-300'">
              {{ Math.round(day.summit_max_wind_gust) }}mph
            </span>
          </div>
        </button>
      </div>
    </div>

    <!-- Active Hazard Bulletins -->
    <div v-if="activeHazard.reasons.length > 0" class="flex flex-col gap-2">
      <div
        v-for="(reason, idx) in activeHazard.reasons"
        :key="idx"
        :class="[
          'text-xs font-mono px-3.5 py-2 rounded-xl border flex items-start gap-2.5',
          activeHazard.level === 'RED'
            ? 'bg-red-500/10 text-red-300 border-red-500/20'
            : activeHazard.level === 'AMBER'
            ? 'bg-amber-500/10 text-amber-300 border-amber-500/20'
            : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
        ]"
      >
        <span class="mt-0.5">•</span>
        <span>{{ reason }}</span>
      </div>
    </div>

    <!-- Topographic Comparison: Valley Baseline vs Summit Ridge -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Summit Ridge Panel -->
      <div class="bg-alpine-950/80 border border-alpine-800/80 rounded-xl p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold text-white">{{ subRegion.summit.name }}</span>
            <span
              class="elevation-tag summit-elevation px-2 py-0.5 rounded text-[11px] font-mono bg-emerald-500/20 text-emerald-300 font-bold"
              data-testid="summit-elevation"
            >
              {{ subRegion.summit.elevation }}m
            </span>
          </div>
          <span class="text-[11px] font-mono uppercase tracking-wider text-slate-400">
            {{ isToday ? 'SUMMIT RIDGE (LIVE)' : `SUMMIT FORECAST (${activeDay?.day_name.toUpperCase()})` }}
          </span>
        </div>

        <!-- Live Today Metrics -->
        <div v-if="isToday" class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          <!-- Temp / Chill -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Thermometer class="w-3.5 h-3.5 text-rose-400" /> Temp
            </div>
            <div class="text-2xl font-bold font-mono text-white">
              {{ subRegion.summit_current.temperature }}°C
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Feels: <span class="text-rose-300">{{ subRegion.summit_current.apparent_temperature }}°C</span>
            </div>
          </div>

          <!-- Wind & Gusts -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Wind class="w-3.5 h-3.5 text-sky-400" /> Wind
            </div>
            <div class="text-2xl font-bold font-mono text-white">
              {{ subRegion.summit_current.wind_speed }} <span class="text-xs font-normal">mph</span>
            </div>
            <div class="text-[11px] font-mono text-amber-300">
              Gusts: {{ subRegion.summit_current.wind_gust }} mph
            </div>
          </div>

          <!-- Freezing Level -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Snowflake class="w-3.5 h-3.5 text-cyan-400" /> Freezing
            </div>
            <div class="text-lg font-bold font-mono text-white mt-0.5">
              {{ subRegion.summit_current.freezing_level_height ? `${subRegion.summit_current.freezing_level_height}m` : 'N/A' }}
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              AMSL
            </div>
          </div>

          <!-- Cloud & Clag -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Eye class="w-3.5 h-3.5 text-amber-400" /> Cloud Base
            </div>
            <div class="text-lg font-bold font-mono text-white mt-0.5">
              {{ subRegion.summit_current.estimated_cloud_base ? `${subRegion.summit_current.estimated_cloud_base}m` : 'Clear' }}
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Cover: {{ subRegion.summit_current.cloud_cover_low }}%
            </div>
          </div>
        </div>

        <!-- Selected Future Day Forecast -->
        <div v-else-if="activeDay" class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          <!-- Temp Range -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Thermometer class="w-3.5 h-3.5 text-rose-400" /> Temp Range
            </div>
            <div class="text-xl font-bold font-mono text-white">
              {{ activeDay.summit_min_temp }}° to {{ activeDay.summit_max_temp }}°C
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Summit air temp
            </div>
          </div>

          <!-- Peak Wind & Gusts -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Wind class="w-3.5 h-3.5 text-sky-400" /> Peak Gusts
            </div>
            <div class="text-2xl font-bold font-mono" :class="activeDay.summit_max_wind_gust >= 40 ? 'text-red-400' : activeDay.summit_max_wind_gust >= 28 ? 'text-amber-300' : 'text-white'">
              {{ activeDay.summit_max_wind_gust }} <span class="text-xs font-normal">mph</span>
            </div>
            <div class="text-[11px] font-mono text-slate-400">
              Avg: {{ activeDay.summit_max_wind_speed }} mph
            </div>
          </div>

          <!-- Min Freezing Level -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Snowflake class="w-3.5 h-3.5 text-cyan-400" /> Min Freezing
            </div>
            <div class="text-lg font-bold font-mono text-white mt-0.5">
              {{ activeDay.min_freezing_level ? `${activeDay.min_freezing_level}m` : 'N/A' }}
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              AMSL lowest
            </div>
          </div>

          <!-- Rain Risk & Total -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <CloudRain class="w-3.5 h-3.5 text-blue-400" /> Rain Risk
            </div>
            <div class="text-xl font-bold font-mono text-blue-400">
              {{ activeDay.max_precipitation_probability }}%
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Total: {{ activeDay.total_precipitation }}mm
            </div>
          </div>
        </div>
      </div>

      <!-- Valley Baseline Panel -->
      <div class="bg-alpine-950/50 border border-alpine-800/60 rounded-xl p-5 flex flex-col justify-between">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold text-slate-200">{{ subRegion.valley.name }}</span>
            <span
              class="elevation-tag valley-elevation px-2 py-0.5 rounded text-[11px] font-mono bg-slate-700/60 text-slate-300"
              data-testid="valley-elevation"
            >
              {{ subRegion.valley.elevation }}m
            </span>
          </div>
          <span class="text-[11px] font-mono uppercase tracking-wider text-slate-500">
            {{ isToday ? 'VALLEY BASELINE (LIVE)' : `VALLEY BASELINE (${activeDay?.day_name.toUpperCase()})` }}
          </span>
        </div>

        <!-- Live Today Metrics -->
        <div v-if="isToday" class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
          <!-- Temp -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Thermometer class="w-3.5 h-3.5 text-emerald-400" /> Temp
            </div>
            <div class="text-xl font-bold font-mono text-slate-200">
              {{ subRegion.valley_current.temperature }}°C
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Feels: {{ subRegion.valley_current.apparent_temperature }}°C
            </div>
          </div>

          <!-- Wind -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Wind class="w-3.5 h-3.5 text-sky-400" /> Wind
            </div>
            <div class="text-xl font-bold font-mono text-slate-200">
              {{ subRegion.valley_current.wind_speed }} <span class="text-xs font-normal">mph</span>
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Gusts: {{ subRegion.valley_current.wind_gust }} mph
            </div>
          </div>

          <!-- Delta Tag -->
          <div class="col-span-2 sm:col-span-1 bg-alpine-900/60 rounded-lg p-2.5 border border-alpine-800/80">
            <div class="text-[10px] font-mono text-slate-400 uppercase">Lapse Delta</div>
            <div class="text-sm font-bold font-mono text-emerald-400 mt-1" data-testid="temp-delta">
              -{{ computedTempDelta }}°C
            </div>
            <div class="text-[10px] text-slate-500 font-mono">
              Valley to Summit
            </div>
          </div>
        </div>

        <!-- Selected Future Day Forecast -->
        <div v-else-if="activeDay" class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
          <!-- Temp Range -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <Thermometer class="w-3.5 h-3.5 text-emerald-400" /> Temp Range
            </div>
            <div class="text-xl font-bold font-mono text-slate-200">
              {{ activeDay.valley_min_temp }}° to {{ activeDay.valley_max_temp }}°C
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Valley baseline
            </div>
          </div>

          <!-- Max Rain Risk -->
          <div>
            <div class="text-[11px] text-slate-400 font-mono mb-1 flex items-center gap-1">
              <CloudRain class="w-3.5 h-3.5 text-blue-400" /> Rain Risk
            </div>
            <div class="text-xl font-bold font-mono text-slate-200">
              {{ activeDay.max_precipitation_probability }}%
            </div>
            <div class="text-[11px] text-slate-400 font-mono">
              Max probability
            </div>
          </div>

          <!-- Delta Tag -->
          <div class="col-span-2 sm:col-span-1 bg-alpine-900/60 rounded-lg p-2.5 border border-alpine-800/80">
            <div class="text-[10px] font-mono text-slate-400 uppercase">Lapse Delta</div>
            <div class="text-sm font-bold font-mono text-emerald-400 mt-1" data-testid="temp-delta">
              -{{ computedTempDelta }}°C
            </div>
            <div class="text-[10px] text-slate-500 font-mono">
              Max Temp Difference
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hourly Strip: Forecast Timeline for Selected Day -->
    <div v-if="dayHourlyForecast.length > 0" class="pt-2">
      <div class="text-xs font-mono text-slate-400 mb-2 flex items-center justify-between">
        <span>HOURLY TIMELINE FORECAST • {{ activeDay ? activeDay.day_name.toUpperCase() : 'TODAY' }}</span>
        <span class="text-[11px] text-slate-500">UKMO 2km Model</span>
      </div>
      <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <div
          v-for="(h, idx) in dayHourlyForecast"
          :key="idx"
          class="shrink-0 bg-alpine-950/60 border border-alpine-800/60 rounded-xl p-3 flex flex-col items-center gap-1.5 min-w-[74px] text-center"
        >
          <span class="text-[11px] font-mono text-slate-400">{{ formatHour(h.time) }}</span>
          <HazardBadge :status="h.hazard_level" size="sm" :show-label="false" />
          <span class="text-sm font-bold font-mono text-white mt-1">{{ h.summit_temp }}°</span>
          <span class="text-[11px] font-mono text-sky-300 flex items-center gap-0.5">
            <Wind class="w-3 h-3" /> {{ h.summit_wind_gust }}
          </span>
          <span v-if="h.precipitation_probability > 0" class="text-[10px] font-mono text-blue-400">
            {{ h.precipitation_probability }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
