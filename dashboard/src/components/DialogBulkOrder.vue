<template>
  <div class="space-y-4">
    <div class="rounded-2xl border border-gray-200 bg-[#fcfdfd] p-5 shadow-sm">
      <div class="flex flex-col gap-5">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="min-w-0 flex-1">
            <label
              class="flex min-h-[56px] cursor-pointer items-center rounded-2xl border border-dashed border-[#cfe5d8] bg-[#f3faf6] px-4 transition hover:border-[#2f9e62] hover:bg-[#eef8f1]"
            >
              <input
                ref="fileInputRef"
                type="file"
                @change="handleFileUpload"
                class="sr-only"
              />
              <span
                class="inline-flex h-9 items-center rounded-full bg-white px-4 text-sm font-semibold text-[#2f9e62] shadow-sm"
              >
                Choose File
              </span>
              <span class="ml-4 min-w-0 truncate text-sm text-slate-500">
                {{ selectedFileName || 'No file chosen' }}
              </span>
            </label>
          </div>
          <a
            href="https://pickndropnepal.com/files/Orders.xlsx"
            download
            class="shrink-0 rounded-xl border border-[#d8eadf] bg-[#f3faf6] px-4 py-2 text-sm font-semibold text-[#2f9e62] transition hover:bg-[#eaf5ef]"
          >
            Download Template
          </a>
        </div>

        <div class="grid gap-3 md:grid-cols-[1fr_auto]">
          <input
            v-model="importUrl"
            type="url"
            placeholder="Paste Google Sheet or file URL"
            class="h-11 w-full rounded-2xl border border-gray-200 bg-white px-4 text-sm text-slate-700 outline-none ring-0 transition focus:border-[#2f9e62]"
          />
          <Button
            variant="outline"
            class="h-11 rounded-2xl border-gray-200 px-5 font-semibold text-slate-700 hover:border-[#2f9e62] hover:text-[#2f9e62]"
            :loading="isImportingUrl"
            @click="importFromUrl"
          >
            Get Data
          </Button>
        </div>
        <p class="text-sm text-slate-500">
          Supports local Excel upload and public Google Sheet or direct `.xlsx` / `.csv` URLs.
        </p>
      </div>
    </div>

    <div
      v-if="formattedJson.length"
      class="rounded-2xl border border-[#bfe7cb] bg-[#eef8f1] px-4 py-3 text-sm font-medium text-[#2f9e62]"
    >
      {{ formattedJson.length }} ready to import. Please review the data preview below before starting the import process.
    </div>

    <ErrorMessage :message="errorMessage" />

    <p v-if="bulkDisplay.isProcessing" class="text-sm text-slate-600">
      Processing...{{ uploadProgress.toFixed(2) }}%
    </p>

    <div class="flex justify-end">
      <Button
        variant="solid"
        class="rounded-2xl bg-[#111111] px-5 py-2.5 font-semibold text-white hover:bg-[#222222]"
        :loading="bulkDisplay.isProcessing"
        @click="postOrders"
      >
        Start Import
      </Button>
    </div>

    <div
      v-if="previewRows.length"
      class="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm"
    >
      <div class="border-b border-gray-200 px-4 py-3">
        <h2 class="text-sm font-semibold text-slate-900">Imported Rows Preview</h2>
      </div>
      <div class="max-h-[420px] overflow-auto">
        <table class="min-w-full text-left text-sm">
          <thead class="sticky top-0 bg-gray-100 text-slate-600">
            <tr>
              <th
                v-for="column in previewColumns"
                :key="column"
                class="whitespace-nowrap px-4 py-3 font-medium"
              >
                {{ column }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, index) in previewRows"
              :key="index"
              class="border-t border-gray-100 text-slate-700"
            >
              <td
                v-for="column in previewColumns"
                :key="column"
                class="whitespace-nowrap px-4 py-3"
              >
                {{ row[column] ?? '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
a {
  transition: color 0.3s ease;
}

a:hover {
  color: #1e40af; /* Tailwind's blue-700 */
}
</style>
<script setup>
import { useToast } from 'vue-toastification'
import { computed, onMounted, ref } from 'vue'
import * as XLSX from 'xlsx'
import { Button, ErrorMessage } from 'frappe-ui'
import { bulkDisplay } from '../composables/bulkDisplay'

const toast = useToast()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''

const formattedJson = ref([])
const errorMessage = ref('')
const uploadProgress = ref(0)
const importUrl = ref('')
const isImportingUrl = ref(false)
const previewRows = ref([])
const branchOptions = ref([])
const fileInputRef = ref(null)
const selectedFileName = ref('')
const requiredFields = [
  'Customer Name',
  'Primary Mobile No.',
  'Landmark',
  'COD Amount',
  'Destination Branch',
  'City / Area',
]
const previewColumns = computed(() => {
  const columns = new Set()
  previewRows.value.forEach((row) => {
    Object.keys(row).forEach((key) => {
      if (key !== '__rowNum__') {
        columns.add(key)
      }
    })
  })
  return Array.from(columns)
})
const branchLookup = computed(() => {
  const lookup = new Map()

  branchOptions.value.forEach((branch) => {
    const values = [
      branch?.name,
      branch?.branch_name,
      branch?.branch_code,
    ].filter(Boolean)

    values.forEach((value) => {
      lookup.set(String(value).trim().toLowerCase(), branch.branch_name)
    })
  })

  return lookup
})

const fetchBranches = async () => {
  const token = localStorage.getItem('access_token')

  try {
    const response = await fetch(`${Frappe_URL}/api/method/ecommerce.api.get_branches`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })
    const responseData = await response.json()
    branchOptions.value = responseData?.message?.data?.branches || []
  } catch (error) {
    branchOptions.value = []
  }
}

onMounted(() => {
  fetchBranches()
})

const validateOrders = (orders) => {
  const validOrderTypes = new Set(['regular', 'return', 'exchange'])
  const errors = []
  const sanitizedOrders = []

  orders.forEach((order) => {
    const phone = String(order.primaryMobileNo || '').trim()
    const orderType = String(order.orderType || '').trim()
    const destinationBranch = String(order.destinationBranch || '').trim()
    const normalizedBranch = branchLookup.value.get(destinationBranch.toLowerCase())

    if (!/^\d{10}$/.test(phone)) {
      errors.push(`Row ${order.__rowNum__}: Primary Mobile No. must be exactly 10 digits.`)
      return
    }

    if (!validOrderTypes.has(orderType.toLowerCase())) {
      errors.push(
        `Row ${order.__rowNum__}: Order Type must be Regular, Return or Exchange.`,
      )
      return
    }

    if (!normalizedBranch) {
      errors.push(
        `Row ${order.__rowNum__}: Destination Branch "${destinationBranch}" does not match any branch.`,
      )
      return
    }

    sanitizedOrders.push({
      ...order,
      primaryMobileNo: phone,
      orderType:
        orderType.charAt(0).toUpperCase() + orderType.slice(1).toLowerCase(),
      destinationBranch: normalizedBranch,
    })
  })

  return {
    errors,
    orders: sanitizedOrders,
  }
}

const normalizeRows = (jsonData) => {
  return jsonData
    .map((row, index) => {
      const missingFields = requiredFields.filter(
        (field) => !Object.prototype.hasOwnProperty.call(row, field),
      )
      if (missingFields.length > 0) {
        errorMessage.value = `Row ${index + 1} is missing fields: ${missingFields.join(', ')}`
        return null
      }
      return {
        customerName: row['Customer Name'],
        primaryMobileNo: row['Primary Mobile No.'],
        secondaryMobileNo: row['Secondary Mobile No.'] || '',
        destinationCityArea: row['City / Area'] || '',
        landmark: row['Landmark'],
        codAmount: row['COD Amount'] || 0,
        is_paid_order: row['Is Paid Order'] || 'No',
        pickup_branch: row['Origin Branch'] || '',
        destinationBranch: row['Destination Branch'],
        orderType: row['Order Type'] || 'Regular',
        orderDescription: row['Product Description'] || '',
        instruction: row['Instruction'] || '',
        weight: row['Weight'] || 0,
        ref: 'Bulk Upload',
        businessAddress: row['Vendor Address'] || '',
        vendorTrackingNumber: row['Reference ID'] || '',
        __rowNum__: row.__rowNum__ || index + 1,
      }
    })
    .filter((row) => row !== null)
}

const populateRows = (jsonData) => {
  errorMessage.value = ''
  previewRows.value = jsonData
  formattedJson.value = normalizeRows(jsonData)
  if (formattedJson.value.length === 0 && !errorMessage.value) {
    errorMessage.value = 'No valid rows found. Please check the data format.'
  }
}

const parseWorkbook = (data, type) => {
  const workbook = XLSX.read(data, { type })
  const firstSheet = workbook.Sheets[workbook.SheetNames[0]]
  const jsonData = XLSX.utils.sheet_to_json(firstSheet)
  populateRows(jsonData)
}

const normalizeImportUrl = (url) => {
  const trimmedUrl = url.trim()
  if (!trimmedUrl) return ''

  if (
    trimmedUrl.includes('docs.google.com/spreadsheets/d/') &&
    !trimmedUrl.includes('/export?')
  ) {
    const match = trimmedUrl.match(/\/d\/([^/]+)/)
    if (match?.[1]) {
      return `https://docs.google.com/spreadsheets/d/${match[1]}/export?format=xlsx`
    }
  }

  return trimmedUrl
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (!file) return
  selectedFileName.value = file.name
  const reader = new FileReader()

  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      parseWorkbook(data, 'array')
    } catch (error) {
      errorMessage.value = 'Error reading file. Please try again.'
    }
  }
  reader.readAsArrayBuffer(file)
}

const resetBulkForm = () => {
  formattedJson.value = []
  previewRows.value = []
  importUrl.value = ''
  errorMessage.value = ''
  uploadProgress.value = 0
  isImportingUrl.value = false
  selectedFileName.value = ''

  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

const importFromUrl = async () => {
  const normalizedUrl = normalizeImportUrl(importUrl.value)
  if (!normalizedUrl) {
    errorMessage.value = 'Please enter a valid URL.'
    return
  }

  isImportingUrl.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(normalizedUrl)
    if (!response.ok) {
      throw new Error('Failed to fetch URL')
    }

    const buffer = await response.arrayBuffer()
    parseWorkbook(new Uint8Array(buffer), 'array')
  } catch (error) {
    errorMessage.value =
      'Unable to import from URL. Make sure the file or Google Sheet is publicly accessible.'
  } finally {
    isImportingUrl.value = false
  }
}

const postOrders = () => {
  if (formattedJson.value.length > 0) {
    const validation = validateOrders(formattedJson.value)

    if (validation.errors.length > 0) {
      errorMessage.value = validation.errors.slice(0, 5).join(' | ')
      return
    }

    createBulkOrders(validation.orders)
  } else {
    errorMessage.value = 'No valid rows found. Please check the data format.'
  }
}

const createBulkOrders = async (orders) => {
  bulkDisplay.isProcessing = true // Show processing state
  errorMessage.value = ''
  let completedRequests = 0
  let successCount = 0
  const failedRows = []
  const token = localStorage.getItem('access_token')

  const batchSize = 100 // Adjust the batch size as needed
  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

  // Process orders in batches
  for (let i = 0; i < orders.length; i += batchSize) {
    const batch = orders.slice(i, i + batchSize)

    for (const order of batch) {
      try {
        const response = await fetch(`${Frappe_URL}/api/method/ecommerce.api.create_order`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(order),
        })

        const responseData = await response.json()
        const result = responseData?.message

        if (response.ok && result?.status === 'success') {
          successCount++
        } else {
          failedRows.push({
            row: order.__rowNum__ || completedRequests + 1,
            message:
              result?.message ||
              responseData?.exception ||
              'Order creation failed.',
          })
        }
      } catch (error) {
        failedRows.push({
          row: order.__rowNum__ || completedRequests + 1,
          message: error.message || 'Network error while creating order.',
        })
      }

      completedRequests++
      uploadProgress.value = (completedRequests / orders.length) * 100
    }

    // Wait before processing the next batch
    await delay(2000) // Adjust the delay as needed
  }

  bulkDisplay.isProcessing = false // Hide processing state

  if (failedRows.length > 0) {
    const previewErrors = failedRows
      .slice(0, 5)
      .map((item) => `Row ${item.row}: ${item.message}`)
      .join(' | ')

    errorMessage.value = `Imported ${successCount}/${orders.length}. Failed ${failedRows.length}. ${previewErrors}`
    toast.error(`Imported ${successCount}/${orders.length}. Failed ${failedRows.length}.`)
    return
  }

  resetBulkForm()
  toast.success(`All orders processed successfully! Total orders: ${successCount}`)
}
</script>
