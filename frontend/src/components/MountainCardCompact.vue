<script setup lang="ts">
import { Mountain, Wind, Thermometer, CloudRain } from 'lucide-vue-next'
import type { SubRegionWeather } from '../types/weather'
import HazardBadge from './HazardBadge.vue'

defineProps<{
  subRegion: SubRegionWeather
}>()
</script>

<template>
  <div class="bg-alpine-900/80 border border-alpine-800 rounded-2xl p-5 shadow-lg backdrop-blur-md flex flex-col justify-between gap-4">
    <div class="flex items-start justify-between gap-3">
      <div>
        <div class="flex items-center gap-2">
          <Mountain class="w-4 h-4 text-emerald-400" />
          <h4 class="font-bold font-heading text-lg text-white">
            {{ subRegion.name }}
          </h4>
        </div>
        <p class="text-xs font-mono text-slate-400 mt-0.5">
          {{ subRegion.summit.name }} ({{ subRegion.summit.elevation }}m)
        </p>
      </div>
      <HazardBadge :status="subRegion.hazard.level" size="sm" />
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-3 gap-2 bg-alpine-950/60 rounded-xl p-3 border border-alpine-800/60 text-center font-mono">
      <div>
        <div class="text-[10px] text-slate-400 uppercase">Temp</div>
        <div class="text-base font-bold text-white mt-0.5">
          {{ subRegion.summit_current.temperature }}°C
        </div>
        <div class="text-[10px] text-slate-400">
          Feels {{ subRegion.summit_current.apparent_temperature }}°
        </div>
      </div>

      <div>
        <div class="text-[10px] text-slate-400 uppercase">Wind</div>
        <div class="text-base font-bold text-white mt-0.5">
          {{ subRegion.summit_current.wind_speed }} <span class="text-xs">mph</span>
        </div>
        <div class="text-[10px] text-amber-300">
          Gust {{ subRegion.summit_current.wind_gust }}
        </div>
      </div>

      <div>
        <div class="text-[10px] text-slate-400 uppercase">Rain Risk</div>
        <div class="text-base font-bold text-blue-400 mt-0.5">
          {{ subRegion.summit_current.precipitation_probability }}%
        </div>
        <div class="text-[10px] text-slate-400">
          {{ subRegion.summit_current.precipitation }}mm
        </div>
      </div>
    </div>

    <!-- Quick Reason Bulletin -->
    <div v-if="subRegion.hazard.reasons.length > 0" class="text-xs font-mono text-slate-300">
      <span class="text-amber-400 mr-1">Notice:</span>
      {{ subRegion.hazard.reasons[0] }}
    </div>
  </div>
</template>
