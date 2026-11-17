<template>
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen">
    <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen">
      <div class="items-center rounded">
        <TicketList />
      </div>
    </div>
  </div>
</template>

<script setup>
import TicketList from '../components/TicketList.vue'
</script>
