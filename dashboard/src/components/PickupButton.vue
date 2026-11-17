<template>
  <!-- <div>
    <div
      class="flex items-center gap-2 rounded-full bg-gradient-to-r from-orange-400 to-yellow-400 p-3 md:p-3 shadow-lg hover:from-orange-500 hover:to-yellow-500 transition duration-300 ease-in-out transform hover:scale-105 cursor-pointer"
      @click="displayPickup.isDisplay = true"
    >
      <span class="material-symbols-outlined text-white text-lg md:text-lg font-bold">directions_bike</span>
      <span class="text-white text-sm md:text-base font-bold">Request for Pickup</span>
    </div>

    <DialogPickup v-model="displayPickup.isDisplay" />
  </div> -->
</template>

<script setup>
import { displayPickup } from '../composables/displayPickup'
import DialogPickup from '../components/DialogPickup.vue'
</script>
