<template>
  <main class="flex-1 bg-gray-50 px-5 py-10 text-gray-900 sm:px-8">
    <div class="mx-auto max-w-6xl">
      <header class="mb-8 flex items-center justify-between gap-4">
        <div>
          <p class="text-xs font-extrabold uppercase tracking-widest" data-store-accent-text>Store checkout</p>
          <h1 class="mt-1 text-4xl font-bold tracking-tight">Checkout</h1>
          <RouterLink :to="{ name: 'StorefrontCart', params: { websiteId: route.params.websiteId } }" class="mt-2 inline-block text-sm font-semibold text-gray-600 underline">
            Back to cart
          </RouterLink>
        </div>
        <span class="rounded-full bg-white px-4 py-2 text-sm font-semibold shadow-sm">{{ itemCount }} items</span>
      </header>

      <div v-if="submitted" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center">
        <p class="text-xs font-extrabold uppercase tracking-widest text-emerald-700">Cash on Delivery</p>
        <h2 class="mt-2 text-3xl font-bold text-emerald-900">Order received</h2>
        <p class="mt-2 text-emerald-800">Your order number is <strong>{{ orderResult.order_id }}</strong>.</p>
        <p class="mx-auto mt-2 max-w-lg text-sm text-emerald-700">The store will review and confirm your order.</p>
        <div class="mx-auto mt-6 max-w-sm rounded-xl bg-white p-5 text-left shadow-sm">
          <div class="flex justify-between text-sm text-gray-500"><span>Products</span><span>Rs {{ money(orderResult.subtotal) }}</span></div>
          <div class="mt-2 flex justify-between text-sm text-gray-500"><span>Delivery</span><span>Rs {{ money(orderResult.delivery_amount) }}</span></div>
          <div class="mt-4 flex justify-between border-t border-gray-200 pt-4 text-lg font-bold"><span>COD total</span><span>Rs {{ money(orderResult.total) }}</span></div>
        </div>
        <a v-if="orderResult.tracking_url" :href="orderResult.tracking_url" class="mt-6 inline-block font-semibold text-emerald-800 underline">Track this order</a>
      </div>

      <div v-else-if="!cart.length" class="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center">
        <h2 class="text-2xl font-bold">Your cart is empty</h2>
        <p class="mt-2 text-gray-500">Add a product before checking out.</p>
      </div>

      <div v-else class="grid gap-8 lg:grid-cols-[1fr_400px]">
        <section class="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 class="text-xl font-bold">Delivery information</h2>
          <p class="mt-1 text-sm text-gray-500">The store will review, pack, and confirm your order.</p>

          <p v-if="error" class="mt-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{{ error }}</p>

          <form class="mt-6 grid gap-5 sm:grid-cols-2" @submit.prevent="placeOrder">
            <label class="block text-sm font-semibold">
              Full name
              <input v-model.trim="customer.name" required autocomplete="name" class="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 font-normal outline-none focus:border-emerald-600" />
            </label>
            <label class="block text-sm font-semibold">
              Phone
              <input v-model.trim="customer.phone" required type="tel" inputmode="numeric" pattern="[0-9]{10}" maxlength="10" autocomplete="tel" placeholder="98XXXXXXXX" class="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 font-normal outline-none focus:border-emerald-600" />
            </label>
            <label class="block text-sm font-semibold">
              Destination branch
              <span v-if="loadingOptions" class="mt-2 flex h-12 items-center rounded-xl border border-gray-300 bg-gray-50 px-4 font-normal text-gray-500">
                Loading branches…
              </span>
              <BranchSelect
                v-else
                v-model="customer.destination_branch"
                class="storefront-branch-select mt-2 w-full"
                :options="branches"
                :auto-select-first-area="false"
                placeholder="Search branch, area, district or municipality..."
                @change="handleDestinationBranchChange"
              />
            </label>
            <label class="block text-sm font-semibold">
              City / area
              <input v-model.trim="customer.city_area" required autocomplete="address-level2" placeholder="Area / city" class="mt-2 w-full rounded-xl border border-gray-300 px-4 py-3 font-normal outline-none focus:border-emerald-600" />
            </label>
            <label class="block text-sm font-semibold sm:col-span-2">
              Delivery address
              <textarea v-model.trim="customer.address" required rows="3" autocomplete="street-address" placeholder="Enter the complete delivery address" class="mt-2 w-full resize-none rounded-xl border border-gray-300 px-4 py-3 font-normal outline-none focus:border-emerald-600" />
            </label>
            <label class="block text-sm font-semibold sm:col-span-2">
              Order note <span class="font-normal text-gray-400">(optional)</span>
              <textarea v-model.trim="customer.instruction" rows="2" class="mt-2 w-full resize-none rounded-xl border border-gray-300 px-4 py-3 font-normal outline-none focus:border-emerald-600" />
            </label>
          </form>
        </section>

        <aside class="h-fit rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:sticky lg:top-8">
          <h2 class="text-xl font-bold">Order summary</h2>
          <div class="mt-5 max-h-72 space-y-4 overflow-auto pr-1">
            <article v-for="item in cart" :key="item.key" class="flex gap-3 border-b border-gray-100 pb-4">
              <img v-if="item.image" :src="item.image" :alt="item.product_name" class="h-16 w-16 rounded-lg bg-gray-50 object-contain p-1" />
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-bold">{{ item.product_name }}</p>
                <p v-if="item.variant" class="text-xs text-gray-500">{{ item.variant.variant_name || item.variant.name }}</p>
                <p class="mt-1 text-sm">{{ item.quantity }} × Rs {{ money(item.price) }}</p>
              </div>
            </article>
          </div>
          <div class="mt-5 border-t border-gray-200 pt-4">
            <div class="flex justify-between text-sm text-gray-500"><span>Product subtotal</span><span>Rs {{ total }}</span></div>
            <div class="mt-2 flex justify-between gap-4 text-sm text-gray-500">
              <span>Delivery</span>
              <span v-if="deliveryLoading">Calculating…</span>
              <span v-else-if="deliveryAmount !== null" class="font-semibold text-gray-800">Rs {{ money(deliveryAmount) }}</span>
              <span v-else>{{ customer.destination_branch ? 'Unavailable' : 'Select destination branch' }}</span>
            </div>
            <p v-if="deliveryError" class="mt-2 text-right text-xs text-red-600">{{ deliveryError }}</p>
            <div class="mt-3 flex justify-between border-t border-gray-100 pt-3 text-xl font-bold">
              <span>COD total</span>
              <span>Rs {{ money(estimatedTotal) }}</span>
            </div>
          </div>
          <div class="mt-5 rounded-xl border p-4" data-store-tone="accent">
            <p class="text-sm font-bold">Cash on Delivery</p>
            <p class="mt-1 text-xs leading-5">Delivery is calculated from the selected destination branch and your cart weight.</p>
          </div>
          <button type="button" :disabled="submitting || loadingOptions" class="mt-5 w-full rounded-xl bg-gray-900 px-5 py-4 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50" @click="placeOrder">
            {{ submitting ? 'Placing order…' : 'Place COD order' }}
          </button>
        </aside>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import BranchSelect from '@/components/BranchSelect.vue'

const route = useRoute()
const storageKey = 'ecommerce_storefront_cart'
const allCartItems = ref(readCart())
const customer = reactive({
  name: '',
  phone: '',
  destination_branch: '',
  city_area: '',
  address: '',
  instruction: '',
})
const submitted = ref(false)
const submitting = ref(false)
const loadingOptions = ref(true)
const error = ref('')
const orderResult = ref({})
const branches = ref([])
const deliveryAmount = ref(null)
const deliveryLoading = ref(false)
const deliveryError = ref('')
let deliveryQuoteRequest = 0
const cart = computed(() => allCartItems.value.filter(item => String(item.website_id) === String(route.params.websiteId)))
const itemCount = computed(() => cart.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0))
const productSubtotal = computed(() => cart.value.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0))
const total = computed(() => productSubtotal.value.toFixed(2))
const estimatedTotal = computed(() => productSubtotal.value + Number(deliveryAmount.value || 0))

function readCart() {
  try { return JSON.parse(localStorage.getItem(storageKey) || '[]') }
  catch (_) { return [] }
}

function saveCart() {
  localStorage.setItem(storageKey, JSON.stringify(allCartItems.value))
  window.dispatchEvent(new CustomEvent('ecommerce:cart-updated', { detail: { cart: allCartItems.value } }))
}

function money(value) {
  return Number(value || 0).toFixed(2)
}

function apiHeaders() {
  const headers = { 'Content-Type': 'application/json' }
  const csrfToken = window.frappe?.csrf_token
  const accessToken = localStorage.getItem('access_token')
  if (csrfToken) headers['X-Frappe-CSRF-Token'] = csrfToken
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`
  return headers
}

function responseMessage(payload) {
  const result = payload?.message ?? payload
  if (typeof result?.message === 'string') return result.message
  try {
    const messages = JSON.parse(payload?._server_messages || '[]')
    const parsed = messages.map(value => JSON.parse(value)?.message).filter(Boolean)
    if (parsed.length) return parsed.join(' ')
  } catch (_) {}
  return 'Unable to place your order. Please try again.'
}

async function loadCheckoutOptions() {
  loadingOptions.value = true
  error.value = ''
  try {
    const query = new URLSearchParams({ website_id: String(route.params.websiteId || '') })
    const response = await fetch(`/api/method/ecommerce.api.get_storefront_checkout_options?${query}`)
    const payload = await response.json()
    const result = payload?.message ?? payload
    if (!response.ok || result?.status !== 'success') throw new Error(responseMessage(payload))
    const branchRows = Array.isArray(result?.data?.branches) ? result.data.branches : []
    branches.value = branchRows.map(branch => ({
      label: branch.label || branch.value || '',
      value: branch.value || '',
      name: branch.value || '',
      branch_name: branch.label || branch.value || '',
      branch_code: branch.branch_code || '',
      district: branch.district || '',
      municipality: branch.municipality || '',
      areas: Array.isArray(branch.areas) ? branch.areas : [],
    }))
    if (!branches.value.length) error.value = 'No delivery branches are currently available.'
  } catch (requestError) {
    error.value = requestError?.message || 'Unable to load delivery destinations.'
  } finally {
    loadingOptions.value = false
  }
}

function handleDestinationBranchChange(selection) {
  if (selection?.area) customer.city_area = selection.area
}

async function loadDeliveryQuote() {
  const requestId = ++deliveryQuoteRequest
  deliveryAmount.value = null
  deliveryError.value = ''
  if (!customer.destination_branch || !cart.value.length) return

  deliveryLoading.value = true
  try {
    const response = await fetch(
      '/api/method/ecommerce.api.get_storefront_delivery_quote',
      {
        method: 'POST',
        headers: apiHeaders(),
        body: JSON.stringify({
          website_id: route.params.websiteId,
          destination_branch: customer.destination_branch,
          city_area: customer.city_area,
          address: customer.address,
          items: cart.value.map(item => ({
            product_id: item.product_id,
            variant: item.variant || null,
            quantity: Number(item.quantity || 1),
          })),
        }),
      },
    )
    const payload = await response.json()
    const result = payload?.message ?? payload
    if (!response.ok || result?.status !== 'success') {
      throw new Error(responseMessage(payload))
    }
    if (requestId !== deliveryQuoteRequest) return
    deliveryAmount.value = Number(result.data?.delivery_amount || 0)
  } catch (requestError) {
    if (requestId !== deliveryQuoteRequest) return
    deliveryError.value = requestError?.message || 'Unable to calculate delivery charge.'
  } finally {
    if (requestId === deliveryQuoteRequest) deliveryLoading.value = false
  }
}

async function placeOrder() {
  if (submitting.value || !cart.value.length) return
  const phone = String(customer.phone || '').replace(/\D/g, '')
  if (!customer.name || phone.length !== 10 || !customer.destination_branch || !customer.city_area || !customer.address) {
    error.value = 'Complete all required delivery fields and enter a valid 10-digit phone number.'
    return
  }

  submitting.value = true
  error.value = ''
  try {
    const response = await fetch('/api/method/ecommerce.api.place_storefront_order', {
      method: 'POST',
      headers: apiHeaders(),
      body: JSON.stringify({
        website_id: route.params.websiteId,
        customer: { ...customer, phone },
        items: cart.value.map(item => ({
          product_id: item.product_id,
          variant: item.variant || null,
          quantity: Number(item.quantity || 1),
        })),
      }),
    })
    const payload = await response.json()
    const result = payload?.message ?? payload
    if (!response.ok || result?.status !== 'success') throw new Error(responseMessage(payload))

    orderResult.value = result.data || {}
    const submittedKeys = new Set(cart.value.map(item => item.key))
    allCartItems.value = allCartItems.value.filter(item => !submittedKeys.has(item.key))
    saveCart()
    submitted.value = true
  } catch (requestError) {
    error.value = requestError?.message || 'Unable to place your order. Please try again.'
  } finally {
    submitting.value = false
  }
}

watch(() => customer.destination_branch, loadDeliveryQuote)
onMounted(loadCheckoutOptions)
</script>

<style scoped>
.storefront-branch-select :deep(> button) {
  height: 3rem;
  border-radius: 0.75rem;
  border-color: rgb(209 213 219);
  background: white;
  padding-left: 1rem;
  padding-right: 1rem;
}

.storefront-branch-select :deep(> button > div > div:first-child) {
  font-size: 1rem;
  font-weight: 400;
}
</style>
