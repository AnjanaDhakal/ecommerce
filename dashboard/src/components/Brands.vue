<template>
  <div :class="embedded ? 'flex h-full min-h-0 flex-col' : ''">
    <!-- Header -->
    <div
      v-if="!embedded && !dialogOnly"
      class="bg-white mb-4 flex items-center justify-between"
    >
      <strong class="text-gray-800">Brands</strong>
      <Button
        theme="green"
        variant="solid"
        @click="openCreateBrand"
      >
        + Add Brand
      </Button>
    </div>

    <p v-if="feedback && !dialogOnly" class="mb-3 text-sm" :class="feedbackClass">
      {{ feedback }}
    </p>

    <EcommerceCollectionView
      v-if="!dialogOnly"
      :class="embedded ? 'min-h-0 flex-1' : ''"
      title="Brands"
      :items="brandItems"
      :selected-key="selectedBrandKey"
      :loading="isLoading"
      create-label="Add New Brand"
      short-create-label="Add Brand"
      empty-title="Create Your First Brand"
      empty-description="Add a brand to organize products and present a consistent identity across your storefront."
      empty-icon="sell"
      @create="openCreateBrand"
      @select="selectBrand"
    >
      <template #detail="{ item }">
        <div v-if="item" class="space-y-6">
          <div class="flex items-start gap-4 border-b border-gray-200 pb-5">
            <div
              class="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-50"
            >
              <img
                v-if="item.brand_logo"
                :src="item.brand_logo"
                :alt="item.brand_name"
                class="h-full w-full object-contain"
              />
              <span v-else class="text-xl font-semibold text-green-700">
                {{ item.brand_name.charAt(0).toUpperCase() }}
              </span>
            </div>
            <div class="min-w-0">
              <h3 class="text-xl font-semibold text-gray-900">
                {{ item.brand_name }}
              </h3>
              <span
                class="mt-2 inline-flex rounded-full px-2.5 py-1 text-xs font-medium"
                :class="item.publication_status === 'Published' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'"
              >
                {{ item.publication_status || 'Published' }}
              </span>
              <p class="mt-1 text-sm text-gray-500">
                {{ item.seo_title || 'No SEO title added' }}
              </p>
            </div>
            <Button
              class="ml-auto shrink-0"
              theme="green"
              variant="solid"
              @click="editBrand(item)"
            >
              Edit Brand
            </Button>
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Brand name</p>
              <p class="mt-2 break-words text-sm text-gray-700">{{ item.brand_name || '—' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Slug</p>
              <p class="mt-2 break-all text-sm text-gray-700">{{ item.slug ? `/${item.slug}` : 'No slug added.' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">SEO title</p>
              <p class="mt-2 break-words text-sm text-gray-700">{{ item.seo_title || 'No SEO title added.' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Website</p>
              <p class="mt-2 break-words text-sm text-gray-700">{{ item.website || 'Not assigned' }}</p>
            </div>
            <div class="sm:col-span-2">
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">SEO description</p>
              <p class="mt-2 whitespace-pre-line break-words text-sm leading-6 text-gray-700">
                {{ item.seo_description || 'No SEO description added.' }}
              </p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Brand logo</p>
              <div class="mt-2 flex h-28 w-36 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-50">
                <img v-if="item.brand_logo" :src="item.brand_logo" :alt="`${item.brand_name} logo`" class="h-full w-full object-contain" />
                <span v-else class="text-sm text-gray-400">No logo</span>
              </div>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">SEO logo</p>
              <div class="mt-2 flex h-28 w-36 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-50">
                <img v-if="item.seo_logo" :src="item.seo_logo" :alt="`${item.brand_name} SEO logo`" class="h-full w-full object-contain" />
                <span v-else class="text-sm text-gray-400">No SEO logo</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </EcommerceCollectionView>

    <!-- Dialog for Adding Brand -->
    <Dialog v-model="displayBrand.isDisplay" :options="{ size: 'xl' }">
      <template #body>
        <div class="mx-auto max-h-[calc(100dvh-8rem)] max-w-full overflow-y-auto bg-white p-3 sm:p-4">
          <div class="mb-4 border-b border-gray-200 pb-4">
            <h2 class="text-xl font-semibold tracking-tight text-gray-900">{{ editingBrand ? 'Edit brand' : 'Add brand' }}</h2>
            <p class="mt-1 text-sm text-gray-500">Create a recognizable storefront identity and search preview.</p>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">

          <!-- Brand Name -->
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">Brand name</label>
            <input
              v-model="brand.name"
              type="text"
              placeholder="Enter brand name"
              class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">Slug</label>
            <input
              v-model="brand.slug"
              type="text"
              placeholder="brand-url-slug"
              class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">Storefront status</label>
            <select
              v-model="brand.publication_status"
              class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
            >
              <option value="Published">Published</option>
              <option value="Hidden">Hidden</option>
              <option value="Archived">Archived</option>
            </select>
          </div>

          <!-- Brand Logo -->
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">Brand logo</label>
            <label class="flex min-h-20 cursor-pointer items-center justify-center gap-4 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 px-4 transition hover:border-green-400 hover:bg-green-50/40">
              <input type="file" accept="image/*" class="sr-only" @change="onLogoChange" />
              <img v-if="previewUrl" :src="previewUrl" alt="Logo preview" class="h-14 w-14 rounded-lg border bg-white object-contain" />
              <span v-else class="material-symbols-outlined text-2xl text-green-600" aria-hidden="true">add_photo_alternate</span>
              <span><strong class="block text-sm text-gray-800">{{ previewUrl ? 'Replace brand logo' : 'Add brand logo' }}</strong><small class="text-xs text-gray-500">Click to browse an image</small></span>
            </label>
          </div>

          <!-- SEO Title -->
          <div class="md:col-span-2">
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">SEO title</label>
            <input
              v-model="brand.seo_title"
              type="text"
              placeholder="Enter SEO title"
              class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"
            />
          </div>

          <!-- SEO Description -->
          <div class="md:col-span-2">
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">SEO description</label>
            <textarea
              v-model="brand.seo_description"
              placeholder="Enter SEO description"
              rows="3"
              class="w-full resize-none rounded-lg border border-gray-300 px-3.5 py-2.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"
            ></textarea>
          </div>

          <!-- SEO Logo -->
          <div class="md:col-span-2">
            <label class="mb-1.5 block text-sm font-semibold text-gray-700">SEO image</label>
            <label class="flex min-h-20 cursor-pointer items-center justify-center gap-4 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 px-4 transition hover:border-green-400 hover:bg-green-50/40">
              <input type="file" accept="image/*" class="sr-only" @change="onSeoLogoChange" />
              <img v-if="previewUrlSeo" :src="previewUrlSeo" alt="SEO image preview" class="h-14 w-20 rounded-lg border bg-white object-contain" />
              <span v-else class="material-symbols-outlined text-2xl text-green-600" aria-hidden="true">add_photo_alternate</span>
              <span><strong class="block text-sm text-gray-800">{{ previewUrlSeo ? 'Replace SEO image' : 'Add SEO image' }}</strong><small class="text-xs text-gray-500">Used when the brand is shared</small></span>
            </label>
          </div>
          </div>

          <p
            v-if="feedbackType === 'error' && feedback"
            class="mb-3 text-sm text-red-600"
          >
            {{ feedback }}
          </p>

          <!-- Buttons -->
          <div class="mt-4 flex justify-end gap-2 border-t border-gray-200 pt-4">
            <Button variant="subtle" @click="closeBrandDialog">
              Cancel
            </Button>
            <Button
              theme="green"
              variant="solid"
              :disabled="isSubmitting"
              @click="submitBrand"
            >
              {{ isSubmitting ? 'Saving...' : editingBrand ? 'Update Brand' : 'Save Brand' }}
            </Button>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { Dialog, Button } from 'frappe-ui'
import { displayBrand } from '../composables/displayBrand.js'
import EcommerceCollectionView from './EcommerceCollectionView.vue'
import { useRoutedCollectionSelection } from '@/composables/useRoutedCollectionSelection'

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
  dialogOnly: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['created', 'closed'])

const brand = ref({
  name: '',
  slug: '',
  logo: null,
  seo_title: '',
  seo_description: '',
  seo_logo: null,
  publication_status: 'Published',
})

const previewUrl = ref(null)
const previewUrlSeo = ref(null)
const editingBrand = ref(null)
const brands = ref([])
const selectedBrandKey = ref('')
const isLoading = ref(false)
const isSubmitting = ref(false)
const feedback = ref('')
const feedbackType = ref('')
const feedbackClass = computed(() =>
  feedbackType.value === 'error' ? 'text-red-600' : 'text-green-700',
)
const brandItems = computed(() =>
  brands.value.map((item) => ({
    key: item.name,
    title: item.brand_name || item.name,
    subtitle: item.seo_title || 'Brand',
    image: item.brand_logo,
    status: item.publication_status || 'Published',
    raw: item,
  })),
)

const token = localStorage.getItem('access_token')
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const {
  selectItem: selectBrand,
  restoreSelection: restoreBrandSelection,
} = useRoutedCollectionSelection(brands, selectedBrandKey, 'brands')

function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

function getApiResult(responseData) {
  return responseData?.message ?? responseData ?? {}
}

function openCreateBrand() {
  resetBrandForm()
  editingBrand.value = null
  displayBrand.isDisplay = true
}

function editBrand(item) {
  resetBrandForm()
  editingBrand.value = item
  brand.value = {
    name: item.brand_name || '',
    slug: item.slug || '',
    logo: null,
    seo_title: item.seo_title || '',
    seo_description: item.seo_description || '',
    seo_logo: null,
    publication_status: item.publication_status || 'Published',
  }
  previewUrl.value = item.brand_logo || null
  previewUrlSeo.value = item.seo_logo || null
  displayBrand.isDisplay = true
}

function closeBrandDialog() {
  displayBrand.isDisplay = false
  editingBrand.value = null
  resetBrandForm()
}

function onLogoChange(event) {
  const file = event.target.files[0]
  if (file) {
    brand.value.logo = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

function onSeoLogoChange(event) {
  const file = event.target.files[0]
  if (file) {
    brand.value.seo_logo = file
    previewUrlSeo.value = URL.createObjectURL(file)
  }
}

async function submitBrand() {
  if (!brand.value.name.trim()) {
    feedback.value = 'Brand Name is required.'
    feedbackType.value = 'error'
    return
  }

  isSubmitting.value = true
  feedback.value = ''

  try {
    // Convert both logos to Base64 if available
    const logoBase64 = brand.value.logo
      ? await fileToBase64(brand.value.logo)
      : null
    const seoLogoBase64 = brand.value.seo_logo
      ? await fileToBase64(brand.value.seo_logo)
      : null

    const payload = {
      ...(editingBrand.value ? { name: editingBrand.value.name } : {}),
      brand_name: brand.value.name.trim(),
      slug: brand.value.slug.trim(),
      website_id: JSON.parse(localStorage.getItem('selectedWebsite') || '{}').name || null,
      brand_logo: logoBase64,
      seo_title: brand.value.seo_title,
      seo_description: brand.value.seo_description,
      seo_logo: seoLogoBase64,
      publication_status: brand.value.publication_status || 'Published',
    }

    // console.log('🧾 Submitting brand:', payload)

    const method = editingBrand.value ? 'update_brand' : 'add_brand'
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.${method}`,
      {
        method: 'POST',
        headers: apiHeaders(),
        body: JSON.stringify({ doc: JSON.stringify(payload) }),
      },
    )

    const responseData = await response.json().catch(() => ({}))
    const result = getApiResult(responseData)
    if (!response.ok || result.status !== 'success') {
      throw new Error(
        result.message || `Unable to save brand (HTTP ${response.status})`,
      )
    }

    const wasEditing = Boolean(editingBrand.value)
    const savedId = result.data?.name || editingBrand.value?.name
    displayBrand.isDisplay = false
    feedback.value = result.message || (editingBrand.value ? 'Brand updated successfully.' : 'Brand created successfully.')
    feedbackType.value = 'success'
    editingBrand.value = null
    resetBrandForm()
    await fetchBrands()
    if (savedId) selectBrand(savedId)
    if (savedId && !wasEditing) emit('created', savedId)
  } catch (err) {
    console.error('❌ API error:', err)
    feedback.value = err.message || 'Unable to save brand.'
    feedbackType.value = 'error'
  } finally {
    isSubmitting.value = false
  }
}

async function fetchBrands() {
  isLoading.value = true
  try {
    const websiteId = JSON.parse(localStorage.getItem('selectedWebsite') || '{}').name
    const websiteQuery = websiteId ? `?website_id=${encodeURIComponent(websiteId)}` : ''
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_brands${websiteQuery}`,
      {
        method: 'GET',
        headers: apiHeaders(),
      },
    )
    const responseData = await response.json().catch(() => ({}))
    const result = getApiResult(responseData)
    if (!response.ok || result.status !== 'success') {
      throw new Error(
        result.message || `Unable to fetch brands (HTTP ${response.status})`,
      )
    }
    brands.value = Array.isArray(result.data) ? result.data : []
    restoreBrandSelection()
  } catch (err) {
    console.error('❌ Brand fetch error:', err)
    brands.value = []
    feedback.value = err.message || 'Unable to fetch brands.'
    feedbackType.value = 'error'
  } finally {
    isLoading.value = false
  }
}

function resetBrandForm() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  if (previewUrlSeo.value) URL.revokeObjectURL(previewUrlSeo.value)
  brand.value = {
    name: '',
    slug: '',
    logo: null,
    seo_title: '',
    seo_description: '',
    seo_logo: null,
    publication_status: 'Published',
  }
  previewUrl.value = null
  previewUrlSeo.value = null
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = (error) => reject(error)
  })
}

onMounted(fetchBrands)
watch(
  () => displayBrand.isDisplay,
  (isOpen, wasOpen) => {
    if (wasOpen && !isOpen) emit('closed')
  },
)
defineExpose({ openCreateBrand })
</script>
