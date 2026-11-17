<template>
  <div :class="embedded ? 'flex h-full min-h-0 flex-col' : ''">
    <!-- Header -->
    <div
      v-if="!embedded"
      class="bg-white mb-4 flex items-center justify-between p-3"
    >
      <strong class="text-gray-800">Add Products</strong>
      <Button
        theme="green"
        variant="solid"
        @click="displayProduct.isDisplay = true"
      >
        + Add Product
      </Button>
    </div>

    <p v-if="feedback" class="mb-3 text-sm text-red-600">{{ feedback }}</p>

    <EcommerceCollectionView
      :class="embedded ? 'min-h-0 flex-1' : ''"
      title="Products"
      :items="productItems"
      :selected-key="selectedProductKey"
      :loading="isLoading"
      create-label="Add New Product"
      short-create-label="Add Product"
      empty-title="Create Your First Product"
      empty-description="Add your first product and start building the catalog customers will explore."
      empty-icon="inventory_2"
      @create="displayProduct.isDisplay = true"
      @select="selectProduct"
    >
      <template #detail="{ item }">
        <div v-if="item" class="space-y-6">
          <div class="flex items-start gap-4 border-b border-gray-200 pb-5">
            <div
              class="flex h-20 w-20 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-gray-200 bg-gray-50"
            >
              <img
                v-if="item.product_image"
                :src="item.product_image"
                :alt="item.product_name"
                class="h-full w-full object-contain"
              />
              <span v-else class="material-symbols-outlined text-3xl text-green-700">
                inventory_2
              </span>
            </div>
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <h3 class="text-xl font-semibold text-gray-900">
                  {{ item.product_name }}
                </h3>
                <StorefrontStatusToggle
                  :status="item.publication_status"
                  :loading="updatingProductStatus === String(item.name)"
                  @toggle="toggleProductStatus(item)"
                />
              </div>
              <p class="mt-1 text-sm text-gray-500">
                {{ item.brand_name || 'No brand' }} ·
                {{ item.category_name || 'No category' }}
              </p>
            </div>
            <Button
              class="ml-auto shrink-0"
              theme="green"
              variant="solid"
              @click="editProduct(item)"
            >
              Edit Product
            </Button>
          </div>
          <div class="grid gap-5 sm:grid-cols-2">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Description
              </p>
              <p class="mt-2 text-sm leading-6 text-gray-700">
                {{ item.product_description || 'No description added.' }}
              </p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Variants
              </p>
              <p class="mt-2 text-sm text-gray-700">
                {{ item.enable ? 'Enabled' : 'Disabled' }}
              </p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500">
                Storefront status
              </p>
              <p class="mt-2 text-sm text-gray-700">
                {{ statusDescription(item.publication_status) }}
              </p>
            </div>
          </div>
          <div v-if="(item.variant || item.varient || []).length" class="overflow-x-auto">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
              Price and stock
            </p>
            <table class="min-w-full overflow-hidden rounded-lg border border-gray-200 text-sm">
              <thead class="bg-gray-50 text-left text-gray-500">
                <tr>
                  <th class="px-3 py-2">Variant</th>
                  <th class="px-3 py-2">Linked image</th>
                  <th class="px-3 py-2">Selling</th>
                  <th class="px-3 py-2">Discounted</th>
                  <th class="px-3 py-2">Stock</th>
                  <th class="px-3 py-2">SKU</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="variant in item.variant || item.varient" :key="variant.name" class="border-t border-gray-200">
                  <td class="px-3 py-2 font-medium">{{ variant.variant_name || variant.name }}</td>
                  <td class="px-3 py-2">
                    <div class="flex min-w-32 items-center gap-2">
                      <div class="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-gray-200 bg-gray-50">
                        <img
                          v-if="variant.image || variant.variant_image || item.product_image"
                          :src="variant.image || variant.variant_image || item.product_image"
                          :alt="`${variant.variant_name || variant.name} image`"
                          class="h-full w-full object-contain"
                        />
                        <span v-else class="material-symbols-outlined text-lg text-gray-400">image</span>
                      </div>
                      <span class="text-xs text-gray-500">
                        {{ variantImageLabel(item, variant) }}
                      </span>
                    </div>
                  </td>
                  <td class="px-3 py-2">Rs {{ variant.selling_price ?? 0 }}</td>
                  <td class="px-3 py-2">Rs {{ variant.discounted_price ?? 0 }}</td>
                  <td class="px-3 py-2">{{ variant.quantity ?? 0 }}</td>
                  <td class="px-3 py-2">{{ variant.sku || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </EcommerceCollectionView>

    <DialogProduct
      :product-to-edit="productToEdit"
      @product-created="handleProductSaved"
      @product-updated="handleProductSaved"
      @closed="productToEdit = null"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { displayProduct } from '../composables/displayProduct'
import DialogProduct from './DialogProduct.vue'
import EcommerceCollectionView from './EcommerceCollectionView.vue'
import StorefrontStatusToggle from './StorefrontStatusToggle.vue'
import { Button } from 'frappe-ui'
import { useRoutedCollectionSelection } from '@/composables/useRoutedCollectionSelection'

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const products = ref([])
const productToEdit = ref(null)
const selectedProductKey = ref('')
const isLoading = ref(false)
const feedback = ref('')
const updatingProductStatus = ref('')
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')
const {
  selectItem: selectProduct,
  restoreSelection: restoreProductSelection,
} = useRoutedCollectionSelection(products, selectedProductKey, 'add-product')
const productItems = computed(() =>
  products.value.map((item) => ({
    key: item.name,
    title: item.product_name || item.name,
    status:
      (item.publication_status || 'Published') === 'Published'
        ? 'Published'
        : 'Unpublished',
    subtitle:
      [item.publication_status || 'Published', item.brand_name, item.category_name].filter(Boolean).join(' · ') ||
      'Product',
    image: item.product_image,
    raw: item,
  })),
)

function variantImageLabel(product, variant) {
  const linkedImage = variant.image || variant.variant_image
  if (!linkedImage) return product.product_image ? 'Main image (default)' : 'No image'
  const imageIndex = (product.images || []).indexOf(linkedImage)
  return imageIndex >= 0 ? `Image ${imageIndex + 1}` : 'Linked image'
}

function statusDescription(status) {
  if (status === 'Archived') return 'Archived and unavailable on the storefront.'
  if (status === 'Hidden') return 'Saved for later and currently hidden from customers.'
  return 'Published and visible to customers.'
}

async function toggleProductStatus(item) {
  const itemId = String(item.name || '')
  if (!itemId || updatingProductStatus.value) return
  const nextStatus = item.publication_status === 'Published' ? 'Hidden' : 'Published'
  updatingProductStatus.value = itemId
  feedback.value = ''
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.update_storefront_item_status`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          item_type: 'product',
          name: item.name,
          publication_status: nextStatus,
        }),
      },
    )
    const responseData = await response.json().catch(() => ({}))
    const result = responseData?.message ?? responseData
    if (!response.ok || result.status !== 'success') {
      throw new Error(result.message || 'Unable to update product status.')
    }
    item.publication_status = result.data?.publication_status || nextStatus
    await fetchProducts()
  } catch (err) {
    feedback.value = err.message || 'Unable to update product status.'
  } finally {
    updatingProductStatus.value = ''
  }
}

async function fetchProducts() {
  isLoading.value = true
  feedback.value = ''
  try {
    const websiteId = JSON.parse(localStorage.getItem('selectedWebsite') || '{}').name
    const websiteQuery = websiteId ? `?website_id=${encodeURIComponent(websiteId)}` : ''
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_products${websiteQuery}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      },
    )
    const responseData = await response.json().catch(() => ({}))
    const result = responseData?.message ?? responseData
    if (!response.ok || result.status !== 'success') {
      throw new Error(
        result.message || `Unable to fetch products (HTTP ${response.status})`,
      )
    }
    products.value = Array.isArray(result.data) ? result.data : []
    restoreProductSelection()
  } catch (err) {
    console.error('Product fetch error:', err)
    products.value = []
    feedback.value = err.message || 'Unable to fetch products.'
  } finally {
    isLoading.value = false
  }
}

function editProduct(item) {
  productToEdit.value = JSON.parse(JSON.stringify(item))
  displayProduct.isDisplay = true
}

async function handleProductSaved(savedProduct) {
  const savedId = savedProduct?.name || savedProduct?.id
  await fetchProducts()
  if (savedId !== undefined && savedId !== null) selectProduct(savedId)
  productToEdit.value = null
}

onMounted(fetchProducts)
</script>
