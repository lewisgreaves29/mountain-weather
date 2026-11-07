<script setup lang="ts">
import { computed, ref } from 'vue'
import { Mountain, Wind, Calendar } from 'lucide-vue-next'
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
</script>

<template>
  <div class="bg-alpine-900/80 border border-alpine-800 rounded-2xl p-5 shadow-lg backdrop-blur-md flex flex-col justify-between gap-4">
    <!-- Header -->
    <div class="flex items-start justify-between gap-3">
      <div>
        <div class="flex items-center gap-2">
          <Mountain class="w-4 h-4 text-emerald-400" />
          <h4 class="font-bold font-heading text-lg text-white">
            {{ subRegion.name }}
          </h4>
        </div>
        <p class="text-xs font-mono text-slate-400 mt-0.5">
          {{ subRegion.summit.name }} ({{ subRegion.summit.elevation }}m) •
          <span :class="isToday ? 'text-emerald-400 font-bold' : 'text-slate-300'">
            {{ isToday ? 'Live Now' : activeDay?.day_name }}
          </span>
        </p>
      </div>
      <HazardBadge :status="activeHazard.level" size="sm" />
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-3 gap-2 bg-alpine-950/60 rounded-xl p-3 border border-alpine-800/60 text-center font-mono">
      <!-- Temp -->
      <div>
        <div class="text-[10px] text-slate-400 uppercase">Temp</div>
        <div class="text-base font-bold text-white mt-0.5">
          <template v-if="isToday">
            {{ subRegion.summit_current.temperature }}°C
          </template>
          <template v-else-if="activeDay">
            {{ Math.round(activeDay.summit_min_temp) }}°/{{ Math.round(activeDay.summit_max_temp) }}°
          </template>
        </div>
        <div class="text-[10px] text-slate-400">
          <template v-if="isToday">
            Feels {{ subRegion.summit_current.apparent_temperature }}°
          </template>
          <template v-else>
            Summit air
          </template>
        </div>
      </div>

      <!-- Wind -->
      <div>
        <div class="text-[10px] text-slate-400 uppercase">Wind</div>
        <div class="text-base font-bold mt-0.5" :class="isToday ? 'text-white' : (activeDay?.summit_max_wind_gust ?? 0) >= 40 ? 'text-red-400' : (activeDay?.summit_max_wind_gust ?? 0) >= 28 ? 'text-amber-300' : 'text-white'">
          <template v-if="isToday">
            {{ subRegion.summit_current.wind_speed }} <span class="text-xs font-normal">mph</span>
          </template>
          <template v-else-if="activeDay">
            {{ Math.round(activeDay.summit_max_wind_gust) }} <span class="text-xs font-normal">mph</span>
          </template>
        </div>
        <div class="text-[10px] text-amber-300">
          <template v-if="isToday">
            Gust {{ subRegion.summit_current.wind_gust }}
          </template>
          <template v-else-if="activeDay">
            Max Peak Gust
          </template>
        </div>
      </div>

      <!-- Rain Risk -->
      <div>
        <div class="text-[10px] text-slate-400 uppercase">Rain Risk</div>
        <div class="text-base font-bold text-blue-400 mt-0.5">
          <template v-if="isToday">
            {{ subRegion.summit_current.precipitation_probability }}%
          </template>
          <template v-else-if="activeDay">
            {{ activeDay.max_precipitation_probability }}%
          </template>
        </div>
        <div class="text-[10px] text-slate-400">
          <template v-if="isToday">
            {{ subRegion.summit_current.precipitation }}mm
          </template>
          <template v-else-if="activeDay">
            {{ activeDay.total_precipitation }}mm total
          </template>
        </div>
      </div>
    </div>

    <!-- 7-Day Mini Outlook Chips -->
    <div v-if="subRegion.daily_forecast && subRegion.daily_forecast.length > 0" class="flex flex-col gap-1.5 pt-1">
      <div class="text-[10px] font-mono text-slate-500 uppercase flex items-center justify-between">
        <span>7-DAY OUTLOOK</span>
        <span class="text-slate-400 font-sans">Tap to switch</span>
      </div>
      <div class="grid grid-cols-7 gap-1">
        <button
          v-for="(day, idx) in subRegion.daily_forecast"
          :key="day.date"
          type="button"
          @click="selectedDayIndex = idx"
          :class="[
            'py-1 px-1 rounded-lg border flex flex-col items-center gap-0.5 text-center cursor-pointer transition-all',
            selectedDayIndex === idx
              ? 'bg-alpine-800 border-emerald-500 shadow ring-1 ring-emerald-500'
              : 'bg-alpine-950/60 border-alpine-800/60 hover:bg-alpine-900/40'
          ]"
        >
          <span :class="['text-[10px] font-mono font-bold', selectedDayIndex === idx ? 'text-emerald-300' : 'text-slate-400']">
            {{ day.day_name.split(' ')[0].slice(0, 3) }}
          </span>
          <span
            :class="[
              'w-1.5 h-1.5 rounded-full inline-block',
              day.hazard.level === 'RED'
                ? 'bg-red-500'
                : day.hazard.level === 'AMBER'
                ? 'bg-amber-400'
                : 'bg-emerald-400'
            ]"
          />
          <span class="text-[9px] font-mono text-slate-300">
            {{ Math.round(day.summit_max_temp) }}°
          </span>
        </button>
      </div>
    </div>

    <!-- Quick Reason Bulletin -->
    <div v-if="activeHazard.reasons.length > 0" class="text-xs font-mono text-slate-300">
      <span class="text-amber-400 mr-1">Notice:</span>
      {{ activeHazard.reasons[0] }}
    </div>
  </div>
</template>
