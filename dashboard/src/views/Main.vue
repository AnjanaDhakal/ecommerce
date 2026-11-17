<template>
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen">
    <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen">
      <div class="items-center rounded">
        <ListViewLiveUpdate />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import ListViewLiveUpdate from '@/components/ListViewLiveUpdate.vue'
const router = useRouter()
import { useRoute } from 'vue-router'

const route = useRoute()

const getAccountRoute = () => {
  const route = router.resolve('/account')
  return route.href
}
</script>
