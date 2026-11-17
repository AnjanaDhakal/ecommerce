<template>
  <div
    class="flex flex-col gap-4 p-3 w-80 h-96 overflow-y-auto custom-scrollbar"
  >
    <div
      class="flex items-start gap-3"
      v-for="notification in notificationList"
      :key="notification.name"
      v-if="notificationList.length > 0"
    >
      <h2>
        <p class="text-blue-500">{{ notification.title_name }}:</p>
        <p class="text-gray-700">{{ notification.message }}</p>
      </h2>
    </div>
    <div v-else>
      <p class="text-gray-500 text-center">
        You don't have any notifications yet.
      </p>
    </div>
  </div>
</template>
<script setup>
import notification from '../data/notification'
import { onMounted, ref } from 'vue'

let notificationList = ref([])
let isLoading = ref(false)
let hasFetched = ref(false)

const fetchNotifications = async () => {
  if (hasFetched.value || isLoading.value) return
  isLoading.value = true
  await notification.fetch()
  const notifications = notification?.data || []

  notificationList.value = notifications
  hasFetched.value = true
  isLoading.value = false
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 10px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #555;
}
</style>
