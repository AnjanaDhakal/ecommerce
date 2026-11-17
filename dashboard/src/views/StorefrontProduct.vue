<template>
  <main class="flex-1 bg-white text-gray-900">
    <div class="mx-auto max-w-7xl px-5 py-8 sm:px-8 lg:px-10">
      <div v-if="loading" class="flex min-h-[70vh] items-center justify-center">
        <p class="text-sm font-medium text-gray-500">Loading product…</p>
      </div>

      <div v-else-if="error" class="flex min-h-[70vh] flex-col items-center justify-center text-center">
        <h1 class="text-3xl font-bold">Product unavailable</h1>
        <p class="mt-3 text-gray-500">{{ error }}</p>
        <RouterLink to="/" class="mt-6 rounded-xl bg-gray-900 px-5 py-3 text-sm font-semibold text-white">
          Back to dashboard
        </RouterLink>
      </div>

      <template v-else-if="product">
        <p class="mb-8 text-sm text-gray-500">
          Store <span class="mx-2">/</span> Product <span class="mx-2">/</span>
          <span class="font-medium text-gray-900">{{ product.product_name }}</span>
        </p>

        <section class="grid gap-10 lg:grid-cols-[minmax(0,1.05fr)_minmax(360px,.95fr)] lg:gap-16">
          <div class="min-w-0">
            <div class="flex aspect-square items-center justify-center overflow-hidden rounded-3xl border border-gray-200 bg-gray-50">
              <img
                v-if="selectedMedia?.type === 'image'"
                :src="selectedMedia.src"
                :alt="product.product_name"
                class="h-full w-full object-contain p-8"
              />
              <video
                v-else-if="selectedMedia?.type === 'video'"
                :key="selectedMedia.src"
                :src="selectedMedia.src"
                :aria-label="`${product.product_name} video`"
                controls
                playsinline
                preload="metadata"
                class="h-full w-full bg-black object-contain"
              />
              <span v-else class="text-sm text-gray-400">No media available</span>
            </div>

            <div v-if="media.length > 1" class="mt-4 flex gap-3 overflow-x-auto p-0.5">
              <button
                v-for="item in media"
                :key="`${item.type}:${item.src}`"
                type="button"
                class="relative h-20 w-20 shrink-0 overflow-hidden rounded-xl border-2 bg-gray-50"
                :class="item.src === selectedMedia?.src ? '' : 'border-transparent'"
                :data-store-selection="item.src === selectedMedia?.src ? 'active' : null"
                @click="selectedMedia = item"
              >
                <img
                  v-if="item.type === 'image'"
                  :src="item.src"
                  :alt="product.product_name"
                  class="h-full w-full object-contain"
                />
                <template v-else>
                  <video :src="item.src" muted preload="metadata" class="h-full w-full bg-black object-contain" />
                  <span class="absolute inset-0 flex items-center justify-center bg-black/20 text-xl text-white" aria-hidden="true">▶</span>
                </template>
              </button>
            </div>
          </div>

          <div class="lg:sticky lg:top-8 lg:self-start">
            <div class="flex flex-wrap gap-2">
              <span v-if="product.brand_name" class="rounded-full border px-3 py-2 text-xs font-bold uppercase tracking-wide" data-store-tone="accent">
                {{ product.brand_name }}
              </span>
              <span v-for="category in product.categories || []" :key="category.id" class="rounded-full border px-3 py-2 text-xs font-bold uppercase tracking-wide" data-store-tone="accent">
                {{ category.categories_name }}
              </span>
            </div>

            <h1 class="mt-5 text-4xl font-bold tracking-tight sm:text-5xl">{{ product.product_name }}</h1>
            <p v-if="product.description" class="mt-4 text-base leading-7 text-gray-500">{{ product.description }}</p>

            <div class="my-7 flex items-center justify-between gap-5 border-y border-gray-200 py-5">
              <strong class="text-3xl">Rs {{ displayPrice }}</strong>
              <span v-if="selectedVariant" class="text-sm font-bold" :class="inStock ? 'text-emerald-700' : 'text-red-600'">
                {{ stockStatus }}
              </span>
            </div>

            <fieldset v-if="variants.length" class="mb-6">
              <legend class="mb-3 text-sm font-bold">Choose a variant</legend>
              <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                <button
                  v-for="variant in variants"
                  :key="variant.name"
                  type="button"
                  class="flex justify-between gap-3 rounded-xl border px-4 py-3 text-left"
                  :class="variant === selectedVariant ? '' : 'border-gray-200 bg-white'"
                  :data-store-selection="variant === selectedVariant ? 'active' : null"
                  @click="selectVariant(variant)"
                >
                  <span class="font-medium">{{ variant.variant_name || variant.name }}</span>
                  <small class="text-gray-500">Rs {{ variantPrice(variant) }}</small>
                </button>
              </div>
            </fieldset>

            <div class="grid gap-3 sm:grid-cols-[150px_1fr]">
              <label>
                <span class="mb-2 block text-xs font-bold text-gray-500">Quantity</span>
                <span class="grid h-12 grid-cols-[38px_1fr_38px] overflow-hidden rounded-xl border border-gray-200">
                  <button type="button" class="text-xl" @click="changeQuantity(-1)">−</button>
                  <input v-model.number="quantity" type="number" min="1" :max="maximumQuantity" class="min-w-0 border-0 text-center outline-none" />
                  <button type="button" class="text-xl" @click="changeQuantity(1)">+</button>
                </span>
              </label>
              <button
                type="button"
                class="h-12 self-end rounded-xl bg-gray-900 text-sm font-bold text-white disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="selectedVariant && !inStock"
                @click="addToCart"
              >
                Add to cart
              </button>
            </div>
            <div class="mt-3 flex min-h-5 items-center justify-between gap-4 text-sm font-semibold">
              <p class="text-emerald-700">{{ cartFeedback }}</p>
              <RouterLink
                v-if="cartFeedback"
                :to="{ name: 'StorefrontCart', params: { websiteId: route.params.websiteId } }"
                class="text-gray-900 underline"
              >
                View cart
              </RouterLink>
            </div>

            <dl class="mt-5 border-t border-gray-200 text-sm">
              <div v-if="product.brand_name" class="grid grid-cols-[110px_1fr] border-b border-gray-200 py-3">
                <dt class="text-gray-500">Brand</dt><dd class="font-semibold">{{ product.brand_name }}</dd>
              </div>
              <div v-if="selectedVariant?.sku" class="grid grid-cols-[110px_1fr] border-b border-gray-200 py-3">
                <dt class="text-gray-500">SKU</dt><dd class="font-semibold">{{ selectedVariant.sku }}</dd>
              </div>
            </dl>
          </div>
        </section>

        <section v-if="product.long_description" class="mt-16 max-w-4xl border-t border-gray-200 pt-10">
          <p class="text-xs font-extrabold uppercase tracking-widest" data-store-accent-text>Product details</p>
          <h2 class="mt-2 text-3xl font-bold">About this product</h2>
          <p class="mt-4 whitespace-pre-line leading-8 text-gray-500">{{ product.long_description }}</p>
        </section>
      </template>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'

const route = useRoute()
const toast = useToast()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const loading = ref(true)
const error = ref('')
const product = ref(null)
const selectedMedia = ref(null)
const selectedVariant = ref(null)
const quantity = ref(1)
const cartFeedback = ref('')

const images = computed(() => {
  const values = [product.value?.image, ...(product.value?.images || [])]
  return [...new Set(values.filter(Boolean))]
})
const videos = computed(() => {
  const values = product.value?.videos || product.value?.product_videos || []
  return [...new Set((Array.isArray(values) ? values : []).filter(Boolean))]
})
const media = computed(() => [
  ...images.value.map(src => ({ type: 'image', src })),
  ...videos.value.map(src => ({ type: 'video', src })),
])
const variants = computed(() => product.value?.variant || product.value?.varient || [])
const displayPrice = computed(() => selectedVariant.value ? variantPrice(selectedVariant.value) : Number(product.value?.price || 0))
const continueSelling = computed(() => Boolean(Number(product.value?.continue_selling || 0)))
const availableStock = computed(() => Number(selectedVariant.value?.quantity || 0))
const inStock = computed(() => availableStock.value > 0 || continueSelling.value)
const stockStatus = computed(() => {
  if (availableStock.value > 0) return `${availableStock.value} available`
  return continueSelling.value ? 'Available to order' : 'Out of stock'
})
const maximumQuantity = computed(() => {
  if (!selectedVariant.value || continueSelling.value) return 999
  return Math.max(1, availableStock.value)
})

function variantPrice(variant) {
  const discountedPrice = Number(variant?.discounted_price || 0)
  return Number(discountedPrice > 0 ? discountedPrice : (variant?.selling_price ?? variant?.cost_price ?? 0))
}

function selectVariant(variant) {
  selectedVariant.value = variant
  const variantImage = variant?.image || variant?.variant_image || product.value?.image
  if (variantImage) selectedMedia.value = { type: 'image', src: variantImage }
  quantity.value = Math.min(Math.max(1, quantity.value), maximumQuantity.value)
  cartFeedback.value = ''
}

function changeQuantity(amount) {
  quantity.value = Math.min(maximumQuantity.value, Math.max(1, Number(quantity.value || 1) + amount))
}

function addToCart() {
  const requestedQuantity = Math.min(maximumQuantity.value, Math.max(1, Number(quantity.value || 1)))
  const storageKey = 'ecommerce_storefront_cart'
  let cart = []
  try {
    cart = JSON.parse(localStorage.getItem(storageKey) || '[]')
  } catch (_) {
    cart = []
  }

  const variantName = selectedVariant.value?.variant_name || selectedVariant.value?.name || ''
  const key = `${product.value.website}:${product.value.id}:${variantName}`
  const existing = cart.find((item) => item.key === key)
  if (existing) existing.quantity += requestedQuantity
  else cart.push({
    key,
    website_id: product.value.website,
    product_id: product.value.id,
    product_name: product.value.product_name,
    image: selectedVariant.value?.image || selectedVariant.value?.variant_image || product.value.image || '',
    variant: selectedVariant.value,
    price: displayPrice.value,
    quantity: requestedQuantity,
  })
  localStorage.setItem(storageKey, JSON.stringify(cart))
  window.dispatchEvent(new CustomEvent('ecommerce:cart-updated', { detail: { cart } }))
  cartFeedback.value = `${requestedQuantity} item${requestedQuantity > 1 ? 's' : ''} added to cart.`
  toast.success(
    `${product.value.product_name} added to cart${requestedQuantity > 1 ? ` (${requestedQuantity})` : ''}.`,
  )
}

async function loadProduct() {
  loading.value = true
  error.value = ''
  product.value = null
  try {
    const params = new URLSearchParams({
      website_id: String(route.params.websiteId),
      entity_type: 'product',
      slug: String(route.params.slug),
    })
    const response = await fetch(`${Frappe_URL}/api/method/ecommerce.api.get_storefront_entity?${params}`)
    const body = await response.json()
    const result = body?.message
    if (!response.ok || result?.status !== 'success' || !result?.data?.entity) {
      throw new Error(result?.message || 'The requested product could not be found.')
    }
    product.value = result.data.entity
    selectedMedia.value = media.value[0] || null
    if (variants.value[0]) selectVariant(variants.value[0])
    else selectedVariant.value = null
    quantity.value = 1
  } catch (exception) {
    error.value = exception?.message || 'Unable to load this product.'
  } finally {
    loading.value = false
  }
}

watch(() => [route.params.websiteId, route.params.slug], loadProduct, { immediate: true })
</script>
