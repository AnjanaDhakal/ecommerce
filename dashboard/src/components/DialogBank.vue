<template>
  <Dialog v-model="displaybank.isDisplay" v-if="messageStatus === 'success'">
    <template #body-title>
      {{ active_data ? 'Bank Withdrawal Request Chat' : 'Bank Withdrawal Request' }}
    </template>
    <template #body-content>
      <div class="space-y-4">
        <transition name="fade">
          <div
            v-if="active_data"
            class="p-1 rounded-lg border border-yellow-400 bg-yellow-100 text-yellow-800 flex items-center animate-slide-in"
          >
            <div class="flex items-center gap-2 text-sm">
              <span
                class="border bg-yellow-600 rounded-full text-white text-xs flex items-center justify-center w-6 h-6"
              >
                {{ active_data }}
              </span>
              <strong class="text-gray-800"> Pending Payment Request </strong>
            </div>
          </div>
        </transition>

        <div v-if="active_data">
          <!-- Left Column: Form or Summary (your original form can stay here) -->
          <div class="space-y-4">
            <!-- Your existing form stays here if needed -->
          </div>

          <!-- Right Column: WhatsApp-like Chat UI -->
          <div class="flex flex-col border rounded-lg h-[400px]">
            <!-- Chat Messages -->

            <div
              ref="chatContainer"
              class="flex-1 overflow-y-auto p-4 space-y-3 rounded-t-lg"
            >
              <div
                v-for="(msg, index) in messages"
                :key="index"
                :class="[
                  'max-w-xs px-4 py-2 rounded-lg text-sm',
                  msg.from === 'me'
                    ? 'ml-auto bg-green-500 text-white rounded-br-none'
                    : 'mr-auto bg-gray-200 text-gray-800 rounded-bl-none',
                ]"
              >
                {{ msg.text }}
              </div>
            </div>

            <!-- Chat Input -->
            <div class="p-2 bg-white flex items-center gap-2 rounded-b-lg">
              <input
                v-model="newMessage"
                @keyup.enter="sendMessage"
                type="text"
                placeholder="Type a message"
                class="flex-1 border rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
              <button
                @click="sendMessage"
                class="px-3 py-2 bg-green-600 text-white rounded-full hover:bg-green-700"
              >
                Send
              </button>
            </div>
          </div>
        </div>

        <div v-else class="space-y-4">
          <div>
            <p class="text-sm text-gray-600">
              <span>*</span>
              Please note that bank details may be changed once in a 3-month
              period. Write the valid reason to change the bank account in the
              description.
            </p>
          </div>
          <!-- Bank Name -->
          <div>
            <label class="text-sm font-semibold text-gray-700 block mb-1">
              Bank Name <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.bank_code"
              :disabled="isDisabled"
              required
              class="w-full p-2 border border-gray-300 text-base rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              style="position: relative; z-index: 10"
            >
              <option value="" disabled>Select Bank</option>
              <option
                v-for="bank in bankOptions"
                :key="bank.name"
                :value="bank.name"
              >
                {{ bank.bank_name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Account Holder Name -->
            <div>
              <label class="text-sm font-semibold text-gray-700 block mb-1">
                Account Holder Name <span class="text-red-500">*</span>
              </label>
              <Input
                v-model="form.ac_holder_name"
                placeholder="Enter Account Holder Name"
                required
                :disabled="isDisabled"
                @blur="form.ac_holder_name = form.ac_holder_name?.trim()"
              />
            </div>
            <!-- Account Number -->
            <div>
              <label class="text-sm font-semibold text-gray-700 block mb-1">
                Bank Account Number <span class="text-red-500">*</span>
              </label>
              <Input
                v-model="form.account_number"
                placeholder="Enter Account Number"
                required
                :disabled="isDisabled"
                @blur="form.account_number = form.account_number?.trim()"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Branch -->
            <div>
              <label class="text-sm font-semibold text-gray-700 block mb-1">
              </label>
              <Input
                v-model="form.branch"
                placeholder="Enter Branch Name"
                required
                :disabled="isDisabled"
                @blur="form.branch = form.branch?.trim()"
              />
            </div>
            <!-- Phone -->
            <div>
              <label class="text-sm font-semibold text-gray-700 block mb-1">
              </label>
              <Input
                v-model="form.phone"
                placeholder="Enter Phone Number"
                required
                :disabled="isDisabled"
                pattern="\d*"
                maxlength="10"
                @blur="form.phone = form.phone?.trim()"
              />
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="text-sm font-semibold text-gray-700 block mb-1">
              Description
            </label>
            <textarea
              v-model="form.description"
              placeholder="Enter description"
              required
              :disabled="isDisabled"
              rows="4"
              class="w-full p-2 border text-base border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div class="flex flex-row justify-between items-center gap-4 mt-4">
            <!-- Amount -->
            <div class="flex-1">
              <label class="text-sm font-semibold text-gray-700 block mb-1">
                Amount
              </label>
              <div class="text-gray-900 font-medium">{{ newAmount }}</div>
            </div>

            <!-- Submit Button -->
            <div>
              <button
                :disabled="isDisabled"
                @click="submitRequest"
                :class="[
                  'px-6 py-2 text-base rounded focus:outline-none',
                  isDisabled
                    ? 'bg-gray-400 text-white cursor-not-allowed'
                    : 'bg-black text-white hover:bg-gray-800',
                ]"
              >
                Request Payment
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { useToast } from 'vue-toastification'
import { Dialog, Input } from 'frappe-ui'
import { ref, watch, computed, onMounted, nextTick } from 'vue'
import { displaybank } from '../composables/displaybank'
import vendorbank from '../data/vendorbank'
import chat from '../data/chat'

const toast = useToast()
const props = defineProps({
  messageStatus: String,
  amount: Number,
})

// Form state
const form = ref({
  bank_code: '',
  account_number: '',
  branch: '',
  phone: '',
  ac_holder_name: '',
  amount: props.amount?.toFixed(2) ?? '0.00',
  description: '',
})

const active_data = ref('')
const bankOptions = ref([])
const newAmount = ref(props.amount)
let hasInteracted = false
const chatContainer = ref(null)

// Chat-related refs
const newMessage = ref('')
const messages = ref('')

// Chat method
// function sendMessage() {
//   const trimmed = newMessage.value.trim()
//   if (!trimmed) return

//   messages.value.push({ from: 'me', text: trimmed })
//   newMessage.value = ''

//   // Simulated response
//   setTimeout(() => {
//     messages.value.push({ from: 'other', text: 'Got your message.' })
//   }, 1000)
// }

watch(
  () => form.value.bank_code,
  (newVal, oldVal) => {
    if (!hasInteracted) {
      hasInteracted = true
      return
    }

    if (newVal !== oldVal && newVal) {
      form.value.account_number = ''
      form.value.branch = ''
      form.value.phone = ''
      form.value.ac_holder_name = ''
      form.value.description = ''
    }
  },
)

watch(
  () => props.amount,
  (val) => {
    newAmount.value = val
    form.value.amount = typeof val === 'number' ? val.toFixed(2) : '0.00'
  },
  { immediate: true },
)

const reference_name = ref('')

const fetchBanks = async () => {
  try {
    const res = await vendorbank.fetch()
    if (res?.data) {
      const bankData = res.data
      bankOptions.value = bankData.banks || []
      active_data.value = bankData.active_request || ''

      // Match default bank name to get the bank code
      const matchedBank = bankOptions.value.find(
        (b) => b.bank_name === bankData.bank_name,
      )

      form.value = {
        ...form.value,
        bank_code: matchedBank?.name || '',
        account_number: bankData.account_number || '',
        branch: bankData.branch_name || '',
        phone: bankData.primary_phone || '',
        ac_holder_name: bankData.ac_holder_name || '',
      }

      // Set reference_name to the first doc_name.name from the response
      reference_name.value = bankData.doc_name?.[0]?.name || ''
    }
  } catch (err) {
    console.error('Error fetching banks:', err)
  }
}

watch(
  () => props.messageStatus,
  (val) => {
    if (val === 'success') fetchBanks()
  },
  { immediate: true },
)

watch(messages, () => {
  nextTick(scrollToBottom)
})

watch(
  () => displaybank.isDisplay,
  async (visible) => {
    if (visible && messageStatus.value === 'success') {
      await nextTick()
      scrollToBottom()
    }
  },
)

// Submit handler
const submitRequest = async () => {
  if (
    !form.value.bank_code ||
    !form.value.account_number ||
    !form.value.ac_holder_name ||
    !newAmount
  ) {
    toast.error('Please fill all required fields')
    return
  }

  try {
    const payload = {
      ...form.value,
      bank_name: form.value.bank_code, // send code as bank_name
    }
    delete payload.bank_code
    payload.amount = newAmount.value

   //  //console.log('Submitting payload:', payload)

    const response = await fetch(
      '/api/method/ecommerce.api.vendor_bank_request',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      },
    )

    const result = await response.json()

    if (response.ok) {
      toast.success('Payment request send successfully')
      window.location.reload() // Reload the page to reflect changes
     //  //  console.log('API Response:', result)
      displaybank.isDisplay = false
      form.value = {
        bank_code: '',
        account_number: '',
        branch: '',
        phone: '',
        ac_holder_name: '',
        amount: newAmount.value,
        description: '',
      }
    } else {
      console.error('API Error:', result)
    }
  } catch (error) {
    console.error('Error:', error)
  }
}

const fetchchats = async () => {
  try {
    const res = await chat.fetch()
   //  //console.log('Chat Data:', res)

    messages.value = [
      { from: 'other', text: 'Hello! You have 1 active request' },
      ...res.data.chat.map((comment) => ({
        from: comment.from === 'me' ? 'me' : 'other',
        text: comment.content,
      })),
    ]

    scrollToBottom()
  } catch (err) {
    console.error('Error fetching chats:', err)
  }
}

const scrollToBottom = () => {
  const el = chatContainer.value
  if (el) el.scrollTop = el.scrollHeight
}
const messageStatus = ref('success')

watch(
  () => displaybank.isDisplay,
  (visible) => {
    if (visible && messageStatus.value === 'success') {
      scrollToBottom()
    }
  },
)

watch(messages, scrollToBottom)

const chatpost = async (content, reference_name) => {
 //  // console.log('Posting comment:', { content, reference_name });

  const response = await fetch('/api/method/ecommerce.api.post_payment_comment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, reference_name }),
  })

  const data = await response.json()
 //  // console.log('API response:', data);

  if (data.status === 'success') {
    toast.success('Comment posted successfully')
    return data.data
  } else {
    throw new Error(data.message)
  }
}

const sendMessage = async () => {
  const trimmed = newMessage.value.trim()
  if (!trimmed) return

  messages.value.push({ from: 'me', text: trimmed })
  newMessage.value = ''

  await nextTick() // Wait for the new message to render
  scrollToBottom()

  try {
    await chatpost(trimmed, reference_name.value)
  } catch (error) {
    // Optional: Show a toast or revert message if sending fails
  }
}

onMounted(() => {
  fetchchats()
  fetchBanks()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.animate-slide-in {
  animation: slideIn 0.4s ease-out forwards;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
