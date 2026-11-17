<template>
  <div class="mb-4 px-1 sm:px-0">
    <!-- Header -->
    <div class="bg-white pb-3">
      <strong class="text-lg text-gray-800 sm:text-base"
        >Orderwise Payment</strong
      >
    </div>

    <!-- Filters -->
    <div
      class="grid grid-cols-2 gap-3 pb-4 xl:flex xl:flex-nowrap xl:items-end xl:justify-start xl:gap-4"
    >
      <!-- Start Date -->
      <div class="min-w-0">
        <label class="mb-1 block text-xs font-medium text-gray-700"
          >Start Date</label
        >

        <DatePicker
          class="w-full xl:w-36"
          variant="subtle"
          placeholder="YYYY-MM-DD"
          v-model="startDate"
        />
      </div>

      <!-- End Date -->
      <div class="min-w-0">
        <label class="mb-1 block text-xs font-medium text-gray-700"
          >End Date</label
        >

        <DatePicker
          class="w-full xl:w-36"
          variant="subtle"
          placeholder="YYYY-MM-DD"
          v-model="endDate"
        />
      </div>

      <!-- Status Filter -->
      <div class="min-w-0">
        <label class="mb-1 block text-xs font-medium text-gray-700"
          >Status Filter</label
        >
        <FormControl
          v-model="inputValue1"
          class="w-full xl:w-36"
          type="select"
          variant="subtle"
          :options="[
            { label: 'All', value: '' },
            { label: 'Unsettled', value: 'Unsettled' },
            { label: 'Settled', value: 'Settled' },
          ]"
        />
      </div>

      <!-- Search -->
      <div class="min-w-0">
        <label class="mb-1 block text-xs font-medium text-gray-700 xl:invisible"
          >Search</label
        >
        <FormControl
          class="w-full xl:w-36"
          type="search"
          variant="subtle"
          placeholder="Search orders"
          v-model="inputValue"
        />
      </div>

      <!-- Actions -->
      <div
        class="col-span-2 grid grid-cols-3 gap-2 xl:ml-1 xl:flex xl:items-center"
      >
        <Button
          class="w-full justify-center whitespace-nowrap px-2 text-xs sm:text-sm xl:w-auto xl:px-5"
          variant="solid"
          @click="fetchorderwisepayment(inputValue1)"
        >
          Apply Filters
        </Button>
        <Button
          class="w-full justify-center whitespace-nowrap px-2 text-xs sm:text-sm xl:w-auto xl:px-5"
          variant="solid"
          @click="downloadCSV"
          >Export in CSV</Button
        >
        <Button
          class="w-full justify-center whitespace-nowrap px-2 text-xs sm:text-sm xl:w-auto xl:px-5"
          variant="solid"
          @click="downloadpdf"
          >Export in PDF</Button
        >
      </div>
    </div>

    <!-- Table -->
    <div
      class="custom-table-container"
      ref="pdfTarget"
      :class="{ 'pdf-export': isPdfExport }"
    >
      <div class="pdf-header" v-if="isPdfExport">
        <div class="pdf-header-left">
          <div class="pdf-title">Orderwise Payment</div>
        </div>
        <div class="pdf-header-right">
          <div class="pdf-date">Printed Date: {{ formattedToday }}</div>
        </div>
      </div>
      <AppDataTable
        :columns="tableColumns"
        :rows="filteredRows"
        :loading="isLoading"
        :stack-on-mobile="false"
        row-key="name"
        empty-text="No records found"
        table-class="min-w-[1200px] table-fixed text-sm [&_th]:!px-3 [&_th]:!py-2 [&_th]:!text-xs [&_th]:!font-medium [&_th]:!normal-case [&_th]:!tracking-normal [&_td]:!px-3 [&_td]:!py-2.5 [&_td]:!text-sm"
        wrapper-class="shadow-none"
      >
        <template #loading> Loading... </template>

        <template #cell-sn="{ index }">
          <span class="block text-right">{{ index + 1 }}</span>
        </template>

        <template #cell-name="{ row }">
          <button
            type="button"
            class="inline-flex items-center justify-center gap-1 font-semibold text-blue-700"
            @click.stop="goToDetail(row.order_id || row.name)"
          >
            {{ row.name }}
            <Rocket
              v-if="Number(row.express_delivery) === 1"
              class="h-3.5 w-3.5 text-rose-600"
              title="Express Delivery"
            />
          </button>
        </template>

        <template #cell-vendor_tracking_number="{ row }">
          <span>{{ row.vendor_tracking_number || '-' }}</span>
        </template>

        <template
          v-for="key in numericKeys"
          :key="`cell-${key}`"
          #[`cell-${key}`]="{ row }"
        >
          <span class="block text-right">{{ row[key] }}</span>
        </template>

        <template #cell-status="{ row }">
          <span
            class="inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold"
            :class="getStatusBadgeClass(row.status)"
          >
            {{ row.status }}
          </span>
        </template>

        <template #mobile-row="{ row, index }">
          <button
            type="button"
            class="block w-full space-y-1 text-left text-sm text-gray-700"
            @click="goToDetail(row.order_id || row.name)"
          >
            <p>
              <span class="font-medium text-gray-500">SN:</span> {{ index + 1 }}
            </p>
            <p class="inline-flex items-center gap-1">
              <span class="font-medium text-gray-500">Order ID:</span>
              <span class="font-semibold text-blue-700">{{ row.name }}</span>
              <Rocket
                v-if="Number(row.express_delivery) === 1"
                class="h-3.5 w-3.5 text-rose-600"
                title="Express Delivery"
              />
            </p>
            <p>
              <span class="font-medium text-gray-500">Reference ID:</span>
              {{ row.vendor_tracking_number || '' }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Created Date:</span>
              {{ row.creation }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Delivered Date:</span>
              {{ row.delivered_date }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Customer:</span>
              {{ row.customer }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Phone:</span>
              {{ row.phone }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Pre-Payment:</span>
              {{ row.prepayment }}
            </p>
            <p>
              <span class="font-medium text-gray-500">COD:</span> {{ row.cod }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Delivery Amount:</span>
              {{ row.delivery }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Net Amount:</span>
              {{ row.net }}
            </p>
            <p>
              <span class="font-medium text-gray-500">COD Transfer:</span>
              {{ row.cod_transfer }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Status:</span>
              <span
                class="ml-2 inline-flex rounded-full px-2.5 py-1 text-[11px] font-semibold"
                :class="getStatusBadgeClass(row.status)"
              >
                {{ row.status }}
              </span>
            </p>
          </button>
        </template>
      </AppDataTable>

      <div
        v-if="!isLoading && filteredRows.length"
        class="hidden grid-cols-[minmax(0,1fr)_repeat(5,auto)] gap-3 border-t border-gray-200 bg-gray-50 px-4 py-3 text-sm font-semibold text-gray-700 sm:grid"
      >
        <span>Total</span>
        <span class="text-right">Rs {{ totalprepayment }}</span>
        <span class="text-right">Rs {{ totalCOD }}</span>
        <span class="text-right">Rs {{ totalDelivery }}</span>
        <span class="text-right">Rs {{ totalNet }}</span>
        <span class="text-right">Rs {{ totalCODTransfer }}</span>
      </div>

      <div
        v-if="!isLoading && filteredRows.length"
        class="mt-3 rounded-xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700 sm:hidden"
      >
        <p class="mb-3 font-semibold text-gray-900">Payment totals</p>
        <dl class="grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 gap-y-2">
          <dt class="text-gray-500">Pre-Payment</dt>
          <dd class="text-right font-semibold">Rs {{ totalprepayment }}</dd>
          <dt class="text-gray-500">COD</dt>
          <dd class="text-right font-semibold">Rs {{ totalCOD }}</dd>
          <dt class="text-gray-500">Delivery Amount</dt>
          <dd class="text-right font-semibold">Rs {{ totalDelivery }}</dd>
          <dt class="text-gray-500">Net Amount</dt>
          <dd class="text-right font-semibold">Rs {{ totalNet }}</dd>
          <dt class="text-gray-500">COD Transfer</dt>
          <dd class="text-right font-semibold">Rs {{ totalCODTransfer }}</dd>
        </dl>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import dayjs from 'dayjs'
import { Button, FormControl, DatePicker } from 'frappe-ui'
import { useRouter } from 'vue-router'
import html2pdf from 'html2pdf.js'
import { Rocket } from 'lucide-vue-next'
import AppDataTable from './AppDataTable.vue'

// Reactive state
const inputValue = ref('')
const inputValue1 = ref('Unsettled')
const rows = ref([])
const router = useRouter()
const isLoading = ref(false)
const pdfTarget = ref(null)
const isPdfExport = ref(false)
const formattedToday = computed(() => dayjs().format('YYYY-MM-DD'))

const startDate = ref(dayjs().subtract(365, 'day').format('YYYY-MM-DD'))
const endDate = ref(dayjs().format('YYYY-MM-DD'))

const downloadCSV = () => {
  const dataToExport = filteredRows.value
  if (!dataToExport.length) return

  const csv = convertToCSV(dataToExport)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'OrderWise Payment.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const downloadpdf = async () => {
  if (!filteredRows.value.length) return
  isPdfExport.value = true
  await nextTick()
  const element = pdfTarget.value
  if (!element) return

  const options = {
    margin: 0.2,
    filename: 'OrderWise Payment.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true },
    jsPDF: { unit: 'in', format: 'a3', orientation: 'landscape' },
  }

  html2pdf()
    .from(element)
    .set(options)
    .save()
    .finally(() => {
      isPdfExport.value = false
    })
}
// API Fetch
// const fetchorderwisepayment = async (status = '') => {
//   let allRows = []
//   let page = 0
//   let totalPages = 1

//   while (page < totalPages) {
//     const params = {
//       start_date: startDate.value,
//       end_date: endDate.value,
//       // offset: page * limit.value,
//       // limit_start: page * limit.value,
//       // limit_page_length: limit.value,
//       status,
//     }

//     const queryString = new URLSearchParams(params).toString()
//     const fullUrl = `/api/method/ecommerce.api.get_orderwise_payment?${queryString}`
//     console.log (fullUrl)
//     const response = await fetch(fullUrl)

//     if (!response.ok) throw new Error(`HTTP error: ${response.status}`)

//     const { message } = await response.json()

//     allRows = allRows.concat(message.data)
//     totalPages = message.total_pages
//     page++
//   }

//   rows.value = allRows.map((t) => ({
//     ...t,
//     creation: dayjs(t.created).format('YYYY-MM-DD HH:mm'),
//     delivered_date: dayjs(t.delivered_date).format('YYYY-MM-DD HH:mm'),
//   }))
// }

const fetchorderwisepayment = async (status = '') => {
  isLoading.value = true
  try {
    const isUnsettled = status === 'Unsettled'
    const oneYearAgo = dayjs().subtract(1, 'year').format('YYYY-MM-DD')

    const params = {
      start_date: isUnsettled ? oneYearAgo : startDate.value,
      end_date: endDate.value,
      status,
    }

    const queryString = new URLSearchParams(params).toString()

    const fullUrl = `/api/method/ecommerce.api.get_orderwise_payment?${queryString}`
    // console.log (fullUrl)
    const response = await fetch(fullUrl)
    if (!response.ok) throw new Error(`HTTP error: ${response.status}`)

    const { message } = await response.json()

    rows.value = (message?.data || []).map((t) => ({
      ...t,
      creation: dayjs(t.created).format('YYYY-MM-DD HH:mm'),
      delivered_date: dayjs(t.delivered_date).format('YYYY-MM-DD HH:mm'),
    }))
  } finally {
    isLoading.value = false
  }
}

// Filtering
const filteredRows = computed(() => {
  return rows.value.filter((row) => {
    const matchesStatus =
      !inputValue1.value ||
      row.status.toLowerCase() === inputValue1.value.toLowerCase()
    const matchesSearch =
      !inputValue.value ||
      Object.values(row).some(
        (val) =>
          val &&
          val.toString().toLowerCase().includes(inputValue.value.toLowerCase()),
      )
    return matchesStatus && matchesSearch
  })
})

// Row styling
const getRowClass = (status) => {
  return (
    {
      Unsettled: 'row-red',
      Settled: 'row-blue',
    }[status] || 'row-gray'
  )
}

// Table Columns
const tableColumns = [
  {
    key: 'sn',
    label: 'SN',
    headerClass: 'w-[6%] text-right',
    cellClass: 'text-right',
  },
  { key: 'name', label: 'Order ID', headerClass: 'w-[12%]' },
  {
    key: 'vendor_tracking_number',
    label: 'Reference ID',
    headerClass: 'w-[11%]',
  },
  { key: 'creation', label: 'Created Date', headerClass: 'w-[12%]' },
  { key: 'delivered_date', label: 'Delivered Date', headerClass: 'w-[12%]' },
  { key: 'customer', label: 'Customer', headerClass: 'w-[12%]' },
  { key: 'phone', label: 'Phone', headerClass: 'w-[10%]' },
  {
    key: 'prepayment',
    label: 'Pre-Payment',
    headerClass: 'w-[9%] text-right',
    cellClass: 'text-right',
  },
  {
    key: 'cod',
    label: 'COD',
    headerClass: 'w-[7%] text-right',
    cellClass: 'text-right',
  },
  {
    key: 'delivery',
    label: 'Delivery Amount',
    headerClass: 'w-[10%] text-right',
    cellClass: 'text-right',
  },
  {
    key: 'net',
    label: 'Net Amount',
    headerClass: 'w-[9%] text-right',
    cellClass: 'text-right',
  },
  {
    key: 'cod_transfer',
    label: 'COD Transfer',
    headerClass: 'w-[10%] text-right',
    cellClass: 'text-right',
  },
  { key: 'status', label: 'Status', headerClass: 'w-[9%]' },
]

const numericKeys = ['prepayment', 'cod', 'delivery', 'net', 'cod_transfer']
const isNumericColumn = (key) => numericKeys.includes(key)

const getStatusBadgeClass = (status) => {
  return (
    {
      Unsettled: 'bg-red-100 text-red-700',
      Settled: 'bg-emerald-100 text-emerald-700',
    }[status] || 'bg-gray-100 text-gray-600'
  )
}

// Totals
const totalprepayment = computed(() =>
  filteredRows.value.reduce((sum, row) => sum + (row.prepayment || 0), 0),
)
const totalDelivery = computed(() =>
  filteredRows.value.reduce((sum, row) => sum + (row.delivery || 0), 0),
)
const totalCOD = computed(() =>
  filteredRows.value.reduce((sum, row) => sum + (row.cod || 0), 0),
)
const totalNet = computed(() =>
  filteredRows.value.reduce((sum, row) => sum + (row.net || 0), 0),
)
const totalCODTransfer = computed(() =>
  filteredRows.value.reduce((sum, row) => sum + (row.cod_transfer || 0), 0),
)

// CSV Export
const convertToCSV = (objArray) => {
  const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray
  if (!array.length) return ''

  const header = Object.keys(array[0])
    .map((k) => `"${k}"`)
    .join(',')
  const rows = array
    .map((row) =>
      Object.values(row)
        .map((v) => `"${v ?? ''}"`)
        .join(','),
    )
    .join('\r\n')
  return `${header}\r\n${rows}`
}

const goToDetail = (orderId) => {
  if (!orderId) return
  router.push(`/main/${orderId}`)
}

// Fetch on mount and on filter change
onMounted(() => fetchorderwisepayment(inputValue1.value))
watch([startDate, endDate, inputValue1], () => {
  fetchorderwisepayment(inputValue1.value)
})
</script>

<style scoped>
.custom-table-container {
  border-radius: 10px;
}

.pdf-export .custom-table {
  font-size: 10px;
}

.pdf-export .custom-table th,
.pdf-export .custom-table td {
  padding: 4px 6px;
}

.pdf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #d1d5db;
}

.pdf-header-left .pdf-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
}

.pdf-header-left .pdf-date {
  font-size: 12px;
  color: #4b5563;
}

.pdf-header-right {
  text-align: right;
  font-size: 12px;
  color: #16a34a;
  font-weight: 700;
  line-height: 1.3;
}

.row-red {
  background-color: #fcfafa;
  /* Light red for unsettled */
}

.row-blue {
  background-color: #04c27f;
  /* Light blue for settled */
}

.row-gray {
  background-color: #f4f4f4;
  /* Light gray for other statuses */
}
</style>
