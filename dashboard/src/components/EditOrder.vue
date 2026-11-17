<template>
  <Dialog
    :options="dialogOptions"
    :modelValue="props.modelValue"
    @update:modelValue="handleMainDialogToggle"
  >
    <template #body-content>
      <div
        class="min-h-0 max-h-[calc(100dvh-16rem)] overflow-y-auto overscroll-contain px-2 font-bold"
        style="-webkit-overflow-scrolling: touch; scrollbar-gutter: stable;"
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
              v-model="selectedRowOrder.order_type"
              @change="handleUserChange"
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
              v-model="selectedRowOrder.return_shipping_type"
            />
          </div>
        </div>
        <div class="border-t border-gray-200 pt-3 overflow-visible">
          <div class="grid grid-cols-1 gap-3 md:grid-cols-3 overflow-visible">
            <div class="space-y-1">
              <label class="block text-sm text-gray-600 font-bold">
                Refrence ID (Unique Order ID)
              </label>
              <FormControl
                class="w-full"
                type="text"
                size="sm"
                variant="subtle"
                placeholder="Refrence ID"
                :disabled="false"
                label=""
                v-model="selectedRowOrder.vendor_tracking_number"
              />
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
                v-model="selectedRowOrder.vendor_address"
                @change="handleUserChange"
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
                v-model="selectedRowOrder.customer_name"
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
                v-model="selectedRowOrder.primary_mobile_no"
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
                v-model="selectedRowOrder.secondary_mobile_no"
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
                class="w-full"
                :options="branchOptions"
                placeholder="Search branch, area, district or municipality..."
                v-model="selectedRowOrder.destination_branch"
                @change="handleDestinationBranchChange"
              />
            </div>
            <div class="space-y-1">
              <label class="block text-sm text-gray-600 font-bold">
                Area/City <span class="text-red-500">*</span>
              </label>
              <FormControl
                :type="'text'"
                size="sm"
                variant="subtle"
                maxlength="100"
                placeholder="area/city"
                :disabled="false"
                label=""
                v-model="selectedRowOrder.name_of_city_area"
                @input="handleUserChange"
              />
            </div>
            <div class="space-y-1">
              <label class="block text-sm text-gray-600 font-bold mb-1">
                Landmark <span class="text-red-500">*</span>
              </label>
              <FormControl
                ref="landmarkInput"
                :type="'text'"
                size="sm"
                variant="subtle"
                maxlength="100"
                placeholder="landmark"
                :disabled="false"
                label=""
                v-model="selectedRowOrder.location"
                @input="handleUserChange"
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
                size="sm"
                variant="subtle"
                placeholder="cod amount"
                :disabled="false"
                v-model="selectedRowOrder.cod_amount"
              />
               <div>
                <span class="text-[11px] text-green-500"
                  >Total cod amount including delivery charge</span
                >
              </div>
            </div>

            <div class="space-y-2 md:col-span-2 overflow-visible">
              <label class="block text-sm text-gray-600 font-bold">
                Delivery Type
              </label>

              <div class="grid grid-cols-1 gap-2 xl:grid-cols-2 overflow-visible">
                <label
                  class="group relative flex min-h-[74px] items-center justify-between rounded-xl border border-gray-200 bg-white px-2 py-1 cursor-pointer transition-colors"
                  :class="
                    Number(selectedRowOrder.express_delivery) === 0
                      ? 'border-green-600 ring-1 ring-green-600'
                      : 'hover:border-gray-300'
                  "
                >
                  <div class="flex items-center gap-1.5">
                    <input
                      type="radio"
                      name="express_delivery"
                      :value="0"
                      v-model="selectedRowOrder.express_delivery"
                      class="sr-only"
                    />
                    <span
                      class="flex h-3.5 w-3.5 items-center justify-center rounded-full border"
                      :class="
                        Number(selectedRowOrder.express_delivery) === 0
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

                <div class="relative">
                  <!-- <button
                    type="button"
                    class="absolute right-2 top-2 rounded-full border border-gray-300 p-1 text-xs font-bold leading-none text-gray-500 hover:text-gray-700"
                    @click.stop="confirmExpressDelivery()"
                  >
                    !
                  </button> -->
                  <div>
                    <label
                      v-if="hasExpressDeliveryRate"
                      class="flex min-h-[74px] items-center justify-between rounded-xl border border-gray-200 bg-white px-2 py-1 transition-colors"
                      :class="
                        Number(selectedRowOrder.express_delivery) === 1
                          ? 'cursor-pointer border-green-600 ring-1 ring-green-600'
                          : 'cursor-pointer hover:border-gray-300'
                      "
                    >
                    <div class="flex items-center gap-1.5">
                      <input
                        type="radio"
                        name="express_delivery"
                        :value="1"
                        v-model="selectedRowOrder.express_delivery"
                        class="sr-only"
                      />
                      <span
                        class="flex h-3.5 w-3.5 items-center justify-center rounded-full border"
                        :class="
                          Number(selectedRowOrder.express_delivery) === 1
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
                        <span class="text-md font-bold text-gray-700">2PM Express</span>
                        <span class="mt-0.5 text-[9px] font-bold text-green-600">
                          Pickup by 2PM, same day delivery
                        </span>
                      </div>
                    </div>
                    <div class="text-right whitespace-nowrap">
                      <div class="text-[16px] font-bold leading-none text-gray-700">
                        Rs {{ formatDeliveryCharge(deliveryTypeRates.express) }}
                      </div>
                    </div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div class="space-y-1">
              <label class="block text-sm text-gray-600 font-bold">
                Weight (Kg)
              </label>
              <FormControl
                class="w-full"
                type="number"
                min="0"
                max="30"
                size="sm"
                variant="subtle"
                placeholder="weight"
                :disabled="false"
                label=""
                v-model="selectedRowOrder.package_weight"
                @focus="clearDefaultWeight"
              />
              <p v-if="weightLimitError" class="text-xs text-red-600" role="alert">
                {{ weightLimitError }}
              </p>
            </div>

            <div class="flex flex-col justify-center gap-1 md:col-span-2">
              <label class="block text-sm text-gray-600 font-bold">
                Delivery Charge Rs {{ selectedRowOrder.delivery_amount }}
              </label>
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
                v-model="selectedRowOrder.order_description"
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
                v-model="selectedRowOrder.instruction"
              />
            </div>
            <div class="space-y-5">
              <label class="block text-sm text-gray-600 font-bold mb-5"
                >Green Delivery Available</label
              >
              <div class="flex items-center">
                <span class="mr-2 text-gray-600 text-xs"
                  >Enable For Green Delivery</span
                >
                <Switch
                  size="md"
                  :value="false"
                  v-model="selectedRowOrder.green_delivery"
                  :disabled="isSwitchDisabled"
                  @click="handleUserChange"
                />
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


</template>

<script setup>
import { useToast } from 'vue-toastification'
import { Dialog, FormControl, Switch } from 'frappe-ui'
import { onMounted, ref, watch, nextTick, computed } from 'vue'
import branch from '../data/branch'
import vendorAddressBranchInfo from '../data/vendorAddressBranchInfo'
import deliveryInfo from '../data/deliveryInfo'
import openorderDetails from '../data/openorderdetail'
import BranchSelect from './BranchSelect.vue'

const emit = defineEmits(['OrderCreated', 'update:modelValue'])
const landmarkInput = ref(null)

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

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  selectedRowOrder: {
    type: Object,
    required: true,
  },
})
const isReadOnly = ref(true)
const isReturn = computed(() => props.selectedRowOrder?.order_type === 'Return')
const weightLimitError = computed(() =>
  Number(props.selectedRowOrder?.package_weight) > 30
    ? 'Weight cannot be more than 30 kg.'
    : '',
)

const clearDefaultWeight = () => {
  if (
    props.selectedRowOrder.package_weight === 0 ||
    props.selectedRowOrder.package_weight === '0'
  ) {
    props.selectedRowOrder.package_weight = ''
  }
}

const branchSwapState = ref({
  swapped: false,
  originalPickup: null,
  originalDestination: null,
})

const swapBranchesForReturn = () => {
  const temp = props.selectedRowOrder.pickup_branch
  props.selectedRowOrder.pickup_branch =
    props.selectedRowOrder.destination_branch
  props.selectedRowOrder.destination_branch = temp
}

watch(
  () => props.selectedRowOrder.order_type,
  (val) => {
    if (val === 'Return') {
      if (!branchSwapState.value.swapped) {
        branchSwapState.value.originalPickup =
          props.selectedRowOrder.pickup_branch
        branchSwapState.value.originalDestination =
          props.selectedRowOrder.destination_branch
        swapBranchesForReturn()
        branchSwapState.value.swapped = true
      }
    } else if (branchSwapState.value.swapped) {
      props.selectedRowOrder.pickup_branch =
        branchSwapState.value.originalPickup ??
        props.selectedRowOrder.pickup_branch
      props.selectedRowOrder.destination_branch =
        branchSwapState.value.originalDestination ??
        props.selectedRowOrder.destination_branch
      branchSwapState.value.swapped = false
    }
  },
  { immediate: true },
)

// Ensure return shipping type has a default for return orders
watch(
  () => props.selectedRowOrder.return_shipping_type,
  (val) => {
    if (!val) {
      props.selectedRowOrder.return_shipping_type = 'Pickup'
    }
  },
  { immediate: true },
)

const showDialog3 = ref(false)
const handleMainDialogToggle = (value) => {
  if (!value && showDialog3.value) {
    showDialog3.value = false
    return
  }

  emit('update:modelValue', value)
}



const confirmExpressDelivery = async () => {
  return new Promise((resolve) => {
    showDialog3.value = true // Show the dialog
  })
}
const confirm = (event) => {
  event?.stopPropagation?.()
  showDialog3.value = false // Close the dialog
}

//console.log('selectedRowOrder:', props.selectedRowOrder);
const toast = useToast()

const { creation, delivery_amount, ...rest } = props.selectedRowOrder
//console.log('restgh:', rest);
const updateOrder = ref({ ...rest })

watch(
  () => props.selectedRowOrder,
  (newVal) => {
    const { creation, delivery_amount, ...rest } = newVal
    updateOrder.value = { ...rest }
   //  // console.log('updateOrder:', updateOrder.value);
    if (!updateOrder.value.return_shipping_type) {
      updateOrder.value.return_shipping_type = 'Pickup'
    }
    if (
      updateOrder.value.express_delivery === undefined ||
      updateOrder.value.express_delivery === null ||
      updateOrder.value.express_delivery === ''
    ) {
      updateOrder.value.express_delivery = 0
    } else {
      updateOrder.value.express_delivery = Number(
        updateOrder.value.express_delivery,
      )
    }
    if (
      props.selectedRowOrder.express_delivery === undefined ||
      props.selectedRowOrder.express_delivery === null ||
      props.selectedRowOrder.express_delivery === ''
    ) {
      props.selectedRowOrder.express_delivery = 0
    } else {
      props.selectedRowOrder.express_delivery = Number(
        props.selectedRowOrder.express_delivery,
      )
    }
  },
  { deep: true, immediate: true },
)

const errorMessage = ref('')

const dialogOptions = {
  title: 'Edit Order',
  description: 'Update Order',
  size: '3xl',
  actions: [
    {
      label: 'Update Order',
      variant: 'solid',
      onClick: async (close) => {
        const updated = await updateOrderDetails()
        if (updated) close()
      },
    },
  ],
}
let isUserTriggered = ref(false)
watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal) {
      isUserTriggered.value = false
    }
  },
)
const updateOrderDetails = async () => {
  const apiUrl = '/api/method/ecommerce.api.update_order'
 //  // console.log('updateOrder:', updateOrder.value);
  const packageWeight = Number(updateOrder.value.package_weight)
  if (!Number.isFinite(packageWeight) || packageWeight < 0 || packageWeight > 30) {
    errorMessage.value = 'Weight must be between 0 and 30 kg.'
    return false
  }

  errorMessage.value = ''
  try {
    const isReturnOrder = updateOrder.value.order_type === 'Return'

    let destBranch =
      typeof updateOrder.value.destination_branch === 'object'
        ? updateOrder.value.destination_branch?.value || ''
        : updateOrder.value.destination_branch || ''

    let pickupBranchVal =
      typeof updateOrder.value.pickup_branch === 'object'
        ? updateOrder.value.pickup_branch?.value || ''
        : updateOrder.value.pickup_branch || ''

    if (isReturnOrder) {
      ;[pickupBranchVal, destBranch] = [destBranch, pickupBranchVal]
    }

    const orderData = {
      ...updateOrder.value,
      destination_branch: destBranch,
      pickup_branch: pickupBranchVal,
      vendor_address: normalizeValue(updateOrder.value.vendor_address),
      is_paid_order: updateOrder.value.is_paid_order,
      green_delivery: updateOrder.value.green_delivery,
      express_delivery: Number(updateOrder.value.express_delivery || 0),
      package_weight: `${String(updateOrder.value.package_weight || 1)}`,
      cod_amount: `${String(updateOrder.value.cod_amount || 0)}`,
    }

   //  // console.log('orderData:', orderData);
   //  // console.log('JSON orderData:', JSON.stringify(orderData));

    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    })
    const responseData = await response.json()

   //  // console.log('responseData:', responseData);

    if (response.ok && responseData.message.status === 'success') {
      emit('orderCreated')
      toast.success('Order updated successfully')
      window.location.reload()
      return true
    } else {
      // console.error('Error updating order:', responseData);
      toast.error(
        `Error updating order: ${responseData.message.message || 'Unknown error'}`,
      )
      return false
    }
  } catch (error) {
    errorMessage.value = `Error updating order: ${error.message || error}`
    return false
  }
}

const branchOptions = ref([])

const pickupAddress = ref([])
const pickupBranch = ref([])

const pickupBranchLabel = computed(() => {
  const val = props.selectedRowOrder.pickup_branch
  if (!val) return ''
  return typeof val === 'object' ? val.label || val.value || '' : val
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

const focusLandmark = () => {
  nextTick(() => {
    const el =
      landmarkInput.value?.$el?.querySelector('input,textarea,select') ||
      landmarkInput.value?.$el ||
      landmarkInput.value
    el?.focus?.()
  })
}

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

  pickupBranch.value = pickupBranchDetails.map((branch) => ({
    label: branch,
    value: branch,
  }))
}

watch(
  () => props.selectedRowOrder.vendor_address,
  (newVal) => {
    const selectedAddress = normalizeValue(newVal)
    const index = pickupAddress.value.findIndex(
      (address) => normalizeValue(address) === selectedAddress,
    )
   //  // console.log('index:', index);
    if (index !== -1) {
      props.selectedRowOrder.pickup_branch = pickupBranch.value[index]
    }
  },
)

let resultgreendeliverycheck = ref(false)
const deliveryAmount = ref(props.selectedRowOrder.delivery_amount)
const normalizeValue = (value, fallback = '') => {
  if (value === undefined || value === null) {
    return fallback
  }
  return typeof value === 'object' ? (value.value ?? fallback) : value
}
const resolveBranchParams = (pickupBranch, destinationBranch) => {
  const pickup = normalizeValue(pickupBranch)
  const destination = normalizeValue(destinationBranch)
  if (isReturn.value) {
    return { pickup: destination, destination: pickup }
  }
  return { pickup, destination }
}

const refreshDeliveryTypeRates = async () => {
  const { pickup, destination } = resolveBranchParams(
    props.selectedRowOrder.pickup_branch,
    props.selectedRowOrder.destination_branch,
  )

  if (!pickup || !destination) {
    return
  }

  await fetchdiscountInfo(
    pickup,
    destination,
    normalizeValue(props.selectedRowOrder.location),
    normalizeValue(props.selectedRowOrder.name_of_city_area),
    props.selectedRowOrder.green_delivery ?? false,
    props.selectedRowOrder.express_delivery,
  )
}

const fetchdiscountInfo = async (
  pickupBranch,
  destinationBranch,
  landmark,
  destinationCityArea,
  green_delivery,
  express_delivery,
) => {
 //  // console.log('Fetching delivery rate for:', pickupBranch, destinationBranch, landmark, destinationCityArea, green_delivery);
  try {
    const pickupBranchValue = normalizeValue(pickupBranch)
    const destinationBranchValue = normalizeValue(destinationBranch)
    const locationValue = normalizeValue(landmark)
    const cityAreaValue = normalizeValue(destinationCityArea)
    const greenDeliveryValue = green_delivery ?? false
    const expressDeliveryValue = Number(express_delivery || 0)
    const apiUrl = `/api/method/ecommerce.api.get_delivery_rate?pickup_branch=${encodeURIComponent(pickupBranchValue)}&destination_branch=${encodeURIComponent(destinationBranchValue)}&location=${encodeURIComponent(locationValue)}&city_area=${encodeURIComponent(cityAreaValue)}&green_delivery=${encodeURIComponent(greenDeliveryValue)}&express_delivery=${expressDeliveryValue}`
   //  // console.log('API URL:', apiUrl);

    const response = await fetch(apiUrl, {
      method: 'GET',
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
      Number(props.selectedRowOrder.express_delivery) === 1
    ) {
      props.selectedRowOrder.express_delivery = 0
    }

    if (result && result.message && result.message.total_delivery_sum) {
      deliveryAmount.value = result.message.total_delivery_sum
      props.selectedRowOrder.delivery_amount = result.message.total_delivery_sum
    }

    const resultgreendelivery = result.message.result
    resultgreendeliverycheck.value = !!resultgreendelivery
   //  //console.log('resultgreendelivery:', resultgreendeliverycheck.value);
    if (!isUserTriggered.value) {
      props.selectedRowOrder.green_delivery = resultgreendeliverycheck.value
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

watch(
  [
    () => props.selectedRowOrder.pickup_branch,
    () => props.selectedRowOrder.destination_branch,
    () => props.selectedRowOrder.location,
    () => props.selectedRowOrder.name_of_city_area,
    () => props.selectedRowOrder.green_delivery,
    () => props.selectedRowOrder.express_delivery,
    () => props.selectedRowOrder.order_type,
  ],
  async ([
    newPickupBranch,
    newDestinationBranch,
    newLocation,
    newCityArea,
    newGreenDelivery,
    newExpressDelivery,
    _newOrderType,
  ]) => {
    const { pickup, destination } = resolveBranchParams(
      newPickupBranch,
      newDestinationBranch,
    )
    const locationValue = normalizeValue(newLocation)
    const cityAreaValue = normalizeValue(newCityArea)
    const greenDeliveryValue = normalizeValue(newGreenDelivery, false)
   //  // console.log('pickupBranchValue:', pickup, 'destinationBranchValue:', destination, 'locationValue:', locationValue, 'cityAreaValue:', cityAreaValue, 'greenDeliveryValue:', greenDeliveryValue);

    await fetchdiscountInfo(
      pickup,
      destination,
      locationValue,
      cityAreaValue,
      greenDeliveryValue,
      newExpressDelivery,
    )
  },
)

const handleUserChange = () => {
  isUserTriggered.value = true
  if (resultgreendeliverycheck.value) {
    isReadOnly.value = false
  }
 //  // console.log('User interaction detected, API calls enabled.');
}

const handleDestinationBranchChange = (selection) => {
  props.selectedRowOrder.name_of_city_area = selection?.area || ''
  handleUserChange()
  focusLandmark()
}

const isSwitchDisabled = computed(() => {
  return (
    !(isUserTriggered.value && resultgreendeliverycheck.value) &&
    props.selectedRowOrder.green_delivery !== 1
  )
})

// Watch for changes in green_delivery and update isReadOnly accordingly
watch(
  () => props.selectedRowOrder.green_delivery,
  (newValue) => {
    if (newValue === 0) {
      isReadOnly.value = true
    }
  },
)

// Watch for changes in resultgreendeliverycheck and update green_delivery accordingly
watch(resultgreendeliverycheck, (newValue) => {
  if (isUserTriggered.value) {
    props.selectedRowOrder.green_delivery = newValue ? 1 : 0
  }
})

watch(
  () => props.selectedRowOrder.cod_amount,
  (newVal) => {
    if (
      newVal === null ||
      newVal === 0 ||
      newVal === '' ||
      newVal === 'Rs 0.0'
    ) {
      props.selectedRowOrder.is_paid_order = 'Yes'
      props.selectedRowOrder.cod_amount = 0
    } else {
      props.selectedRowOrder.is_paid_order = 'No'
    }
  },
)

onMounted(() => {
  fetchBranchOptions()
  fetchAddressBranchInfo()
})

watch(
  () => props.modelValue,
  async (newVal) => {
    if (newVal) {
      await elevateDialogLayer(dialogOptions.title)
      await refreshDeliveryTypeRates()
    }
  },
)
</script>
