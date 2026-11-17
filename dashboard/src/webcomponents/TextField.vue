<template>
  <div class="border-b border-gray-200 bg-white">
    <div class="flex h-14 items-center gap-2 px-3">
      <div class="min-w-0 flex-1">
        <input
          :id="id"
          type="text"
          class="block h-10 w-full rounded-lg border border-gray-200 bg-gray-50 px-3 text-base font-medium text-gray-900 outline-none transition focus:border-green-500 focus:bg-white focus:ring-2 focus:ring-green-100"
          :placeholder="placeholder"
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
        />
      </div>

      <div class="flex shrink-0 items-center gap-1 border-l border-gray-200 pl-2">
        <button
          type="button"
          class="flex h-10 items-center justify-center gap-1.5 rounded-lg px-3 text-green-700 transition hover:bg-green-50"
          title="Open the live website in a new tab"
          @click="openLiveWebsite"
        >
          <span class="material-symbols-outlined text-xl">language</span>
          <span class="text-sm font-medium">Live</span>
        </button>

        <button
          type="button"
          class="flex h-10 items-center justify-center gap-1.5 rounded-lg px-3 text-gray-700 transition hover:bg-gray-100"
        >
          <span class="material-symbols-outlined text-xl text-[#1c264b]">info</span>
          <span class="text-sm font-medium">Info</span>
        </button>

        <div ref="actionsContainer" class="relative flex">
          <button
            type="button"
            class="flex h-10 items-center justify-center gap-1 rounded-lg px-3 text-gray-800 transition hover:bg-gray-100"
            aria-haspopup="menu"
            :aria-expanded="showActions"
            @click.stop="showActions = !showActions"
          >
            <span class="text-sm font-medium">Actions</span>
            <span class="material-symbols-outlined text-xl transition-transform" :class="{ 'rotate-180': showActions }">arrow_drop_down</span>
          </button>

          <div
            v-if="showActions"
            class="absolute right-0 top-[calc(100%+6px)] z-50 w-72 overflow-hidden rounded-xl border border-gray-200 bg-white p-1.5 shadow-xl"
            role="menu"
            @click.stop
          >
            <button
              type="button"
              class="flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left text-gray-800 hover:bg-green-50 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="isUnsavedPage || isArchivedPage"
              @click="runPageAction('create-child')"
            >
              <span class="material-symbols-outlined mt-0.5 text-lg text-green-700">account_tree</span>
              <span>
                <span class="block text-sm font-semibold">Add subpage</span>
                <span class="mt-0.5 block text-xs text-gray-500">Shares this page’s header and footer.</span>
              </span>
            </button>

            <button
              type="button"
              class="flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left text-gray-800 hover:bg-gray-50"
              @click="runPageAction('create-independent')"
            >
              <span class="material-symbols-outlined mt-0.5 text-lg text-gray-500">note_add</span>
              <span>
                <span class="block text-sm font-semibold">Add separate page</span>
                <span class="mt-0.5 block text-xs text-gray-500">Uses its own header and footer.</span>
              </span>
            </button>

            <button
              type="button"
              class="flex w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left text-gray-800 hover:bg-green-50 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="isUnsavedPage || isArchivedPage"
              @click="runPageAction('change-template')"
            >
              <span class="material-symbols-outlined mt-0.5 text-lg text-green-700">dashboard_customize</span>
              <span>
                <span class="block text-sm font-semibold">Change template</span>
                <span class="mt-0.5 block text-xs text-gray-500">Choose a new design for this page.</span>
              </span>
            </button>

            <div class="my-1 border-t border-gray-200"></div>

            <button
              type="button"
              class="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40"
              :disabled="isUnsavedPage"
              @click="runPageAction(isArchivedPage ? 'restore' : 'archive')"
            >
              <span class="material-symbols-outlined text-lg">{{ isArchivedPage ? 'unarchive' : 'archive' }}</span>
              {{ isArchivedPage ? 'Restore page' : 'Archive page' }}
            </button>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'

defineProps({
  modelValue: String,
  label: String,
  placeholder: String,
  id: {
    type: String,
    default: () => `input-${Math.random().toString(36).substring(2, 7)}`,
  },
})
defineEmits(['update:modelValue'])

const route = useRoute()
const toast = useToast()
const showActions = ref(false)
const actionsContainer = ref(null)
const pageStatusVersion = ref(0)
const isUnsavedPage = computed(() => route.query.source === 'newpage')
const isArchivedPage = computed(() => {
  // Route dependency makes this refresh whenever another page is opened.
  String(route.params.page_name || '')
  pageStatusVersion.value
  try {
    return JSON.parse(localStorage.getItem('mainpage') || '{}').page_status === 'Archived'
  } catch {
    return false
  }
})

function selectedWebsite() {
  try {
    return JSON.parse(localStorage.getItem('selectedWebsite') || '{}')
  } catch {
    return {}
  }
}

function openLiveWebsite() {
  const publicUrl = String(selectedWebsite().canonical_url || '').trim()
  if (!publicUrl) {
    toast.info('Publish this website before opening its live URL.')
    return
  }
  window.open(publicUrl, '_blank', 'noopener,noreferrer')
}

function runPageAction(action) {
  if (isUnsavedPage.value && action !== 'create-independent') return
  showActions.value = false
  window.dispatchEvent(
    new CustomEvent('ecommerce:website-page-action', { detail: { action } }),
  )
}

function closeActions(event) {
  if (!actionsContainer.value?.contains(event.target)) showActions.value = false
}

function refreshPageStatus() {
  pageStatusVersion.value += 1
}

onMounted(() => {
  document.addEventListener('click', closeActions)
  window.addEventListener('ecommerce:page-status-updated', refreshPageStatus)
})
onBeforeUnmount(() => {
  document.removeEventListener('click', closeActions)
  window.removeEventListener('ecommerce:page-status-updated', refreshPageStatus)
})
</script>
