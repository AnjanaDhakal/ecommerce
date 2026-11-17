<template>
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen">
    <div v-if="isLoading" class="mt-40 text-center">
      <PageLoader />
    </div>
    <div v-if="filteredDetails.length">
      <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen">
        <div
          class="flex items-center justify-between h-15 rounded bg-gray-50 p-5 mb-5"
        >
          <BreadCrums />
        </div>

        <div class="bg-white min-h-screen p-4 rounded">
          <div class="flex justify-between items-center flex-wrap gap-2">
            <div class="bg-white mb-4">
              <strong class="text-gray-800">COD Transfer Details</strong>
            </div>
            <div class="flex items-center gap-2 ml-auto">
              <Button variant="solid" @click="downloadCSV">Export in CSV</Button>
              <Button variant="solid" @click="downloadpdf">Export in PDF</Button>
            </div>
          </div>

          <div
            class="cod-list-wrapper"
            ref="pdfTarget"
            :class="{ 'pdf-export': isPdfExport }"
          >
            <div class="pdf-header" v-if="isPdfExport">
              <div class="pdf-header-left">
                <div class="pdf-title">COD Transfer Details</div>
                <div class="pdf-meta">
                  <div v-if="pdfMeta.transfer_id"><span class="pdf-meta-label">Transfer ID:</span> {{ pdfMeta.transfer_id }}</div>
                  <div v-if="pdfMeta.created_date"><span class="pdf-meta-label">Payment Date:</span> {{ pdfMeta.created_date }}</div>
                </div>
              </div>
              <div class="pdf-header-right">
                <div class="pdf-date">Printed Date: {{ formattedToday }}</div>
              </div>
            </div>
            <ListView
              class="text-sm cod-table"
              :columns="columns"
              :rows="filteredDetailsWithTotal"
              :options="options"
              row-key="package_id"
            >
              <template #cell="{ item, column }">
                <span :class="cellAlignClass(column.key)">
                  <template v-if="column.key === 'package_id'">
                    <span class="inline-flex items-center gap-1">
                      <span>{{ item }}</span>
                      <Rocket
                        v-if="Number(item?.express_delivery) === 1"
                        class="h-3.5 w-3.5 text-rose-600"
                        title="Express Delivery"
                      />
                    </span>
                  </template>
                  <template v-if="column.key === 'order_type' && item === '-'">
                    <!-- keep dash aligned without italic/offset -->
                    -
                  </template>
                  <template v-else-if="column.key !== 'package_id'">
                    {{ item }}
                  </template>
                </span>
              </template>
            </ListView>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <div v-if="!isLoading" class="text-center">
        <FoundNot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import BreadCrums from '../components/BreadCrums.vue'
import PageLoader from '../components/PageLoader.vue'
import {
  DatePicker,
  Button,
  FormControl,
  ListView,
  Badge,
  FeatherIcon,
} from 'frappe-ui'
import FoundNot from '../components/FoundNot.vue'
import html2pdf from 'html2pdf.js'
import dayjs from 'dayjs'
import { Rocket } from 'lucide-vue-next'

const route = useRoute()
const id = route.params.id
let isLoading = ref(true)
const transfers = ref([])
//console.log("gsjjsgf",id)
const dateValue = ref('')
const dateValue1 = ref('')
const inputValue = ref('')
const detail = ref([])
const pdfTarget = ref(null)
const isPdfExport = ref(false)
const formattedToday = computed(() => dayjs().format('YYYY-MM-DD'))

import codtransfer from '../data/codtransfer'
//console.log(codtransfer)
const fetchcodtransferdetails = async () => {
  isLoading.value = true
  try {
    await codtransfer.fetch()
    if (
      codtransfer.data &&
      codtransfer.data.data &&
      codtransfer.data.data.cod_transfer &&
      Array.isArray(codtransfer.data.data.cod_transfer)
    ) {
      const codTransferData = codtransfer.data.data.cod_transfer
      transfers.value = codTransferData
      const toNumber = (val) =>
        parseFloat(String(val || '').replace(/[^0-9.-]+/g, '')) || 0
      rows.value = codTransferData.flatMap((t) =>
        t.table_data.map((td) => ({
          ...td,
          net_amount: `Rs ${(toNumber(td.cod_amount) - toNumber(td.delivery_charge)).toFixed(2)}`,
        })),
      )
     //  //console.log('rows:', rows.value);
    } else {
      //console.error('No data available or data is not an array')
    }
  } catch (error) {
    //console.error('Error fetching :', error)
  } finally {
    isLoading.value = false
  }
}

const filteredDetails = computed(() => {
  return rows.value.filter((row) => row.id === id)
})

onMounted(() => {
  fetchcodtransferdetails()
})

const pdfMeta = computed(() => {
  const selected = transfers.value.find((t) => t.id === id) || {}
  return {
    created_date: selected.created_date || '',
    transfer_id: selected.id || '',
  }
})

const options = reactive({
  selectable: false,
  showTooltip: false,
  resizeColumn: true,
  emptyState: {
    title: 'No records found',
    description: 'Create a new record to get started',
  },
})

const filteredDetailsWithTotal = computed(() => {
  const details = filteredDetails.value
  if (details.length === 0) return []

  const total = details.reduce(
    (acc, row) => {
      acc.pre_payment += parseFloat(row.pre_payment.replace('Rs ', '') || 0)
      acc.cod_amount += parseFloat(row.cod_amount.replace('Rs ', '') || 0)
      acc.delivery_charge += parseFloat(
        row.delivery_charge.replace('Rs ', '') || 0,
      )
      acc.net_amount += parseFloat(row.net_amount.replace('Rs ', '') || 0)
      return acc
    },
    {
      package_id: 'Total',
      delivered_date: '-',
      customer_name: '-',
      customer_phone: '-',
      pre_payment: 0,
      cod_amount: 0,
      delivery_charge: 0,
      net_amount: 0,
      order_type: '-',
      isTotal: true,
    },
  )

  // Format the totals back to "Rs X.XX"
  total.cod_amount = `Rs ${total.cod_amount.toFixed(2)}`
  total.delivery_charge = `Rs ${total.delivery_charge.toFixed(2)}`
  total.pre_payment = `Rs ${total.pre_payment.toFixed(2)}`
  total.net_amount = `Rs ${total.net_amount.toFixed(2)}`

  return [...details, total]
})

const columns = reactive([
  {
    label: 'ID',
    key: 'package_id',
    width: '100px',
    align: 'left',
  },
  {
    label: 'Delivered Date',
    key: 'delivered_date',
    width: '130px',
    align: 'left',
  },
  {
    label: 'Customer Name',
    key: 'customer_name',
    width: '160px',
    align: 'left',
  },
  {
    label: 'Phone',
    key: 'customer_phone',
    width: '140px',
    align: 'left',
  },
  {
    label: 'Pre Payment',
    key: 'pre_payment',
    width: '110px',
    align: 'right',
  },
  {
    label: 'COD Amount',
    key: 'cod_amount',
    width: '110px',
    align: 'right',
  },
  {
    label: 'Delivery Charge',
    key: 'delivery_charge',
    width: '120px',
    align: 'right',
  },
  {
    label: 'Net Amount',
    key: 'net_amount',
    width: '120px',
    align: 'right',
  },
  {
    label: 'Order Type',
    key: 'order_type',
    width: '120px',
    align: 'left',
  },
])

// CSV Export
const convertToCSV = (objArray) => {
  const array = typeof objArray != 'object' ? JSON.parse(objArray) : objArray
  let str = `${Object.keys(array[0])
    .map((value) => `"${value}"`)
    .join(',')}\r\n`

  return array.reduce((str, next) => {
    str += `${Object.values(next)
      .map((value) => `"${value}"`)
      .join(',')}\r\n`
    return str
  }, str)
}

const downloadCSV = () => {
  let csv = convertToCSV(filteredDetails.value)
  let blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  let link = document.createElement('a')
  let url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', 'COD Transfer Details.csv')
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
const rows = ref([])

const downloadpdf = async () => {
  if (!filteredDetailsWithTotal.value.length) return
  isPdfExport.value = true
  await nextTick()
  const element = pdfTarget.value
  if (!element) {
    isPdfExport.value = false
    return
  }

  const options = {
    margin: 0.2,
    filename: 'COD Transfer Details.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      scrollX: 0,
      scrollY: -window.scrollY,
      width: (pdfTarget.value?.scrollWidth || pdfTarget.value?.offsetWidth) + 24,
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

const cellAlignClass = (key) => {
  const rightAligned = ['pre_payment', 'cod_amount', 'delivery_charge', 'net_amount']
  if (rightAligned.includes(key)) return 'block w-full text-right text-gray-800'
  return 'block w-full text-left text-gray-800'
}
</script>

<style scoped>
.cod-list-wrapper :deep(.overflow-x-auto) {
  overflow-x: visible;
}

.cod-list-wrapper :deep(.w-max.min-w-full) {
  width: 100%;
  min-width: 0;
}

.cod-list-wrapper :deep(.grid) {
  min-width: 0;
}

.cod-list-wrapper :deep(.grid > div) {
  min-width: 0;
  word-break: break-word;
  overflow-wrap: anywhere;
  display: flex;
  align-items: center;
}

.pdf-export {
  overflow: visible;
  width: max-content;
  padding: 12px;
  background: #ffffff;
  border-radius: 0;
  box-shadow: none;
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

.pdf-meta {
  margin-top: 4px;
  font-size: 12px;
  color: #4b5563;
}

.pdf-meta-label {
  font-weight: 600;
  color: #111827;
  margin-right: 4px;
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

.cod-table :deep(.grid > div),
.cod-table :deep(.grid > div span) {
  color: #1f2937; /* text-gray-800 */
}
</style>
