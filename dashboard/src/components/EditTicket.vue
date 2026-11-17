<template>
  <Dialog :options="options">
    <template #body-content>
      {{ selectedRow.name }}
      <div class="p-2">
        <FormControl
          type="text"
          size="sm"
          variant="subtle"
          placeholder="subject"
          :disabled="true"
          label="Subject"
          v-model="selectedRow.subject"
        />
        <FormControl
          :type="'textarea'"
          size="sm"
          variant="subtle"
          placeholder="description"
          :disabled="false"
          label="Description"
          v-model="selectedRow.description"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { useToast } from 'vue-toastification'
import { Dialog, FormControl, TextEditor } from 'frappe-ui'
import { computed, ref, watch } from 'vue'

const props = defineProps({
  selectedRow: {
    type: Object,
    required: true,
  },
})

const toast = useToast()
const emit = defineEmits(['ticketCreated'])

const updateIssueData = ref({
  name: '',
  subject: '',
  description: '',
})

// Watch selectedRow and update updateIssueData when selectedRow changes
watch(
  () => props.selectedRow,
  (newVal) => {
    updateIssueData.value.subject = newVal.subject
    updateIssueData.value.description = newVal.description
    updateIssueData.value.name = newVal.name
  },
  { deep: true }, // Add deep: true to watch for changes in nested properties
)

//console.log(updateIssueData.value,"updateIssueData");

const options = computed(() => ({
  title: 'Edit Ticket',
  message: props.selectedRow.name,
  size: 'xl',
  actions: [
    {
      label: 'Update',
      variant: 'solid',
      onClick: (close) => {
        updateTicket()
        close()
      },
    },
  ],
}))

const updateTicket = async () => {
  const apiUrl = '/api/method/ecommerce.api.update_ticket'

  try {
    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateIssueData.value),
    })
    const responseData = await response.json()

    if (response.ok) {
      toast.success('Ticket updated successfully')
      emit('ticketCreated')
     //  // console.log('Ticket updated:', responseData);
    } else {
      // console.error('Error updating ticket:', responseData);
    }
  } catch (error) {
    //console.error('Error updating ticket:', error);
  }
}
</script>
