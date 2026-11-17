<template>
  <div :class="embedded ? 'flex h-full min-h-0 flex-col' : ''">
    <!-- Header -->
    <div
      v-if="!embedded && !dialogOnly"
      class="bg-white mb-4 flex items-center justify-between p-3"
    >
      <strong class="text-gray-800">Categories</strong>
      <Button
        theme="green"
        variant="solid"
        @click="openCreateCategory"
      >
        + Add Category
      </Button>
    </div>

    <p v-if="feedback && !dialogOnly" class="mb-3 text-sm" :class="feedbackClass">
      {{ feedback }}
    </p>

    <EcommerceCollectionView
      v-if="!dialogOnly"
      :class="embedded ? 'min-h-0 flex-1' : ''"
      title="Categories"
      :items="categoryItems"
      :selected-key="selectedCategoryKey"
      :loading="isLoading"
      create-label="Add New Category"
      short-create-label="Add Category"
      empty-title="Create Your First Category"
      empty-description="Create categories to organize products and make your storefront easier to browse."
      empty-icon="category"
      @create="openCreateCategory"
      @select="selectCategory"
    >
      <template #detail="{ item }">
        <div v-if="item" class="space-y-6">
          <div class="flex items-start gap-4 border-b border-gray-200 pb-5">
            <div
              class="flex h-16 w-16 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-50"
            >
              <img
                v-if="item.categories_logo"
                :src="item.categories_logo"
                :alt="item.categories_name"
                class="h-full w-full object-contain"
              />
              <span v-else class="material-symbols-outlined text-2xl text-green-700">
                category
              </span>
            </div>
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-gray-900">
                  {{ item.categories_name }}
                </h3>
                <StorefrontStatusToggle
                  :status="item.publication_status"
                  :loading="updatingCategoryStatus === String(item.name)"
                  @toggle="toggleCategoryStatus(item)"
                />
              </div>
              <p class="mt-1 text-sm text-gray-500">
                /{{ item.slug || 'no-slug' }}
              </p>
            </div>
            <Button
              class="ml-auto shrink-0"
              theme="green"
              variant="solid"
              @click="editCategory(item)"
            >
              Edit Category
            </Button>
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Category name</p>
              <p class="mt-2 break-words text-sm text-gray-700">{{ item.categories_name || '—' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Slug</p>
              <p class="mt-2 break-all text-sm text-gray-700">{{ item.slug ? `/${item.slug}` : 'No slug added.' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Website</p>
              <p class="mt-2 break-words text-sm text-gray-700">{{ item.website || 'Not assigned' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Parent category</p>
              <p class="mt-2 break-words text-sm text-gray-700">{{ item.parent_category_name || 'Main category' }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Storefront status</p>
              <p class="mt-2 text-sm text-gray-700">{{ statusDescription(item.publication_status) }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">Category logo</p>
              <div class="mt-2 flex h-28 w-36 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-50">
                <img v-if="item.categories_logo" :src="item.categories_logo" :alt="`${item.categories_name} logo`" class="h-full w-full object-contain" />
                <span v-else class="text-sm text-gray-400">No logo</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </EcommerceCollectionView>

    <!-- Dialog for Adding Category -->
    <Dialog v-model="displayCategory.isDisplay" :options="{ size: 'xl' }">
      <template #body>
        <div class="mx-auto max-h-[calc(100dvh-8rem)] max-w-full overflow-y-auto bg-white p-3 sm:p-4">
          <div class="mb-4 border-b border-gray-200 pb-4">
            <h2 class="text-xl font-semibold tracking-tight text-gray-900">{{ editingCategory ? 'Edit category' : 'Add category' }}</h2>
            <p class="mt-1 text-sm text-gray-500">Organize products and control how this category appears in your storefront.</p>
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1.5 block text-sm font-semibold text-gray-700">Category name</label>
              <input v-model="category.name" type="text" placeholder="Enter category name" class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-semibold text-gray-700">Slug</label>
              <input v-model="category.slug" type="text" placeholder="category-url-slug" class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100" />
            </div>
            <div>
              <div class="mb-1.5 flex items-center gap-1.5">
                <label class="text-sm font-semibold text-gray-700">Parent category <span class="font-normal text-gray-400">(optional)</span></label>
                <span class="group/parent-help relative inline-flex" tabindex="0" aria-label="Parent category information">
                  <span class="material-symbols-outlined cursor-help text-base text-gray-400" aria-hidden="true">info</span>
                  <span role="tooltip" class="pointer-events-none absolute bottom-full left-1/2 z-30 mb-2 hidden w-64 -translate-x-1/2 rounded-lg bg-gray-900 px-3 py-2 text-xs font-normal leading-5 text-white shadow-lg group-hover/parent-help:block group-focus/parent-help:block">Choose a parent to display this as a subcategory in the store menu.</span>
                </span>
              </div>
              <select v-model="category.parent_category" class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100">
                <option value="">No parent — main category</option>
                <option v-for="item in availableParentCategories" :key="item.name" :value="item.name">{{ item.categories_name }}</option>
              </select>
            </div>
            <div>
              <div class="mb-1.5 flex items-center gap-1.5">
                <label class="text-sm font-semibold text-gray-700">Storefront status</label>
                <span class="group/category-status-help relative inline-flex" tabindex="0" aria-label="Category status information">
                  <span class="material-symbols-outlined cursor-help text-base text-gray-400" aria-hidden="true">info</span>
                  <span role="tooltip" class="pointer-events-none absolute bottom-full right-0 z-30 mb-2 hidden w-72 rounded-lg bg-gray-900 px-3 py-2 text-xs font-normal leading-5 text-white shadow-lg group-hover/category-status-help:block group-focus/category-status-help:block">Hidden and archived categories and their subcategories are removed from the public storefront.</span>
                </span>
              </div>
              <select v-model="category.publication_status" class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100">
                <option value="Published">Published — show on website</option>
                <option value="Hidden">Hidden — keep for later</option>
                <option value="Archived">Archived — discontinued</option>
              </select>
            </div>
            <div class="md:col-span-2">
              <label class="mb-1.5 block text-sm font-semibold text-gray-700">Icon / logo</label>
              <label class="flex min-h-20 cursor-pointer items-center justify-center gap-4 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 px-4 transition hover:border-green-400 hover:bg-green-50/40">
                <input type="file" accept="image/*" class="sr-only" @change="onFileChange" />
                <img v-if="previewUrl" :src="previewUrl" alt="Category preview" class="h-16 w-16 rounded-lg border bg-white object-contain" />
                <span v-else class="material-symbols-outlined text-3xl text-green-600" aria-hidden="true">add_photo_alternate</span>
                <span><strong class="block text-sm text-gray-800">{{ previewUrl ? 'Replace category image' : 'Add category image' }}</strong><small class="text-xs text-gray-500">Click to browse an image</small></span>
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
            <Button variant="subtle" @click="closeCategoryDialog">
              Cancel
            </Button>
            <Button
              theme="green"
              variant="solid"
              :disabled="isSubmitting"
              @click="submitCategory"
            >
              {{ isSubmitting ? 'Saving...' : editingCategory ? 'Update Category' : 'Save Category' }}
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
import { displayCategory } from '../composables/displayCategory.js'
import EcommerceCollectionView from './EcommerceCollectionView.vue'
import StorefrontStatusToggle from './StorefrontStatusToggle.vue'
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

const category = ref({
  name: '',
  icon: null,
  slug: '',
  parent_category: '',
  publication_status: 'Published',
})

const previewUrl = ref(null)
const editingCategory = ref(null)
const categories = ref([])
const selectedCategoryKey = ref('')
const isLoading = ref(false)
const isSubmitting = ref(false)
const feedback = ref('')
const feedbackType = ref('')
const updatingCategoryStatus = ref('')
const feedbackClass = computed(() =>
  feedbackType.value === 'error' ? 'text-red-600' : 'text-green-700',
)
const categoryItems = computed(() =>
  categories.value.map((item) => ({
    key: item.name,
    title: item.categories_name || item.name,
    status:
      (item.publication_status || 'Published') === 'Published'
        ? 'Published'
        : 'Unpublished',
    subtitle: item.parent_category_name
      ? `${item.publication_status || 'Published'} · Subcategory of ${item.parent_category_name}`
      : `${item.publication_status || 'Published'} · ${item.slug ? `/${item.slug}` : 'Main category'}`,
    image: item.categories_logo,
    raw: item,
  })),
)
const availableParentCategories = computed(() =>
  categories.value.filter(
    (item) => !item.parent_category && item.name !== editingCategory.value?.name,
  ),
)

function openCreateCategory() {
  resetCategoryForm()
  editingCategory.value = null
  displayCategory.isDisplay = true
}

function editCategory(item) {
  resetCategoryForm()
  editingCategory.value = item
  category.value = {
    name: item.categories_name || '',
    icon: null,
    slug: item.slug || '',
    parent_category: item.parent_category || '',
    publication_status: item.publication_status || 'Published',
  }
  previewUrl.value = item.categories_logo || null
  displayCategory.isDisplay = true
}

function closeCategoryDialog() {
  displayCategory.isDisplay = false
  editingCategory.value = null
  resetCategoryForm()
}

function onFileChange(event) {
  const file = event.target.files[0]
  if (file) {
    category.value.icon = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')
const {
  selectItem: selectCategory,
  restoreSelection: restoreCategorySelection,
} = useRoutedCollectionSelection(categories, selectedCategoryKey, 'categories')
function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function submitCategory() {
  if (!category.value.name.trim()) {
    feedback.value = 'Category Name is required.'
    feedbackType.value = 'error'
    return
  }

  isSubmitting.value = true
  feedback.value = ''
  try {
    let iconBase64 = null
    if (category.value.icon) {
      iconBase64 = await fileToBase64(category.value.icon)
    }

    const payload = {
      ...(editingCategory.value ? { name: editingCategory.value.name } : {}),
      categories_name: category.value.name.trim(),
      website_id: JSON.parse(localStorage.getItem('selectedWebsite') || '{}').name || null,
      categories_logo: iconBase64,
      slug: category.value.slug.trim(),
      parent_category: category.value.parent_category || null,
      publication_status: category.value.publication_status || 'Published',
    }

    // console.log('Submitting category:', payload)

    const method = editingCategory.value ? 'update_category' : 'add_category'
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.${method}`,
      {
        method: 'POST',
        headers: apiHeaders(),
        body: JSON.stringify({ doc: JSON.stringify(payload) }),
      },
    )

    const responseData = await response.json().catch(() => ({}))
    const result = responseData?.message ?? responseData
    if (!response.ok || result.status !== 'success') {
      throw new Error(
        result.message || `Unable to save category (HTTP ${response.status})`,
      )
    }

    const wasEditing = Boolean(editingCategory.value)
    const savedId = result.data?.name || editingCategory.value?.name
    displayCategory.isDisplay = false
    feedback.value = result.message || (editingCategory.value ? 'Category updated successfully.' : 'Category created successfully.')
    feedbackType.value = 'success'
    editingCategory.value = null
    resetCategoryForm()
    await fetchCategories()
    if (savedId) selectCategory(savedId)
    if (savedId && !wasEditing) emit('created', savedId)
  } catch (err) {
    console.error('API error:', err)
    feedback.value = err.message || 'Unable to save category.'
    feedbackType.value = 'error'
  } finally {
    isSubmitting.value = false
  }
}

async function fetchCategories() {
  isLoading.value = true
  try {
    const websiteId = JSON.parse(localStorage.getItem('selectedWebsite') || '{}').name
    const websiteQuery = websiteId ? `?website_id=${encodeURIComponent(websiteId)}` : ''
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_categories${websiteQuery}`,
      { method: 'GET', headers: apiHeaders() },
    )
    const responseData = await response.json().catch(() => ({}))
    const result = responseData?.message ?? responseData
    if (!response.ok || result.status !== 'success') {
      throw new Error(
        result.message || `Unable to fetch categories (HTTP ${response.status})`,
      )
    }
    categories.value = Array.isArray(result.data) ? result.data : []
    restoreCategorySelection()
  } catch (err) {
    console.error('Category fetch error:', err)
    categories.value = []
    feedback.value = err.message || 'Unable to fetch categories.'
    feedbackType.value = 'error'
  } finally {
    isLoading.value = false
  }
}

function resetCategoryForm() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  category.value = {
    name: '',
    icon: null,
    slug: '',
    parent_category: '',
    publication_status: 'Published',
  }
  previewUrl.value = null
}

function statusDescription(status) {
  if (status === 'Archived') return 'Archived and unavailable on the storefront.'
  if (status === 'Hidden') return 'Saved for later and currently hidden from customers.'
  return 'Published and visible to customers.'
}

async function toggleCategoryStatus(item) {
  const itemId = String(item.name || '')
  if (!itemId || updatingCategoryStatus.value) return
  const nextStatus = item.publication_status === 'Published' ? 'Hidden' : 'Published'
  updatingCategoryStatus.value = itemId
  feedback.value = ''
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.update_storefront_item_status`,
      {
        method: 'POST',
        headers: apiHeaders(),
        body: JSON.stringify({
          item_type: 'category',
          name: item.name,
          publication_status: nextStatus,
        }),
      },
    )
    const responseData = await response.json().catch(() => ({}))
    const result = responseData?.message ?? responseData
    if (!response.ok || result.status !== 'success') {
      throw new Error(result.message || 'Unable to update category status.')
    }
    item.publication_status = result.data?.publication_status || nextStatus
    await fetchCategories()
  } catch (err) {
    feedback.value = err.message || 'Unable to update category status.'
    feedbackType.value = 'error'
  } finally {
    updatingCategoryStatus.value = ''
  }
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = (error) => reject(error)
  })
}

onMounted(fetchCategories)
watch(
  () => displayCategory.isDisplay,
  (isOpen, wasOpen) => {
    if (wasOpen && !isOpen) emit('closed')
  },
)
defineExpose({ openCreateCategory })
</script>
