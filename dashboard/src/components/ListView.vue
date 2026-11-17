<template>
  <div>
    <div class="">
      <div class="bg-white">
        <strong class="text-gray-800">Branch List</strong>
      </div>
      <div class="flex items-start gap-4 mb-4">
        <span class="flex min-w-0 flex-col">
          <label class="block text-sm text-gray-700 font-medium"
            >Pickup Address</label
          >
          <Autocomplete
            :options="pickupAddressOptions"
            placeholder="Select Address"
            v-model="orderData.address"
          />
        </span>
        <span class="flex min-w-0 flex-col">
          <label class="block text-sm text-gray-700 font-medium"
            >Pickup Branch</label
          >
          <Autocomplete
            :options="uniquePickupBranchOptions"
            placeholder="Select Branch"
            v-model="orderData.pickupBranch"
          />
        </span>
        <span class="flex min-w-0 flex-col">
          <label class="block text-sm font-medium text-transparent select-none">
            Search
          </label>
          <input
            type="search"
            class="form-input form-input-sm border-none"
            placeholder="Search"
            v-model="inputValue"
          />
        </span>
      </div>
      <p
        v-if="pickupAddressWarning"
        class="mt-0.5 leading-none text-xs font-medium text-red-500"
      >
        {{ pickupAddressWarning }}
      </p>
    </div>

    <AppDataTable
      :columns="tableColumns"
      :rows="filteredRows"
      :loading="isLoading"
      row-key="name"
      empty-text="No records found"
      table-class="table-fixed"
    >
      <template #loading>
        Loading branches...
      </template>

      <template #cell-sn="{ row }">
        <span class="whitespace-nowrap">{{ row.sn }}</span>
      </template>

      <template #cell-name="{ row }">
        <div class="flex flex-col gap-0.5">
          <span>{{ row.name }}</span>
          <span>{{ row.district }}</span>
          <span>{{ row.municipality }}</span>
        </div>
      </template>

      <template #cell-area="{ row }">
        <span class="break-all">{{ row.area.join(', ') }}</span>
      </template>

      <template #cell-contact="{ row }">
        <div class="flex flex-col gap-0.5 whitespace-normal">
          <span v-if="row.primary_phone_no">{{ row.primary_phone_no }}</span>
          <span v-if="row.secondary_phone_no">{{ row.secondary_phone_no }}</span>
          <span v-if="!row.primary_phone_no && !row.secondary_phone_no">N/A</span>
        </div>
      </template>

      <template #cell-fare="{ row }">
        <span v-if="row.vendor_fare == 0" class="text-gray-700">
          {{ row.amount }}
        </span>
        <span
          v-else-if="row.amount == row.vendor_fare"
          class="text-gray-700"
        >
          {{ row.amount }}
        </span>
        <span v-else>
          <span class="line-through text-gray-700">{{ row.amount }}</span>
          /
          {{ row.vendor_fare }}
        </span>
      </template>

      <template #mobile-row="{ row }">
        <div class="space-y-1 text-xs text-gray-700">
          <p><span class="font-medium text-gray-500">Branch:</span> {{ row.name }}</p>
          <p><span class="font-medium text-gray-500">District:</span> {{ row.district }}</p>
          <p><span class="font-medium text-gray-500">Area:</span> {{ row.area.join(', ') }}</p>
          <p><span class="font-medium text-gray-500">Municipality:</span> {{ row.municipality }}</p>
          <p>
            <span class="font-medium text-gray-500">Phone:</span>
            {{ [row.primary_phone_no, row.secondary_phone_no].filter(Boolean).join(' / ') || 'N/A' }}
          </p>
          <p>
            <span class="font-medium text-gray-500">Fare:</span>
            <span
              v-if="row.vendor_fare == 0 || row.amount == row.vendor_fare"
              class="text-gray-700"
            >
              {{ row.amount }}
            </span>
            <span v-else>
              <span class="line-through text-gray-700">{{ row.amount }}</span>
              /
              {{ row.vendor_fare }}
            </span>
          </p>
        </div>
      </template>
    </AppDataTable>
  </div>
</template>

<script setup>
import { Autocomplete } from 'frappe-ui'
import { ref, onMounted, computed, watch } from 'vue'
import AppDataTable from './AppDataTable.vue'
import branch from '../data/branch'
import vendorAddressBranchInfo from '../data/vendorAddressBranchInfo'
const inputValue = ref('')
const isLoading = ref(false)
const pickupAddressOptions = ref([])
const pickupBranchOptions = ref([])
const mappedPickupBranches = ref([])
const branchMetaByName = ref({})
const uniquePickupBranchOptions = computed(() => {
  return pickupBranchOptions.value
})
const pickupAddressWarning = computed(() => {
  const selectedBranch = getOptionValue(orderData.value.pickupBranch)
  if (!selectedBranch) return ''

  const hasMappedAddress = mappedPickupBranches.value.some(
    (branch) => branch?.value === selectedBranch,
  )

  return hasMappedAddress
    ? ''
    : 'You do not have pickup address in this branch.'
})

const orderData = ref({
  address: '',
  pickupBranch: '',
})
const amount = ref('')
const isSyncingFromAddress = ref(false)

const getOptionValue = (value) => {
  return typeof value === 'object' && value !== null && 'value' in value
    ? value.value
    : value
}

watch(
  () => orderData.value.address,
  (newVal) => {
    const newAddress = getOptionValue(newVal)
    if (typeof newAddress !== 'string' || !newAddress.trim()) return

    const index = pickupAddressOptions.value.findIndex(
      (address) => address.value === newAddress,
    )
    const mappedBranch = mappedPickupBranches.value[index]
    if (mappedBranch?.value) {
      isSyncingFromAddress.value = true
      orderData.value.address = newAddress
      orderData.value.pickupBranch = mappedBranch
      fetchbranch(mappedBranch.value)
      queueMicrotask(() => {
        isSyncingFromAddress.value = false
      })
    }
  },
)

watch(
  () => orderData.value.pickupBranch,
  (newVal) => {
    const newBranch = getOptionValue(newVal)
    if (typeof newBranch !== 'string' || !newBranch.trim()) return

    orderData.value.pickupBranch = newBranch
    if (isSyncingFromAddress.value) return

    const mappedIndex = mappedPickupBranches.value.findIndex(
      (branch) => branch?.value === newBranch,
    )
    if (mappedIndex === -1) {
      orderData.value.address = ''
    } else if (pickupAddressOptions.value[mappedIndex]) {
      orderData.value.address = pickupAddressOptions.value[mappedIndex]
    }
    fetchbranch(newBranch)
  },
)
const CACHE_KEY = 'branchFareCache:v2'

const loadCache = () => {
  try {
    return JSON.parse(localStorage.getItem(CACHE_KEY) || '{}')
  } catch (e) {
    return {}
  }
}

const saveCache = (data) => {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data))
  } catch (e) {
    // ignore storage errors
  }
}

const normalizeBranches = (branches = []) => {
  if (!Array.isArray(branches)) return []
  return branches.filter(
    (branch) => branch && typeof branch.name === 'string' && branch.name.trim(),
  )
}

const applyBranchData = (branches = []) => {
  const normalizedBranches = normalizeBranches(branches)
  // console.log('Branch list:', normalizedBranches)
  rows.value = normalizedBranches.map((branchItem, index) => ({
    ...branchItem,
    sn: index + 1,
    area: Array.isArray(branchItem.area) ? branchItem.area : [],
    district: branchItem.district || '',
    municipality:
      branchItem.municipality ||
      branchMetaByName.value[branchItem.name]?.municipality ||
      '',
    primary_phone_no:
      branchItem.primary_phone_no ||
      branchMetaByName.value[branchItem.name]?.primary_phone_no ||
      '',
    secondary_phone_no:
      branchItem.secondary_phone_no ||
      branchMetaByName.value[branchItem.name]?.secondary_phone_no ||
      '',
    amount: branchItem.amount ?? 0,
    vendor_fare: branchItem.vendor_fare ?? 0,
  }))
}

const fetchbranch = async (address) => {
  const addr = address || orderData.value.address || ''

  // Show cached data immediately, but always refresh from API
  // so newly added fields like municipality are not stuck stale.
  const cache = loadCache()
  const cachedBranches = normalizeBranches(cache[addr])
  if (cachedBranches.length) {
    applyBranchData(cachedBranches)
  }

  isLoading.value = true // Set loading state to true
  try {
    const url = `/api/method/ecommerce.api.get_branchesfare?orderData=${encodeURIComponent(addr)}`
    const response = await fetch(url)

    if (!response.ok) {
      //   console.error('API Error:', response.statusText)
      return
    }

    const branch = await response.json()
    // console.log('Branch API response:', branch)
    const apiBranches = normalizeBranches(branch?.message?.data?.branches)

    // Handle both cases: branches found or not found
    if (apiBranches.length) {
      applyBranchData(apiBranches)
      cache[addr] = apiBranches
      saveCache(cache)
    } else {
      rows.value = []
    }
  } catch (error) {
    // console.error('Error fetching branches:', error)
  } finally {
    isLoading.value = false
  }
}

const fetchPickupAddressInfo = async () => {
  await vendorAddressBranchInfo.fetch()
  const addressList = vendorAddressBranchInfo.data?.data?.addresses || []
  const branchList = vendorAddressBranchInfo.data?.data?.branches || []

  pickupAddressOptions.value = addressList.map((address) => ({
    label: address,
    value: address,
  }))
  mappedPickupBranches.value = branchList.map((branch) => ({
    label: branch,
    value: branch,
  }))

  if (pickupAddressOptions.value.length) {
    orderData.value.address = pickupAddressOptions.value[0]
  }
}

const fetchPickupBranches = async () => {
  await branch.fetch()
  const branches = Array.isArray(branch.data?.data?.branches)
    ? branch.data.data.branches
    : []
  branchMetaByName.value = branches.reduce((acc, item) => {
    if (item?.name) {
      acc[item.name] = item
    }
    return acc
  }, {})
  const seen = new Set()
  pickupBranchOptions.value = branches
    .filter((item) => {
      if (!item?.name || seen.has(item.name)) return false
      seen.add(item.name)
      return true
    })
    .map((item) => ({
      label: item.branch_name || item.name,
      value: item.name,
    }))

  if (!orderData.value.pickupBranch && pickupBranchOptions.value.length) {
    orderData.value.pickupBranch = pickupBranchOptions.value[0]
  }
}

onMounted(() => {
  fetchPickupAddressInfo()
  fetchPickupBranches()
})

const filteredRows = computed(() => {
  if (!inputValue.value) {
    return rows.value
  }
  return rows.value.filter((row) =>
    Object.values(row).some(
      (val) =>
        val &&
        val.toString().toLowerCase().includes(inputValue.value.toLowerCase()),
    ),
  )
})

const rows = ref([])
const tableColumns = [
  {
    key: 'sn',
    label: 'SN',
    headerClass: 'w-[8%]',
    cellClass: 'w-[8%] whitespace-nowrap',
  },
  {
    key: 'name',
    label: 'Name',
    headerClass: 'w-[18%]',
    cellClass: 'w-[18%]',
  },
  {
    key: 'area',
    label: 'Description',
    headerClass: 'w-[32%]',
    cellClass: 'w-[32%]',
  },
  {
    key: 'contact',
    label: 'Contact',
    headerClass: 'w-[24%]',
    cellClass: 'w-[24%] whitespace-nowrap',
  },
  {
    key: 'fare',
    label: 'Fare',
    headerClass: 'w-[16%]',
    cellClass: 'w-[16%] whitespace-nowrap',
  },
]
</script>
