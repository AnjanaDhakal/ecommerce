<template>
  <main class="flex-1 bg-gray-50 px-5 py-10 text-gray-900 sm:px-8">
    <div class="mx-auto max-w-5xl">
      <header class="mb-8 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p class="text-xs font-extrabold uppercase tracking-widest text-emerald-700">Shopping cart</p>
          <h1 class="mt-1 text-4xl font-bold tracking-tight">Review your items</h1>
        </div>
        <span class="rounded-full bg-white px-4 py-2 text-sm font-semibold shadow-sm">{{ itemCount }} items</span>
      </header>

      <div v-if="!cart.length" class="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center">
        <h2 class="text-2xl font-bold">Your cart is empty</h2>
        <p class="mt-2 text-gray-500">Add a product before continuing to checkout.</p>
      </div>

      <div v-else class="grid gap-8 lg:grid-cols-[1fr_320px]">
        <section class="space-y-4">
          <article v-for="item in cart" :key="item.key" class="flex gap-5 rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <img v-if="item.image" :src="item.image" :alt="item.product_name" class="h-28 w-28 rounded-xl bg-gray-50 object-contain p-2" />
            <div class="min-w-0 flex-1">
              <h2 class="text-lg font-bold">{{ item.product_name }}</h2>
              <p v-if="item.variant" class="mt-1 text-sm text-gray-500">{{ item.variant.variant_name || item.variant.name }}</p>
              <strong class="mt-2 block">Rs {{ item.price }}</strong>
              <div class="mt-4 flex items-center justify-between gap-4">
                <div class="flex items-center overflow-hidden rounded-lg border border-gray-200">
                  <button type="button" class="px-3 py-2" aria-label="Decrease quantity" @click="changeQuantity(item, -1)">−</button>
                  <span class="min-w-10 text-center text-sm font-semibold">{{ item.quantity }}</span>
                  <button type="button" class="px-3 py-2" aria-label="Increase quantity" @click="changeQuantity(item, 1)">+</button>
                </div>
                <button type="button" class="text-sm font-semibold text-red-600" @click="removeItem(item.key)">Remove</button>
              </div>
            </div>
          </article>
        </section>

        <aside class="h-fit rounded-2xl border border-gray-200 bg-white p-6 shadow-sm lg:sticky lg:top-8">
          <h2 class="text-xl font-bold">Order summary</h2>
          <div class="mt-5 border-t border-gray-200 pt-4">
            <div class="flex justify-between text-sm text-gray-500"><span>Subtotal</span><span>Rs {{ total }}</span></div>
            <div class="mt-3 flex justify-between text-xl font-bold"><span>Total</span><span>Rs {{ total }}</span></div>
          </div>
          <RouterLink
            :to="{ name: 'StorefrontCheckout', params: { websiteId: route.params.websiteId } }"
            class="mt-6 block w-full rounded-xl bg-gray-900 px-5 py-4 text-center text-sm font-bold text-white"
          >
            Continue to checkout
          </RouterLink>
        </aside>
      </div>
    </div>
  </main>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'vue-toastification'

const route = useRoute()
const toast = useToast()
const storageKey = 'ecommerce_storefront_cart'
const allCartItems = ref(readCart())
const cart = computed(() => allCartItems.value.filter(item => String(item.website_id) === String(route.params.websiteId)))
const itemCount = computed(() => cart.value.reduce((sum, item) => sum + Number(item.quantity || 0), 0))
const total = computed(() => cart.value.reduce((sum, item) => sum + Number(item.price || 0) * Number(item.quantity || 0), 0).toFixed(2))

function readCart() {
  try { return JSON.parse(localStorage.getItem(storageKey) || '[]') }
  catch (_) { return [] }
}

function saveCart() {
  localStorage.setItem(storageKey, JSON.stringify(allCartItems.value))
  window.dispatchEvent(new CustomEvent('ecommerce:cart-updated', { detail: { cart: allCartItems.value } }))
}

function changeQuantity(item, amount) {
  item.quantity = Math.max(1, Number(item.quantity || 1) + amount)
  saveCart()
}

function removeItem(key) {
  const removedItem = allCartItems.value.find(item => item.key === key)
  allCartItems.value = allCartItems.value.filter(item => item.key !== key)
  saveCart()
  toast.success(`${removedItem?.product_name || 'Item'} removed from cart.`)
}
</script>
