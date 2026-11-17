<template>
  <section class="flex h-full min-h-0 flex-col overflow-hidden rounded-xl border border-gray-200 bg-white">
    <header class="shrink-0 border-b border-gray-200 p-4">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h3 class="text-base font-semibold text-gray-900">Archived items</h3>
          <p class="mt-1 text-sm text-gray-500">
            Restore items without permanently deleting any data.
          </p>
        </div>
        <select
          v-model="sortBy"
          class="h-10 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 outline-none focus:border-green-500"
          aria-label="Sort archived items"
        >
          <option value="newest">Recently archived</option>
          <option value="oldest">Oldest first</option>
          <option value="name">Name A–Z</option>
          <option value="type">Type A–Z</option>
        </select>
      </div>

      <div class="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div class="relative min-w-0 flex-1">
          <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-gray-400">search</span>
          <input
            v-model="search"
            type="search"
            placeholder="Search archived items..."
            class="h-10 w-full rounded-lg border border-gray-200 bg-gray-50 pl-10 pr-3 text-sm outline-none transition focus:border-green-500 focus:bg-white"
          />
        </div>
        <button
          type="button"
          class="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-gray-200 px-3 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          :disabled="loading"
          @click="fetchArchive"
        >
          <span class="material-symbols-outlined text-lg">refresh</span>
          Refresh
        </button>
      </div>

      <div class="mt-3 flex gap-2 overflow-x-auto pb-1">
        <button
          v-for="filter in filters"
          :key="filter.value"
          type="button"
          class="whitespace-nowrap rounded-full border px-3 py-1.5 text-xs font-medium transition"
          :class="activeType === filter.value
            ? 'border-green-600 bg-green-50 text-green-700'
            : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
          @click="activeType = filter.value"
        >
          {{ filter.label }} {{ filter.count }}
        </button>
      </div>
    </header>

    <div class="min-h-0 flex-1 overflow-y-auto">
      <div v-if="loading" class="grid min-h-[24rem] place-items-center text-sm text-gray-500">
        Loading archive...
      </div>

      <div v-else-if="error" class="grid min-h-[24rem] place-items-center px-6 text-center">
        <div>
          <span class="material-symbols-outlined text-3xl text-red-400">error</span>
          <p class="mt-2 text-sm text-red-600">{{ error }}</p>
          <button type="button" class="mt-3 text-sm font-medium text-green-700 hover:underline" @click="fetchArchive">
            Try again
          </button>
        </div>
      </div>

      <div v-else-if="!visibleItems.length" class="grid min-h-[24rem] place-items-center px-6 text-center">
        <div>
          <span class="material-symbols-outlined text-4xl text-gray-300">inventory_2</span>
          <h4 class="mt-3 text-base font-semibold text-gray-800">No archived items</h4>
          <p class="mt-1 text-sm text-gray-500">
            {{ search || activeType !== 'all' ? 'Try another search or filter.' : 'Archived data will appear here.' }}
          </p>
        </div>
      </div>

      <ul v-else class="divide-y divide-gray-100">
        <li
          v-for="item in visibleItems"
          :key="`${item.type}-${item.name}`"
          class="flex items-center gap-3 px-4 py-3 transition hover:bg-gray-50"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
            <img v-if="item.image" :src="item.image" :alt="item.title" class="h-full w-full object-contain" />
            <span v-else class="material-symbols-outlined text-xl text-gray-500">{{ typeMeta[item.type]?.icon || 'inventory_2' }}</span>
          </div>

          <div class="min-w-0 flex-1">
            <div class="flex min-w-0 items-center gap-2">
              <p class="truncate text-sm font-medium text-gray-900">{{ item.title }}</p>
              <span class="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-[10px] font-medium text-gray-600">
                {{ typeMeta[item.type]?.label || item.type }}
              </span>
            </div>
            <p class="mt-0.5 truncate text-xs text-gray-500">
              {{ item.subtitle }}<span v-if="formatDate(item.modified)"> · {{ formatDate(item.modified) }}</span>
            </p>
          </div>

          <button
            type="button"
            class="inline-flex h-9 shrink-0 items-center gap-1.5 rounded-lg border border-green-200 bg-white px-3 text-sm font-medium text-green-700 transition hover:bg-green-50 disabled:cursor-wait disabled:opacity-60"
            :disabled="restoringKey === `${item.type}-${item.name}`"
            @click="restoreItem(item)"
          >
            <span class="material-symbols-outlined text-lg">unarchive</span>
            {{ restoringKey === `${item.type}-${item.name}` ? 'Restoring...' : 'Restore' }}
          </button>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token') || ''
const items = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const activeType = ref('all')
const sortBy = ref('newest')
const restoringKey = ref('')

const typeMeta = {
  website: { label: 'Website', plural: 'Websites', icon: 'language' },
  page: { label: 'Page', plural: 'Pages', icon: 'description' },
  product: { label: 'Product', plural: 'Products', icon: 'inventory_2' },
  category: { label: 'Category', plural: 'Categories', icon: 'category' },
  brand: { label: 'Brand', plural: 'Brands', icon: 'sell' },
}

const filters = computed(() => [
  { value: 'all', label: 'All', count: items.value.length },
  ...Object.entries(typeMeta).map(([value, meta]) => ({
    value,
    label: meta.plural,
    count: items.value.filter((item) => item.type === value).length,
  })),
])

const visibleItems = computed(() => {
  const term = search.value.trim().toLowerCase()
  const result = items.value.filter((item) => {
    if (activeType.value !== 'all' && item.type !== activeType.value) return false
    return !term || `${item.title} ${item.subtitle} ${item.type}`.toLowerCase().includes(term)
  })
  return [...result].sort((a, b) => {
    if (sortBy.value === 'oldest') return String(a.modified || '').localeCompare(String(b.modified || ''))
    if (sortBy.value === 'name') return String(a.title || '').localeCompare(String(b.title || ''))
    if (sortBy.value === 'type') return `${a.type} ${a.title}`.localeCompare(`${b.type} ${b.title}`)
    return String(b.modified || '').localeCompare(String(a.modified || ''))
  })
})

function headers() {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
  }
}

function apiResult(payload) {
  return payload?.message ?? payload ?? {}
}

function formatDate(value) {
  return String(value || '').match(/^\d{4}-\d{2}-\d{2}/)?.[0] || ''
}

async function fetchArchive() {
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(`${Frappe_URL}/api/method/ecommerce.api.get_ecommerce_archive`, {
      headers: headers(),
    })
    const result = apiResult(await response.json().catch(() => ({})))
    if (!response.ok || result.status !== 'success') throw new Error(result.message || 'Unable to load archive.')
    items.value = Array.isArray(result.data) ? result.data : []
  } catch (err) {
    error.value = err.message || 'Unable to load archive.'
    items.value = []
  } finally {
    loading.value = false
  }
}

async function restoreItem(item) {
  const key = `${item.type}-${item.name}`
  restoringKey.value = key
  error.value = ''
  try {
    const response = await fetch(`${Frappe_URL}/api/method/ecommerce.api.restore_ecommerce_archive_item`, {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ item_type: item.type, name: item.name }),
    })
    const result = apiResult(await response.json().catch(() => ({})))
    if (!response.ok || result.status !== 'success') throw new Error(result.message || 'Unable to restore item.')
    items.value = items.value.filter((entry) => `${entry.type}-${entry.name}` !== key)
    window.dispatchEvent(new CustomEvent('ecommerce:website-updated'))
  } catch (err) {
    error.value = err.message || 'Unable to restore item.'
  } finally {
    restoringKey.value = ''
  }
}

onMounted(fetchArchive)
</script>
