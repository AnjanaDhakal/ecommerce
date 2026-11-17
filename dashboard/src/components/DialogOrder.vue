<template>
  <Dialog
    :options="dialogOptions"
    :modelValue="displayDialog.isDisplay"
    @update:modelValue="handleMainDialogToggle"
  >
    <template #body-content>
      <div
        ref="orderFormContainer"
        class="min-h-0 max-h-[calc(100dvh-16rem)] overflow-y-auto overscroll-contain px-2 font-bold"
        style="-webkit-overflow-scrolling: touch; scrollbar-gutter: stable;"
        @keydown.enter="focusNextFormField"
      >
        <div class="space-y-3">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-start">
          <div class="space-y-1">
            <label class="block text-sm text-gray-600 font-bold"
              >Order Type <span class="text-red-500">*</span></label
            >
            <FormControl
              class="w-56"
              type="select"
              :options="[
                { label: 'Regular', value: 'Regular' },
                { label: 'Exchange', value: 'Exchange' },
                { label: 'Return', value: 'Return' },
              ]"
              size="sm"
              variant="subtle"
              placeholder="select"
              :disabled="false"
              label=""
              v-model="newOrder.orderType"
            />
          </div>

          <div v-if="isReturn" class="space-y-1">
            <label class="block text-sm text-gray-600 font-bold"
              >Return Shipping Type <span class="text-red-500">*</span></label
            >
            <FormControl
              class="w-56"
              type="select"
              :options="[
                { label: 'Pickup', value: 'Pickup' },
                { label: 'Drop-off', value: 'Drop-off' },
              ]"
              size="sm"
              variant="subtle"
              placeholder="select"
              :disabled="false"
              label=""
              v-model="newOrder.return_shipping_type"
            />
          </div>
        </div>
        <div class="border-t border-gray-200 pt-3 overflow-visible">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3 overflow-visible">
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold">
            Reference ID (Unique Order ID)
          </label>
          <FormControl
            class="w-full"
            type="text"
            size="sm"
            variant="subtle"
            placeholder="Reference ID"
            :disabled="false"
            label=""
            v-model="newOrder.vendorTrackingNumber"
          />
          <div
            v-if="referenceInfo.exists"
            class="mt-1 text-xs text-red-500 leading-4"
          >
            This reference ID already exists for order
            {{ referenceInfo.orderId }} and customer
            {{ referenceInfo.customerName }}, You cannot use this.
          </div>
          <!-- <div class="flex items-center w-56 gap-1 mt-1 text-xs text-gray-500">
            <span>
              Optional field — skip if you don’t have a unique system ID.
            </span>
          </div> -->
        </div>

        <div class="w-full space-y-1">
          <label class="block text-sm text-gray-600 font-bold">
            {{ isReturn ? 'Received Address' : 'Pickup Address' }}
            <span class="text-red-500">*</span>
          </label>
          <FormControl
            class="w-full"
            type="select"
            :options="pickupAddress"
            size="sm"
            variant="subtle"
            placeholder="Select Address"
            :disabled="false"
            label=""
            v-model="newOrder.businessAddress"
          />
        </div>

        <div class="space-y-1 cursor-not-allowed w-full">
          <label class="block text-sm text-gray-600 font-bold">
            {{ isReturn ? 'Receive Branch' : 'Pickup Branch' }}
            <span class="text-red-500">*</span>
          </label>
          <FormControl
            class="w-full"
            type="text"
            size="sm"
            variant="subtle"
            :model-value="pickupBranchLabel"
            disabled
            placeholder="Pickup Branch"
          />
        </div>
          </div>
        </div>
        <div class="border-t border-gray-200 pt-3">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold">
            Customer Name <span class="text-red-500">*</span>
          </label>
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            placeholder="customer name"
            :disabled="false"
            label=""
            v-model="newOrder.customerName"
            ref="customerNameInput"
          />
        </div>
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold">
            Mobile <span class="text-red-500">*</span>
          </label>
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            placeholder="mobile"
            :disabled="false"
            v-model="newOrder.primaryMobileNo"
            pattern="\d*"
            maxlength="10"
          />
        </div>
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold">
            Secondary Phone
          </label>
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            placeholder="phone"
            :disabled="false"
            label=""
            v-model="newOrder.secondaryMobileNo"
            pattern="\d*"
            maxlength="10"
          />
        </div>
          </div>
        </div>

        <div class="border-t border-gray-200 pt-3">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div class="w-full space-y-1">
          <div class="relative pr-7">
            <label class="block text-sm text-gray-600 font-bold">
              {{ isReturn ? 'Pickup Branch' : 'Destination Branch' }}
              <span class="text-red-500">*</span>
            </label>
            <router-link
              to="/branch"
              class="absolute right-0 top-1/2 inline-flex h-6 w-6 -translate-y-1/2 items-center justify-center text-gray-500 transition hover:text-green-600"
              title="Open branch page"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="h-3.5 w-3.5"
              >
                <circle cx="12" cy="12" r="10" />
                <path d="M9.09 9a3 3 0 0 1 5.82 1c0 2-3 3-3 3" />
                <path d="M12 17h.01" />
              </svg>
            </router-link>
          </div>
          <BranchSelect
            class="order-form-branch-select w-full"
            :options="branchOptions"
            placeholder="Search branch, area, district or municipality..."
            :auto-select-first-area="false"
            v-model="newOrder.destinationBranch"
            @change="handleDestinationBranchChange"
          />
        </div>
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold">
            Area/City <span class="text-red-500">*</span>
          </label>
          <FormControl
            ref="destinationCityAreaInput"
            :type="'text'"
            size="sm"
            variant="subtle"
            maxlength="100"
            placeholder="area/city"
            :disabled="false"
            label=""
            v-model="newOrder.destinationCityArea"
          />
        </div>
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold mb-1">
            Landmark <span class="text-red-500">*</span>
          </label>
          <FormControl
            :type="'text'"
            size="sm"
            variant="subtle"
            maxlength="100"
            placeholder="landmark"
            :disabled="false"
            label=""
            v-model="newOrder.landmark"
          />
        </div>
          </div>
        </div>

        <div class="border-t border-gray-200 pt-3">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div v-if="!isReturn" class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold"
            >COD Amount
          </label>
          <FormControl
            class="w-full"
            type="number"
            size="sm"
            variant="subtle"
            placeholder="cod amount"
            :disabled="false"
            label=""
            v-model="newOrder.codAmount"
            @input="validateNumberInput"
          />
            <div>
                <span class="text-[11px] text-green-500"
                  >Total cod amount including delivery charge</span
                >
              </div>
        </div>
        <div class="space-y-2 md:col-span-2 overflow-visible">


            <div class="grid grid-cols-1 gap-2 xl:grid-cols-2 overflow-visible">
            <label
              class="group relative flex min-h-[74px] items-center justify-between rounded-xl border border-gray-200 bg-white px-2 py-1 cursor-pointer transition-colors"
              :class="
                Number(newOrder.express_delivery) === 0
                  ? 'border-green-600 ring-1 ring-green-600'
                  : 'hover:border-gray-300'
              "
            >
              <div class="flex items-center gap-1.5">
                <input
                  type="radio"
                  name="express_delivery"
                  :value="0"
                  v-model="newOrder.express_delivery"
                  class="sr-only"
                />
                <span
                  class="flex h-3.5 w-3.5 items-center justify-center rounded-full border"
                  :class="
                    Number(newOrder.express_delivery) === 0
                      ? 'border-green-600 bg-green-600 text-white'
                      : 'border-gray-300 bg-white text-transparent'
                  "
                >
                  <svg
                    class="h-2 w-2"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M5 10.5l3.2 3.2L15 7" />
                  </svg>
                </span>
                <div class="flex flex-col leading-none">
                  <span class="text-md font-bold text-gray-700">Standard</span>
                    <span class="mt-0.5 text-[9px] font-bold text-green-600">Regular delivery</span>
                </div>
              </div>
              <div class="text-right whitespace-nowrap">
                <div class="text-[16px] font-bold leading-none text-gray-700">
                  Rs {{ formatDeliveryCharge(deliveryTypeRates.standard) }}
                </div>
              </div>
            </label>

            <div v-if="hasExpressDeliveryRate" class="relative">
              <button
                type="button"
                class="absolute right-2 top-2 z-10 flex h-6 w-6 items-center justify-center text-xs font-bold leading-none text-gray-500 hover:text-gray-700"
                @click.stop.prevent="confirmExpressDelivery()"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="h-3.5 w-3.5"
                >
                  <circle cx="12" cy="12" r="10" />
                  <path d="M12 16v-4" />
                  <path d="M12 8h.01" />
                </svg>
              </button>
              <label
                class="flex min-h-[74px] items-center justify-between rounded-xl border border-gray-200 bg-white px-2 py-1 transition-colors"
                :class="
                  Number(newOrder.express_delivery) === 1
                    ? 'cursor-pointer border-green-600 ring-1 ring-green-600'
                    : 'cursor-pointer hover:border-gray-300'
                "
              >
                <div class="flex min-w-0 flex-1 items-center gap-1.5">
                  <input
                    type="radio"
                    name="express_delivery"
                    :value="1"
                    v-model="newOrder.express_delivery"
                    class="sr-only"
                  />
                  <span
                    class="flex h-3.5 w-3.5 items-center justify-center rounded-full border flex-shrink-0"
                    :class="
                      Number(newOrder.express_delivery) === 1
                        ? 'border-green-600 bg-green-600 text-white'
                        : 'border-gray-300 bg-white text-transparent'
                    "
                  >
                  <svg
                    class="h-2 w-2"
                    viewBox="0 0 20 20"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  >
                    <path d="M5 10.5l3.2 3.2L15 7" />
                  </svg>
                </span>
                <div class="flex flex-col leading-none gap-0.5">
                  <span class="text-md font-bold text-gray-700">2PM Express</span>
                  <span class="mt-0.5 text-[9px] font-bold text-green-600">
                    Pickup by 2PM, same day delivery
                  </span>
                   <span class="mt-0.5 text-[9px] font-bold text-gray-500">
                     Pickup available Inside Ringroad Only
                  </span>

                </div>
              </div>
              <div class="text-right whitespace-nowrap flex-shrink-0 ml-4">
                <div class="text-[16px] font-bold leading-none text-gray-700">
                  Rs {{ formatDeliveryCharge(deliveryTypeRates.express) }}
                </div>
              </div>
              </label>
            </div>
          </div>
        </div>
        <div>
          <label class="block text-sm text-gray-600 font-bold">Weight(Kg)</label>
          <FormControl class="w-57" type="number" min="0" max="30" size="sm" variant="subtle" placeholder="weight" :disabled="false"
            label="" v-model="newOrder.weight" @focus="clearDefaultWeight" />
          <p v-if="weightLimitError" class="mt-1 text-xs text-red-600" role="alert">
            {{ weightLimitError }}
          </p>
        </div>
         <div class="flex flex-col gap-1 justify-center">
          <label class="block text-sm text-gray-600 font-bold"
            >Delivery Charge Rs {{ newOrder.delivery_amount }}</label
          >
        </div>
          </div>
        </div>
        <div class="border-t border-gray-200 pt-3">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3">
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold"
            >Description</label
          >
          <FormControl
            :type="'textarea'"
            size="sm"
            variant="outline"
            maxlength="140"
            placeholder="description"
            :disabled="false"
            label=""
            v-model="newOrder.orderDescription"
          />
        </div>
        <div class="space-y-1">
          <label class="block text-sm text-gray-600 font-bold"
            >Instruction</label
          >
          <FormControl
            type="textarea"
            size="sm"
            variant="outline"
            maxlength="140"
            placeholder="instruction"
            :disabled="false"
            label=""
            v-model="newOrder.instruction"
          />
        </div>
        <div v-if="resultgreendeliverycheck" class="space-y-5">
          <label class="block text-sm text-gray-600 font-bold mb-5"
            >Green Delivery Available</label
          >
          <div class="flex items-center">
            <span class="mr-2 text-gray-600 text-xs"
              >Enable For Green Delivery</span
            >
            <Switch size="md" :value="false" v-model="newOrder.enableGreen" />
          </div>
        </div>
          </div>
        </div>

        <div v-if="errorMessage" class="text-sm text-red-500">
        {{ errorMessage }}
        </div>
        </div>
      </div>
    </template>
  </Dialog>
    <Dialog
      :modelValue="showDialog2"
      @update:modelValue="(value) => (showDialog2 = value)"
    >
    <template #body-title>
      <h3>Express Delivery</h3>
    </template>
    <template #body-content>
      <div>
        <table class="w-full overflow-hidden rounded-lg border border-gray-200 text-sm">
          <tbody>
            <tr class="border-b">
              <td class="p-3 text-gray-600">Base delivery amount</td>
              <td class="p-3 text-right font-bold text-gray-700">
                Rs {{ formatDeliveryCharge(deliveryTypeRates.expressBase) }}
              </td>
            </tr>

            <tr class="border-b">
              <td class="p-3 text-gray-600">Pickup charge</td>
              <td class="p-3 text-right font-bold text-gray-700">
                Rs {{ formatDeliveryCharge(deliveryTypeRates.expressPickupCharge) }}
              </td>
            </tr>

            <tr class="border-b bg-gray-200">
              <td class="p-3 text-gray-600">Total</td>
              <td class="p-3 text-right font-bold text-gray-700">
                Rs {{ formatDeliveryCharge(deliveryTypeRates.express) }}
              </td>
            </tr>

            <tr>
              <td colspan="2" class="p-3 font-semibold text-red-500">
                <ul class="list-disc space-y-1 pl-5">
                  <li>Pickup available Inside Ringroad Only</li>
                  <li>Orders placed after 1:30 PM are not eligible for pickup and same-day delivery.</li>
                  <li>Pickup charges are waived when you place 3 or more orders.</li>
                </ul>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

  </Dialog>

</template>

<script setup>
import { useToast } from 'vue-toastification'
import { Dialog, FormControl, Switch } from 'frappe-ui'
import { displayDialog } from '../composables/displayDialog'
import { onMounted, ref, watch, computed, nextTick } from 'vue'
import branch from '../data/branch'
import vendorAddressBranchInfo from '../data/vendorAddressBranchInfo'
import BranchSelect from './BranchSelect.vue'

const toast = useToast()
const emit = defineEmits(['OrderCreated'])
const orderFormContainer = ref(null)
const customerNameInput = ref(null)
const destinationCityAreaInput = ref(null)

const newOrder = ref({
  customerName: '',
  primaryMobileNo: '',
  secondaryMobileNo: '',
  destinationCityArea: '',
  landmark: '',
  destinationBranch: 'KATHMANDU VALLEY',
  codAmount: '',
  weight: 0,
  orderDescription: '',
  instruction: '',
  enableGreen: false,
  orderType: '',
  pickup_branch: '',
  businessAddress: '',
  vendorTrackingNumber: '',
  delivery_amount: '',
  medium: 'Portal',
  return_shipping_type: 'Pickup',
  express_delivery: 0,
})

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token') || ''

const isReturn = computed(() => newOrder.value.orderType === 'Return')

const weightLimitError = computed(() =>
  Number(newOrder.value.weight) > 30
    ? 'Weight cannot be more than 30 kg.'
    : '',
)

const clearDefaultWeight = () => {
  if (newOrder.value.weight === 0 || newOrder.value.weight === '0') {
    newOrder.value.weight = ''
  }
}

const showDialog2 = ref(false) // State for showing the express delivery unavailable dialog
const handleMainDialogToggle = (value) => {
  if (!value && showDialog2.value) {
    showDialog2.value = false
    return
  }

  displayDialog.isDisplay = value
}
const errorMessage = ref('')
const referenceInfo = ref({
  exists: false,
  orderId: null,
  customerName: null,
  vendorTrackingNumber: '',
})
const deliveryTypeRates = ref({
  standard: null,
  express: null,
  expressBase: null,
  expressPickupCharge: null,
})
const hasExpressDeliveryRate = computed(
  () => deliveryTypeRates.value.express !== null,
)

const formatDeliveryCharge = (amount) => {
  if (amount === null || amount === undefined || amount === '') {
    return '--'
  }

  const numericAmount = Number(amount)
  return Number.isFinite(numericAmount) ? numericAmount : '--'
}

const focusCustomerName = () => {
  nextTick(() => {
    const el =
      customerNameInput.value?.$el?.querySelector('input,textarea,select') ||
      customerNameInput.value?.$el ||
      customerNameInput.value
    el?.focus?.()
  })
}

const focusDestinationCityArea = () => {
  nextTick(() => {
    const el =
      destinationCityAreaInput.value?.$el?.querySelector(
        'input,textarea,select',
      ) ||
      destinationCityAreaInput.value?.$el ||
      destinationCityAreaInput.value
    el?.focus?.()
  })
}

const focusNextFormField = (event) => {
  if (event.defaultPrevented || event.isComposing) {
    return
  }

  if (event.target instanceof HTMLTextAreaElement && event.shiftKey) {
    return
  }

  const container = orderFormContainer.value
  if (!(container instanceof HTMLElement)) {
    return
  }

  const selector = [
    'input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]):not([disabled]):not([readonly])',
    'textarea:not([disabled]):not([readonly])',
    'select:not([disabled])',
    '.order-form-branch-select button[type="button"]:not([disabled])',
  ].join(',')

  const fields = Array.from(container.querySelectorAll(selector)).filter(
    (field) => field instanceof HTMLElement && field.getClientRects().length,
  )
  const currentIndex = fields.findIndex(
    (field) => field === event.target || field.contains(event.target),
  )
  const nextField = fields[currentIndex + 1]

  if (!(nextField instanceof HTMLElement)) {
    return
  }

  event.preventDefault()
  nextField.focus()
}

const DIALOG_LAYER_Z_INDEX = '120'

const findDialogRootByTitle = (title) => {
  const normalizedTitle = `${title || ''}`.trim().toLowerCase()
  const dialogCandidates = Array.from(document.querySelectorAll('.fixed.inset-0'))

  return dialogCandidates.find((candidate) => {
    if (!(candidate instanceof HTMLElement)) {
      return false
    }

    const textContent = candidate.textContent?.trim().toLowerCase() || ''
    if (normalizedTitle && textContent.includes(normalizedTitle)) {
      return true
    }

    return candidate.querySelector(`[data-dialog="${title}"]`) !== null
  })
}

const elevateDialogLayer = async (title, attempts = 6) => {
  for (let index = 0; index < attempts; index += 1) {
    await nextTick()

    const dialogRoot = findDialogRootByTitle(title)
    if (dialogRoot instanceof HTMLElement) {
      dialogRoot.style.zIndex = DIALOG_LAYER_Z_INDEX
      return true
    }

    await new Promise((resolve) => window.setTimeout(resolve, 16))
  }

  return false
}

const fetchJsonWithTimeout = async (url, options = {}, timeoutMs = 20000) => {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    })
    const responseData = await response.json()
    return { response, responseData }
  } finally {
    clearTimeout(timer)
  }
}

const resetReferenceInfo = () => {
  referenceInfo.value = {
    exists: false,
    orderId: null,
    customerName: null,
    vendorTrackingNumber: '',
  }
}

const checkReferenceNumber = async (vendorTrackingNumber) => {
  const referenceId = `${vendorTrackingNumber || ''}`.trim()

  if (!referenceId) {
    resetReferenceInfo()
    return
  }

  const url = `${Frappe_URL}/api/method/ecommerce.api.get_reference_number?vendorTrackingNumber=${encodeURIComponent(referenceId)}`

  try {
    const { response, responseData } = await fetchJsonWithTimeout(url, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      method: 'GET',
    })
    const data = responseData?.message?.data

    if (
      response.ok &&
      responseData?.message?.status === 'success' &&
      data?.exists
    ) {
      referenceInfo.value = {
        exists: true,
        orderId: data.order_id,
        customerName: data.customer_name,
        vendorTrackingNumber: data.vendor_tracking_number,
      }
      return
    }

    resetReferenceInfo()
  } catch (error) {
    resetReferenceInfo()
  }
}

const validateNumberInput = (event) => {
  const value = event.target.value
  // Remove any non-numeric characters
  event.target.value = value.replace(/[^0-9.]/g, '')
  newOrder.value.codAmount = event.target.value
}

const handleDestinationBranchChange = (selection) => {
  newOrder.value.destinationCityArea = selection?.area || ''
  focusDestinationCityArea()
}

const getFieldValue = (field) => {
  if (field && typeof field === 'object') {
    return field.value || field.label || ''
  }
  return field || ''
}

const getOrderErrorMessage = (responseData) => {
  const message = responseData?.message

  if (typeof message === 'string' && message.trim()) {
    return message
  }

  if (message && typeof message === 'object') {
    if (typeof message.message === 'string' && message.message.trim()) {
      return message.message
    }

    if (typeof message.exc === 'string' && message.exc.trim()) {
      return message.exc
    }
  }

  return 'If you encounter a technical error while adding an order, please send us a screenshot on our Technical WhatsApp number 9801230106 for quick support.'
}

const validateForm = () => {
  const phoneNumberPattern = /^\d{10}$/
  const customerName = `${newOrder.value.customerName || ''}`.trim()
  const primaryMobileNo = `${newOrder.value.primaryMobileNo || ''}`.trim()
  const secondaryMobileNo = `${newOrder.value.secondaryMobileNo || ''}`.trim()
  const landmark = `${newOrder.value.landmark || ''}`.trim()
  const destinationCityArea =
    `${newOrder.value.destinationCityArea || ''}`.trim()
  const businessAddress = getFieldValue(newOrder.value.businessAddress).trim()
  const destinationBranch = getFieldValue(
    newOrder.value.destinationBranch,
  ).trim()
  const orderType = `${newOrder.value.orderType || ''}`.trim()
  const codAmount = `${newOrder.value.codAmount ?? ''}`.trim()
  const packageWeight = Number(newOrder.value.weight || 0)

  if (!customerName) {
    errorMessage.value = 'Please provide customer name.'
    return false
  } else if (!primaryMobileNo || !phoneNumberPattern.test(primaryMobileNo)) {
    errorMessage.value =
      'Please provide a valid primary mobile number with exactly 10 digits.'
    return false
  } else if (secondaryMobileNo && !phoneNumberPattern.test(secondaryMobileNo)) {
    errorMessage.value =
      'Please provide a valid secondary mobile number with exactly 10 digits.'
    return false
  } else if (!landmark) {
    errorMessage.value = 'Please provide landmark.'
    return false
  } else if (!destinationCityArea) {
    errorMessage.value = 'Please provide destination city area.'
    return false
  } else if (!businessAddress) {
    errorMessage.value = 'Please provide business address.'
    return false
  } else if (!destinationBranch) {
    errorMessage.value = 'Please provide destination branch.'
    return false
  } else if (!orderType) {
    errorMessage.value = 'Please provide order type.'
    return false
  } else if (!Number.isFinite(packageWeight) || packageWeight < 0 || packageWeight > 30) {
    errorMessage.value = 'Weight must be between 0 and 30 kg.'
    return false
  } else if (!isReturn.value && !codAmount) {
    errorMessage.value = 'Please provide COD amount.'
    return false
  }
  errorMessage.value = ''
  return true
}

const confirmExpressDelivery = async () => {
  return new Promise((resolve) => {
    showDialog2.value = true // Show the dialog
  })
}


const createNewOrderAndContinue = async () => {
  if (!validateForm()) {
    return
  }
  const apiUrl = `${Frappe_URL}/api/method/ecommerce.api.create_order`

  try {
    const orderData = {
      ...newOrder.value,
      destinationBranch:
        newOrder.value.destinationBranch?.value ||
        newOrder.value.destinationBranch ||
        'KATHMANDU VALLEY',
      pickup_branch: newOrder.value.pickup_branch?.value || '',
      businessAddress: getFieldValue(newOrder.value.businessAddress),
      return_shipping_type: newOrder.value.return_shipping_type || 'Pickup',
      express_delivery: newOrder.value.express_delivery,
    }

    const { response, responseData } = await fetchJsonWithTimeout(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(orderData),
    })

    if (response.ok && responseData.message.status === 'success') {
      emit('OrderCreated', newOrder.value)
      displayDialog.isDisplay = true
     //  //console.log(responseData);
      toast.success('Order created successfully')
      resetForm()
    } else {
      errorMessage.value = getOrderErrorMessage(responseData)
    }
  } catch (error) {
    errorMessage.value =
      error?.name === 'AbortError'
        ? 'Order creation timed out. Please try again.'
        : `Error creating order: ${error.message || error}. If you encounter a technical error while adding an order, please send us a screenshot on our Technical WhatsApp number 9801230106 for quick support.`
  }
}

const createNewOrder = async () => {
  if (!validateForm()) {
    return
  }

  const apiUrl = `${Frappe_URL}/api/method/ecommerce.api.create_order`
 //  // console.log('Checkbox value:', newOrder.value.enableGreen);
  try {
    const orderData = {
      ...newOrder.value,
      destinationBranch:
        newOrder.value.destinationBranch?.value ||
        newOrder.value.destinationBranch ||
        'KATHMANDU VALLEY',
      pickup_branch: newOrder.value.pickup_branch?.value || '',
      businessAddress: getFieldValue(newOrder.value.businessAddress),
      return_shipping_type: newOrder.value.return_shipping_type || 'Pickup',
      express_delivery: newOrder.value.express_delivery,
    }
//console.log('Order Data:', orderData);
    const { response, responseData } = await fetchJsonWithTimeout(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(orderData),
    })
   //  // console.log("jgkj",responseData.message.data.status)
    if (response.ok && responseData.message.status === 'success') {
      emit('OrderCreated', newOrder.value)
      displayDialog.isDisplay = false
      toast.success('Order created successfully')
     //  // console.log(responseData)
      resetForm()
      window.location.reload()
    } else {
      errorMessage.value = getOrderErrorMessage(responseData)
    }
  } catch (error) {
    errorMessage.value =
      error?.name === 'AbortError'
        ? 'Order creation timed out. Please try again.'
        : `Error creating order: ${error.message || error}. If you encounter a technical error while adding an order, please send us a screenshot on our Technical WhatsApp number 9801230106 for quick support.`
  }
}

const setDefaultValues = () => {
  newOrder.value.codAmount = 0
  newOrder.value.orderType = 'Regular'
  //newOrder.value.weight = '1'
}

const resetForm = () => {
  const defaultBusiness = pickupAddress.value?.[0]?.value || ''
  const defaultPickupBranch = pickupBranch.value?.[0] || ''

  newOrder.value = {
    customerName: '',
    primaryMobileNo: '',
    secondaryMobileNo: '',
    destinationCityArea: '',
    landmark: '',
    destinationBranch: 'KATHMANDU VALLEY',
    codAmount: '',
    delivery_amount: '',
    is_paid_order: '',
    weight: 0,
    enableGreen: false,
    orderDescription: '',
    instruction: '',
    orderType: 'Regular',
    return_shipping_type: 'Pickup',
    express_delivery: 0,
    vendorTrackingNumber: '',
    medium: 'Portal',
    pickup_branch: defaultPickupBranch,
    businessAddress: defaultBusiness,
  }
  setDefaultValues()
  resetReferenceInfo()
  errorMessage.value = ''
}

const dialogOptions = {
  title: 'Add Order',
  description: 'Add new order',
  size: '3xl',
  actions: [
    {
      label: 'Place Order',
      variant: 'solid',
      onClick: createNewOrder,
    },
    {
      label: 'Add Order and Continue',
      variant: 'solid',
      onClick: createNewOrderAndContinue,
    },
  ],
}

const branchOptions = ref([])
const pickupAddress = ref([])
const pickupBranch = ref([])
const destinationBranch = 'KATHMANDU VALLEY'

const fetchBranchOptions = async () => {
  await branch.fetch()
  const branches =
    branch.data?.message?.data?.branches ||
    branch.data?.data?.branches ||
    branch.data?.branches ||
    []

  branchOptions.value = branches.map((item) => ({
    label: item.branch_name || item.name || '',
    value: item.branch_name || item.name || '',
    name: item.name || '',
    branch_name: item.branch_name || item.name || '',
    branch_code: item.branch_code || '',
    district: item.district || '',
    municipality: item.municipality || '',
    areas: Array.isArray(item.area) ? item.area : [],
  }))
}

const fetchAddressBranchInfo = async () => {
  await vendorAddressBranchInfo.fetch()
  const pickupAddressDetails = vendorAddressBranchInfo.data.data.addresses
  const pickupBranchDetails = vendorAddressBranchInfo.data.data.branches

  pickupAddress.value = pickupAddressDetails.map((address) => ({
    label: address,
    value: address,
  }))

  newOrder.value.businessAddress = pickupAddress.value[0]?.value || ''

  pickupBranch.value = pickupBranchDetails.map((branch) => ({
    label: branch,
    value: branch,
  }))
}

watch(
  () => newOrder.value.businessAddress,
  (newVal) => {
    if (!newVal) return
    const val = typeof newVal === 'object' ? newVal.value : newVal
    const index = pickupAddress.value.findIndex(
      (address) => address.value === val,
    )
    if (index !== -1) {
      newOrder.value.pickup_branch = pickupBranch.value[index]
    }
  },
)

watch(
  () => displayDialog.isDisplay,
  async (val) => {
    if (val) {
      await elevateDialogLayer(dialogOptions.title)
      resetForm()
      await nextTick()
      await refreshDeliveryTypeRates()
      focusCustomerName()
    }
  },
)

watch(showDialog2, async (val) => {
  if (val) {
    await elevateDialogLayer('Express Delivery')
  }
})

const deliveryDetails = ref([])

const pickupBranchLabel = computed(() => {
  const val = newOrder.value.pickup_branch
  if (!val) return ''
  return typeof val === 'object' ? val.label || val.value || '' : val
})

const refreshDeliveryTypeRates = async () => {
  const pickupBranchValue =
    typeof newOrder.value.pickup_branch === 'object'
      ? newOrder.value.pickup_branch?.value ||
        newOrder.value.pickup_branch?.label ||
        ''
      : newOrder.value.pickup_branch || ''

  const destinationBranchValue =
    typeof newOrder.value.destinationBranch === 'object'
      ? newOrder.value.destinationBranch?.value ||
        newOrder.value.destinationBranch?.label ||
        'KATHMANDU VALLEY'
      : newOrder.value.destinationBranch || 'KATHMANDU VALLEY'

  if (!pickupBranchValue || !destinationBranchValue) {
    return
  }

  await fetchdiscountInfo(
    pickupBranchValue,
    destinationBranchValue,
    newOrder.value.landmark,
    newOrder.value.destinationCityArea,
    newOrder.value.enableGreen,
    newOrder.value.express_delivery,
  )
}

const debounce = (func, wait) => {
  let timeout
  return (...args) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func.apply(this, args), wait)
  }
}

watch(
  [
    () => newOrder.value.pickup_branch,
    () => newOrder.value.destinationBranch,
    () => newOrder.value.landmark,
    () => newOrder.value.destinationCityArea,
    () => newOrder.value.enableGreen,
    () => newOrder.value.express_delivery,
  ],
  async ([newPickupBranch, newDestinationBranch]) => {
    const destinationBranch =
      typeof newDestinationBranch === 'object'
        ? newDestinationBranch.value ||
          newDestinationBranch.label ||
          'KATHMANDU VALLEY'
        : newDestinationBranch || 'KATHMANDU VALLEY'

    await debouncedFetchDiscountInfo(
      newPickupBranch.value,
      destinationBranch,
      newOrder.value.landmark,
      newOrder.value.destinationCityArea,
      newOrder.value.enableGreen,
      newOrder.value.express_delivery,
    )
  },
)

let resultgreendeliverycheck = ref(false)
const fetchdiscountInfo = async (
  pickupBranch,
  destinationBranch,
  landmark,
  destinationCityArea,
  enableGreen,
  deliveryType,
) => {
 //  //console.log('Fetching delivery rate for:', pickupBranch, destinationBranch, landmark, destinationCityArea, enableGreen);
  try {
    const expressDelivery = deliveryType
    const apiUrl = `${Frappe_URL}/api/method/ecommerce.api.get_delivery_rate?pickup_branch=${encodeURIComponent(pickupBranch)}&destination_branch=${encodeURIComponent(destinationBranch)}&location=${encodeURIComponent(landmark)}&city_area=${encodeURIComponent(destinationCityArea)}&green_delivery=${encodeURIComponent(enableGreen)}&express_delivery=${expressDelivery}`
  //  // console.log('API URL:', apiUrl);

    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Network response was not ok')
    }

    const result = await response.json()

    Object.assign(deliveryTypeRates.value, {
      standard: result?.message?.rate_details?.standard?.delivery_amount ?? null,
      express: result?.message?.rate_details?.express?.delivery_amount ?? null,
      expressBase:
        result?.message?.rate_details?.express?.base_delivery_amount ?? null,
      expressPickupCharge:
        result?.message?.rate_details?.express?.pickup_charge ?? null,
    })

    if (
      deliveryTypeRates.value.express === null &&
      Number(newOrder.value.express_delivery) === 1
    ) {
      newOrder.value.express_delivery = 0
    }

    if (result && result.message && result.message.total_delivery_sum) {
      const deliveryAmount = result.message.total_delivery_sum

      newOrder.value.delivery_amount = deliveryAmount
     //  //  console.log('Delivery Amount:', deliveryAmount);
    } else {
    }
    const resultgreendelivery = result.message.result
   //  // console.log('result:', resultgreendelivery);
    if (resultgreendelivery) {
      resultgreendeliverycheck.value = true
    } else {
      resultgreendeliverycheck.value = false
    }
  } catch (error) {
    Object.assign(deliveryTypeRates.value, {
      standard: null,
      express: null,
      expressBase: null,
      expressPickupCharge: null,
    })
    // console.error('Error fetching discount info:', error);
  }
}

const debouncedFetchDiscountInfo = debounce(fetchdiscountInfo, 300)
const debouncedCheckReferenceNumber = debounce(checkReferenceNumber, 300)

watch(
  () => newOrder.value.vendorTrackingNumber,
  (value) => {
    const referenceId = `${value || ''}`.trim()
    if (!referenceId) {
      resetReferenceInfo()
      return
    }

    debouncedCheckReferenceNumber(referenceId)
  },
)

// Call fetchdiscountInfo when the page mounts
onMounted(async () => {
  await fetchBranchOptions()
  await fetchAddressBranchInfo()
  setDefaultValues()
  await nextTick()
  await refreshDeliveryTypeRates()

  // Fetch discount info based on current pickup_branch and destinationBranch
  // // // if (newOrder.value.pickup_branch && newOrder.value.destinationBranch) {
  // // //   fetchdiscountInfo(newOrder.value.pickup_branch.value, newOrder.value.destinationBranch.value)
  // // // }
})
</script>

<!-- // fetchdiscountInfo function remains unchanged // const fetchdiscountInfo =
async (pickupBranch, destinationBranch) => { // try { // const response = await
fetch( //
`/api/method/ecommerce.api.get_delivery_rate?pickup_branch=${encodeURIComponent(pickupBranch)}&destination_branch=${encodeURIComponent(destinationBranch)}`,
// { // method: 'GET', // } // ); // if (!response.ok) { // throw new
Error('Network response was not ok'); // } // const result = await
response.json(); // if ( // result && // result.message && //
result.message.data && // result.message.data.delivery_amount // ) { // const
deliveryAmount = result.message.data.delivery_amount; //
// newOrder.value.delivery_amount = deliveryAmount; // // console.log('Delivery
Amount:', deliveryAmount); // Log the delivery amount // } else { // //
// console.log('No delivery amount data found'); // } // } catch (error) { //
console.error('Error fetching discount info:', error); // } // }; -->
