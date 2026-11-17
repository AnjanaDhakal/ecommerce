<template>
  <div>
    <div class="mb-4">
      <div class="bg-white mb-2">
        <strong class="text-gray-800">COD Transfer</strong>
      </div>

      <div
        class="grid grid-cols-1 gap-3 sm:flex sm:items-end sm:justify-between"
      >
        <FormControl
          class="w-full sm:w-48"
          :type="'search'"
          size="sm"
          variant="subtle"
          placeholder="Search"
          :disabled="false"
          v-model="inputValue"
        />
        <div class="grid grid-cols-3 gap-2 sm:ml-auto sm:flex sm:items-center">
          <Button
            class="w-full justify-center whitespace-nowrap px-2 text-xs sm:w-auto sm:text-sm"
            variant="solid"
            >Search</Button
          >
          <Button
            class="w-full justify-center whitespace-nowrap px-2 text-xs sm:w-auto sm:text-sm"
            variant="solid"
            @click="downloadCSV"
            >Export CSV</Button
          >
          <Button
            class="w-full justify-center whitespace-nowrap px-2 text-xs sm:w-auto sm:text-sm"
            variant="solid"
            @click="downloadpdf"
            >Export PDF</Button
          >
        </div>
      </div>
    </div>

    <div v-if="isLoading" class="py-6 text-center text-gray-500 text-sm">
      Loading...
    </div>
    <div
      v-else
      ref="pdfTarget"
      :class="{ 'pdf-export': isPdfExport }"
      class="custom-table-container overflow-x-auto"
    >
      <div class="pdf-header" v-if="isPdfExport">
        <div class="pdf-header-left">
          <div class="pdf-title">COD Transfer</div>
        </div>
        <div class="pdf-header-right">
          <div class="pdf-date">Printed Date: {{ formattedToday }}</div>
        </div>
      </div>
      <AppDataTable
        :columns="tableColumns"
        :rows="displayedRows"
        :stack-on-mobile="false"
        row-key="id"
        empty-text="No records found"
        table-class="min-w-[760px] table-fixed text-sm [&_th]:!px-3 [&_th]:!py-2 [&_th]:!text-xs [&_th]:!font-medium [&_th]:!normal-case [&_th]:!tracking-normal [&_td]:!px-3 [&_td]:!py-2.5 [&_td]:!text-sm"
        wrapper-class="shadow-none"
      >
        <template #cell-created_date="{ row }">
          <span :class="row.isTotal ? 'font-semibold' : ''">
            {{ row.created_date }}
          </span>
        </template>

        <template #cell-id="{ row }">
          <button
            v-if="!row.isTotal"
            type="button"
            class="font-medium text-blue-600"
            @click.stop="goToDetail(row.id)"
          >
            {{ row.id }}
          </button>
          <span v-else>{{ row.id }}</span>
        </template>

        <template
          v-for="key in numericKeys"
          :key="`cod-${key}`"
          #[`cell-${key}`]="{ row }"
        >
          <span
            class="block text-right"
            :class="row.isTotal ? 'font-semibold' : ''"
          >
            {{ row[key] }}
          </span>
        </template>

        <template #cell-branch_name="{ row }">
          <span :class="row.isTotal ? 'font-semibold' : ''">
            {{ row.branch_name }}
          </span>
        </template>

        <template #mobile-row="{ row }">
          <button
            v-if="!row.isTotal"
            type="button"
            class="block w-full space-y-1 text-left text-sm text-gray-700"
            @click="goToDetail(row.id)"
          >
            <p>
              <span class="font-medium text-gray-500">Created Date:</span>
              {{ row.created_date }}
            </p>
            <p>
              <span class="font-medium text-gray-500">ID:</span>
              <span class="font-medium text-blue-600">{{ row.id }}</span>
            </p>
            <p>
              <span class="font-medium text-gray-500">Order Count:</span>
              {{ row.child_row_count }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Paid Amount:</span>
              {{ row.paid_amount }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Received Amount:</span>
              {{ row.received_amount }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Branch:</span>
              {{ row.branch_name }}
            </p>
          </button>
          <div v-else class="space-y-1 text-sm font-semibold text-gray-700">
            <p>{{ row.created_date }}</p>
            <p>
              <span class="font-medium text-gray-500">Paid Amount:</span>
              {{ row.paid_amount }}
            </p>
            <p>
              <span class="font-medium text-gray-500">Received Amount:</span>
              {{ row.received_amount }}
            </p>
          </div>
        </template>
      </AppDataTable>
    </div>
  </div>
</template>

<script setup>
import { Button, FormControl } from 'frappe-ui'
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import AppDataTable from './AppDataTable.vue'
import codtransfer from '../data/codtransfer'
import html2pdf from 'html2pdf.js'
import dayjs from 'dayjs'
const inputValue = ref('')

const isLoading = ref(true)
const pdfTarget = ref(null)
const isPdfExport = ref(false)
const formattedToday = computed(() => dayjs().format('YYYY-MM-DD'))
const router = useRouter()

const formatCreatedDate = (value) => {
  if (!value) return '-'

  const parsedDate = dayjs(value)
  return parsedDate.isValid() ? parsedDate.format('YYYY-MM-DD hh:mm A') : '-'
}

const fetchcodtransfer = async () => {
  try {
    await codtransfer.fetch()
    if (
      codtransfer.data &&
      codtransfer.data.data &&
      codtransfer.data.data.cod_transfer &&
      Array.isArray(codtransfer.data.data.cod_transfer)
    ) {
      rows.value = codtransfer.data.data.cod_transfer.map((t) => {
        return {
          ...t,
          created_date: formatCreatedDate(
            t.created_date || t.creation || t.created_at,
          ),
        }
      })

      //  //console.log("gfsdhfg",rows.value) // log the result
    } else {
      //console.error('No data available or data is not an array')
    }
  } catch (error) {
    //console.error('Error fetching :', error)
  } finally {
    isLoading.value = false
  }
}

const totalRow = computed(() => {
  if (filteredRows.value.length === 0) return null

  const totalPaidAmount = filteredRows.value.reduce((sum, row) => {
    const amount = parseFloat(row.paid_amount.replace(/[^0-9.-]+/g, '')) || 0
    return sum + amount
  }, 0)

  const totalReceivedAmount = filteredRows.value.reduce((sum, row) => {
    const amount =
      parseFloat(row.received_amount.replace(/[^0-9.-]+/g, '')) || 0
    return sum + amount
  }, 0)

  const total = {
    created_date: 'Total', // Indicate this is the total row
    id: '-',
    child_row_count: '-',
    paid_amount: `Rs ${totalPaidAmount.toFixed(2)}`, // Format totals back to currency
    received_amount: `Rs ${totalReceivedAmount.toFixed(2)}`, // Format totals back to currency
    branch_name: '-',
    isTotal: true,
  }

  //  // console.log('Computed Total Row:', total); // Log the total row for verification
  return total
})

const displayedRows = computed(() => {
  return totalRow.value
    ? [...filteredRows.value, totalRow.value]
    : filteredRows.value
})

const filteredRows = computed(() => {
  let result = rows.value
  if (inputValue.value) {
    result = result.filter((row) =>
      Object.values(row).some(
        (val) =>
          val &&
          val.toString().toLowerCase().includes(inputValue.value.toLowerCase()),
      ),
    )
  }

  return result
})

onMounted(() => {
  fetchcodtransfer()
})

const numericKeys = ['child_row_count', 'paid_amount', 'received_amount']

const tableColumns = [
  {
    key: 'created_date',
    label: 'Created Date',
    headerClass: 'w-[24%]',
    cellClass: 'w-[24%]',
  },
  {
    key: 'id',
    label: 'ID',
    headerClass: 'w-[18%]',
    cellClass: 'w-[18%]',
  },
  {
    key: 'child_row_count',
    label: 'Order Count',
    headerClass: 'w-[14%] text-right',
    cellClass: 'w-[14%] text-right',
  },

  {
    key: 'paid_amount',
    label: 'Paid Amount',
    headerClass: 'w-[16%] text-right',
    cellClass: 'w-[16%] text-right',
  },
  {
    key: 'received_amount',
    label: 'Received Amount',
    headerClass: 'w-[16%] text-right',
    cellClass: 'w-[16%] text-right',
  },
  {
    key: 'branch_name',
    label: 'Branch',
    headerClass: 'w-[22%]',
    cellClass: 'w-[22%]',
  },
]

const rows = ref([])

const goToDetail = (id) => {
  if (!id || id === '-') return
  router.push(`/account/COD/${id}`)
}

const convertToCSV = (objArray) => {
  const array = typeof objArray !== 'object' ? JSON.parse(objArray) : objArray
  if (!array.length) return ''
  const exportColumns = columns.filter((c) => c.key !== 'action')
  const header = exportColumns.map((c) => `"${c.label}"`).join(',')
  const rows = array
    .map((row) => exportColumns.map((c) => `"${row[c.key] ?? ''}"`).join(','))
    .join('\r\n')
  return `${header}\r\n${rows}`
}

const downloadCSV = () => {
  const dataToExport = filteredRows.value
  if (!dataToExport.length) return
  const csv = convertToCSV(dataToExport)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'COD Transfer.csv')
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
  if (!element) {
    isPdfExport.value = false
    return
  }
  const options = {
    margin: 0.2,
    filename: 'COD Transfer.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      scrollX: 0,
      scrollY: -window.scrollY,
      width:
        (pdfTarget.value?.scrollWidth || pdfTarget.value?.offsetWidth) + 24,
      windowWidth:
        (pdfTarget.value?.scrollWidth || pdfTarget.value?.offsetWidth) + 24,
    },
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
</script>

<style scoped>
.custom-table-container {
  border-radius: 10px;
}

.pdf-export {
  overflow: visible;
  width: max-content;
  padding: 12px;
  background: #ffffff;
  border-radius: 0;
  box-shadow: none;
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

.pdf-export :deep(.grid) {
  width: max-content;
  gap: 0;
}

.pdf-export :deep(.grid > div) {
  padding: 4px 6px;
  font-size: 12px;
  white-space: normal;
  display: flex;
  align-items: center;
}

.pdf-export :deep(.truncate) {
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: normal !important;
}
</style>
