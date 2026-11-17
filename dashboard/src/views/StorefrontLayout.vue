<template>
  <div class="storefront-theme flex min-h-screen flex-col bg-white" :style="themeStyle">
    <component :is="'style'" v-if="shell.styles">{{ shell.styles }}</component>

    <div
      v-if="shell.header"
      ref="headerElement"
      class="storefront-builder-header"
      v-html="shell.header"
      @click="handleShellNavigation"
    />

    <div class="flex flex-1 flex-col">
      <RouterView />
    </div>

    <div
      v-if="shell.footer"
      class="storefront-builder-footer"
      v-html="shell.footer"
      @click="handleShellNavigation"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const defaultTheme = {
  primary_color: '#ff4964',
  secondary_color: '#111827',
  additional_color_1: '#111827',
  additional_color_2: '#ff4964',
  font: 'Inter',
}
const shell = reactive({ header: '', footer: '', styles: '', theme: { ...defaultTheme } })
const headerElement = ref(null)
const cartStorageKey = 'ecommerce_storefront_cart'
const visitorStorageKey = 'ecommerce_storefront_visitor_id'
const activeTawkWidgetId = ref('')
const themeStyle = computed(() => ({
  '--store-primary': shell.theme.primary_color,
  '--store-secondary': shell.theme.secondary_color,
  '--store-additional-1': shell.theme.additional_color_1,
  '--store-additional-2': shell.theme.additional_color_2,
  '--store-surface': '#f5f5f5',
  '--store-action': shell.theme.additional_color_1 || '#111827',
  '--store-highlight': shell.theme.additional_color_2 || shell.theme.primary_color,
  '--store-ui-accent': shell.theme.secondary_color || '#2563eb',
  '--store-font': `"${shell.theme.font}", ui-sans-serif, system-ui, sans-serif`,
}))

function loadThemeFont(font) {
  const id = 'ecommerce-storefront-font'
  document.getElementById(id)?.remove()
  const family = String(font || '').trim().replace(/\s+/g, ' ')
  if (!/^[A-Za-z0-9][A-Za-z0-9 .&+'-]{0,79}$/.test(family)) return
  const link = document.createElement('link')
  link.id = id
  link.rel = 'stylesheet'
  link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(family).replaceAll('%20', '+')}&display=swap`
  document.head.appendChild(link)
}

function removeTawkWidget() {
  try {
    window.Tawk_API?.hideWidget?.()
    window.Tawk_API?.shutdown?.()
  } catch (_error) {
    // The third-party widget may not have finished loading yet.
  }
  document.getElementById('ecommerce-tawk-widget')?.remove()
  activeTawkWidgetId.value = ''
}

function syncTawkWidget(widgetId) {
  const normalized = String(widgetId || '').trim().replace(/^https?:\/\/embed\.tawk\.to\//i, '').replace(/^\/+|\/+$/g, '')
  if (normalized === activeTawkWidgetId.value) return
  removeTawkWidget()
  if (!/^[A-Za-z0-9_-]{4,100}\/[A-Za-z0-9_-]{1,100}$/.test(normalized)) return

  window.Tawk_API = {}
  window.Tawk_LoadStart = new Date()
  const script = document.createElement('script')
  script.id = 'ecommerce-tawk-widget'
  script.async = true
  script.src = `https://embed.tawk.to/${normalized}`
  script.charset = 'UTF-8'
  script.setAttribute('crossorigin', '*')
  document.head.appendChild(script)
  activeTawkWidgetId.value = normalized
}

function readCart() {
  try {
    const cart = JSON.parse(localStorage.getItem(cartStorageKey) || '[]')
    return Array.isArray(cart) ? cart : []
  } catch (_error) {
    return []
  }
}

function cartItemCount() {
  const websiteId = String(route.params.websiteId || '')
  return readCart()
    .filter(item => String(item.website_id || '') === websiteId)
    .reduce((total, item) => total + Math.max(0, Number(item.quantity || 0)), 0)
}

function findCartLink() {
  const root = headerElement.value
  if (!root) return null

  const explicitLink = root.querySelector(
    '[data-storefront-cart], .ecommerce-storefront-cart, a[href*="/cart"]',
  )
  if (explicitLink) return explicitLink

  return Array.from(root.querySelectorAll('#list-action a, #list-action button')).find(link => {
    const iconPath = link.querySelector('svg path')?.getAttribute('d') || ''
    return iconPath.includes('239.89') || iconPath.includes('120A16')
  }) || null
}

function refreshCartIndicator() {
  const cartLink = findCartLink()
  if (!cartLink) return

  const count = cartItemCount()
  const cartUrl = `/dashboard/store/${encodeURIComponent(String(route.params.websiteId))}/cart`
  if (cartLink.tagName === 'A') cartLink.setAttribute('href', cartUrl)
  else cartLink.dataset.cartUrl = cartUrl
  cartLink.removeAttribute('aria-disabled')
  cartLink.removeAttribute('tabindex')
  cartLink.removeAttribute('target')
  cartLink.removeAttribute('rel')
  cartLink.classList.add('ecommerce-storefront-cart')
  cartLink.dataset.storefrontCart = 'true'
  cartLink.setAttribute('aria-label', `Cart, ${count} item${count === 1 ? '' : 's'}`)

  let badge = cartLink.querySelector(
    '.ecommerce-cart-count, [data-cart-count]',
  )
  if (!badge) {
    badge = Array.from(cartLink.children).find(child => (
      child.tagName === 'SPAN' && /^\s*\d+\s*$/.test(child.textContent || '')
    )) || null
  }
  if (!badge) {
    badge = document.createElement('span')
    badge.setAttribute('aria-hidden', 'true')
    cartLink.appendChild(badge)
  }
  badge.classList.add('ecommerce-cart-count')
  badge.dataset.cartCount = 'true'
  badge.textContent = count > 99 ? '99+' : String(count)
}

function handleCartChange() {
  refreshCartIndicator()
}

function handleCartStorage(event) {
  if (!event.key || event.key === cartStorageKey) refreshCartIndicator()
}

function storefrontVisitorId() {
  let visitorId = localStorage.getItem(visitorStorageKey) || ''
  if (!visitorId) {
    visitorId = globalThis.crypto?.randomUUID?.()
      || `${Date.now()}-${Math.random().toString(36).slice(2)}`
    localStorage.setItem(visitorStorageKey, visitorId)
  }
  return visitorId
}

function trackStorefrontVisit() {
  let source = 'Direct'
  try {
    source = document.referrer
      ? new URL(document.referrer).hostname || 'Direct'
      : 'Direct'
  } catch (_error) {
    source = 'Direct'
  }
  fetch(`${Frappe_URL}/api/method/ecommerce.api.track_storefront_visit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      website_id: String(route.params.websiteId || ''),
      visitor_id: storefrontVisitorId(),
      path: route.fullPath,
      source,
    }),
    keepalive: true,
  }).catch(() => {
    // Analytics must never interrupt the storefront experience.
  })
}

function ensureBuilderStyles() {
  const existing = document.querySelector('script[data-ecommerce-builder-tailwind]')
  if (existing?.dataset.loaded === 'true') return Promise.resolve()
  if (existing) {
    return new Promise(resolve => {
      existing.addEventListener('load', resolve, { once: true })
      existing.addEventListener('error', resolve, { once: true })
    })
  }

  return new Promise(resolve => {
    const script = document.createElement('script')
    script.src = 'https://cdn.tailwindcss.com'
    script.dataset.ecommerceBuilderTailwind = 'true'
    script.addEventListener('load', () => {
      script.dataset.loaded = 'true'
      resolve()
    }, { once: true })
    script.addEventListener('error', resolve, { once: true })
    document.head.appendChild(script)
  })
}

async function loadShell() {
  shell.header = ''
  shell.footer = ''
  shell.styles = ''
  shell.theme = { ...defaultTheme }
  syncTawkWidget('')
  try {
    const params = new URLSearchParams({ website_id: String(route.params.websiteId) })
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_storefront_shell?${params}`,
    )
    const body = await response.json()
    const result = body?.message ?? body
    if (!response.ok || result?.status !== 'success') return
    shell.header = result.data?.header || ''
    shell.footer = result.data?.footer || ''
    shell.styles = result.data?.styles || ''
    shell.theme = { ...defaultTheme, ...(result.data?.theme || {}) }
    syncTawkWidget(result.data?.tawk_widget_id)
    loadThemeFont(shell.theme.font)
    await nextTick()
    refreshCartIndicator()
  } catch (_error) {
    // The storefront content remains usable if no published shell is available.
  }
}

function handleShellNavigation(event) {
  const cartLink = event.target.closest(
    '[data-storefront-cart], .ecommerce-storefront-cart',
  )
  if (cartLink) {
    event.preventDefault()
    router.push({
      name: 'StorefrontCart',
      params: { websiteId: String(route.params.websiteId) },
    })
    return
  }

  const link = event.target.closest('a[href]')
  if (!link) return
  const href = link.getAttribute('href') || ''
  let routePath = ''

  if (href.startsWith('/dashboard/store/')) {
    routePath = href.replace(/^\/dashboard/, '')
  } else {
    // Also support older saved blocks whose storefront links are relative.
    // The shell is trusted builder output, so these known storefront routes
    // should stay inside the currently selected dashboard website.
    let target
    try {
      target = new URL(href, window.location.origin)
    } catch (_error) {
      return
    }
    if (!/^\/(?:product|category|brand|page|cart|checkout)(?:\/|$)/.test(target.pathname)) return
    routePath = `/store/${encodeURIComponent(String(route.params.websiteId))}${target.pathname}${target.search}${target.hash}`
  }

  event.preventDefault()
  router.push(routePath)
}

onMounted(async () => {
  window.addEventListener('ecommerce:cart-updated', handleCartChange)
  window.addEventListener('storage', handleCartStorage)
  window.addEventListener('focus', handleCartChange)
  await ensureBuilderStyles()
  await loadShell()
  trackStorefrontVisit()
})
onBeforeUnmount(() => {
  window.removeEventListener('ecommerce:cart-updated', handleCartChange)
  window.removeEventListener('storage', handleCartStorage)
  window.removeEventListener('focus', handleCartChange)
  document.getElementById('ecommerce-storefront-font')?.remove()
  removeTawkWidget()
})
watch(() => route.params.websiteId, loadShell)
watch(() => route.fullPath, (path, previousPath) => {
  if (path !== previousPath) trackStorefrontVisit()
})
</script>

<style scoped>
.storefront-theme {
  font-family: var(--store-font);
}

.storefront-theme :deep(button),
.storefront-theme :deep(input),
.storefront-theme :deep(select),
.storefront-theme :deep(textarea) {
  font-family: inherit;
}

.storefront-theme :deep(.bg-gray-900) {
  background-color: var(--store-action) !important;
}

.storefront-theme :deep(.bg-gray-50) {
  background-color: var(--store-surface) !important;
}

.storefront-theme :deep(.accent-emerald-700) {
  accent-color: var(--store-ui-accent) !important;
}

.storefront-theme :deep(.focus\:border-emerald-600:focus) {
  border-color: var(--store-ui-accent) !important;
}

/* Blue/theme accents are for ordinary choices; green remains success and red remains error. */
.storefront-theme :deep([data-store-tone='accent']) {
  border-color: var(--store-ui-accent) !important;
  background-color: color-mix(in srgb, var(--store-ui-accent) 10%, white) !important;
  color: var(--store-ui-accent) !important;
}

.storefront-theme :deep([data-store-accent-text]) {
  color: var(--store-ui-accent) !important;
}

.storefront-theme :deep([data-store-selection='active']) {
  border-color: var(--store-ui-accent) !important;
  background-color: color-mix(in srgb, var(--store-ui-accent) 9%, white) !important;
  box-shadow: 0 0 0 1px var(--store-ui-accent) !important;
}

.storefront-theme :deep([data-theme-color='primary']) {
  color: var(--store-primary) !important;
}

.storefront-theme :deep([data-theme-bg='primary']) {
  background-color: var(--store-primary) !important;
}

.storefront-theme :deep([data-theme-bg='secondary']) {
  background-color: var(--store-secondary) !important;
}

.storefront-theme :deep([data-theme-bg='surface']) {
  background-color: var(--store-surface) !important;
}

.storefront-theme :deep([data-theme-bg='accent']) {
  background-color: var(--store-highlight) !important;
}

.storefront-builder-header :deep(input) {
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  outline: none !important;
}

.storefront-builder-header :deep(input:focus) {
  border: 0 !important;
  box-shadow: none !important;
  outline: none !important;
}

.storefront-builder-header :deep(.ecommerce-storefront-cart) {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.storefront-builder-header :deep(.ecommerce-cart-count) {
  position: static;
  display: inline-grid;
  min-width: 1.25rem;
  height: 1.25rem;
  place-items: center;
  margin-left: 0.35rem;
  padding: 0 0.3rem;
  border: 2px solid white;
  border-radius: 9999px;
  background: var(--store-ui-accent);
  color: white;
  font: 700 0.65rem/1 system-ui, sans-serif;
  box-sizing: border-box;
}

.storefront-builder-header :deep(.rt-announcement a) {
  color: white !important;
}

.storefront-builder-header :deep(.rt-nav__actions span) {
  background: var(--store-ui-accent) !important;
}

/* Shared storefront footers use the same color family as the header, not the
   default black action color baked into older templates. */
.storefront-builder-footer {
  --ecommerce-action-background: var(--store-ui-accent);
  --store-action: var(--store-ui-accent);
  --store-role-30: var(--store-ui-accent);
}

.storefront-builder-footer :deep(.rt-footer),
.storefront-builder-footer :deep(.pc-footer) {
  background-color: var(--store-ui-accent) !important;
}
</style>
