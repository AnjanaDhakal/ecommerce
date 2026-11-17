<template>
  <div
    class="p-6 lg:bg-gradient-to-r from-blue-50 via-indigo-50 to-gray-100 min-h-screen"
  >
    <div class="p-3 lg:p-8 rounded-lg bg-white min-h-screen">
      <h1
        class="text-xl font-semibold font-pregular text-indigo-700 mb-2 leading-relaxed"
      >
        Pick &amp; Drop Webhook Integration
        <span class="text-red-600">(In Beta)</span>
      </h1>
      <h3 class="text-sm font-pregular text-indigo-700 mb-2 leading-relaxed">
        Pick & Drop will send POST request when the status is triggered
      </h3>
      <div class="p-4 rounded-md mb-3 bg-[#ebebeb5c]">
        <h1 class="text-lg font-bold text-indigo-700 mb-2 leading-relaxed">
          Status Change Event Webhook
        </h1>
        <!-- Toggle Switch Section -->
        <div class="flex items-center space-x-2 mb-4">
          <Switch
            size="sm"
            :label="isWebhookEnabled ? 'Enabled' : 'Disabled'"
            v-model="isWebhookEnabled"
            @update:modelValue="handleStatusToggle"
            :disabled="!isFeatureEnabled"
            class="text-lg"
          />
        </div>

        <!-- Base URL Input -->
        <div class="flex items-center space-x-2 mb-4">
          <!--  <p class="text-base text-gray-800 font-pthin leading-relaxed mb-0">
       <strong>Base URL<span class="text-red-700 text-lg">*</span>:</strong>
        </p>
        <input
          type="text"
          v-model="request_url"
          placeholder="Enter Base URL"
          class="w-full lg:w-2/3 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        /> -->
          <p class="font-pregular">
            <strong
              >Base URL<span class="text-red-700 text-lg">*</span>:</strong
            >
          </p>
          <TextInput
            type="text"
            size="sm"
            variant="subtle"
            v-model="request_url"
            placeholder="https://example.com"
            class="w-1/2 bg-white font-pregular hover:bg-white"
          />
        </div>

        <!-- Webhook Key Input -->
        <div class="flex items-center space-x-2 mb-6">
          <!-- <p class="text-base text-gray-800 font-pthin leading-relaxed mb-0">
          <strong
            >Webhook Key<span class="text-red-700 text-lg">*</span>:</strong
          >
        </p>
        <input
          type="password"
          v-model="webhookKey"
          placeholder="Enter Webhook Key"
          class="w-full lg:w-2/3 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
        /> -->
          <p class="font-pregular">
            <strong
              >Webhook Secret
              <span class="text-red-700 text-lg">*</span>:</strong
            >
          </p>
          <TextInput
            type="password"
            size="sm"
            variant="subtle"
            v-model="webhookKey"
            placeholder="************"
            class="w-1/2 bg-white font-pregular hover:bg-white"
          />
        </div>


        <!-- Connect Button (Disabled if Base URL or Webhook Key are missing) -->
        <div class="flex-1">
          <Button
            variant="solid"
            @click="handleConnect"
            class="bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-6 rounded-md text-lg font-semibold focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Save
          </Button>
        </div>
        <!-- Success & Error Messages -->
        <p
          v-if="message"
          class="text-base text-red-800 font-pthin leading-relaxed"
        >
          {{ message.message }}
        </p>
        <p
          v-if="error"
          class="text-base text-red-800 font-pthin leading-relaxed"
        >
          {{ error }}
        </p>
        <div class="my-2">
          <p class="text-sm pb-2">Webhook Payload</p>

          <div class="border rounded-md p-2 bg-gray-100">
            <pre class="text-sm">
{
  "comments": "Customer cancel before Delivery",
  "epod": "",
  "package_type": "Regular",
  "status": "return_at_transit_hub",
  "timestamp": "08-18-2025 13:13:15",
  "tracking_number": "PND-NP-000566118"
}
        </pre
            >
          </div>
           <h2
          class="text-xl font-semibold  text-indigo-700 mb-2 leading-relaxed"
        >
          API Documentation Link
        </h2>
        <p class="text-base text-gray-800  leading-relaxed mb-6">
          <a
            href="https://pickndrop.apidog.io/-pick-drop-webhook-integration-1375447m0"
            target="_blank"
            class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded inline-flex items-center"
          >
            <svg
              class="w-4 h-4 mr-2"
              fill="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2ZM13 9V3.5L18.5 9H13Z"
              ></path>
            </svg>
            <span>Go to API Documentation</span>
          </a>
        </p>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { Checkbox, Switch } from 'frappe-ui'
import webhook from '../data/webhook'
import webhookcomment from '../data/webhookcomment'

import { useToast } from 'vue-toastification'
import { Button, TextInput, Dialog } from 'frappe-ui'

const toast = useToast()
const request_url = ref(webhook.data?.url || '') // User input for Base URL
const webhookKey = ref('') // User input for Webhook Key

const message = ref('') // Success message
const error = ref('') // Error message
const isWebhookEnabled = ref(webhook.data?.enabled === 1) // Initialize based on webhook.data.enabled
const isFeatureEnabled = ref(true) // This controls whether the feature itself is enabled
const selectedOptions = ref(['Completed']) // Default selection is "complete"

const isCommentEnabled = ref(webhookcomment.data?.enabled === 1) // Initialize based on webhook.data.enabled
const isFeaturedEnabled = ref(true)
const request_comment_url = ref(webhookcomment.data?.url || '') // User input for Base URL
const webhooksecretKey = ref('') // User input for Webhook Key
const statusWebhookName = ref(webhook.data?.webhook_name || '')
const commentWebhookName = ref(webhookcomment.data?.webhook_name || '')
const statusToggleReady = ref(false)
const commentToggleReady = ref(false)
// Check if "All" is selected
const isAllSelected = computed(() => selectedOptions.value.includes('All'))

watch(
  () => webhook.data,
  (val) => {
    statusToggleReady.value = false
    if (val) {
      statusWebhookName.value = val.webhook_name || ''
      request_url.value = val.url || request_url.value
      isWebhookEnabled.value = val.enabled === 1
    }
    statusToggleReady.value = true
  },
  { immediate: true },
)

watch(
  () => webhookcomment.data,
  (val) => {
    commentToggleReady.value = false
    if (val) {
      commentWebhookName.value = val.webhook_name || ''
      request_comment_url.value = val.url || request_comment_url.value
      isCommentEnabled.value = val.enabled === 1
    }
    commentToggleReady.value = true
  },
  { immediate: true },
)

const toggleWebhookState = async (name, enabled) => {
  if (!name) {
    toast.error('Webhook not found. Please configure the URL first.')
    return
  }
  try {
    const response = await fetch('/api/method/ecommerce.webhook.toggle_webhook', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ webhook_name: name, enabled }),
    })
    let data = {}
    try {
      data = await response.json()
    } catch (e) {
      data = {}
    }
    if (!response.ok) {
      throw new Error(data.message || 'Unable to update webhook state.')
    }
    if (data.status && data.status !== 'success') {
      throw new Error(data.message || 'Unable to update webhook state.')
    }
    toast.success(`Webhook ${enabled ? 'enabled' : 'disabled'} successfully`)
  } catch (err) {
    toast.error(err.message || 'Failed to update webhook state.')
  }
}

const handleStatusToggle = async (value) => {
  if (!statusToggleReady.value) return
  await toggleWebhookState(statusWebhookName.value, value)
}

const handleCommentToggle = async (value) => {
  if (!commentToggleReady.value) return
  await toggleWebhookState(commentWebhookName.value, value)
}

// Handle selection logic
const handleSelection = (value) => {
  if (value === 'All') {
    if (selectedOptions.value.includes('All')) {
      // If "All" is already selected, deselect it
      selectedOptions.value = []
    } else {
      // If "All" is not selected, clear other selections and select "All"
      selectedOptions.value = ['All']
    }
  } else {
    // If "All" is already selected, remove it
    selectedOptions.value = selectedOptions.value.filter(
      (option) => option !== 'All',
    )

    // Add or remove the selected value
    if (selectedOptions.value.includes(value)) {
      selectedOptions.value = selectedOptions.value.filter(
        (option) => option !== value,
      )
    } else {
      selectedOptions.value.push(value)
    }
  }
}

// Watch for changes in isWebhookEnabled and log to the console
//   watch(isWebhookEnabled, (newValue) => {
//     console.log('Webhook enabled:', newValue); // Logs the new value whenever it changes
//   })

const handleConnect = async () => {
  message.value = ''
  error.value = ''

  if (!request_url.value || !webhookKey.value) {
    error.value = 'Both Base URL and Webhook Key are required!'
    return
  }
 //  //console.log(selectedOptions.value,)
  try {
    const response = await fetch('/api/method/ecommerce.webhook.get_status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_url: request_url.value,
        webhook_secret: webhookKey.value,
        webhook_mode: selectedOptions.value, // Corrected to pass the selected radio option
        enabled: isWebhookEnabled.value, // Send the correct value of the switch
      }),
    })

    if (!response.ok) {
      throw new Error('Failed to connect. Please try again.')
    }

    const data = await response.json()

    toast.success('Webhook added successfully')
    setTimeout(() => window.location.reload(), 400)
  } catch (err) {
    error.value = err.message || 'An error occurred.'
  }
}

const handlecommentConnect = async () => {
  message.value = ''
  error.value = ''

  if (!request_comment_url.value || !webhooksecretKey.value) {
    error.value = 'Both Base URL and Webhook Key are required!'
    return
  }
 //  //console.log(selectedOptions.value,)
  try {
    const response = await fetch('/api/method/ecommerce.webhook.get_comment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_url: request_comment_url.value,
        webhook_secret: webhooksecretKey.value,
        enabled: isCommentEnabled.value, // Send the correct value of the switch
      }),
    })

    if (!response.ok) {
      throw new Error('Failed to connect. Please try again.')
    }

    const data = await response.json()

    toast.success('Webhook comment added successfully')
    setTimeout(() => window.location.reload(), 400)
  } catch (err) {
    error.value = err.message || 'An error occurred.'
  }
}

</script>
