<template>
  <div class="w-full overflow-x-auto">
    <div
      class="flex h-11 items-end gap-6 px-4"
      :style="{ minWidth }"
      role="tablist"
    >
      <button
        v-for="button in buttons"
        :key="button.value"
        type="button"
        role="tab"
        :aria-selected="modelValue === button.value"
        class="relative flex h-full items-center whitespace-nowrap border-b-2 px-1 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-green-500 focus-visible:ring-offset-2"
        :class="
          modelValue === button.value
            ? 'border-green-600 text-green-700'
            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-900'
        "
        @click="emit('update:modelValue', button.value)"
      >
        {{ button.label }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: [String, Boolean, Number],
    default: '',
  },
  buttons: {
    type: Array,
    required: true,
  },
  minWidth: {
    type: String,
    default: '640px',
  },
})

const emit = defineEmits(['update:modelValue'])
</script>
