<template>
  <button
    type="button"
    role="switch"
    :aria-checked="isPublished"
    :disabled="loading"
    class="inline-flex items-center gap-2 rounded-full px-2 py-1 text-xs font-semibold transition focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:cursor-wait disabled:opacity-60"
    :class="
      isPublished
        ? 'bg-green-100 text-green-800'
        : 'bg-gray-100 text-gray-600'
    "
    @click="$emit('toggle')"
  >
    <span>{{ isPublished ? 'Published' : 'Unpublished' }}</span>
    <span
      class="relative h-5 w-9 shrink-0 rounded-full transition-colors"
      :class="isPublished ? 'bg-green-600' : 'bg-gray-300'"
      aria-hidden="true"
    >
      <span
        class="absolute top-0.5 h-4 w-4 rounded-full bg-white shadow-sm transition-all"
        :class="isPublished ? 'left-[1.125rem]' : 'left-0.5'"
      ></span>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: 'Published' },
  loading: { type: Boolean, default: false },
})

defineEmits(['toggle'])

const isPublished = computed(() => props.status === 'Published')
</script>
