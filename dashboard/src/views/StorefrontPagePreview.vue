<template>
  <main class="min-h-screen bg-white">
    <div v-if="loading" class="flex min-h-screen items-center justify-center">
      <p class="text-sm font-medium text-gray-500">Loading page preview…</p>
    </div>

    <div v-else-if="error" class="flex min-h-screen flex-col items-center justify-center px-6 text-center">
      <h1 class="text-3xl font-bold text-gray-900">Preview unavailable</h1>
      <p class="mt-3 text-gray-500">{{ error }}</p>
    </div>

    <iframe
      v-else
      ref="previewFrame"
      :srcdoc="previewHtml"
      title="Storefront page preview"
      class="block h-screen w-full border-0"
      sandbox="allow-forms allow-modals allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"
      @load="handlePreviewFrameLoad"
    />
  </main>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const loading = ref(true)
const error = ref('')
const previewHtml = ref('')
const previewFrame = ref(null)
const cartStorageKey = 'ecommerce_storefront_cart'
const visitorStorageKey = 'ecommerce_storefront_visitor_id'
const guardedFrameDocuments = new WeakSet()

function removeTawkWidget() {
  try {
    window.Tawk_API?.hideWidget?.()
    window.Tawk_API?.shutdown?.()
  } catch (_error) {
    // The third-party widget may not have finished loading yet.
  }
  document.getElementById('ecommerce-tawk-widget')?.remove()
}

function injectTawkWidget(widgetId) {
  const normalized = String(widgetId || '').trim().replace(/^https?:\/\/embed\.tawk\.to\//i, '').replace(/^\/+|\/+$/g, '')
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
}

async function loadStorefrontPlugins() {
  try {
    const websiteId = encodeURIComponent(String(route.params.websiteId || ''))
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_storefront_shell?website_id=${websiteId}`,
    )
    const body = await response.json().catch(() => ({}))
    const result = body?.message ?? body
    if (response.ok && result?.status === 'success') {
      injectTawkWidget(result.data?.tawk_widget_id)
    }
  } catch (_error) {
    // Optional integrations must not prevent the page preview from loading.
  }
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

function handlePreviewNavigation(event) {
  const cartControl = event.target?.closest?.(
    '[data-storefront-cart], .ecommerce-storefront-cart',
  )
  if (cartControl) {
    event.preventDefault()
    event.stopImmediatePropagation()
    router.push({
      name: 'StorefrontCart',
      params: { websiteId: String(route.params.websiteId) },
    })
    return
  }

  const link = event.target?.closest?.('a')
  if (!link) return
  const href = String(link.getAttribute('href') || '').trim()
  if (
    link.getAttribute('aria-disabled') === 'true' ||
    !href ||
    href.startsWith('#')
  ) {
    event.preventDefault()
    event.stopImmediatePropagation()
    return
  }

  let target
  try {
    target = new URL(href, window.location.origin)
  } catch (_error) {
    return
  }
  if (
    /\/(?:dashboard\/)?store\/[^/]+\/cart\/?$/.test(target.pathname) ||
    /\/storefront\/cart\/?$/.test(target.pathname)
  ) {
    event.preventDefault()
    event.stopImmediatePropagation()
    router.push({
      name: 'StorefrontCart',
      params: { websiteId: String(route.params.websiteId) },
    })
  }
}

function handlePreviewFrameLoad() {
  try {
    const frameDocument = previewFrame.value?.contentDocument
    if (frameDocument && !guardedFrameDocuments.has(frameDocument)) {
      frameDocument.addEventListener(
        'click',
        handlePreviewNavigation,
        true,
      )
      guardedFrameDocuments.add(frameDocument)
    }
  } catch (_error) {
    // The preview remains readable if iframe access is restricted.
  }
  refreshPreviewCartIndicator()
}

function cartItemCount() {
  try {
    const cart = JSON.parse(localStorage.getItem(cartStorageKey) || '[]')
    if (!Array.isArray(cart)) return 0
    const websiteId = String(route.params.websiteId || '')
    return cart
      .filter(item => String(item.website_id || '') === websiteId)
      .reduce(
        (total, item) => total + Math.max(0, Number(item.quantity || 0)),
        0,
      )
  } catch (_error) {
    return 0
  }
}

function refreshPreviewCartIndicator() {
  try {
    const frameDocument = previewFrame.value?.contentDocument
    let cartLink = frameDocument?.querySelector(
      '[data-storefront-cart], .ecommerce-storefront-cart, a[href*="/cart"]',
    )
    if (!cartLink) {
      cartLink = Array.from(
        frameDocument?.querySelectorAll('#list-action a, #list-action button') || [],
      ).find(link => {
        const iconPath = link.querySelector('svg path')?.getAttribute('d') || ''
        return iconPath.includes('239.89') || iconPath.includes('120A16')
      })
    }
    if (!cartLink) return

    const count = cartItemCount()
    const cartUrl = `/dashboard/store/${encodeURIComponent(String(route.params.websiteId))}/cart`
    if (cartLink.tagName === 'A') cartLink.setAttribute('href', cartUrl)
    else cartLink.dataset.cartUrl = cartUrl
    cartLink.removeAttribute('aria-disabled')
    cartLink.removeAttribute('tabindex')
    cartLink.classList.add('ecommerce-storefront-cart')
    cartLink.dataset.storefrontCart = 'true'
    cartLink.setAttribute(
      'aria-label',
      `Cart, ${count} item${count === 1 ? '' : 's'}`,
    )
    let badge = cartLink.querySelector(
      '.ecommerce-cart-count, [data-cart-count]',
    )
    if (!badge) {
      badge = frameDocument.createElement('span')
      badge.setAttribute('aria-hidden', 'true')
      cartLink.appendChild(badge)
    }
    badge.classList.add('ecommerce-cart-count')
    badge.dataset.cartCount = 'true'
    badge.textContent = count > 99 ? '99+' : String(count)
  } catch (_error) {
    // A restricted iframe can still display the page without cart decoration.
  }
}

function handleCartStorage(event) {
  if (!event.key || event.key === cartStorageKey) refreshPreviewCartIndicator()
}

async function loadPublishedPreview() {
  const token = localStorage.getItem('access_token') || ''
  const pageId = encodeURIComponent(String(route.params.pageId))
  const response = await fetch(
    `${Frappe_URL}/api/method/ecommerce.api.get_page_preview?page_name=${pageId}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    },
  )
  const body = await response.json()
  const result = body?.message
  if (!response.ok || result?.status !== 'success') {
    throw new Error(result?.message || 'Unable to load this page preview.')
  }
  return result?.data?.preview || result?.data?.block_render || ''
}

onMounted(async () => {
  window.addEventListener('ecommerce:cart-updated', refreshPreviewCartIndicator)
  window.addEventListener('storage', handleCartStorage)
  window.addEventListener('focus', refreshPreviewCartIndicator)
  loadStorefrontPlugins()
  trackStorefrontVisit()
  try {
    const previewKey = String(route.query.preview_key || '')
    if (previewKey) {
      previewHtml.value = localStorage.getItem(previewKey) || ''
      localStorage.removeItem(previewKey)
      await router.replace({
        name: 'StorefrontPagePreview',
        params: {
          websiteId: route.params.websiteId,
          pageId: route.params.pageId,
        },
      })
    }
    if (!previewHtml.value) previewHtml.value = await loadPublishedPreview()
    if (!previewHtml.value) throw new Error('No rendered preview is available.')
  } catch (exception) {
    error.value = exception?.message || 'Unable to load this page preview.'
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('ecommerce:cart-updated', refreshPreviewCartIndicator)
  window.removeEventListener('storage', handleCartStorage)
  window.removeEventListener('focus', refreshPreviewCartIndicator)
  removeTawkWidget()
})
</script>
