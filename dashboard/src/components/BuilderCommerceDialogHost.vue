<template>
  <DialogProduct
    ref="productDialog"
    @product-created="handleProductCreated"
    @brand-created="handleBrandCreated"
    @category-created="handleCategoryCreated"
    @closed="pendingProductCreated = null"
  />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, shallowRef } from 'vue'
import DialogProduct from './DialogProduct.vue'
import { displayProduct } from '@/composables/displayProduct'
import { registerBuilderCommerceHost } from '@/composables/useBuilderCommerceCreator'

const productDialog = ref(null)
const pendingProductCreated = shallowRef(null)
const pendingBrandCreated = shallowRef(null)
const pendingCategoryCreated = shallowRef(null)
let unregisterHost = null

function openProduct(onCreated) {
  pendingBrandCreated.value = null
  pendingCategoryCreated.value = null
  pendingProductCreated.value = onCreated
  displayProduct.isDisplay = true
}

function openCategory(onCreated) {
  pendingProductCreated.value = null
  pendingBrandCreated.value = null
  pendingCategoryCreated.value = onCreated
  productDialog.value?.openStandaloneCategoryDialog()
}

function openBrand(onCreated) {
  pendingProductCreated.value = null
  pendingCategoryCreated.value = null
  pendingBrandCreated.value = onCreated
  productDialog.value?.openStandaloneBrandDialog()
}

async function handleProductCreated(product) {
  const onCreated = pendingProductCreated.value
  pendingProductCreated.value = null
  await onCreated?.(product)
}

async function handleCategoryCreated(categoryId) {
  const onCreated = pendingCategoryCreated.value
  pendingCategoryCreated.value = null
  await onCreated?.(categoryId)
}

async function handleBrandCreated(brandId) {
  const onCreated = pendingBrandCreated.value
  pendingBrandCreated.value = null
  await onCreated?.(brandId)
}

onMounted(() => {
  unregisterHost = registerBuilderCommerceHost({
    openProduct,
    openBrand,
    openCategory,
  })
})

onBeforeUnmount(() => {
  unregisterHost?.()
})
</script>
