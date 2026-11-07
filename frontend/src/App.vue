<script setup lang="ts">
import { onMounted } from 'vue'
import { RotateCw, Mountain, ShieldAlert, Clock, Layers } from 'lucide-vue-next'
import { useWeather } from './composables/useWeather'
import RegionNav from './components/RegionNav.vue'
import MountainCardDetailed from './components/MountainCardDetailed.vue'
import MountainCardCompact from './components/MountainCardCompact.vue'

const {
  weatherData,
  selectedRegionId,
  selectedRegion,
  isLoading,
  isRefreshing,
  error,
  fetchWeather,
  selectRegion
} = useWeather()

onMounted(() => {
  fetchWeather()
})

function formatTime(isoStr?: string) {
  if (!isoStr) return 'N/A'
  try {
    const d = new Date(isoStr)
    return d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) + ' UTC'
  } catch {
    return isoStr
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col justify-between selection:bg-emerald-500/30 selection:text-emerald-200">
    <!-- Header Bar -->
    <header class="sticky top-0 z-50 backdrop-blur-xl bg-alpine-950/80 border-b border-alpine-800/80 px-4 sm:px-8 py-3.5">
      <div class="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <a
            href="https://www.lewisgreaves.co.uk"
            target="_blank"
            rel="noopener noreferrer"
            class="font-heading font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5"
          >
            greaveslabs<span class="text-emerald-400 font-normal italic">.io</span>
          </a>
          <span class="text-slate-600 hidden sm:inline">/</span>
          <div class="hidden sm:flex flex-col">
            <span class="text-[10px] font-mono tracking-widest uppercase text-terracotta font-semibold">HOMELAB TELEMETRY</span>
            <span class="text-sm font-bold font-heading text-slate-200">UK Mountain Weather</span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-3">
          <div v-if="weatherData" class="hidden md:flex items-center gap-2 text-xs font-mono text-slate-400 bg-alpine-900/80 px-3 py-1.5 rounded-xl border border-alpine-800">
            <Clock class="w-3.5 h-3.5 text-emerald-400" />
            <span>Updated: {{ formatTime(weatherData.generated_at) }}</span>
            <span v-if="weatherData.cached" class="text-[10px] text-amber-400 font-bold ml-1">CACHED</span>
          </div>

          <button
            @click="fetchWeather(true)"
            :disabled="isRefreshing || isLoading"
            class="inline-flex items-center justify-center gap-2 px-3.5 py-1.5 rounded-xl text-xs font-bold font-sans bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-950/40 transition-all disabled:opacity-50 cursor-pointer"
            title="Force refresh upstream from UK Met Office"
          >
            <RotateCw :class="['w-3.5 h-3.5', isRefreshing ? 'animate-spin' : '']" />
            <span class="hidden sm:inline">Sync Upstream</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content Container -->
    <main class="max-w-7xl mx-auto px-4 sm:px-8 py-8 flex-1 w-full flex flex-col gap-8">
      <!-- Title & Model Meta -->
      <div class="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <div class="inline-flex items-center gap-2 text-xs font-mono text-terracotta font-semibold uppercase tracking-widest mb-1.5">
            <Layers class="w-3.5 h-3.5" />
            UK MET OFFICE SEAMLESS 2KM RESOLUTION
          </div>
          <h1 class="text-3xl sm:text-4xl font-extrabold font-heading text-white tracking-tight">
            Mountain Ridge <span class="text-emerald-400 italic font-medium">Hazards & Telemetry</span>
          </h1>
          <p class="text-sm text-slate-400 mt-2 max-w-2xl">
            High-resolution deterministic summit forecasts evaluating wind gust thresholds, freezing level verglas hazards, and ridge clag against valley baselines.
          </p>
        </div>
      </div>

      <!-- Region Navigation -->
      <div v-if="weatherData && weatherData.regions.length > 0">
        <RegionNav
          :regions="weatherData.regions"
          :selected-id="selectedRegionId"
          @select="selectRegion"
        />
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="py-24 flex flex-col items-center justify-center gap-4 text-center">
        <RotateCw class="w-8 h-8 text-emerald-400 animate-spin" />
        <div class="font-heading text-lg text-slate-200">Ingesting Met Office Telemetry...</div>
        <p class="text-xs font-mono text-slate-400 max-w-sm">
          Fetching 2km deterministic forecasts for summits and valleys across the UK.
        </p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="p-6 bg-red-950/40 border border-red-800/80 rounded-2xl flex items-start gap-4">
        <ShieldAlert class="w-6 h-6 text-red-400 shrink-0 mt-0.5" />
        <div>
          <h4 class="font-bold font-heading text-lg text-white">Weather Ingestion Error</h4>
          <p class="text-sm text-red-200 mt-1 font-mono">{{ error }}</p>
          <button
            @click="fetchWeather(true)"
            class="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl text-xs font-bold font-mono transition-all"
          >
            Retry Connection
          </button>
        </div>
      </div>

      <!-- Active Region Weather View -->
      <div v-else-if="selectedRegion" class="flex flex-col gap-6">
        <!-- Detailed Layout (Lake District, Wales, Peak District) -->
        <div v-if="selectedRegion.layout === 'detailed'" class="flex flex-col gap-6">
          <MountainCardDetailed
            v-for="sub in selectedRegion.sub_regions"
            :key="sub.id"
            :sub-region="sub"
          />
        </div>

        <!-- Compact Layout (Southern Ridges) -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MountainCardCompact
            v-for="sub in selectedRegion.sub_regions"
            :key="sub.id"
            :sub-region="sub"
          />
        </div>
      </div>
    </main>

    <!-- GreavesLabs Footer -->
    <footer class="border-t border-alpine-800/80 bg-alpine-950/60 py-8 px-4 sm:px-8 mt-16">
      <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6 text-center sm:text-left">
        <div>
          <a
            href="https://www.lewisgreaves.co.uk"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2.5 px-4 py-2 rounded-full border border-alpine-700 bg-alpine-900/60 hover:border-emerald-500/50 text-xs font-mono transition-all shadow-sm group"
          >
            <span class="text-slate-400">POWERED BY</span>
            <span class="text-white font-bold font-heading text-sm">Greaves<span class="text-emerald-400 font-normal">Labs</span></span>
            <span class="text-emerald-400 group-hover:translate-x-0.5 transition-transform">↗</span>
          </a>
          <p class="text-xs text-slate-500 mt-2 font-sans">
            Self-hosted K3s microservice running Met Office UKMO 2km forecast models.
          </p>
        </div>

        <div class="flex items-center gap-4 text-xs font-mono text-slate-400">
          <a href="/api/v1/weather" target="_blank" class="hover:text-emerald-400 transition-colors">JSON API</a>
          <span>•</span>
          <a href="/healthz" target="_blank" class="hover:text-emerald-400 transition-colors">Healthz</a>
          <span>•</span>
          <a href="/readyz" target="_blank" class="hover:text-emerald-400 transition-colors">Readyz</a>
        </div>
      </div>
    </footer>
  </div>
</template>
