<template>
  <div>
    <div
      class="flex items-center gap-2 rounded-lg bg-gradient-to-r from-orange-400 to-yellow-400 p-3 md:p-3 shadow-lg hover:from-orange-500 hover:to-yellow-500 transition duration-300 ease-in-out transform hover:scale-105 cursor-pointer"
      @click="openPanel"
    >
      <span
        class="material-symbols-outlined text-white text-lg md:text-lg font-bold"
        >directions_bike</span
      >
      <span class="text-white text-sm md:text-base font-bold"
        >Request for Pickup</span
      >
    </div>

    <Teleport to="body">
      <div v-if="displayPickup.isDisplay" class="fixed inset-0 z-50">
        <div class="absolute inset-0 bg-black/20" @click="closePanel"></div>

        <div
          class="absolute w-[min(32rem,calc(100vw-2rem))] overflow-hidden rounded-2xl bg-white text-left shadow-2xl ring-1 ring-black/10"
          :style="panelStyle"
        >
        <div
          class="flex cursor-move select-none items-center justify-between border-b border-gray-200 bg-white px-4 py-4"
          @mousedown.stop.prevent="startDrag"
        >
            <div>
              <h3 class="text-lg font-semibold text-gray-900">Pickup Confirmation</h3>
              <p class="text-sm text-gray-500">
                Please confirm before requesting pickup
              </p>
            </div>
            <button
              type="button"
              class="rounded-lg p-2 text-gray-500 transition hover:bg-gray-100 hover:text-gray-800"
              @click="closePanel"
            >
              <span class="material-symbols-outlined text-lg">close</span>
            </button>
          </div>

          <div class="space-y-4 bg-white px-4 pb-4 pt-4">
            <label class="block text-sm font-bold text-gray-800">
              Pickup Address
            </label>
            <Autocomplete
              :options="pickupAddress"
              placeholder="Select Address"
              v-model="orderData.businessAddress"
            />
            <label
              v-if="pickupScheduleOptions.length"
              class="block text-sm font-bold text-gray-800"
            >
              Schedule your pickup
            </label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="schedule in pickupScheduleOptions"
                :key="schedule.value"
                type="button"
                @click="handleScheduleSelect(schedule)"
                :class="[
                  'rounded-lg px-4 py-2 text-sm font-medium transition-colors duration-200',
                  orderData.pickup_schedule === schedule.value
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-200 text-gray-800 hover:bg-green-600 hover:text-white',
                ]"
              >
                {{ schedule.label }}
              </button>
            </div>
          </div>

          <div class="space-y-2 bg-white px-4 pb-5 pt-2">
            <button
              type="button"
              class="w-full rounded-xl bg-green-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="isSubmitting"
              @click="submitPickup"
            >
              {{ isSubmitting ? 'Requesting...' : 'Request Pickup' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { Autocomplete } from 'frappe-ui'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import vendorAddressBranchInfo from '../data/vendorAddressBranchInfo'
import { useToast } from 'vue-toastification'

const orderData = ref({
  businessAddress: '',
  pickup_schedule: '',
})

const displayPickup = ref({ isDisplay: false })
const toast = useToast()
const pickupAddress = ref([])
const pickupScheduleOptions = ref([])
const selectedSchedule = ref(null)
const isSubmitting = ref(false)

const panelPosition = ref({
  top: 96,
  left: 0,
})

const dragState = ref({
  active: false,
  offsetX: 0,
  offsetY: 0,
})

const panelStyle = computed(() => ({
  top: `${panelPosition.value.top}px`,
  left: `${panelPosition.value.left}px`,
}))

function setDefaultPanelPosition() {
  if (typeof window === 'undefined') return

  const panelWidth = Math.min(512, window.innerWidth - 32)
  const estimatedPanelHeight = 340
  panelPosition.value = {
    top: Math.max(16, (window.innerHeight - estimatedPanelHeight) / 2),
    left: Math.max(16, (window.innerWidth - panelWidth) / 2),
  }
}

function openPanel() {
  setDefaultPanelPosition()
  displayPickup.value.isDisplay = true
}

function closePanel() {
  displayPickup.value.isDisplay = false
}

function startDrag(event) {
  if (event.button !== 0) return

  dragState.value = {
    active: true,
    offsetX: event.clientX - panelPosition.value.left,
    offsetY: event.clientY - panelPosition.value.top,
  }

  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

function onDrag(event) {
  if (!dragState.value.active) return

  const panelWidth = Math.min(512, window.innerWidth - 32)
  const nextLeft = event.clientX - dragState.value.offsetX
  const nextTop = event.clientY - dragState.value.offsetY

  panelPosition.value = {
    left: Math.min(
      Math.max(16, nextLeft),
      Math.max(16, window.innerWidth - panelWidth - 16),
    ),
    top: Math.min(
      Math.max(16, nextTop),
      Math.max(16, window.innerHeight - 220),
    ),
  }
}

function stopDrag() {
  dragState.value.active = false
  document.body.style.userSelect = ''
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

const handleScheduleSelect = (schedule) => {
  selectedSchedule.value = schedule
  orderData.value.pickup_schedule = schedule.name
}

const requestPickup = async () => {
  if (!orderData.value.businessAddress) {
    toast.error('Please select a pickup address')
    return false
  }

  const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
  const apiUrl = `${Frappe_URL}/api/method/ecommerce.api.pickup_notification`
  const payload = JSON.stringify(orderData.value)

  try {
    isSubmitting.value = true
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
      body: payload,
    })

    const data = await response.json().catch(() => ({}))

    const responseMessage =
      typeof data?.message === 'string'
        ? data.message
        : data?.message?.message || data?.error || response.statusText || ''
    const isSuccess =
      response.ok &&
      (data?.message?.status === 'success' ||
        data?.status === 'success' ||
        data?.message?.indicator === 'green' ||
        data?.indicator === 'green')

    if (!isSuccess) {
      const errorMessage =
        responseMessage || data?.message || response.statusText || 'Error creating pickup request'
      toast.error(errorMessage)
      return false
    }

    toast.success(responseMessage || 'Pickup request created successfully')
    return true
  } catch (error) {
    toast.error(error?.message || 'Error creating pickup request')
    return false
  } finally {
    isSubmitting.value = false
  }
}

async function submitPickup() {
  const success = await requestPickup()
  if (success) {
    closePanel()
  }
}

const fetchAddressBranchInfo = async () => {
  try {
    await vendorAddressBranchInfo.fetch()
    const response = vendorAddressBranchInfo.data.data

    const pickupAddressDetails = response.addresses
    if (pickupAddressDetails && pickupAddressDetails.length > 0) {
      orderData.value.businessAddress = pickupAddressDetails[0]
    }

    pickupAddress.value = pickupAddressDetails.map((address) => ({
      label: address,
      value: address,
    }))

    pickupScheduleOptions.value = response.pickup_schedule.map((schedule) => ({
      label: schedule.pickup_schedule,
      value: schedule.name,
      name: schedule.name,
      to_time: schedule.to_time,
      pickup_schedule: schedule.pickup_schedule,
    }))

    if (
      pickupScheduleOptions.value.length > 0 &&
      !orderData.value.pickup_schedule
    ) {
      const defaultSchedule = pickupScheduleOptions.value[0]
      orderData.value.pickup_schedule = defaultSchedule.name
      selectedSchedule.value = defaultSchedule
    }
  } catch (error) {
    // noop
  }
}

onMounted(() => {
  fetchAddressBranchInfo()
  setDefaultPanelPosition()
  window.addEventListener('resize', setDefaultPanelPosition)
})

onBeforeUnmount(() => {
  stopDrag()
  window.removeEventListener('resize', setDefaultPanelPosition)
})
</script>
