<!-- Sidebar.vue -->
<template>
  <div>
    <!-- Backdrop -->
    <div
      v-if="modelValue"
      @click="$emit('update:modelValue', false)"
      class="fixed inset-0 bg-black bg-opacity-10 z-40"
    ></div>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed top-0 right-0 h-full bg-white shadow-lg z-50 transition-transform duration-300 ease-in-out flex flex-col',
        modelValue ? 'translate-x-0' : 'translate-x-full',
      ]"
      :style="`width: ${width};`"
    >
      <!-- Header -->
      <div class="p-4 flex justify-between items-center border-b shrink-0">
        <h2 class="text-lg font-semibold"><slot name="title">Sidebar</slot></h2>
        <button
          @click="$emit('update:modelValue', false)"
          class="text-gray-600 hover:text-gray-900"
        >
          &times;
        </button>
      </div>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto p-4 min-h-0">
        <slot>
          <!-- Default sidebar content -->
          This is sidebar content.
        </slot>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  width: {
    type: String,
    default: '900px',
  },
})

const emit = defineEmits(['update:modelValue'])

function closeOnEscape(event) {
  if (event.key !== 'Escape' || event.defaultPrevented || !props.modelValue) return
  emit('update:modelValue', false)
}

onMounted(() => document.addEventListener('keydown', closeOnEscape))
onBeforeUnmount(() => document.removeEventListener('keydown', closeOnEscape))
</script>
