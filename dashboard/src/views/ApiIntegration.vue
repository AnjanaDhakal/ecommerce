<template>
  <div
    class="p-6 lg:bg-gradient-to-r from-blue-50 via-indigo-50 to-gray-100 min-h-screen"
  >
    <div class="p-3 lg:p-8 rounded-lg bg-white min-h-screen">
      <!-- <h1 class="text-xl font-semibold font-pregular text-indigo-700 mb-2 leading-relaxed">Pick &amp; Drop API
          Integration &amp; Benefits</h1>
        <p class="text-base text-gray-800 font-pthin leading-relaxed mb-6">PickNDrop (PND) offers cutting-edge
          technology to streamline logistics for your business. Our comprehensive suite of API endpoints allows seamless
          integration between your software and our logistics system. By integrating your e-commerce or business
          platform with our API, you can bypass the need to access the PND vendor portal and manage logistics directly
          from your own system. Key benefits include:</p>
        <ul class="text-base text-gray-800 font-pthin leading-relaxed mb-6">
          <li class="flex items-center space-x-3"><svg xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg><span>Automatic PND pickup order creation</span></li>
          <li class="flex items-center space-x-3"><svg xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg><span>Order status changes monitoring via your system</span></li>
          <li class="flex items-center space-x-3"><svg xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg><span>Commenting via your own system</span></li>
          <li class="flex items-center space-x-3"><svg xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg><span>Provide better customer service &amp; employee experience</span></li>
          <li class="flex items-center space-x-3"><svg xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg><span>Design your own system the way you like it</span></li>
        </ul> -->
      <div class="mb-8">
        <h2
          class="text-2xl font-semibold  text-indigo-700 mb-2 leading-relaxed"
        >
          Pick &amp; Drop API Integration Demo Token Key
        </h2>
        <p class="text-base text-gray-800  leading-relaxed mb-6">
          We provide you a demo portal to test and try our APIs and system
          before you integrate it into our production server. We strongly
          recommend you try our demo portal and demo server first. We recommend
          you not to use real customer data for demo server.
        </p>
        <div class="bg-gray-100 p-4 rounded mb-6 shadow-sm">
          <h3 class="text-lg font-semibold font-pregular leading-relaxed">
            Demo Server Login Details:
          </h3>
          <div class="space-y-1">
            <div class="text-base text-gray-800 leading-relaxed">
              Url:
              <strong
                ><a target="_blank" href="https://app-t.pickndropnepal.com/login"
                  >https://app-t.pickndropnepal.com/login</a
                ></strong
              >
            </div>
            <div class="text-base text-gray-800 leading-relaxed">
              BaseURL: <strong>https://app-t.pickndropnepal.com</strong>
            </div>
            <div class="text-base text-gray-800 leading-relaxed">
              Email: <strong>demo@user.test</strong>
            </div>
            <div class="text-base text-gray-800 leading-relaxed">
              Password: <strong>Demo@1234</strong>
            </div>
            <div class="text-base text-gray-800 leading-relaxed">
              Demo API Key: <strong>bf1a7ce75dacf51</strong>
            </div>
            <div class="text-base text-gray-800 leading-relaxed">
              Demo API Secret: <strong>63b8931e70aee27</strong>
            </div>
          </div>
        </div>
        <h2
          class="text-xl font-semibold  text-indigo-700 mb-2 leading-relaxed"
        >
          API Documentation Link
        </h2>
        <p class="text-base text-gray-800  leading-relaxed mb-6">
          <a
            href="https://pickndrop.apidog.io/"
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
      <h2
        class="text-xl font-semibold  text-indigo-700 mb-4 leading-relaxed"
      >
        Pick &amp; Drop API Integration Production Token Key
      </h2>
      <p class="text-base text-gray-800  leading-relaxed mb-6">
        Once you have tried our system with the demo portal and demo server, you
        can generate a production token for finalizing integration. We monitor
        all use of our APIs, and any misuse or violation can lead to automatic
        suspension of your account.
      </p>
      <Button
        variant="solid"
        @click="generateApiKeys"
        class="mb-6 bg-indigo-600 hover:bg-indigo-700 text-white font-pregular"
      >
        {{ apiKey ? 'Generate API Secret' : 'Generate API Key' }}
      </Button>

      <!-- Display API Keys -->
      <div v-if="apiKey" class="mb-6">
        <div class="p-4 rounded shadow-sm">
          <h3
            class="text-lg font-semibold text-indigo-700 mb-2 leading-relaxed"
          >
            Your API Keys
          </h3>
          <div class="flex flex-col space-y-4">
            <div class="flex items-center space-x-2">
              <p class="font-pregular"><strong>API Key:</strong></p>
              <TextInput
                type="text"
                size="sm"
                variant="subtle"
                v-model="apiKey"
                readonly
                class="w-1/2 bg-white font-pregular"
              />
            </div>
            <div class="flex items-center space-x-2">
              <p class="font-pregular"><strong>API Secret:</strong></p>
              <TextInput
                type="password"
                size="sm"
                variant="subtle"
                placeholder="************"
                readonly
                class="w-1/2 bg-white font-pregular"
              />
            </div>
          </div>
        </div>
      </div>
      <h2
        class="text-xl font-bold  text-indigo-700 mb-4 leading-relaxed"
      >
        Contact for Integration Help and Support
      </h2>
      <p class="text-base text-gray-800 ">
        If you need any help with integration, we can provide extensive support.
        Please contact us at
        <a
          href="mailto:developer@pickndropnepal.com"
          class="text-blue-600 hover:text-indigo-500"
          >developer@pickndropnepal.com</a
        >
        and we will provide support to you.
      </p>
    </div>
  </div>

  <Dialog v-model="dialog2">
    <template #body-title>
      <h3>{{ dialogTitle }}</h3>
    </template>
    <template #body-content>
      <p>{{ dialogMessage }}</p>
    </template>
    <!-- <template #actions>
    <Button variant="solid">
      Confirm
    </Button>
    <Button
      class="ml-2"
      @click="dialog2 = false"
    >
      Close
    </Button>
  </template> -->
  </Dialog>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button, TextInput, Dialog } from 'frappe-ui'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

// State to hold the API key and API secret
const apiKey = ref(null)
const apiSecret = ref(null)
const dialog2 = ref(false)
const dialogTitle = ref('')
const dialogMessage = ref('')

// Function to generate new API keys
// const generateApiKeys = async () => {
//   try {
//     const response = await fetch('/api/method/ecommerce.get_role_profile_of_logged_user.generate_keys', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       }
//     })

//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`)
//     }

//     const data = await response.json()
//      //console.log(data.message)

//     apiSecret.value = data.message.api_secret

//     alert(`Save API Secret: ${apiSecret.value} `)

//   } catch (error) {
//     console.error('Error generating API keys:', error)
//     if (error.message.includes('PermissionError')) {
//       alert('You do not have permission to generate API keys.')
//     } else {
//       alert('An error occurred while generating API keys.')
//     }
//   }
// }

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''

const generateApiKeys = async () => {
  const token = localStorage.getItem('access_token')
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.get_role_profile_of_logged_user.generate_keys`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )
    // console.log('djfjdnfjlnfl')

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
   //  // console.log(data.message)

    // Check for demo user message
    if (data.message.message === 'Demo user cannot generate API key') {
      dialogTitle.value = 'Error'
      dialogMessage.value = 'Demo user cannot generate API key.'
      dialog2.value = true
      return
    }

    // If API secret is available, update and show it
    if (data.message.api_secret) {
      apiSecret.value = data.message.api_secret
      dialogTitle.value = 'API Secret'
      dialogMessage.value = `Save API Secret: ${apiSecret.value}, Api Key: ${data.message.api_key}`
      dialog2.value = true
    }
  } catch (error) {
    //console.error('Error generating API keys:', error)
    // Handle specific errors
    if (error.message.includes('PermissionError')) {
      dialogTitle.value = 'Permission Error'
      dialogMessage.value = 'You do not have permission to generate API keys.'
      dialog2.value = true
    } else {
      dialogTitle.value = 'Error'
      dialogMessage.value = 'An error occurred while generating API keys.'
      dialog2.value = true
    }
  }
}

// const generateApiKeys = async () => {
//   try {
//     const response = await fetch('/api/method/ecommerce.get_role_profile_of_logged_user.generate_keys', {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//       }
//     })

//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`)
//     }

//     const data = await response.json()

//     if (data.message.message === "Demo user cannot generate API key") {

//       alert('Demo user cannot generate API key')
//       return
//     }

//     if (data.api_secret) {
//       apiSecret.value = data.api_secret
//       alert(`Save API Secret: ${apiSecret.value}`)
//     }

//   } catch (error) {
//     console.error('Error generating API keys:', error)
//     if (error.message.includes('PermissionError')) {
//       alert('You do not have permission to generate API keys.')
//     } else {
//       alert('An error occurred while generating API keys.')
//     }
//   }
// }
// Function to retrieve existing API keys
const getapikey = async () => {
  try {
    const response = await fetch('/api/method/ecommerce.api.get_apikey', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
   //  // console.log(data.message)

    // Update the API key and secret in the component's state
    apiKey.value = data.message.vendor_info.api_key

    // apiSecret.value = data.message.vendor_info.api_secret
  } catch (error) {
    // console.error('Error retrieving API keys:', error)
    if (error.message.includes('PermissionError')) {
      toast.error('You do not have permission to access the API keys.')
    } else {
      toast.error('An error occurred while retrieving the API keys.')
    }
  }
}

onMounted(() => {
  getapikey()
})
</script>
