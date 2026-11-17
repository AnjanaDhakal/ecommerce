<template>
  <main class="flex-1 bg-gray-50 text-gray-900">
    <div class="mx-auto max-w-7xl px-5 py-10 sm:px-8">
      <div v-if="loading" class="flex min-h-[70vh] items-center justify-center text-gray-500">
        Loading category…
      </div>
      <div v-else-if="error" class="flex min-h-[70vh] flex-col items-center justify-center text-center">
        <h1 class="text-3xl font-bold">{{ entityLabel }} unavailable</h1>
        <p class="mt-3 text-gray-500">{{ error }}</p>
      </div>
      <template v-else>
        <header class="mb-10 flex items-center gap-5">
          <img v-if="category.image" :src="category.image" :alt="category.title" class="h-24 w-24 rounded-2xl bg-white object-contain p-2 shadow-sm" />
          <div>
            <p class="text-xs font-extrabold uppercase tracking-widest text-emerald-700">{{ entityLabel }}</p>
            <h1 class="mt-1 text-4xl font-bold tracking-tight">{{ category.title }}</h1>
            <p class="mt-2 text-gray-500">Browse products from this {{ entityType }}.</p>
          </div>
        </header>

        <div v-if="products.length" class="lg:grid lg:grid-cols-[250px_minmax(0,1fr)] lg:gap-8">
          <aside class="mb-6 lg:mb-0">
            <button
              type="button"
              class="flex w-full items-center justify-between rounded-xl border border-gray-300 bg-white px-4 py-3 font-bold lg:hidden"
              :aria-expanded="filtersOpen"
              @click="filtersOpen = !filtersOpen"
            >
              <span>Filter products</span>
              <span aria-hidden="true">{{ filtersOpen ? '−' : '+' }}</span>
            </button>

            <div
              class="mt-3 rounded-2xl border border-gray-200 bg-white p-5 lg:sticky lg:top-6 lg:mt-0"
              :class="filtersOpen ? 'block' : 'hidden lg:block'"
            >
              <div class="flex items-center justify-between gap-3 border-b border-gray-200 pb-4">
                <h2 class="text-lg font-extrabold uppercase tracking-wide">Filter by</h2>
                <button
                  v-if="hasActiveFilters"
                  type="button"
                  class="text-xs font-bold text-emerald-700 hover:text-emerald-900"
                  @click="resetFilters"
                >
                  Clear all
                </button>
              </div>

              <fieldset class="border-b border-gray-200 py-5">
                <legend class="text-base font-bold">Price</legend>
                <div class="mt-3 grid grid-cols-[1fr_auto_1fr] items-end gap-2">
                  <label class="text-xs font-semibold text-gray-500">
                    From
                    <input
                      v-model.number="priceMin"
                      type="number"
                      min="0"
                      :max="priceMax"
                      class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-emerald-600"
                    />
                  </label>
                  <span class="pb-2 text-gray-400">–</span>
                  <label class="text-xs font-semibold text-gray-500">
                    To
                    <input
                      v-model.number="priceMax"
                      type="number"
                      :min="priceMin"
                      class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:border-emerald-600"
                    />
                  </label>
                </div>
              </fieldset>

              <fieldset v-if="brandOptions.length" class="border-b border-gray-200 py-5">
                <legend class="text-base font-bold">Brands</legend>
                <div class="mt-3 space-y-2.5">
                  <label v-for="brand in brandOptions" :key="brand.id" class="flex cursor-pointer items-center gap-3 text-sm text-gray-600">
                    <input v-model="selectedBrands" type="checkbox" :value="brand.id" class="h-4 w-4 rounded border-gray-300 accent-emerald-700" />
                    <span>{{ brand.label }}</span>
                    <span class="ml-auto text-xs text-gray-400">{{ brand.count }}</span>
                  </label>
                </div>
              </fieldset>

              <fieldset
                v-for="attribute in attributeOptions"
                :key="attribute.key"
                class="border-t border-gray-200 py-5"
              >
                <legend class="text-base font-bold">{{ attribute.label }}</legend>
                <div class="mt-3 space-y-2.5">
                  <label v-for="option in attribute.values" :key="option.key" class="flex cursor-pointer items-center gap-3 text-sm text-gray-600">
                    <input
                      type="checkbox"
                      :checked="isAttributeSelected(attribute.key, option.key)"
                      class="h-4 w-4 rounded border-gray-300 accent-emerald-700"
                      @change="toggleAttribute(attribute.key, option.key)"
                    />
                    <span
                      v-if="isColorAttribute(attribute.label)"
                      class="h-4 w-4 rounded-full border border-gray-300 shadow-sm"
                      :style="colorSwatchStyle(option.label)"
                    />
                    <span>{{ option.label }}</span>
                    <span class="ml-auto text-xs text-gray-400">{{ option.count }}</span>
                  </label>
                </div>
              </fieldset>
            </div>
          </aside>

          <section class="min-w-0">
            <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
              <p class="font-bold">Showing {{ sortedProducts.length }} {{ sortedProducts.length === 1 ? 'result' : 'results' }}</p>
              <label class="flex items-center gap-3 text-sm font-semibold text-gray-500">
                Sort by
                <select v-model="sortBy" class="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-gray-900 outline-none focus:border-emerald-600">
                  <option value="newest">Newest</option>
                  <option value="price-low">Price: low to high</option>
                  <option value="price-high">Price: high to low</option>
                  <option value="name">Name</option>
                </select>
              </label>
            </div>

            <div v-if="sortedProducts.length" class="grid gap-5 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
              <article v-for="product in sortedProducts" :key="product.id" class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
                <img v-if="product.image" :src="product.image" :alt="product.product_name" class="aspect-square w-full bg-gray-50 object-contain p-5" />
                <div class="p-5">
                  <p v-if="product.brand_name" class="text-xs font-bold uppercase tracking-wide text-emerald-700">{{ product.brand_name }}</p>
                  <h2 class="mt-1 text-xl font-bold">{{ product.product_name }}</h2>
                  <p v-if="product.description" class="mt-2 line-clamp-2 text-sm leading-6 text-gray-500">{{ product.description }}</p>
                  <strong class="mt-4 block text-lg">Rs {{ money(product.price) }}</strong>
                  <RouterLink
                    :to="{ name: 'StorefrontProduct', params: { websiteId: route.params.websiteId, slug: product.slug } }"
                    class="mt-4 block rounded-xl bg-gray-900 px-4 py-3 text-center text-sm font-bold text-white"
                  >
                    View product
                  </RouterLink>
                </div>
              </article>
            </div>
            <div v-else class="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center">
              <h2 class="text-xl font-bold">No matching products</h2>
              <p class="mt-2 text-sm text-gray-500">Try changing or clearing the selected filters.</p>
              <button type="button" class="mt-5 rounded-xl bg-gray-900 px-5 py-3 text-sm font-bold text-white" @click="resetFilters">
                Clear filters
              </button>
            </div>
          </section>
        </div>
        <p v-else class="rounded-2xl border border-dashed border-gray-300 bg-white p-10 text-center text-gray-500">
          No products are assigned to this category yet.
        </p>
      </template>
    </div>
  </main>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const loading = ref(true)
const error = ref('')
const category = ref({})
const products = ref([])
const filtersOpen = ref(false)
const selectedBrands = ref([])
const selectedAttributeValues = ref({})
const priceMin = ref(0)
const priceMax = ref(0)
const sortBy = ref('newest')
const entityType = computed(() => route.meta.storefrontEntity || 'category')
const entityLabel = computed(() => entityType.value === 'brand' ? 'Brand' : 'Category')

function productPrice(product) {
  return Math.max(0, Number(product?.price || 0))
}

function isSizeOnlyVariant(value) {
  return /^(?:x{0,3}s|s|m|l|x{1,3}l|one size|free size|\d+(?:\.\d+)?(?:\s?(?:mm|cm|in|inch|inches))?)$/i.test(
    String(value || '').trim(),
  )
}

function productVariantAttributes(product) {
  const variants = product?.variant || product?.varient || []
  const attributes = new Map()
  const addValue = (name, value) => {
    const label = String(name || '').trim()
    const option = String(value || '').trim()
    if (!label || !option) return
    const key = label.toLowerCase()
    const group = attributes.get(key) || { key, label, values: new Map() }
    group.values.set(option.toLowerCase(), option)
    attributes.set(key, group)
  }
  variants.forEach(variant => {
    const name = String(variant?.variant_name || variant?.name || '').trim()
    if (!name) return
    const parts = name.split('/').map(value => value.trim()).filter(Boolean)
    parts.forEach((part, index) => {
      const separator = part.indexOf(':')
      if (separator > 0) {
        addValue(part.slice(0, separator), part.slice(separator + 1))
      } else if (parts.length > 1) {
        addValue(index === 0 ? 'Color' : index === 1 ? 'Size' : `Option ${index + 1}`, part)
      } else {
        addValue(isSizeOnlyVariant(part) ? 'Size' : 'Color', part)
      }
    })
  })
  return attributes
}

const priceBounds = computed(() => {
  const prices = products.value.map(productPrice)
  return {
    min: prices.length ? Math.floor(Math.min(...prices)) : 0,
    max: prices.length ? Math.ceil(Math.max(...prices)) : 0,
  }
})

const brandOptions = computed(() => {
  const options = new Map()
  products.value.forEach(product => {
    if (!product.brand && !product.brand_name) return
    const id = String(product.brand || product.brand_name)
    const current = options.get(id) || { id, label: product.brand_name || id, count: 0 }
    current.count += 1
    options.set(id, current)
  })
  return [...options.values()].sort((a, b) => a.label.localeCompare(b.label))
})

const attributeOptions = computed(() => {
  const groups = new Map()
  products.value.forEach(product => {
    productVariantAttributes(product).forEach(attribute => {
      const group = groups.get(attribute.key) || {
        key: attribute.key,
        label: attribute.label,
        values: new Map(),
      }
      attribute.values.forEach((label, key) => {
        const option = group.values.get(key) || { key, label, count: 0 }
        option.count += 1
        group.values.set(key, option)
      })
      groups.set(attribute.key, group)
    })
  })
  return [...groups.values()]
    .map(group => ({
      ...group,
      values: [...group.values.values()].sort((a, b) => a.label.localeCompare(b.label, undefined, { numeric: true })),
    }))
    .sort((a, b) => a.label.localeCompare(b.label))
})

const filteredProducts = computed(() => products.value.filter(product => {
  const price = productPrice(product)
  if (price < Number(priceMin.value || 0) || price > Number(priceMax.value || 0)) return false
  if (selectedBrands.value.length && !selectedBrands.value.includes(String(product.brand || product.brand_name))) return false
  const productAttributes = productVariantAttributes(product)
  for (const [attributeKey, selectedValues] of Object.entries(selectedAttributeValues.value)) {
    if (!selectedValues.length) continue
    const availableValues = productAttributes.get(attributeKey)?.values
    if (!availableValues || !selectedValues.some(value => availableValues.has(value))) return false
  }
  return true
}))

const sortedProducts = computed(() => {
  const result = [...filteredProducts.value]
  if (sortBy.value === 'price-low') result.sort((a, b) => productPrice(a) - productPrice(b))
  else if (sortBy.value === 'price-high') result.sort((a, b) => productPrice(b) - productPrice(a))
  else if (sortBy.value === 'name') result.sort((a, b) => String(a.product_name || '').localeCompare(String(b.product_name || '')))
  return result
})

const hasActiveFilters = computed(() => (
  selectedBrands.value.length > 0
  || Object.values(selectedAttributeValues.value).some(values => values.length > 0)
  || Number(priceMin.value) !== priceBounds.value.min
  || Number(priceMax.value) !== priceBounds.value.max
))

function resetFilters() {
  selectedBrands.value = []
  selectedAttributeValues.value = Object.fromEntries(
    attributeOptions.value.map(attribute => [attribute.key, []]),
  )
  priceMin.value = priceBounds.value.min
  priceMax.value = priceBounds.value.max
}

function isAttributeSelected(attributeKey, valueKey) {
  return (selectedAttributeValues.value[attributeKey] || []).includes(valueKey)
}

function toggleAttribute(attributeKey, valueKey) {
  const selected = [...(selectedAttributeValues.value[attributeKey] || [])]
  const index = selected.indexOf(valueKey)
  if (index === -1) selected.push(valueKey)
  else selected.splice(index, 1)
  selectedAttributeValues.value = { ...selectedAttributeValues.value, [attributeKey]: selected }
}

function isColorAttribute(label) {
  return /colou?r/i.test(String(label || ''))
}

function money(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 2 }).format(Number(value || 0))
}

function colorSwatchStyle(color) {
  const normalized = String(color || '').trim().toLowerCase()
  const aliases = {
    'rose gold': '#b76e79',
    gold: '#d4af37',
    silver: '#c0c0c0',
    multicolor: 'linear-gradient(135deg,#ef4444,#facc15,#22c55e,#3b82f6,#a855f7)',
  }
  return { background: aliases[normalized] || normalized || '#d1d5db' }
}

async function loadCategory() {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({
      website_id: String(route.params.websiteId),
      entity_type: entityType.value,
      slug: String(route.params.slug),
    })
    if (route.query.categories) {
      params.set('category_ids', String(route.query.categories))
    }
    const response = await fetch(`${Frappe_URL}/api/method/ecommerce.api.get_storefront_entity?${params}`)
    const body = await response.json()
    const result = body?.message
    if (!response.ok || result?.status !== 'success') throw new Error(result?.message || `${entityLabel.value} not found.`)
    category.value = result.data.entity || {}
    products.value = result.data.products || []
    resetFilters()
  } catch (exception) {
    error.value = exception?.message || `Unable to load this ${entityType.value}.`
  } finally {
    loading.value = false
  }
}

watch(
  () => [route.params.websiteId, route.params.slug, route.query.categories, entityType.value],
  loadCategory,
  { immediate: true },
)
</script>
