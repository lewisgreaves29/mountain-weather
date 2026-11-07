<script setup lang="ts">
import { computed } from 'vue'
import {
  Wind,
  Thermometer,
  CloudRain,
  Eye,
  Snowflake,
  Mountain,
  Compass,
  ArrowDown
} from 'lucide-vue-next'
import type { SubRegionWeather } from '../types/weather'
import HazardBadge from './HazardBadge.vue'

const props = defineProps<{
  subRegion: SubRegionWeather
}>()

const computedTempDelta = computed(() => {
  return (props.subRegion.valley_current.temperature - props.subRegion.summit_current.temperature).toFixed(1)
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
        <HazardBadge :status="subRegion.hazard.level" size="lg" />
      </div>
    </div>

    <!-- Active Hazard Bulletins -->
    <div v-if="subRegion.hazard.reasons.length > 0" class="flex flex-col gap-2">
      <div
        v-for="(reason, idx) in subRegion.hazard.reasons"
        :key="idx"
        :class="[
          'text-xs font-mono px-3.5 py-2 rounded-xl border flex items-start gap-2.5',
          subRegion.hazard.level === 'RED'
            ? 'bg-red-500/10 text-red-300 border-red-500/20'
            : subRegion.hazard.level === 'AMBER'
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
          <span class="text-[11px] font-mono uppercase tracking-wider text-slate-400">SUMMIT RIDGE</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
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
          <span class="text-[11px] font-mono uppercase tracking-wider text-slate-500">VALLEY BASELINE</span>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-2">
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
      </div>
    </div>

    <!-- Hourly Strip: Next 12 Hours Forecast -->
    <div v-if="subRegion.hourly_forecast.length > 0" class="pt-2">
      <div class="text-xs font-mono text-slate-400 mb-2 flex items-center justify-between">
        <span>HOURLY TIMELINE FORECAST</span>
        <span class="text-[11px] text-slate-500">UKMO 2km Model</span>
      </div>
      <div class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
        <div
          v-for="(h, idx) in subRegion.hourly_forecast.slice(0, 14)"
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
