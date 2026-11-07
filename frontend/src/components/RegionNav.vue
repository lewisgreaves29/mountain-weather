<script setup lang="ts">
import type { RegionWeather } from '../types/weather'
import HazardBadge from './HazardBadge.vue'

defineProps<{
  regions: RegionWeather[]
  selectedId: string
}>()

const emit = defineEmits<{
  (e: 'select', id: string): void
}>()
</script>

<template>
  <nav class="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none border-b border-alpine-800">
    <button
      v-for="region in regions"
      :key="region.id"
      @click="emit('select', region.id)"
      :class="[
        'flex items-center gap-2.5 px-4 py-2.5 rounded-xl font-medium text-sm transition-all whitespace-nowrap',
        selectedId === region.id
          ? 'bg-alpine-800 text-white border border-alpine-700 shadow-lg shadow-black/20'
          : 'text-slate-400 hover:text-slate-200 hover:bg-alpine-900/60'
      ]"
    >
      <span>{{ region.name }}</span>
      <HazardBadge :status="region.overall_hazard" size="sm" :show-label="false" />
    </button>
  </nav>
</template>
