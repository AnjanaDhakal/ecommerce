<template>
  <Dialog v-model="dialog2" v-if="messageStatus === 'success'">
    <template #body-title>
      <h3>{{ dialogTitle }}</h3>
    </template>

    <template #body-content>
      <p v-html="broadcastMessage"></p>
      <div class="flex justify-end">
        <button
          @click="handleDialogClose"
          class="mt-4 px-4 py-2 text-sm text-white bg-black rounded hover:bg-black-200 focus:outline-none focus:ring-2 focus:ring-black-500 focus:ring-opacity-50 cursor-pointer"
        >
          Mark Read
        </button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { Dialog } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import message from '../data/message'

const dialog2 = ref(false)
const broadcastMessage = ref('')
const dialogTitle = ref('') // Add a reactive reference for the title
const messageStatus = ref('')
const dialogname = ref('')

// Function to fetch the message
const fetchMessage = async () => {
  try {
    // Assuming message.fetch() returns a promise that resolves with the updated message
    await message.fetch()
   //  //console.log("asjgdk",message.data.status);

    messageStatus.value = message.data.status
    // Check if message.data exists and is an array with at least one item
    if (
      (message.data.status =
        'success' &&
        message.data &&
        message.data.data &&
        Array.isArray(message.data.data) &&
        message.data.data.length > 0)
    ) {
      // Extract the title and format the broadcast message for HTML display
      dialogTitle.value = message.data.data[0].title // Set the dialog title
      dialogname.value = message.data.data[0].name
      broadcastMessage.value = formatBroadcastMessage(
        message.data.data[0].broadcast_message,
      )
      dialog2.value = true // Show the dialog only if there is a message
    }
  } catch (error) {
    //console.error('Error fetching message:', error);
  }
}

const handleDialogClose = async () => {
  try {
    const response = await fetch('/api/method/ecommerce.api.set_seen', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: dialogname.value,
      }),
    })

    const result = await response.json()

    if (result?.message?.status === 'success') {
      window.location.reload()
    }
  } catch (error) {
    //console.error('API error:', error);
  }
}

// Function to format the broadcast message
const formatBroadcastMessage = (msg) => {
  // Split the message into paragraphs based on double new lines
  const paragraphs = msg.split(/\n{2,}/)

  // Wrap each paragraph in <p> tags for HTML display
  return paragraphs.map((paragraph) => `<p>${paragraph.trim()}</p>`).join('')
}

// Fetch the message when the component is mounted
onMounted(() => {
  fetchMessage()
})
</script>
