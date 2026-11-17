<template>
  <section class="flex h-full min-h-0 flex-col gap-4">
    <p v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{{ error }}</p>
    <p v-if="success" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-700">{{ success }}</p>

    <div class="space-y-3 rounded-2xl border border-gray-200 bg-white p-4">
      <div class="relative">
        <span class="material-symbols-outlined pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-xl text-gray-400">search</span>
        <input v-model="searchQuery" type="search" class="w-full rounded-xl border border-gray-200 py-2.5 pl-10 pr-3 text-sm outline-none transition focus:border-gray-400 focus:ring-2 focus:ring-gray-100" placeholder="Search by order ID, customer, phone, tracking or branch" />
      </div>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="filter in filters"
            :key="filter"
            type="button"
            class="whitespace-nowrap rounded-full border px-4 py-2 text-sm font-semibold transition-colors"
            :class="activeFilter === filter ? 'border-gray-900 bg-gray-900 text-white' : 'border-gray-200 bg-white text-gray-600 hover:border-gray-400'"
            @click="selectFilter(filter)"
          >
            {{ filter }} <span class="ml-1 opacity-70">{{ countFor(filter) }}</span>
          </button>
        </div>
        <button
          type="button"
          class="ml-auto inline-flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          :disabled="loading"
          @click="loadOrders()"
        >
          <span class="material-symbols-outlined text-lg">refresh</span>
          {{ loading ? 'Refreshing…' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div class="grid min-h-0 flex-1 overflow-hidden rounded-2xl border border-gray-200 bg-white lg:grid-cols-[18rem_minmax(0,1fr)]">
      <aside class="flex min-h-0 flex-col border-b border-gray-200 lg:border-b-0 lg:border-r">
        <div class="min-h-0 flex-1 space-y-2 overflow-y-auto bg-gray-50/50 p-3">
          <div v-if="loading && !orders.length" class="p-8 text-center text-sm text-gray-500">Loading orders…</div>
          <div v-else-if="!orders.length" class="p-8 text-center">
            <span class="material-symbols-outlined text-4xl text-gray-300">orders</span>
            <p class="mt-2 font-semibold text-gray-700">No matching orders</p>
            <p class="mt-1 text-xs text-gray-400">Try another search or status.</p>
          </div>
          <button
            v-for="order in orders"
            :key="order.name"
            type="button"
            class="block w-full rounded-xl border px-4 py-4 text-left transition"
            :class="selectedOrderName === order.name ? 'border-emerald-400 bg-emerald-50 shadow-sm' : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'"
            @click="selectedOrderName = order.name"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <p class="truncate text-sm font-bold text-gray-900">{{ order.name }}</p>
                <p class="mt-1 truncate text-xs font-medium text-gray-600">{{ order.customer_name }} · {{ order.phone }}</p>
              </div>
              <span class="shrink-0 rounded-full px-2 py-1 text-[10px] font-bold" :class="statusClass(order.status)">{{ order.status }}</span>
            </div>
            <div class="mt-2 flex items-center justify-between gap-3 text-xs">
              <span class="truncate text-gray-400">{{ formatDate(order.creation) }}</span>
              <strong class="shrink-0 text-gray-800">Rs {{ money(order.grand_total) }}</strong>
            </div>
          </button>
        </div>

        <div class="flex items-center justify-between gap-2 border-t border-gray-100 p-3 text-xs text-gray-500">
          <button type="button" class="rounded-lg border border-gray-200 px-3 py-2 font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-40" :disabled="loading || pagination.page <= 1" @click="goToPage(pagination.page - 1)">Previous</button>
          <span class="text-center">Page {{ pagination.page }} of {{ pagination.pages }}<br />{{ pagination.total }} orders</span>
          <button type="button" class="rounded-lg border border-gray-200 px-3 py-2 font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-40" :disabled="loading || pagination.page >= pagination.pages" @click="goToPage(pagination.page + 1)">Next</button>
        </div>
      </aside>

      <main class="min-h-0 min-w-0 overflow-y-auto bg-gray-50/60">
        <div v-if="!selectedOrder" class="flex h-full min-h-[420px] items-center justify-center p-8 text-center">
          <div>
            <span class="material-symbols-outlined text-5xl text-gray-300">order_approve</span>
            <p class="mt-3 font-semibold text-gray-700">Select an order</p>
            <p class="mt-1 text-sm text-gray-400">The order details and actions will appear here.</p>
          </div>
        </div>

        <article v-else class="p-4 sm:p-6">
          <div class="rounded-2xl border border-gray-200 bg-white shadow-sm">
            <header class="sticky top-0 z-10 rounded-t-2xl border-b border-gray-100 bg-white p-5 shadow-sm sm:p-6">
              <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div class="min-w-0">
                  <p class="truncate text-sm font-semibold text-gray-900">{{ selectedOrder.customer_name }}</p>
                  <p class="mt-0.5 truncate text-xs text-gray-500">{{ selectedOrder.phone }}</p>
                </div>
                <div class="flex shrink-0 flex-wrap gap-2">
                  <button v-if="['Pending', 'Packed'].includes(selectedOrder.status)" type="button" class="rounded-lg border border-red-200 px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 disabled:opacity-50" :disabled="busyOrder === selectedOrder.name" @click="changeStatus(selectedOrder, 'Cancelled')">Cancel</button>
                  <button v-if="['Pending', 'Packed'].includes(selectedOrder.status)" type="button" class="rounded-lg bg-gray-900 px-3 py-2 text-xs font-semibold text-white hover:bg-gray-800 disabled:opacity-50" :disabled="busyOrder === selectedOrder.name" @click="confirmOrder(selectedOrder)">{{ busyOrder === selectedOrder.name ? 'Creating order…' : 'Confirm & create delivery order' }}</button>
                </div>
              </div>
              <div class="mt-4 flex flex-col gap-4 border-t border-gray-100 pt-4 sm:flex-row sm:items-start sm:justify-between">
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <h3 class="text-xl font-bold text-gray-900">{{ selectedOrder.name }}</h3>
                    <span class="rounded-full px-2.5 py-1 text-xs font-bold" :class="statusClass(selectedOrder.status)">{{ selectedOrder.status }}</span>
                  </div>
                  <p class="mt-2 text-sm text-gray-500">Placed {{ formatDate(selectedOrder.creation) }}</p>
                </div>
                <div class="shrink-0 sm:text-right">
                  <p class="text-[11px] font-semibold uppercase tracking-wide text-gray-400">COD total</p>
                  <p class="text-2xl font-bold text-gray-900">Rs {{ money(selectedOrder.grand_total) }}</p>
                  <p class="mt-1 text-xs text-gray-500">{{ itemCount(selectedOrder) }} item{{ itemCount(selectedOrder) === 1 ? '' : 's' }}</p>
                </div>
              </div>
            </header>

            <div class="border-b border-gray-100 p-5 sm:p-6">
              <section class="grid gap-4 rounded-xl bg-gray-50 p-4 sm:grid-cols-2 sm:gap-6">
                <div>
                  <p class="text-xs font-bold uppercase tracking-wide text-gray-400">Delivery address</p>
                  <p class="mt-2 text-sm leading-6 text-gray-600">{{ selectedOrder.delivery_address }}, {{ selectedOrder.city_area }}</p>
                </div>
                <div>
                  <p class="text-xs font-bold uppercase tracking-wide text-gray-400">Delivery</p>
                  <p class="mt-2 text-sm text-gray-600">Destination: <strong class="text-gray-900">{{ selectedOrder.destination_branch }}</strong></p>
                  <p class="mt-1 text-sm text-gray-600">Payment: <strong class="text-gray-900">{{ selectedOrder.payment_method || 'Cash on Delivery' }}</strong></p>
                  <p v-if="selectedOrder.system_order" class="mt-2 text-sm text-emerald-700">Ecommerce order: <strong>{{ selectedOrder.system_order }}</strong></p>
                  <p v-if="selectedOrder.order_note" class="mt-2 text-sm text-gray-600">Note: {{ selectedOrder.order_note }}</p>
                </div>
              </section>
            </div>

            <section class="p-5 sm:p-6">
              <div class="flex items-center justify-between">
                <h4 class="font-bold text-gray-900">Order items</h4>
                <span class="text-xs text-gray-400">{{ selectedOrder.items?.length || 0 }} lines</span>
              </div>
              <div class="mt-4 overflow-hidden rounded-xl border border-gray-200">
                <div v-for="(item, index) in selectedOrder.items" :key="`${item.product_id}-${item.variant_name}-${index}`" class="flex items-start justify-between gap-4 border-b border-gray-100 p-4 last:border-b-0">
                  <div class="min-w-0">
                    <p class="font-semibold text-gray-800">{{ item.quantity }} × {{ item.product_name }}</p>
                    <p class="mt-1 text-xs text-gray-500">
                      <span v-if="item.variant_name">{{ item.variant_name }}</span><span v-if="item.sku">{{ item.variant_name ? ' · ' : '' }}SKU {{ item.sku }}</span><span> · Rs {{ money(item.unit_price) }} each</span>
                    </p>
                  </div>
                  <strong class="shrink-0 text-sm text-gray-900">Rs {{ money(item.line_total) }}</strong>
                </div>
              </div>

              <div class="ml-auto mt-5 max-w-xs space-y-2 text-sm">
                <div class="flex justify-between gap-4 text-gray-600"><span>Subtotal</span><span>Rs {{ money(selectedOrder.subtotal) }}</span></div>
                <div class="flex justify-between gap-4 text-gray-600"><span>Delivery charge</span><span>Rs {{ money(selectedOrder.delivery_amount) }}</span></div>
                <div class="flex justify-between gap-4 border-t border-gray-200 pt-2 text-base font-bold text-gray-900"><span>Total</span><span>Rs {{ money(selectedOrder.grand_total) }}</span></div>
              </div>
            </section>

          </div>
        </article>
      </main>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const filters = ['All', 'Pending', 'Confirmed', 'Cancelled']
const route = useRoute()
const requestedFilter = String(route.query.orderStatus || '').trim().toLowerCase()
const initialFilter = filters.find(
  (filter) => filter.toLowerCase() === requestedFilter,
)
const activeFilter = ref(initialFilter || 'All')
const searchQuery = ref('')
const orders = ref([])
const selectedOrderName = ref('')
const loading = ref(false)
const busyOrder = ref('')
const error = ref('')
const success = ref('')
const statusCounts = ref({ All: 0, Pending: 0, Packed: 0, Confirmed: 0, Cancelled: 0 })
const pagination = ref({ page: 1, page_length: 25, total: 0, pages: 1 })
const selectedOrder = computed(() => orders.value.find(order => order.name === selectedOrderName.value) || null)
let searchTimer = null
let requestSequence = 0

function headers() {
  const token = localStorage.getItem('access_token') || ''
  return { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) }
}

function resultFrom(body) { return body?.message ?? body }
function money(value) { return Number(value || 0).toFixed(2) }
function itemCount(order) { return (order.items || []).reduce((sum, item) => sum + Number(item.quantity || 0), 0) }
function countFor(filter) { return Number(statusCounts.value?.[filter] || 0) }
function formatDate(value) {
  if (!value) return ''
  const date = new Date(String(value).replace(' ', 'T'))
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}
function statusClass(status) {
  return { Pending: 'bg-amber-100 text-amber-800', Packed: 'bg-blue-100 text-blue-800', Confirmed: 'bg-emerald-100 text-emerald-800', Cancelled: 'bg-gray-200 text-gray-600' }[status] || 'bg-gray-100 text-gray-700'
}
async function request(method, data = null) {
  const response = await fetch(`${Frappe_URL}/api/method/${method}`, { method: data ? 'POST' : 'GET', headers: headers(), ...(data ? { body: JSON.stringify(data) } : {}) })
  const body = await response.json().catch(() => ({}))
  const result = resultFrom(body)
  if (!response.ok || result?.status !== 'success') throw new Error(result?.message || 'Unable to update ecommerce order.')
  return result
}

async function loadOrders({ preserveSelection = true } = {}) {
  const sequence = ++requestSequence
  const previousSelection = preserveSelection ? selectedOrderName.value : ''
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({ status: activeFilter.value, search: searchQuery.value.trim(), page: String(pagination.value.page), page_length: String(pagination.value.page_length) })
    const result = await request(`ecommerce.api.get_ecommerce_orders?${params.toString()}`)
    if (sequence !== requestSequence) return
    orders.value = Array.isArray(result.data) ? result.data : []
    statusCounts.value = { ...statusCounts.value, ...(result.status_counts || {}) }
    pagination.value = { ...pagination.value, ...(result.pagination || {}) }
    selectedOrderName.value = orders.value.some(order => order.name === previousSelection) ? previousSelection : (orders.value[0]?.name || '')
  } catch (requestError) {
    if (sequence === requestSequence) error.value = requestError?.message || 'Unable to load ecommerce orders.'
  } finally {
    if (sequence === requestSequence) loading.value = false
  }
}

function selectFilter(filter) {
  if (activeFilter.value === filter) return
  activeFilter.value = filter
  pagination.value.page = 1
  loadOrders({ preserveSelection: false })
}
function goToPage(page) {
  pagination.value.page = page
  loadOrders({ preserveSelection: false })
}

async function changeStatus(order, status) {
  busyOrder.value = order.name
  error.value = ''
  success.value = ''
  try {
    const result = await request('ecommerce.api.update_ecommerce_order_status', { order_id: order.name, status })
    success.value = result.message || 'Order updated.'
    await loadOrders()
  } catch (requestError) {
    error.value = requestError?.message || 'Unable to update ecommerce order.'
  } finally {
    busyOrder.value = ''
  }
}

async function confirmOrder(order) {
  busyOrder.value = order.name
  error.value = ''
  success.value = ''
  try {
    const result = await request('ecommerce.api.confirm_ecommerce_order', { order_id: order.name })
    success.value = result.message || 'Delivery order created.'
    await loadOrders()
  } catch (requestError) {
    error.value = requestError?.message || 'Unable to create the delivery order.'
  } finally {
    busyOrder.value = ''
  }
}

watch(searchQuery, () => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.value.page = 1
    loadOrders({ preserveSelection: false })
  }, 350)
})

watch(
  () => route.query.orderStatus,
  (status) => {
    const requestedStatus = String(status || '').trim().toLowerCase()
    const filter = filters.find(
      (option) => option.toLowerCase() === requestedStatus,
    )
    if (filter && filter !== activeFilter.value) selectFilter(filter)
  },
)

onMounted(() => loadOrders({ preserveSelection: false }))
onBeforeUnmount(() => clearTimeout(searchTimer))
</script>
