<template>
  <strong class="text-gray-800">{{ supportTicketTitle }}</strong>

  <Button variant="solid" @click="displayDialog.isDisplay = true">{{
    addTicketLabel
  }}</Button>
</template>

<script setup>
import { Button } from 'frappe-ui'
import { displayDialog } from '../composables/displayDialog'
import DialogTicket from './DialogTicket.vue'

// Define props
const props = defineProps({
  supportTicketTitle: String,
  addTicketLabel: String,
})
</script>
