import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HazardBadge from '../src/components/HazardBadge.vue'
import MountainCardDetailed from '../src/components/MountainCardDetailed.vue'
import type { SubRegionWeather } from '../src/types/weather'

describe('HazardBadge Component', () => {
  it('mounts with status RED and verifies CSS classes include bg-red-500/10 and text-red-400', () => {
    const wrapper = mount(HazardBadge, {
      props: {
        status: 'RED'
      }
    })

    const badge = wrapper.find('[data-testid="hazard-badge"]')
    expect(badge.exists()).toBe(true)
    expect(badge.classes()).toContain('bg-red-500/10')
    expect(badge.classes()).toContain('text-red-400')
    expect(wrapper.text()).toContain('Severe Hazard')
  })

  it('mounts with status AMBER and verifies amber classes', () => {
    const wrapper = mount(HazardBadge, {
      props: {
        status: 'AMBER'
      }
    })
    const badge = wrapper.find('[data-testid="hazard-badge"]')
    expect(badge.classes()).toContain('bg-amber-500/10')
    expect(badge.classes()).toContain('text-amber-400')
  })

  it('mounts with status GREEN and verifies emerald classes', () => {
    const wrapper = mount(HazardBadge, {
      props: {
        status: 'GREEN'
      }
    })
    const badge = wrapper.find('[data-testid="hazard-badge"]')
    expect(badge.classes()).toContain('bg-emerald-500/10')
    expect(badge.classes()).toContain('text-emerald-400')
  })
})

describe('MountainCardDetailed Component', () => {
  const mockSubRegion: SubRegionWeather = {
    id: 'lakes-west-central',
    name: 'Western & Central Fells',
    target_fells: 'Scafell Pike, Great Gable, Pillar',
    valley: {
      name: 'Wasdale Head',
      lat: 54.466,
      lon: -3.255,
      elevation: 80
    },
    summit: {
      name: 'Scafell Pike',
      lat: 54.454,
      lon: -3.211,
      elevation: 978
    },
    valley_current: {
      temperature: 12.0,
      apparent_temperature: 11.0,
      wind_speed: 10.0,
      wind_gust: 15.0,
      wind_direction: 240.0,
      precipitation_probability: 10.0,
      precipitation: 0.0,
      cloud_cover: 30.0,
      cloud_cover_low: 20.0,
      freezing_level_height: 1800,
      estimated_cloud_base: 1500
    },
    summit_current: {
      temperature: 5.5,
      apparent_temperature: 1.0,
      wind_speed: 24.0,
      wind_gust: 36.0,
      wind_direction: 260.0,
      precipitation_probability: 20.0,
      precipitation: 0.0,
      cloud_cover: 60.0,
      cloud_cover_low: 40.0,
      freezing_level_height: 1800,
      estimated_cloud_base: 1500
    },
    temp_delta: 6.5,
    hazard: {
      level: 'AMBER',
      reasons: ['Strong buffeting: Summit wind gusts reaching 36 mph (28-39 mph caution).'],
      wind_hazard: true,
      icing_hazard: false,
      visibility_hazard: false,
      chill_hazard: false
    },
    daily_forecast: [],
    hourly_forecast: []
  }

  it('renders both Valley and Summit elevation tags and calculates the temperature delta accurately', () => {
    const wrapper = mount(MountainCardDetailed, {
      props: {
        subRegion: mockSubRegion
      }
    })

    // 1. Verify summit elevation tag
    const summitElevation = wrapper.find('[data-testid="summit-elevation"]')
    expect(summitElevation.exists()).toBe(true)
    expect(summitElevation.text()).toBe('978m')

    // 2. Verify valley elevation tag
    const valleyElevation = wrapper.find('[data-testid="valley-elevation"]')
    expect(valleyElevation.exists()).toBe(true)
    expect(valleyElevation.text()).toBe('80m')

    // 3. Verify temperature delta accurately: 12.0 - 5.5 = 6.5°C
    const deltaTag = wrapper.find('[data-testid="temp-delta"]')
    expect(deltaTag.exists()).toBe(true)
    expect(deltaTag.text()).toBe('-6.5°C')

    // 4. Verify names and targets
    expect(wrapper.text()).toContain('Western & Central Fells')
    expect(wrapper.text()).toContain('Scafell Pike')
    expect(wrapper.text()).toContain('Wasdale Head')
  })
})
