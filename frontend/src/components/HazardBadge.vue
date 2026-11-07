<script setup lang="ts">
import { computed } from 'vue'
import { AlertTriangle, AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import type { HazardLevel } from '../types/weather'

const props = withDefaults(
  defineProps<{
    status: HazardLevel
    size?: 'sm' | 'md' | 'lg'
    showLabel?: boolean
  }>(),
  {
    size: 'md',
    showLabel: true
  }
)

const badgeClasses = computed(() => {
  switch (props.status) {
    case 'RED':
      return 'bg-red-500/10 text-red-400 border-red-500/30 shadow-red-500/5'
    case 'AMBER':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/30 shadow-amber-500/5'
    case 'GREEN':
    default:
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-emerald-500/5'
  }
})

const labelText = computed(() => {
  switch (props.status) {
    case 'RED':
      return 'Severe Hazard'
    case 'AMBER':
      return 'Technical Caution'
    case 'GREEN':
    default:
      return 'Favourable'
  }
})

const sizeClasses = computed(() => {
  switch (props.size) {
    case 'sm':
      return 'px-2 py-0.5 text-xs gap-1.5'
    case 'lg':
      return 'px-3.5 py-1.5 text-sm gap-2'
    case 'md':
    default:
      return 'px-2.5 py-1 text-xs gap-2'
  }
})
</script>

<template>
  <span
    :class="[
      'inline-flex items-center font-mono font-semibold uppercase tracking-wider rounded-full border shadow-sm transition-colors',
      badgeClasses,
      sizeClasses
    ]"
    data-testid="hazard-badge"
  >
    <AlertTriangle v-if="status === 'RED'" class="w-3.5 h-3.5 shrink-0 animate-pulse" />
    <AlertCircle v-else-if="status === 'AMBER'" class="w-3.5 h-3.5 shrink-0" />
    <CheckCircle2 v-else class="w-3.5 h-3.5 shrink-0" />
    <span v-if="showLabel">{{ labelText }}</span>
  </span>
</template>
