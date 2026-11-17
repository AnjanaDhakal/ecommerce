<template>
  <Dialog :options="dialogOptions" v-model="displayDialog.isDisplay">
    <template #body-content>
      <div class="p-2">
        <label class="block text-sm text-gray-600 font-bold">Ticket Type</label>
        <Autocomplete
          :options="ticketTypes"
          placeholder="Select Ticket Type"
          v-model="selectedTicketType"
        />

        <FormControl
          :type="'textarea'"
          size="sm"
          variant="subtle"
          placeholder="description"
          :disabled="false"
          label="Description"
          v-model="newIssueData.description"
        />

        <div v-if="errorMessage" class="text-red-500 text-sm mt-2">
          {{ errorMessage }}
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import tickettype from '../data/tickettype'
import { useToast } from 'vue-toastification'
import { Dialog, FormControl, TextEditor, Autocomplete } from 'frappe-ui'
import { displayDialog } from '../composables/displayDialog'
import { ref, watch, onMounted } from 'vue'

const emit = defineEmits(['ticketCreated'])

const toast = useToast()
const newIssueData = ref({
  subject: '',
  description: '',
})
const selectedTicketType = ref(null) // New reactive property for the selected ticket type
const errorMessage = ref('')

const validateForm = () => {
  if (!newIssueData.value.subject) {
    errorMessage.value = 'Please provide subject.'
    return false
  }
  errorMessage.value = ''
  return true
}

const createNewTicket = async () => {
  if (!validateForm()) {
    return
  }
  const apiUrl = '/api/method/ecommerce.api.create_ticket'

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newIssueData.value),
    })
    const responseData = await response.json()

    if (response.ok) {
      toast.success('Ticket created successfully')
      emit('ticketCreated')
      displayDialog.isDisplay = false
      resetForm()
    } else {
      errorMessage.value = `Error creating issue: ${responseData.message}`
    }
  } catch (error) {
    // console.error('Error creating issue:', error);
    errorMessage.value = `Error creating issue: ${error.message || error}`
  }
}

const resetForm = () => {
  newIssueData.value = {
    subject: '',
    description: '',
  }
  selectedTicketType.value = null // Reset the selected ticket type
  errorMessage.value = ''
}

const dialogOptions = {
  title: 'Add Ticket',
  description: 'Add a new ticket',
  size: 'xl',
  actions: [
    {
      label: 'Confirm',
      variant: 'solid',
      onClick: createNewTicket,
    },
  ],
}

const ticketTypes = ref([])

const fetchTicketTypes = async () => {
  try {
    await tickettype.fetch()
    const types = tickettype.data.data.ticket_types
    ticketTypes.value = types.map((item) => ({
      value: item.name,
      label: item.name,
    }))
  } catch (error) {
    // console.error('Failed to fetch ticket types:', error);
  }
}

// Watch selectedTicketType and update newIssueData.subject accordingly
watch(selectedTicketType, (newType) => {
  newIssueData.value.subject = newType ? newType.value : ''
})

onMounted(() => {
  fetchTicketTypes()
})
</script>
