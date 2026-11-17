<script setup lang="ts">
import type { ProgressRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import { reactiveOmit } from '@vueuse/core'
import { ProgressRoot } from 'reka-ui'
import { cn } from '@/lib/utils'
import { computed } from 'vue'

const props = withDefaults(
  defineProps<ProgressRootProps & { class?: HTMLAttributes['class'] }>(),
  {
    modelValue: 0,
  },
)

const delegatedProps = reactiveOmit(props, 'class')

// Calculate the stroke-dashoffset based on progress
// Semi-circle circumference is π * radius
const radius = 45
const circumference = Math.PI * radius
const progress = computed(() => props.modelValue ?? 0)
const strokeDashoffset = computed(() => {
  return circumference - (progress.value / 100) * circumference
})
</script>

<template>
  <ProgressRoot v-bind="delegatedProps" :class="cn('relative', props.class)">
    <svg
      class="w-full h-auto"
      viewBox="0 0 100 60"
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- Background semi-circle -->
      <path
        d="M 5 55 A 45 45 0 0 1 95 55"
        fill="none"
        stroke="#6ee7b7"
        stroke-width="10"
        class="text-primary/20"
        stroke-linecap="butt"
      />

      <!-- Progress semi-circle -->
      <path
        d="M 5 55 A 45 45 0 0 1 95 55"
        fill="none"
        stroke="#27b67c"
        stroke-width="10"
        class="text-primary transition-all duration-300"
        stroke-linecap="butt"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="strokeDashoffset"
      />

      <!-- Progress percentage text -->
      <text
        x="50"
        y="42"
        text-anchor="middle"
        class="text-[10px] font-medium fill-current"
      >
        {{ Math.round(progress) }}%
      </text>

      <!-- Percentage change -->
      <text x="50" y="54" text-anchor="middle" class="text-[5px]">
        <tspan class="fill-green-500">+8.02%</tspan>
        <tspan class="fill-current text-gray-700 font-bold">
          from last month
        </tspan>
      </text>
    </svg>
  </ProgressRoot>
</template>
