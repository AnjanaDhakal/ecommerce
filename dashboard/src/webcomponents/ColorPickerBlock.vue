<template>
  <div class="relative">
    <label class="text-sm font-medium text-gray-700">{{ label }}</label>

    <div ref="previewRef" class="relative mt-1">
      <button
        type="button"
        class="flex h-10 w-full items-center gap-3 rounded-lg border border-gray-300 bg-white px-3 text-left shadow-sm transition hover:border-gray-400 focus:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-100"
        :aria-label="`Choose ${label.toLowerCase()}`"
        :aria-expanded="showPicker"
        @click="togglePicker"
      >
        <span
          class="h-6 w-6 shrink-0 rounded-full border border-gray-300 shadow-sm ring-2 ring-white"
          :class="{ 'color-swatch-empty': !modelValue }"
          :style="modelValue ? { backgroundColor: modelValue } : undefined"
        />
        <span
          class="min-w-0 flex-1 truncate font-mono text-sm"
          :class="modelValue ? 'text-gray-800' : 'font-sans text-gray-400'"
        >
          {{ modelValue ? modelValue.toUpperCase() : 'Not set' }}
        </span>
        <svg class="h-4 w-4 shrink-0 text-gray-400" viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <path
            d="M10 3.5a6.5 6.5 0 1 0 0 13h1.25a1.75 1.75 0 0 0 0-3.5h-.5a1.25 1.25 0 0 1 0-2.5h1.75A4.5 4.5 0 0 0 17 6c0-1.38-2.62-2.5-7-2.5Z"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <circle cx="6.25" cy="7" r=".75" fill="currentColor" />
          <circle cx="8.75" cy="5.75" r=".75" fill="currentColor" />
          <circle cx="5.75" cy="10" r=".75" fill="currentColor" />
        </svg>
      </button>

      <button
        v-if="clearable && modelValue"
        type="button"
        class="absolute right-9 top-1/2 flex h-6 w-6 -translate-y-1/2 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 hover:text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-100"
        :aria-label="`Clear ${label.toLowerCase()}`"
        title="Clear color"
        @click.stop="clearColor"
      >
        <svg class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="none" aria-hidden="true">
          <path d="m6 6 8 8m0-8-8 8" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" />
        </svg>
      </button>
    </div>

    <div
      v-if="showPicker"
      ref="pickerRef"
      class="absolute left-0 top-full z-[100] mt-2 rounded-xl border border-gray-200 bg-white p-2 shadow-xl"
    >
      <Sketch
        :modelValue="modelValue || '#111827'"
        @update:modelValue="updateColor"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, getCurrentInstance } from "vue"
import { Sketch } from "@ckpack/vue-color"

const props = defineProps({
  label: String,
  modelValue: String,
  clearable: Boolean,
})
const emit = defineEmits(["update:modelValue"])

const showPicker = ref(false)
const pickerRef = ref(null)
const previewRef = ref(null)
const pickerId = `color-picker-${getCurrentInstance()?.uid}`

function togglePicker() {
  if (showPicker.value) {
    showPicker.value = false
    return
  }

  window.dispatchEvent(
    new CustomEvent("ecommerce:color-picker-open", {
      detail: { id: pickerId },
    }),
  )
  showPicker.value = true
}

function updateColor(newColor) {
  emit("update:modelValue", newColor.hex)
}

function clearColor() {
  emit("update:modelValue", "")
  showPicker.value = false
}

function handleClickOutside(e) {
  if (
    showPicker.value &&
    !pickerRef.value?.contains(e.target) &&
    !previewRef.value?.contains(e.target)
  ) {
    showPicker.value = false
  }
}

function handleOtherPickerOpen(event) {
  if (event.detail?.id !== pickerId) showPicker.value = false
}

function handleEscape(event) {
  if (event.key === "Escape") showPicker.value = false
}

onMounted(() => {
  document.addEventListener("pointerdown", handleClickOutside, true)
  document.addEventListener("keydown", handleEscape)
  window.addEventListener("ecommerce:color-picker-open", handleOtherPickerOpen)
})
onBeforeUnmount(() => {
  document.removeEventListener("pointerdown", handleClickOutside, true)
  document.removeEventListener("keydown", handleEscape)
  window.removeEventListener("ecommerce:color-picker-open", handleOtherPickerOpen)
})
</script>

<style scoped>
.color-swatch-empty {
  background-color: #fff;
  background-image:
    linear-gradient(45deg, #e5e7eb 25%, transparent 25%),
    linear-gradient(-45deg, #e5e7eb 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #e5e7eb 75%),
    linear-gradient(-45deg, transparent 75%, #e5e7eb 75%);
  background-position: 0 0, 0 3px, 3px -3px, -3px 0;
  background-size: 6px 6px;
}
</style>
