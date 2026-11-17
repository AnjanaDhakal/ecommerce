<template>
  <Dialog
    v-model="displayProduct.isDisplay"
    :options="{ size: '3xl' }"
    class="lg:mt-10"
  >
    <template #body>
      <div class="mx-auto max-h-[calc(100dvh-8rem)] max-w-full overflow-y-auto rounded-lg bg-white p-3 sm:p-4">
        <!-- 🧭 Dialog Header and Step Switcher -->
        <div class="mb-4 flex flex-col gap-4 border-b border-gray-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-xl font-semibold tracking-tight text-gray-900">
              {{ isEditing ? 'Edit product' : 'Add product' }}
            </h2>
            <p class="mt-1 text-sm text-gray-500">
              {{ currentStep === 0 ? 'Add the details customers will see.' : 'Configure pricing, options, and inventory.' }}
            </p>
          </div>
          <div class="inline-flex self-start rounded-xl bg-gray-100 p-1" aria-label="Product form progress">
            <div
              v-for="(step, index) in steps"
              :key="index"
              class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold transition"
              :class="currentStep === index ? 'bg-white text-green-700 shadow-sm' : 'text-gray-400'"
            >
              <span
                class="inline-grid h-5 w-5 place-items-center rounded-full text-[10px]"
                :class="currentStep === index ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-500'"
              >{{ index + 1 }}</span>
              {{ step.title }}
            </div>
          </div>
        </div>

        <!-- 🧾 Step 1: Product Information -->
        <div v-if="currentStep === 0">
          <div class="grid grid-cols-1 gap-4 xl:grid-cols-12">
            <section class="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm xl:col-span-8">
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div class="md:col-span-2">
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Product name <span class="text-red-500">*</span></label>
                  <input v-model="product.name" type="text" required placeholder="Enter product name" class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100" />
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Short description <span class="text-red-500">*</span></label>
                  <textarea v-model="product.description" rows="3" required placeholder="Describe the product briefly" class="w-full resize-none rounded-lg border border-gray-300 px-3.5 py-2.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"></textarea>
                </div>
                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Long description</label>
                  <textarea v-model="product.long_description" rows="3" placeholder="Add specifications or detailed information" class="w-full resize-none rounded-lg border border-gray-300 px-3.5 py-2.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"></textarea>
                </div>
                <div class="md:col-span-2">
                  <div class="mb-1.5 flex items-center gap-1.5">
                    <label class="block text-sm font-semibold text-gray-700">Media</label>
                    <span class="group/media-help relative inline-flex" tabindex="0" aria-label="Product media information">
                      <span class="material-symbols-outlined cursor-help text-base text-gray-400" aria-hidden="true">info</span>
                      <span role="tooltip" class="pointer-events-none absolute bottom-full left-1/2 z-30 mb-2 hidden w-72 -translate-x-1/2 rounded-lg bg-gray-900 px-3 py-2 text-xs font-normal leading-5 text-white shadow-lg group-hover/media-help:block group-focus/media-help:block">Choose multiple images or videos. The first image becomes the main product image.</span>
                    </span>
                  </div>
                  <label class="flex min-h-20 cursor-pointer items-center justify-center gap-3 rounded-xl border-2 border-dashed border-gray-300 bg-gray-50 px-4 text-center transition hover:border-green-400 hover:bg-green-50/40">
                    <input type="file" accept="image/*,video/mp4,video/webm,video/ogg,video/quicktime" multiple class="sr-only" @change="onFileChange" />
                    <span class="material-symbols-outlined text-2xl text-green-600" aria-hidden="true">add_photo_alternate</span>
                    <span><strong class="block text-sm text-gray-800">Add images or videos</strong><small class="text-xs text-gray-500">Click to browse files</small></span>
                  </label>
                  <div v-if="previewUrls.length || videoPreviewUrls.length" class="mt-2 flex max-w-full gap-2 overflow-x-auto pb-1">
                    <img v-for="(imageUrl, index) in previewUrls" :key="imageUrl" :src="imageUrl" :alt="`Product preview ${index + 1}`" class="h-14 w-14 shrink-0 rounded-lg border object-cover" />
                    <video v-for="(videoUrl, index) in videoPreviewUrls" :key="videoUrl" :src="videoUrl" :aria-label="`Product video preview ${index + 1}`" controls muted preload="metadata" class="h-14 w-20 shrink-0 rounded-lg border bg-black object-contain" />
                  </div>
                </div>
              </div>
            </section>

            <aside class="rounded-2xl border border-gray-200 bg-gray-50/70 p-4 xl:col-span-4">
              <h3 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-500">Organization</h3>
              <div class="space-y-4">
                <div>
                  <div class="mb-1.5 flex items-center justify-between gap-3">
                    <label class="text-sm font-semibold text-gray-700">Brand <span class="text-red-500">*</span></label>
                    <button type="button" class="text-xs font-semibold text-green-700 hover:underline" @click="openBrandDialog">+ Create</button>
                  </div>
                  <select v-model="brand.name" required class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100">
                    <option value="" disabled>Select a brand</option>
                    <option v-for="item in brandOptions" :key="item.name" :value="item.name">{{ item.brand_name }}</option>
                  </select>
                </div>

                <div class="relative">
                  <div class="mb-1.5 flex items-center justify-between gap-3">
                    <label class="text-sm font-semibold text-gray-700">Categories <span class="text-red-500">*</span></label>
                    <button type="button" class="text-xs font-semibold text-green-700 hover:underline" @click="openCategoryDialog">+ Create</button>
                  </div>
                  <div v-if="optionsLoading" class="flex h-11 items-center rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-500">Loading categories...</div>
                  <template v-else-if="categoryOptions.length">
                    <button type="button" class="flex h-11 w-full items-center justify-between rounded-lg border border-gray-300 bg-white px-3 text-left text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100" :aria-expanded="categoriesOpen" aria-required="true" @click="categoriesOpen = !categoriesOpen">
                      <span class="truncate" :class="categories.names.length ? 'text-gray-800' : 'text-gray-500'">{{ selectedCategoryLabel }}</span>
                      <span class="material-symbols-outlined ml-2 text-lg text-gray-400" aria-hidden="true">expand_more</span>
                    </button>
                    <div v-if="categoriesOpen" class="absolute left-0 right-0 z-30 mt-1 max-h-48 overflow-y-auto rounded-lg border border-gray-200 bg-white p-1 shadow-xl">
                      <button v-for="item in categoryOptions" :key="item.name" type="button" class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm hover:bg-gray-50" @click="toggleCategory(item.name)">
                        <img v-if="item.categories_logo" :src="item.categories_logo" :alt="item.categories_name" class="h-7 w-7 rounded border border-gray-200 object-contain" />
                        <span class="font-medium text-gray-700">{{ item.categories_name }}</span>
                        <span v-if="categories.names.includes(item.name)" class="material-symbols-outlined ml-auto text-lg text-green-700" aria-label="Selected">check</span>
                      </button>
                    </div>
                  </template>
                  <div v-else class="rounded-lg border border-dashed border-gray-300 bg-white px-4 py-4 text-center"><p class="text-sm font-medium text-gray-700">No categories available</p><p class="mt-1 text-xs text-gray-500">Create a category first.</p></div>
                </div>

                <div>
                  <div class="mb-1.5 flex items-center gap-1.5">
                    <label class="text-sm font-semibold text-gray-700">Storefront status <span class="text-red-500">*</span></label>
                    <span class="group/status-help relative inline-flex" tabindex="0" aria-label="Storefront status information">
                      <span class="material-symbols-outlined cursor-help text-base text-gray-400" aria-hidden="true">info</span>
                      <span role="tooltip" class="pointer-events-none absolute bottom-full right-0 z-30 mb-2 hidden w-72 rounded-lg bg-gray-900 px-3 py-2 text-xs font-normal leading-5 text-white shadow-lg group-hover/status-help:block group-focus/status-help:block">Hidden and archived products remain editable but are removed from customer-facing pages.</span>
                    </span>
                  </div>
                  <select v-model="product.publication_status" required class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100">
                    <option value="Published">Published — show on website</option>
                    <option value="Hidden">Hidden — keep for later</option>
                    <option value="Archived">Archived — discontinued</option>
                  </select>
                </div>
              </div>
            </aside>
          </div>
        </div>

        <!-- 🧭 Step 2: Product Variants & Inventory -->
        <div v-else-if="currentStep === 1">
          <h2 class="sr-only">Variants &amp; Inventory</h2>

          <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
            <label class="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-gray-200 bg-gray-50 p-4 transition hover:border-green-300">
              <span><strong class="block text-sm text-gray-800">Product variants</strong><small class="mt-1 block text-xs text-gray-500">Add options such as size, color, or storage.</small></span>
              <input type="checkbox" v-model="variant.hasVariants" class="sr-only peer" />
              <span class="relative h-6 w-11 shrink-0 rounded-full bg-gray-300 transition peer-checked:bg-green-500">
                <span class="absolute left-[2px] top-[2px] h-5 w-5 rounded-full bg-white shadow-sm transition-transform" :class="{ 'translate-x-5': variant.hasVariants }"></span>
              </span>
            </label>
            <label class="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-gray-200 bg-gray-50 p-4 transition hover:border-green-300">
              <span><strong class="block text-sm text-gray-800">Continue selling</strong><small class="mt-1 block text-xs text-gray-500">Allow checkout when inventory reaches zero.</small></span>
              <input type="checkbox" v-model="stock.hasStock" class="sr-only peer" />
              <span class="relative h-6 w-11 shrink-0 rounded-full bg-gray-300 transition peer-checked:bg-green-500">
                <span class="absolute left-[2px] top-[2px] h-5 w-5 rounded-full bg-white shadow-sm transition-transform" :class="{ 'translate-x-5': stock.hasStock }"></span>
              </span>
            </label>
          </div>

          <!-- ✅ Variant Management -->
          <transition name="fade">
            <div v-if="variant.hasVariants" class="mt-4 space-y-4">
              <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
                <div class="flex flex-wrap items-end gap-3">
                  <label class="min-w-64 flex-1 text-sm font-semibold text-gray-700">
                    New option name
                    <input
                      v-model.trim="newAttributeName"
                      type="text"
                      placeholder="e.g., Storage, RAM, Band material"
                      class="mt-1.5 h-10 w-full rounded-lg border border-gray-300 px-3 font-normal outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
                      @keyup.enter="addAttributeGroup"
                    />
                  </label>
                  <button
                    type="button"
                    class="h-10 rounded-lg bg-gray-900 px-4 text-sm font-semibold text-white transition hover:bg-black"
                    @click="addAttributeGroup"
                  >
                    + Add option
                  </button>
                </div>
              </div>

              <div
                v-if="variant.attributes.length"
                ref="optionsScrollRef"
                class="flex max-w-full snap-x snap-mandatory gap-3 overflow-x-auto pb-2"
              >
                <section
                  v-for="(attribute, attributeIndex) in variant.attributes"
                  :key="attribute.id"
                  class="w-[min(28rem,85vw)] shrink-0 snap-start rounded-xl border border-gray-200 bg-gray-50/70 p-4"
                >
                  <div class="flex items-center justify-between gap-3">
                    <input
                      v-model.trim="attribute.name"
                      type="text"
                      aria-label="Option name"
                      class="min-w-0 flex-1 border-0 bg-transparent p-0 font-bold text-gray-800 outline-none focus:ring-0"
                    />
                    <button type="button" class="rounded-md px-2 py-1 text-xs font-semibold text-red-600 transition hover:bg-red-50" @click="removeAttributeGroup(attributeIndex)">
                      Remove
                    </button>
                  </div>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <span
                      v-for="(value, valueIndex) in attribute.values"
                      :key="`${attribute.id}-${value}`"
                      class="inline-flex items-center rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-gray-700 shadow-sm ring-1 ring-gray-200"
                    >
                      {{ value }}
                      <button type="button" class="ml-2 text-red-500" :aria-label="`Remove ${value}`" @click="removeAttributeValue(attributeIndex, valueIndex)">✕</button>
                    </span>
                    <button
                      v-for="suggestion in availableAttributeSuggestions(attribute)"
                      :key="`${attribute.id}-suggestion-${suggestion}`"
                      type="button"
                      class="rounded-full border border-dashed border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-500 hover:border-green-400 hover:text-green-700"
                      @click="addSuggestedAttributeValue(attributeIndex, suggestion)"
                    >
                      + {{ suggestion }}
                    </button>
                    <input
                      v-model.trim="attribute.newValue"
                      type="text"
                      :placeholder="`Add ${attribute.name || 'option'} value`"
                      class="min-w-44 flex-1 rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
                      @keyup.enter="addAttributeValue(attributeIndex)"
                      @blur="addAttributeValue(attributeIndex)"
                    />
                  </div>
                </section>
              </div>

              <!-- Responsive variant cards -->
              <div v-if="generatedVariants.length" class="space-y-3">
                <article v-for="(item, index) in generatedVariants" :key="index" class="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
                  <div class="mb-4 flex flex-wrap items-center justify-between gap-3 border-b border-gray-100 pb-3">
                    <div><p class="text-xs font-semibold uppercase tracking-wider text-gray-400">Variant {{ index + 1 }}</p><h3 class="mt-1 font-semibold text-gray-900">{{ item.name }}</h3></div>
                    <div class="flex items-center gap-2">
                      <img v-if="item.image" :src="item.image" :alt="`${item.name} variant`" class="h-9 w-9 rounded-lg border bg-gray-50 object-contain" />
                      <select v-model="item.image" class="h-9 rounded-lg border border-gray-300 bg-white px-2 text-xs outline-none focus:border-green-500">
                        <option value="">Main image</option>
                        <option v-for="(imageUrl, imageIndex) in previewUrls" :key="`${imageUrl}-${imageIndex}`" :value="imageUrl">Image {{ imageIndex + 1 }}</option>
                      </select>
                    </div>
                  </div>
                  <div class="grid grid-cols-2 gap-3 md:grid-cols-4 xl:grid-cols-7">
                    <label v-for="field in variantFields" :key="field.key" class="text-xs font-semibold text-gray-500">
                      {{ field.label }}
                      <input v-model.number="item[field.key]" :type="field.type" class="mt-1.5 h-10 w-full rounded-lg border border-gray-300 px-3 text-sm font-normal text-gray-900 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100" />
                    </label>
                  </div>
                </article>
              </div>
            </div>
          </transition>
        </div>

        <p v-if="error" class="mt-5 text-sm text-red-600">{{ error }}</p>

        <!-- 🧭 Navigation Buttons -->
        <div class="mt-4 flex justify-between border-t border-gray-200 pt-4">
          <Button
            variant="subtle"
            :disabled="currentStep === 0"
            @click="prevStep"
          >
            Previous
          </Button>

          <Button
            v-if="currentStep < steps.length - 1"
            theme="green"
            variant="solid"
            @click="nextStep"
          >
            Next
          </Button>

          <Button
            v-else
            theme="green"
            variant="solid"
            :disabled="isSubmitting"
            @click="submitForm"
          >
            {{ isSubmitting ? 'Saving...' : isEditing ? 'Update Product' : 'Create Product' }}
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
  <Brands ref="brandDialogRef" dialog-only @created="handleBrandCreated" @closed="restoreProductDialog" />
  <Catagories ref="categoryDialogRef" dialog-only @created="handleCategoryCreated" @closed="restoreProductDialog" />
</template>

<script setup>
import { Dialog, Button } from 'frappe-ui'
import { displayProduct } from '../composables/displayProduct.js'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import Brands from './Brands.vue'
import Catagories from './Catagories.vue'

const props = defineProps({
  productToEdit: { type: Object, default: null },
})
const emit = defineEmits([
  'product-created',
  'product-updated',
  'brand-created',
  'category-created',
  'closed',
])
const isEditing = computed(() => Boolean(props.productToEdit?.name || props.productToEdit?.id))

const brandDialogRef = ref(null)
const categoryDialogRef = ref(null)
const relatedDialogOpen = ref(false)
const returnToProductAfterRelatedDialog = ref(false)

async function openBrandDialog() {
  relatedDialogOpen.value = true
  returnToProductAfterRelatedDialog.value = true
  displayProduct.isDisplay = false
  await nextTick()
  brandDialogRef.value?.openCreateBrand()
}

async function openCategoryDialog() {
  relatedDialogOpen.value = true
  returnToProductAfterRelatedDialog.value = true
  displayProduct.isDisplay = false
  await nextTick()
  categoryDialogRef.value?.openCreateCategory()
}

async function restoreProductDialog() {
  if (!relatedDialogOpen.value) return
  if (returnToProductAfterRelatedDialog.value && !displayProduct.isDisplay) {
    displayProduct.isDisplay = true
    await nextTick()
  }
  relatedDialogOpen.value = false
  returnToProductAfterRelatedDialog.value = false
}

async function openStandaloneCategoryDialog() {
  relatedDialogOpen.value = true
  returnToProductAfterRelatedDialog.value = false
  displayProduct.isDisplay = false
  await nextTick()
  categoryDialogRef.value?.openCreateCategory()
}

async function openStandaloneBrandDialog() {
  relatedDialogOpen.value = true
  returnToProductAfterRelatedDialog.value = false
  displayProduct.isDisplay = false
  await nextTick()
  brandDialogRef.value?.openCreateBrand()
}

async function handleBrandCreated(savedId) {
  await fetchOptions()
  if (savedId && brandOptions.value.some(item => item.name === savedId)) {
    brand.value.name = savedId
  }
  emit('brand-created', savedId)
}

async function handleCategoryCreated(savedId) {
  await fetchOptions()
  if (savedId && categoryOptions.value.some(item => item.name === savedId)) {
    if (!categories.value.names.includes(savedId)) categories.value.names.push(savedId)
  }
  emit('category-created', savedId)
}

defineExpose({ openStandaloneBrandDialog, openStandaloneCategoryDialog })

// Variant structure
const variant = ref({
  hasVariants: false,
  attributes: defaultVariantAttributes(),
})

const stock = ref({
  hasStock: false, // false = don't sell when out of stock
})

// For text inputs
const newAttributeName = ref('')
const generatedVariants = ref([])
const isHydrating = ref(false)
const optionsScrollRef = ref(null)

function attributeId() {
  return `attribute-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}

function defaultSuggestions(name) {
  const normalized = String(name || '').trim().toLowerCase()
  if (normalized === 'size') return ['XS', 'XL', 'Free']
  if (normalized === 'color' || normalized === 'colour') return ['Cream', 'Rust', 'Olive']
  return []
}

function defaultVariantAttributes() {
  return [
    { id: attributeId(), name: 'Size', values: ['S', 'M', 'L'], suggestions: defaultSuggestions('Size'), newValue: '' },
    { id: attributeId(), name: 'Colour', values: ['Indigo', 'Black'], suggestions: defaultSuggestions('Colour'), newValue: '' },
  ]
}

function addAttributeGroup() {
  const name = newAttributeName.value.trim()
  if (!name) return
  if (variant.value.attributes.some(attribute => attribute.name.toLowerCase() === name.toLowerCase())) {
    newAttributeName.value = ''
    return
  }
  variant.value.attributes.unshift({
    id: attributeId(),
    name,
    values: [],
    suggestions: defaultSuggestions(name),
    newValue: '',
  })
  newAttributeName.value = ''
  nextTick(() => {
    optionsScrollRef.value?.scrollTo({ left: 0, behavior: 'smooth' })
  })
}

function removeAttributeGroup(index) {
  variant.value.attributes.splice(index, 1)
}

function addAttributeValue(attributeIndex) {
  const attribute = variant.value.attributes[attributeIndex]
  const value = attribute?.newValue?.trim()
  if (!attribute || !value) return
  if (!attribute.values.some(existing => existing.toLowerCase() === value.toLowerCase())) {
    attribute.values.push(value)
  }
  attribute.newValue = ''
}

function removeAttributeValue(attributeIndex, valueIndex) {
  variant.value.attributes[attributeIndex]?.values.splice(valueIndex, 1)
}

function availableAttributeSuggestions(attribute) {
  return (attribute.suggestions || []).filter(suggestion => (
    !attribute.values.some(value => value.toLowerCase() === suggestion.toLowerCase())
  ))
}

function addSuggestedAttributeValue(attributeIndex, suggestion) {
  const attribute = variant.value.attributes[attributeIndex]
  if (!attribute || attribute.values.some(value => value.toLowerCase() === suggestion.toLowerCase())) return
  attribute.values.push(suggestion)
}

function variantCombinations(attributes) {
  const usable = attributes.filter(attribute => attribute.name.trim() && attribute.values.length)
  if (!usable.length) return []
  return usable.reduce(
    (combinations, attribute) => combinations.flatMap(combination => (
      attribute.values.map(value => [...combination, { name: attribute.name.trim(), value }])
    )),
    [[]],
  )
}

function variantName(attributes) {
  return attributes.map(attribute => `${attribute.name}: ${attribute.value}`).join(' / ')
}

// 🧮 Watch for changes and auto-generate combinations
watch(
  () => variant.value.attributes,
  () => {
    if (isHydrating.value) return
    const previous = new Map(
      generatedVariants.value.map(item => [item.name, { ...item }]),
    )
    generatedVariants.value = variantCombinations(variant.value.attributes).map(attributes => {
      const name = variantName(attributes)
      return previous.get(name) || makeVariant(name)
    })
  },
  { deep: true },
)

function makeVariant(name) {
  return {
    name,
    image: '',
    discounted_price: 0,
    selling_price: 0,
    cost_price: 0,
    weight: 0,
    volumne: 0,
    quantity: 0,
    sku: '',
  }
}

// 🧭 Step definitions
const steps = [{ title: 'Product Information' }, { title: 'Product Variant' }]
const variantFields = [
  { key: 'cost_price', label: 'Cost price', type: 'number' },
  { key: 'selling_price', label: 'Selling price', type: 'number' },
  { key: 'discounted_price', label: 'Discounted price', type: 'number' },
  { key: 'quantity', label: 'Stock quantity', type: 'number' },
  { key: 'weight', label: 'Weight', type: 'number' },
  { key: 'volumne', label: 'Volume', type: 'number' },
  { key: 'sku', label: 'SKU', type: 'text' },
]

const currentStep = ref(0)

// 🧩 Reactive form data
const brand = ref({ name: '' })
const categories = ref({ names: [] })
const categoriesOpen = ref(false)
const product = ref({
  name: '',
  description: '',
  long_description: '',
  images: [],
  videos: [],
  publication_status: 'Published',
})
const previewUrls = ref([])
const videoPreviewUrls = ref([])
const brandOptions = ref([])
const categoryOptions = ref([])
const optionsLoading = ref(false)
const isSubmitting = ref(false)
const error = ref('')
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')

const selectedCategoryLabel = computed(() => {
  if (!categories.value.names.length) return 'Select categories'
  const selectedNames = categoryOptions.value
    .filter(item => categories.value.names.includes(item.name))
    .map(item => item.categories_name)
  return selectedNames.length ? selectedNames.join(', ') : 'Select categories'
})

function toggleCategory(categoryName) {
  const selected = categories.value.names
  const index = selected.indexOf(categoryName)
  if (index === -1) selected.push(categoryName)
  else selected.splice(index, 1)
}

function apiHeaders() {
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

// 🧭 Step navigation
function nextStep() {
  if (validateStep()) currentStep.value++
}

function prevStep() {
  currentStep.value--
}

// ✅ Validation
function validateStep() {
  if (currentStep.value === 0) {
    const requiredFields = [
      [product.value.name, 'Product Name'],
      [brand.value.name, 'Brand'],
      [categories.value.names.length, 'Categories'],
      [product.value.publication_status, 'Storefront Status'],
      [product.value.description, 'Product Description'],
    ]
    const missingFields = requiredFields
      .filter(([value]) => !String(value || '').trim())
      .map(([, label]) => label)

    if (missingFields.length) {
      error.value = `Please complete the required fields: ${missingFields.join(', ')}.`
      return false
    }
  }
  error.value = ''
  return true
}

// 📸 Product media preview
function onFileChange(e) {
  const files = Array.from(e.target.files || [])
  const newImages = files.filter(file => file.type.startsWith('image/'))
  const newVideos = files.filter(file => file.type.startsWith('video/'))
  product.value.images.push(...newImages)
  product.value.videos.push(...newVideos)
  previewUrls.value.push(...newImages.map(file => URL.createObjectURL(file)))
  videoPreviewUrls.value.push(...newVideos.map(file => URL.createObjectURL(file)))
  e.target.value = ''
}

async function fetchOptions() {
  optionsLoading.value = true
  try {
    const selectedWebsite = JSON.parse(localStorage.getItem('selectedWebsite') || '{}')
    if (!selectedWebsite.name) {
      brandOptions.value = []
      categoryOptions.value = []
      return
    }
    const websiteQuery = `?website_id=${encodeURIComponent(selectedWebsite.name)}`
    const [brandResponse, categoryResponse] = await Promise.all([
      fetch(`${Frappe_URL}/api/method/ecommerce.api.get_brands${websiteQuery}`, {
        headers: apiHeaders(),
      }),
      fetch(`${Frappe_URL}/api/method/ecommerce.api.get_categories${websiteQuery}`, {
        headers: apiHeaders(),
      }),
    ])
    const [brandData, categoryData] = await Promise.all([
      brandResponse.json(),
      categoryResponse.json(),
    ])
    const brandResult = brandData?.message ?? brandData
    const categoryResult = categoryData?.message ?? categoryData
    brandOptions.value = Array.isArray(brandResult?.data) ? brandResult.data : []
    categoryOptions.value = Array.isArray(categoryResult?.data)
      ? categoryResult.data
      : []
  } catch (err) {
    console.error('Product option fetch error:', err)
  } finally {
    optionsLoading.value = false
  }
}

async function submitForm() {
  if (!validateStep()) return

  isSubmitting.value = true
  error.value = ''
  try {
    const productImages = await Promise.all(
      product.value.images.map(fileToBase64),
    )
    const productVideos = await Promise.all(
      product.value.videos.map(fileToBase64),
    )
    const payload = {
      ...(isEditing.value ? { name: props.productToEdit.name || props.productToEdit.id } : {}),
      product_name: product.value.name.trim(),
      brand: brand.value.name || null,
      website_id: JSON.parse(localStorage.getItem('selectedWebsite') || '{}').name || null,
      categories: categories.value.names,
      catagories: categories.value.names[0] || null,
      product_description: product.value.description,
      long_description: product.value.long_description,
      enable: variant.value.hasVariants,
      varient: variant.value.hasVariants
        ? generatedVariants.value.map(item => {
            const imageIndex = previewUrls.value.indexOf(item.image)
            return {
              ...item,
              image: imageIndex >= 0 ? '' : (item.image || ''),
              variant_image_index: imageIndex >= 0 ? imageIndex : null,
            }
          })
        : [],
      continue_selling: stock.value.hasStock,
      publication_status: product.value.publication_status || 'Published',
    }
    if (productImages.length) {
      payload.product_image = productImages[0]
      payload.gallery_images = productImages.slice(1)
    }
    if (productVideos.length) payload.product_videos = productVideos
    const method = isEditing.value ? 'update_product' : 'add_product'
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
        result.message || `Unable to save product (HTTP ${response.status})`,
      )
    }

    const wasEditing = isEditing.value
    resetForm()
    displayProduct.isDisplay = false
    emit(wasEditing ? 'product-updated' : 'product-created', result.data)
  } catch (err) {
    console.error('Product API error:', err)
    error.value = err.message || 'Unable to save product.'
  } finally {
    isSubmitting.value = false
  }
}

function fileToBase64(file) {
  if (typeof file === 'string') return Promise.resolve(file)
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
  })
}

function resetForm() {
  previewUrls.value.forEach(imageUrl => URL.revokeObjectURL(imageUrl))
  videoPreviewUrls.value.forEach(videoUrl => URL.revokeObjectURL(videoUrl))
  product.value = {
    name: '',
    description: '',
    long_description: '',
    images: [],
    videos: [],
    publication_status: 'Published',
  }
  brand.value.name = ''
  categories.value.names = []
  variant.value = {
    hasVariants: false,
    attributes: defaultVariantAttributes(),
  }
  newAttributeName.value = ''
  stock.value.hasStock = false
  generatedVariants.value = []
  currentStep.value = 0
  previewUrls.value = []
  videoPreviewUrls.value = []
}

async function hydrateEditForm(item) {
  if (!item) return
  isHydrating.value = true
  product.value = {
    name: item.product_name || '',
    description: item.product_description || item.description || '',
    long_description: item.long_description || '',
    images: Array.isArray(item.images)
      ? [...item.images]
      : [item.product_image].filter(Boolean),
    videos: Array.isArray(item.videos) ? [...item.videos] : [],
    publication_status: item.publication_status || 'Published',
  }
  brand.value.name = item.brand || ''
  categories.value.names = Array.isArray(item.category_ids)
    ? [...item.category_ids]
    : item.category
      ? [String(item.category)]
      : []
  variant.value.hasVariants = Boolean(item.enable)
  stock.value.hasStock = Boolean(item.continue_selling)
  const existingVariants = (item.variant || item.varient || []).map(value => ({
    name: value.variant_name || value.name || '',
    image: value.image || value.variant_image || '',
    discounted_price: Number(value.discounted_price ?? 0),
    selling_price: Number(value.selling_price ?? 0),
    cost_price: Number(value.cost_price ?? 0),
    weight: Number(value.weight ?? 0),
    volumne: Number(value.volume ?? value.volumne ?? 0),
    quantity: Number(value.quantity ?? 0),
    sku: value.sku || '',
  }))
  const attributeGroups = new Map()
  existingVariants.forEach(value => {
    String(value.name || '').split('/').forEach((rawPart, partIndex) => {
      const part = rawPart.trim()
      if (!part) return
      const separator = part.indexOf(':')
      const name = separator > 0
        ? part.slice(0, separator).trim()
        : (partIndex === 0 ? 'Color' : partIndex === 1 ? 'Size' : `Option ${partIndex + 1}`)
      const optionValue = separator > 0 ? part.slice(separator + 1).trim() : part
      if (!name || !optionValue) return
      const key = name.toLowerCase()
      const group = attributeGroups.get(key) || {
        id: attributeId(),
        name,
        values: [],
        suggestions: defaultSuggestions(name),
        newValue: '',
      }
      if (!group.values.some(existing => existing.toLowerCase() === optionValue.toLowerCase())) {
        group.values.push(optionValue)
      }
      attributeGroups.set(key, group)
    })
  })
  variant.value.attributes = [...attributeGroups.values()]
  generatedVariants.value = existingVariants
  previewUrls.value = [...product.value.images]
  videoPreviewUrls.value = [...product.value.videos]
  currentStep.value = 0
  await nextTick()
  isHydrating.value = false
}

onMounted(fetchOptions)

watch(
  () => displayProduct.isDisplay,
  (isOpen) => {
    if (relatedDialogOpen.value) return
    if (isOpen) {
      fetchOptions()
      if (props.productToEdit) hydrateEditForm(props.productToEdit)
      else resetForm()
    } else {
      emit('closed')
    }
  },
)

watch(
  () => props.productToEdit,
  item => {
    if (displayProduct.isDisplay && item) hydrateEditForm(item)
  },
)
</script>
