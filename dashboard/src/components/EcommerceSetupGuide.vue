<template>
  <section class="overflow-hidden rounded-xl border border-emerald-200 bg-emerald-50/60">
    <div class="overflow-x-auto bg-white px-5 py-5">
      <ol class="mx-auto grid min-w-[720px] max-w-5xl grid-cols-4">
        <li
          v-for="(step, index) in setupSteps"
          :key="step.key"
          class="relative"
        >
          <span
            v-if="index < setupSteps.length - 1"
            class="step-connector"
            :style="{
              backgroundColor: setupSteps[index + 1].complete ? '#059669' : '#e5e7eb',
            }"
            aria-hidden="true"
          />

          <button
            type="button"
            class="group relative z-10 flex w-full flex-col items-center px-3 text-center focus:outline-none"
            @click="runStep(step)"
          >
            <span
              class="flex h-9 w-9 items-center justify-center rounded-full border-2 text-xs font-bold shadow-sm transition-all group-hover:scale-105 group-focus:ring-4 group-focus:ring-emerald-100"
              :style="step.complete
                ? { backgroundColor: '#059669', borderColor: '#059669', color: '#ffffff' }
                : step.key === nextStep.key
                  ? { backgroundColor: '#ffffff', borderColor: '#059669', color: '#047857' }
                  : { backgroundColor: '#ffffff', borderColor: '#d1d5db', color: '#6b7280' }"
            >
              <svg
                v-if="step.complete"
                class="h-5 w-5"
                viewBox="0 0 20 20"
                fill="none"
                aria-hidden="true"
              >
                <path
                  d="m5 10.25 3.1 3.1L15.5 6"
                  stroke="currentColor"
                  stroke-width="2.25"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </span>

            <span
              class="mt-3 block text-sm font-semibold transition-colors group-hover:text-emerald-700"
              :class="step.key === nextStep.key && !step.complete ? 'text-emerald-700' : 'text-gray-900'"
            >
              {{ step.title }}
            </span>
            <span class="mt-1 block max-w-48 text-xs leading-5 text-gray-500">
              {{ step.description }}
            </span>
            <span
              class="mt-2 inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide"
              :class="step.complete
                ? 'bg-emerald-100 text-emerald-700'
                : step.key === nextStep.key
                  ? 'bg-amber-100 text-amber-700'
                  : 'bg-gray-100 text-gray-500'"
            >
              {{ step.complete ? 'Complete' : step.key === nextStep.key ? 'Next step' : 'Pending' }}
            </span>
          </button>
        </li>
      </ol>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const emit = defineEmits(['open-tool'])
const router = useRouter()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token') || ''
const loading = ref(true)
const website = ref(null)
const productCount = ref(0)

function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

function pageHasStoreContent(page) {
  try {
    const value = typeof page?.field_value === 'string'
      ? JSON.parse(page.field_value || '{}')
      : page?.field_value || {}
    return ['header', 'main', 'footer'].some(section => Array.isArray(value[section]) && value[section].length)
  } catch (_error) {
    return false
  }
}

const homePage = computed(() => {
  const pages = website.value?.pages || []
  return pages.find(page => /^(home|home page|homepage)$/i.test(String(page.page || '').trim())) || pages[0] || null
})

const hasStoreContent = computed(() => (website.value?.pages || []).some(pageHasStoreContent))

const setupSteps = computed(() => [
  {
    key: 'store',
    title: 'Store details',
    description: website.value ? website.value.website_link : 'Add your store name, logo and contact details.',
    complete: Boolean(website.value),
    actionLabel: website.value ? 'Review store details' : 'Create your store',
    action: 'website',
  },
  {
    key: 'products',
    title: 'Add products',
    description: productCount.value ? `${productCount.value} product${productCount.value === 1 ? '' : 's'} added.` : 'Add a photo, name, price and stock quantity.',
    complete: productCount.value > 0,
    actionLabel: productCount.value ? 'Manage products' : 'Add your first product',
    action: 'add-product',
  },
  {
    key: 'design',
    title: 'Design your storefront',
    description: hasStoreContent.value ? 'Your homepage has content.' : 'Choose sections and see changes in a live preview.',
    complete: hasStoreContent.value,
    actionLabel: hasStoreContent.value ? 'Edit store design' : 'Design your storefront',
    action: 'design',
  },
  {
    key: 'publish',
    title: 'Preview and publish',
    description: website.value?.status === 'Published' ? 'Your storefront is published.' : 'Review the customer journey before going live.',
    complete: website.value?.status === 'Published',
    actionLabel: website.value?.status === 'Published' ? 'Preview your store' : 'Review and publish',
    action: website.value?.status === 'Published' ? 'preview' : 'design',
  },
])

const nextStep = computed(() => setupSteps.value.find(step => !step.complete) || {
  actionLabel: 'Preview your store',
  action: 'preview',
})

function runStep(step) {
  if (!step) return
  if (step.action === 'add-product') {
    emit('open-tool', 'add-product')
    return
  }
  if (step.action === 'preview' && website.value && homePage.value) {
    const destination = router.resolve({
      name: 'StorefrontPagePreview',
      params: { websiteId: website.value.name, pageId: homePage.value.name },
    })
    window.open(destination.href, '_blank', 'noopener,noreferrer')
    return
  }
  if (step.action === 'design' && homePage.value) {
    router.push({ name: 'WebsitePageEdit', params: { page_name: homePage.value.name } })
    return
  }
  router.push({ name: 'WebsiteHome' })
}

async function loadSetupProgress() {
  loading.value = true
  try {
    const websiteResponse = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_vendor_websites`,
      { headers: apiHeaders() },
    )
    const websiteBody = await websiteResponse.json().catch(() => ({}))
    const websiteResult = websiteBody?.message ?? websiteBody
    const websites = Array.isArray(websiteResult?.data) ? websiteResult.data : []
    const selected = JSON.parse(localStorage.getItem('selectedWebsite') || '{}')
    website.value = websites.find(item => String(item.name) === String(selected.name)) || (websites.length === 1 ? websites[0] : null)

    if (!selected.name && website.value && websites.length === 1) {
      localStorage.setItem('selectedWebsite', JSON.stringify(website.value))
    }
    if (!website.value) return

    const params = new URLSearchParams({ website_id: String(website.value.name) })
    const productResponse = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_products?${params}`,
      { headers: apiHeaders() },
    )
    const productBody = await productResponse.json().catch(() => ({}))
    const productResult = productBody?.message ?? productBody
    productCount.value = Array.isArray(productResult?.data) ? productResult.data.length : 0
  } catch (_error) {
    website.value = null
    productCount.value = 0
  } finally {
    loading.value = false
  }
}

onMounted(loadSetupProgress)
</script>

<style scoped>
.step-connector {
  position: absolute;
  top: 1.1rem;
  left: calc(50% + 1.4rem);
  right: calc(-50% + 1.4rem);
  height: 2px;
}
</style>
