<template>
  <Teleport to="body">
    <div
      v-if="displayAddress.isDisplay"
      role="dialog"
      aria-modal="true"
      class="fixed inset-0 z-[100] overflow-y-auto overscroll-contain bg-black/40 px-3 py-4 sm:px-6"
      style="-webkit-overflow-scrolling: touch; touch-action: pan-y"
      @click.self="closeAddressDialog"
      @keydown.esc="closeAddressDialog"
    >
      <div class="mx-auto my-2 w-full max-w-5xl rounded-xl bg-white text-left shadow-xl">
        <div class="sticky top-0 z-20 flex items-center justify-between rounded-t-xl bg-white px-5 pb-4 pt-5 sm:px-6">
          <h3 class="text-2xl font-semibold leading-6 text-gray-900">
            {{ props.editData?.name ? 'Edit Address' : 'Add Address' }}
          </h3>
          <button
            type="button"
            class="flex h-8 w-8 items-center justify-center rounded-md text-gray-600 hover:bg-gray-100"
            aria-label="Close address dialog"
            @click="closeAddressDialog"
          >
            <span class="material-symbols-outlined text-xl">close</span>
          </button>
        </div>

        <div class="address-layout px-5 pb-6 sm:px-6">
        <div class="map-panel">
          <div class="field">
            <div class="mb-2 flex items-center justify-between gap-3">
              <label class="field-label !mb-0">Location Map</label>
              <button
                type="button"
                class="rounded-md border border-slate-300 px-3 py-1 text-xs font-medium text-slate-700 hover:bg-slate-50"
                @click="useNearestBranchLocation"
              >
                Use Nearest Branch
              </button>
            </div>
            <div class="address-map-shell">
              <div ref="mapContainerRef" class="address-map"></div>
              <div class="center-pin" aria-hidden="true">
                <div class="center-pin__dot"></div>
              </div>
            </div>
            <p class="mt-2 text-xs text-slate-500">
              Drag the map to place the center pin on the exact location.
            </p>
          </div>
        </div>

        <div class="form-panel space-y-3">
          <div class="field">
            <label class="field-label">
              Full Address
              <span class="required">*</span>
            </label>
            <FormControl
              type="text"
              size="sm"
              variant="subtle"
              placeholder="Enter full address"
              v-model="newData.address"
            />
          </div>

          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div class="field">
            <label class="field-label">
              Nearest Branch
              <span class="required">*</span>
            </label>
            <BranchSelect
              class="w-full"
              :options="branchdetails"
              placeholder="Search branch, area, district or municipality..."
              :auto-select-first-area="true"
              v-model="newData.child_branch"
              @change="handleBranchChange"
            />
            </div>

            <div class="field">
              <label class="field-label">Area</label>
              <p class="px-1 pt-2 text-sm font-medium text-slate-700">
                {{ selectedBranchArea || 'No area available' }}
              </p>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="field">
              <label class="field-label">
                Contact Person
                <span class="required">*</span>
              </label>
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                placeholder="Enter contact person name"
                v-model="newData.contact_person"
              />
            </div>

            <div class="field">
              <label class="field-label">
                Mobile Number
                <span class="required">*</span>
              </label>
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                placeholder="10-digit mobile number"
                v-model="newData.phone"
                pattern="\d*"
                maxlength="10"
              />
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="field">
              <label class="field-label">Latitude</label>
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                placeholder="Latitude"
                v-model="newData.manual_latitude"
              />
            </div>

            <div class="field">
              <label class="field-label">Longitude</label>
              <FormControl
                type="text"
                size="sm"
                variant="subtle"
                placeholder="Longitude"
                v-model="newData.manual_longitude"
              />
            </div>
          </div>

          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        </div>
      </div>

        <div class="sticky bottom-0 z-20 rounded-b-xl bg-white px-5 pb-6 pt-4 sm:px-6">
          <Button variant="solid" class="w-full" @click="submitAddress">
            Confirm
          </Button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useToast } from 'vue-toastification'
import { computed, ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { displayAddress } from '../composables/displayAddress'
import { Button, FormControl } from 'frappe-ui'
import branch from '../data/branch'
import BranchSelect from './BranchSelect.vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

let branchdetails = ref([])
const mapContainerRef = ref(null)
let mapInstance = null
let branchLocationRequestId = 0

delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

const props = defineProps({
  editData: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['addressCreated'])
const toast = useToast()
const closeAddressDialog = () => {
  displayAddress.isDisplay = false
}
const newData = ref({
  name: '',
  address: '',
  phone: '',
  contact_person: '',
  child_branch: '',
  manual_latitude: '',
  manual_longitude: '',
})
const errorMessage = ref('')
const selectedBranchAreaValue = ref('')

const defaultCenter = [27.7172, 85.324]

const parseCoordinate = (value) => {
  if (
    value === null ||
    value === undefined ||
    String(value).trim() === ''
  ) {
    return null
  }

  const num = Number(value)
  return Number.isFinite(num) ? num : null
}

const getSelectedBranchValue = () => {
  return typeof newData.value.child_branch === 'object'
    ? newData.value.child_branch?.value || newData.value.child_branch?.label || ''
    : newData.value.child_branch
}

const normalizeBranchText = (value) => String(value || '').trim().toLowerCase()

const normalizeAreas = (areas) => {
  if (!Array.isArray(areas)) return []
  return areas
    .flatMap((area) => String(area || '').split(','))
    .map((area) => area.trim())
    .filter(Boolean)
    .sort((firstArea, secondArea) =>
      firstArea.localeCompare(secondArea, undefined, {
        numeric: true,
        sensitivity: 'base',
      }),
    )
}

const resolveSelectedBranch = () => {
  const branchValue = normalizeBranchText(getSelectedBranchValue())
  if (!branchValue) return null

  return branchdetails.value.find((branch) => {
    return [
      branch.value,
      branch.label,
      branch.name,
      branch.branch_code,
    ].some((candidate) => normalizeBranchText(candidate) === branchValue)
  })
}

const selectedBranchArea = computed(() => {
  return selectedBranchAreaValue.value
})

const handleBranchChange = (selection) => {
  selectedBranchAreaValue.value = selection?.area || ''
}

const parseBranchGeolocation = (geolocation) => {
  if (!geolocation) return null

  try {
    const parsed = typeof geolocation === 'string' ? JSON.parse(geolocation) : geolocation
    const feature = parsed?.features?.[0]
    const coordinates = feature?.geometry?.coordinates

    if (Array.isArray(coordinates) && coordinates.length >= 2) {
      const [longitude, latitude] = coordinates
      if (Number.isFinite(Number(latitude)) && Number.isFinite(Number(longitude))) {
        return {
          latitude: Number(latitude),
          longitude: Number(longitude),
        }
      }
    }
  } catch (error) {
    return null
  }

  return null
}

const geocodeBranchAddress = async (branch) => {
  const queryParts = [
    branch?.full_address,
    branch?.street,
    branch?.city,
    branch?.label,
    'Nepal',
  ].filter(Boolean)

  if (!queryParts.length) return null

  const params = new URLSearchParams({
    q: queryParts.join(', '),
    format: 'jsonv2',
    limit: '1',
  })

  const response = await fetch(`https://nominatim.openstreetmap.org/search?${params.toString()}`, {
    headers: {
      Accept: 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error('Failed to geocode branch address')
  }

  const results = await response.json()
  const first = results?.[0]
  if (!first?.lat || !first?.lon) return null

  return {
    latitude: Number(first.lat),
    longitude: Number(first.lon),
  }
}

const geocodeBranchAreaAddress = async (branch, area) => {
  const areaText = String(area || '').trim()
  if (!areaText) return null

  const queryParts = [
    areaText,
    branch?.label,
    branch?.city,
    'Nepal',
  ].filter(Boolean)

  const params = new URLSearchParams({
    q: queryParts.join(', '),
    format: 'jsonv2',
    addressdetails: '1',
    countrycodes: 'np',
    limit: '10',
  })

  const response = await fetch(
    `https://nominatim.openstreetmap.org/search?${params.toString()}`,
    {
      headers: {
        Accept: 'application/json',
      },
    },
  )

  if (!response.ok) {
    throw new Error('Failed to geocode branch area address')
  }

  const results = await response.json()
  const normalizedArea = normalizeBranchText(areaText)
  const compactArea = normalizedArea.replace(/[^a-z0-9\u0900-\u097f]/g, '')
  const branchLocation = parseBranchGeolocation(branch?.geolocation)

  const distanceFromBranch = (result) => {
    if (!branchLocation) return 0

    const latitude = Number(result?.lat)
    const longitude = Number(result?.lon)
    if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
      return Number.POSITIVE_INFINITY
    }

    const toRadians = (degrees) => (degrees * Math.PI) / 180
    const latitudeDelta = toRadians(latitude - branchLocation.latitude)
    const longitudeDelta = toRadians(longitude - branchLocation.longitude)
    const firstLatitude = toRadians(branchLocation.latitude)
    const secondLatitude = toRadians(latitude)
    const haversine =
      Math.sin(latitudeDelta / 2) ** 2 +
      Math.cos(firstLatitude) *
        Math.cos(secondLatitude) *
        Math.sin(longitudeDelta / 2) ** 2

    return 6371 * 2 * Math.atan2(Math.sqrt(haversine), Math.sqrt(1 - haversine))
  }

  const matchingResults = (Array.isArray(results) ? results : [])
    .filter((result) => {
      if (!result?.lat || !result?.lon) return false

      const resultText = normalizeBranchText(
        [
          result.display_name,
          result.name,
          ...Object.values(result.address || {}),
        ]
          .filter(Boolean)
          .join(' '),
      )
      const compactResult = resultText.replace(/[^a-z0-9\u0900-\u097f]/g, '')

      return (
        resultText.includes(normalizedArea) ||
        (compactArea && compactResult.includes(compactArea))
      )
    })
    .sort(
      (firstResult, secondResult) =>
        distanceFromBranch(firstResult) - distanceFromBranch(secondResult),
    )

  const matchedResult = matchingResults[0]
  if (!matchedResult) return null

  return {
    latitude: Number(matchedResult.lat),
    longitude: Number(matchedResult.lon),
  }
}

const updateMarkerPosition = (latitude, longitude, recenter = false) => {
  if (!mapInstance || latitude == null || longitude == null) return
  if (recenter) {
    mapInstance.setView([latitude, longitude], 15)
  }
}

const ensureMap = async () => {
  await nextTick()

  if (!mapContainerRef.value || mapInstance) return

  mapInstance = L.map(mapContainerRef.value).setView(defaultCenter, 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors',
  }).addTo(mapInstance)

  const syncCenterToFields = () => {
    const center = mapInstance.getCenter()
    const { lat, lng } = center
    newData.value.manual_latitude = lat.toFixed(6)
    newData.value.manual_longitude = lng.toFixed(6)
  }

  mapInstance.on('moveend', syncCenterToFields)
  mapInstance.on('zoomend', syncCenterToFields)

  const latitude = parseCoordinate(newData.value.manual_latitude)
  const longitude = parseCoordinate(newData.value.manual_longitude)
  if (latitude != null && longitude != null) {
    updateMarkerPosition(latitude, longitude, true)
  }

  setTimeout(() => {
    mapInstance?.invalidateSize()
  }, 50)
}

const destroyMap = () => {
  if (mapInstance) {
    mapInstance.remove()
    mapInstance = null
  }
}

const useNearestBranchLocation = async (force = true, areaOverride = '') => {
  const matchedBranch = resolveSelectedBranch()
  if (!matchedBranch) return
  const requestId = ++branchLocationRequestId
  const targetArea = String(
    areaOverride || selectedBranchAreaValue.value || '',
  ).trim()

  if (!force) {
    const latitude = parseCoordinate(newData.value.manual_latitude)
    const longitude = parseCoordinate(newData.value.manual_longitude)
    if (latitude != null && longitude != null) {
      updateMarkerPosition(latitude, longitude, true)
      return
    }
  }

  try {
    let location = null

    if (targetArea) {
      location = await geocodeBranchAreaAddress(matchedBranch, targetArea)

      if (requestId !== branchLocationRequestId) return

      if (!location) {
        location = parseBranchGeolocation(matchedBranch?.geolocation)

        if (!location) {
          location = await geocodeBranchAddress(matchedBranch)
        }

        if (requestId !== branchLocationRequestId) return

        if (!location) {
          errorMessage.value =
            'Unable to match the selected area or nearest branch on the map. Please place the pin manually.'
          return
        }

        newData.value.manual_latitude = location.latitude.toFixed(6)
        newData.value.manual_longitude = location.longitude.toFixed(6)
        updateMarkerPosition(location.latitude, location.longitude, true)
        errorMessage.value =
          'The selected area was not found on the map. Showing the nearest branch location.'
        return
      }
    } else {
      location = parseBranchGeolocation(matchedBranch?.geolocation)

      if (!location && matchedBranch) {
        location = await geocodeBranchAddress(matchedBranch)
      }
    }

    if (requestId !== branchLocationRequestId) return

    if (!location) {
      errorMessage.value = 'Selected nearest branch does not have usable location data.'
      return
    }

    newData.value.manual_latitude = location.latitude.toFixed(6)
    newData.value.manual_longitude = location.longitude.toFixed(6)
    updateMarkerPosition(location.latitude, location.longitude, true)
    errorMessage.value = ''
  } catch (error) {
    if (requestId === branchLocationRequestId) {
      errorMessage.value = targetArea
        ? 'Unable to match the selected area or nearest branch on the map. Please place the pin manually.'
        : 'Unable to resolve nearest branch location.'
    }
  }
}

const applyDefaultBranchLocation = async () => {
  if (getSelectedBranchValue() && branchdetails.value.length) {
    await useNearestBranchLocation(false)
    return
  }

  const latitude = parseCoordinate(newData.value.manual_latitude)
  const longitude = parseCoordinate(newData.value.manual_longitude)
  if (latitude != null && longitude != null) {
    updateMarkerPosition(latitude, longitude, true)
  }
}

const validateForm = () => {
  if (
    !newData.value.address ||
    !newData.value.phone ||
    !newData.value.contact_person ||
    !newData.value.child_branch
  ) {
    errorMessage.value = 'Please provide all required fields.'
    return false
  }
  errorMessage.value = ''
  return true
}

const submitAddress = async () => {
  if (!validateForm()) {
    return
  }
  const isEdit = Boolean(props.editData?.name)
  const apiUrl = isEdit
    ? '/api/method/ecommerce.api.update_vendor_address_info'
    : '/api/method/ecommerce.api.create_vendor_address_info'
  const payload = {
    ...newData.value,
    child_branch:
      typeof newData.value.child_branch === 'object'
        ? newData.value.child_branch?.value || newData.value.child_branch?.label || ''
        : newData.value.child_branch,
    manual_latitude: newData.value.manual_latitude || '',
    manual_longitude: newData.value.manual_longitude || '',
    area: selectedBranchArea.value || '',
  }

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
    const responseData = await response.json()

    if (responseData?.message?.status === 'success') {
      toast.success(
        isEdit ? 'Address updated successfully' : 'Address created successfully',
      )
      emit('addressCreated')
      displayAddress.isDisplay = false
      resetForm()
    } else {
      const msg =
        responseData?.message?.message ||
        responseData?.message ||
        'Error creating address'
      errorMessage.value = msg
      toast.error(msg)
    }
  } catch (error) {
    const msg = `Error saving address: ${error.message || error}`
    errorMessage.value = msg
    toast.error(msg)
  }
}

const resetForm = () => {
  const defaultBranch = branchdetails.value[0]

  newData.value = {
    name: '',
    address: '',
    phone: '',
    contact_person: '',
    child_branch: defaultBranch?.value || '',
    manual_latitude: '',
    manual_longitude: '',
  }
  errorMessage.value = ''
  selectedBranchAreaValue.value = defaultBranch?.areas?.[0] || ''
}

watch(
  () => props.editData,
  async (value) => {
    if (value) {
      newData.value = {
        name: value.name || '',
        address: value.address || '',
        phone: value.phone || '',
        contact_person: value.contact_person || '',
        child_branch: value.child_branch || '',
        manual_latitude: value.manual_latitude || '',
        manual_longitude: value.manual_longitude || '',
      }
      selectedBranchAreaValue.value = value.area_label || value.area || ''

      if (displayAddress.isDisplay) {
        await ensureMap()
        await applyDefaultBranchLocation()
      }
      return
    }

    resetForm()
  },
  { immediate: true },
)

const fetchAddressBranchInfo = async () => {
  try {
    await branch.fetch()
    const branchList =
      branch.data?.message?.data?.branches ||
      branch.data?.data?.branches ||
      branch.data?.branches ||
      []

    branchdetails.value = branchList.map((b) => {
      const label = b.branch_name || b.name || ''
      const value = b.name || b.branch_name || ''
      return {
        name: b.name || '',
        label,
        value,
        branch_name: b.branch_name || b.name || '',
        branch_code: b.branch_code || '',
        district: b.district || '',
        municipality: b.municipality || '',
        areas: normalizeAreas(Array.isArray(b.area) ? b.area : []),
        geolocation: b.geolocation || null,
        city: b.city || '',
        street: b.street || '',
        full_address: b.full_address || '',
      }
    })

    if (branchdetails.value.length && !newData.value.child_branch) {
      const defaultBranch = branchdetails.value[0]
      newData.value.child_branch = defaultBranch.value
      selectedBranchAreaValue.value = defaultBranch.areas?.[0] || ''
    } else if (!selectedBranchAreaValue.value) {
      const selectedBranch = resolveSelectedBranch()
      selectedBranchAreaValue.value = selectedBranch?.areas?.[0] || ''
    }

    if (displayAddress.isDisplay) {
      await applyDefaultBranchLocation()
    }
  } catch (error) {
    branchdetails.value = []
  }
}

onMounted(() => {
  fetchAddressBranchInfo()
})

onBeforeUnmount(() => {
  destroyMap()
})

watch(
  () => displayAddress.isDisplay,
  async (isOpen) => {
    if (isOpen) {
      await ensureMap()
      await applyDefaultBranchLocation()
      const latitude = parseCoordinate(newData.value.manual_latitude)
      const longitude = parseCoordinate(newData.value.manual_longitude)
      if (latitude == null || longitude == null) {
        mapInstance.setView(defaultCenter, 12)
      }
      setTimeout(() => {
        mapInstance?.invalidateSize()
      }, 50)
      return
    }

    destroyMap()
  },
)

watch(
  () => [getSelectedBranchValue(), selectedBranchAreaValue.value],
  async ([branchValue, areaValue], [oldBranchValue, oldAreaValue]) => {
    if (
      !displayAddress.isDisplay ||
      !branchValue ||
      (branchValue === oldBranchValue && areaValue === oldAreaValue)
    ) {
      return
    }

    await useNearestBranchLocation(true, areaValue)
  },
)

watch(
  () => [newData.value.manual_latitude, newData.value.manual_longitude],
  ([latitude, longitude]) => {
    const lat = parseCoordinate(latitude)
    const lng = parseCoordinate(longitude)
    if (lat != null && lng != null) {
      updateMarkerPosition(lat, lng)
    }
  },
)

watch(
  () => branchdetails.value.length,
  async (length) => {
    if (!displayAddress.isDisplay || !length) return
    await applyDefaultBranchLocation()
  },
)
</script>

<style scoped>
.field-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.required {
  color: #dc2626;
  margin-left: 4px;
}

.error-message {
  color: #dc2626;
  font-size: 12px;
}

.address-map {
  height: 380px;
  width: 100%;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  overflow: hidden;
}

@media (max-width: 767px) {
  .address-map.leaflet-container {
    -ms-touch-action: pan-y !important;
    touch-action: pan-y !important;
  }
}

.address-layout {
  display: grid;
  gap: 20px;
}

.map-panel,
.form-panel {
  min-width: 0;
}

@media (min-width: 1024px) {
  .address-layout {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    align-items: start;
  }
}

.address-map-shell {
  position: relative;
}

.center-pin {
  pointer-events: none;
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, calc(-100% + 12px));
  z-index: 500;
}

.center-pin__dot {
  position: relative;
  width: 22px;
  height: 22px;
  border: 4px solid #2563eb;
  border-radius: 9999px;
  background: #fff;
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.25);
}

.center-pin__dot::after {
  content: '';
  position: absolute;
  left: 50%;
  top: 100%;
  width: 2px;
  height: 18px;
  background: #2563eb;
  transform: translateX(-50%);
  border-radius: 9999px;
}
</style>
