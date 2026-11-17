<template>
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen">
    <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen">
      <ListViewTotalOrderVue />
    </div>
  </div>
</template>

<script setup>
import { nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { displayDialog } from '../composables/displayDialog'
import ListViewTotalOrderVue from '../components/ListViewTotalOrder.vue'

const route = useRoute()
const router = useRouter()

const openAddOrderFromRoute = async () => {
  if (route.query.openAddOrder !== '1') {
    return
  }

  await nextTick()
  displayDialog.isDisplay = true
  const { openAddOrder, ...remainingQuery } = route.query

  router.replace({
    path: route.path,
    query: remainingQuery,
  })
}

onMounted(() => {
  openAddOrderFromRoute()
})

watch(
  () => route.query.openAddOrder,
  () => {
    openAddOrderFromRoute()
  },
)
</script>
