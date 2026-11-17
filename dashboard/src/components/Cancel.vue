// totalorder
<template>
  <div>
    <div class="mb-4">
      <div class="bg-white">

        <div class="flex flex-col sm:flex-row rounded mt-4 gap-2">
          <div class="">
            <FormControl
              class="w-full sm:w-36"
              type="search"
              size="sm"
              variant="subtle"
              placeholder="Search"
              :disabled="false"
              v-model="inputValue"
            />
          </div>
          <div class="flex flex-row sm:flex-row gap-2">
            <div class="mt-4 sm:mt-0">
              <BulkUpdate />
            </div>
          </div>
        </div>

        <!-- <div class="flex border-b mt-3">
          <div
            class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
            @click="cancel"
          >
            <p class="text-center pt-1 font-pregular text-xs">Open orders</p>
          </div>

          <div
            class="cursor-pointer pb-1 px-2 border-t-2 border-transparent rounded-tl-md rounded-tr-md text-white bg-green-500 transition-all duration-300 ease-in-out transform hover:scale-y-110 hover:translate-y-1"
          >
            <p class="text-center pt-1 font-pregular text-xs">Cancel orders</p>
          </div>

          <div
            class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
            @click="cancel"
          >
            <p class="text-center pt-1 font-pregular text-xs">
              Ongoing Pickups
            </p>
          </div>
        </div> -->

        <div class="flex border-b mt-3">
          <div
            class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
            @click="open"
          >

             <p class="text-center pt-1 font-pregular text-xs">
                Open Orders     <span class="inline-flex items-center justify-center
            min-w-[18px]  mx-2 h-[14px] px-1
            rounded-full
            text-[10px] font-medium
            bg-green-600 text-white"> {{ openCount }} </span>
              </p>
          </div>
          <div
            class="py-1 px-4 border-b-2 border-transparent rounded-tl-md rounded-tr-md text-white bg-green-500 transition-all duration-300 ease-in-out transform hover:scale-y-110 hover:translate-y-1"
          >
            <p class="text-center font-pregular text-xs">
              Cancel Orders
                   <span class="inline-flex items-center justify-center
            min-w-[18px]  mx-2 h-[14px] px-1
            rounded-full
            text-[10px] font-medium
            bg-white text-green-600">
{{ cancelledCount }}
                </span>
            </p>
          </div>
          <div
            class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
            @click="ongoing"
          >
            <p class="text-center pt-1 font-pregular text-xs">
              Ongoing Pickups
               <span class="inline-flex items-center justify-center
            min-w-[18px]  mx-2 h-[14px] px-1
            rounded-full
            text-[10px] font-medium
            bg-green-600 text-white">  {{ initiatedCount }} </span>
            </p>
          </div>
        </div>





        <div class="">
          <ListView
            class="text-sm !font-light"
            :columns="columns"
            :rows="filteredRows"
            :options="options"
            row-key="id"
            @row-click="handleRowClick"
          >
            <PageLoader v-if="isLoading" />
            <template #cell="{ item, row, column }">
              <span v-if="column.key === 'sn'">{{ row.sn }}</span>
              <router-link
                target="_blank"
                v-else-if="column.key !== 'modify' && column.key !== 'action'"
                :to="`/main/${row.name}`"
                class="block"
              >
                <Badge
                  v-if="column.key === 'status'"
                  :variant="'subtle'"
                  :theme="getBadgeClass(item)"
                  size="sm"
                  :label="item"
                />
                <span
                  v-else-if="column.key === 'name'"
                  class="flex flex-col gap-1"
                >
                  <span class="whitespace-normal break-words font-bold">{{
                    item
                  }}</span>
                  <span
                    v-if="row.vendor_tracking_number"
                    class="text-xs text-black whitespace-normal break-words"
                  >
                    {{ row.vendor_tracking_number }}
                  </span>
                  <span v-else class="text-xs text-transparent">&nbsp;</span>
                </span>
                <span v-else>{{ item }}</span>
              </router-link>

              <div
                @click="
                  row.status === 'Disabled' || row.status === 'Cancelled'
                    ? handleEditClick(row)
                    : null
                "
                v-if="column.key === 'modify'"
                :class="[
                  'flex items-center gap-1 cursor-pointer',
                  {
                    'cursor-not-allowed opacity-50':
                      row.status !== 'Disabled' && row.status !== 'Cancelled',
                  },
                ]"
              >
                <FeatherIcon
                  name="edit"
                  class="w-4 text-blue-500 cursor-pointer"
                />
                {{ item }}
              </div>

              <div
                v-if="column.key === 'action'"
                :class="[
                  'flex items-center gap-1 flex-row',
                  {
                    'cursor-not-allowed opacity-50':
                      row.status !== 'Disabled' && row.status !== 'Cancelled',
                  },
                ]"
              >
                <!--   <template v-if="row.status === 'Open'">
                                   <div class="flex items-center gap-1 flex-row" @click="handleCancelClick(row)">
                                        <FeatherIcon name="x-circle" class="w-4 text-red-500 ml-2 cursor-pointer" />
                                        <span class="text-red-600 cursor-pointer">{{ item }}</span>
                                    </div>
                                </template>-->
                <template
                  v-if="row.status === 'Disabled' || row.status === 'Cancelled'"
                >
                  <div
                    class="flex items-center gap-1 flex-row"
                    @click="handleReopenClick(row)"
                  >
                    <FeatherIcon
                      name="check-circle"
                      class="w-4 text-green-500 ml-2 cursor-pointer"
                    />
                    <span class="text-green-600 cursor-pointer"
                      >Re-processing</span
                    >
                  </div>
                </template>
              </div>
            </template>
          </ListView>
        </div>
      </div>

      <!-- <div class="flex p-6">
        <div class="flex space-x-2">
          <span class="block text-sm text-gray-500"
            >Total Orders: {{ totalOrders }}</span
          >

          <span class="block text-sm text-gray-500"
            >Current Orders: {{ orderonPages }}</span
          >

          <span class="block text-sm text-gray-500"
            >Page {{ currentPage }} of {{ totalPages }}</span
          >

          <Button
            variant="outline"
            class="px-6 py-2 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-200 transition-all duration-300 disabled:bg-gray-100"
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
          >
            Previous
          </Button>

          <Button
            variant="outline"
            class="px-6 py-2 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-200 transition-all duration-300 disabled:bg-gray-100"
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
          >
            Next
          </Button>
        </div>
      </div> -->

      <Pagination
        v-slot="{ page }"
        :items-per-page="pageSize"
        :total="totalOrders"
        :default-page="currentPage"
        class="mt-4"
      >
        <PaginationContent v-slot="{ items }">
          <PaginationPrevious @click="changePage(page - 1)" />

          <template v-for="(item, index) in items" :key="index">
            <PaginationItem
              v-if="item.type === 'page'"
              :value="item.value"
              :is-active="item.value === page"
              @click="changePage(item.value)"
            >
              {{ item.value }}
            </PaginationItem>
          </template>

          <PaginationNext @click="changePage(page + 1)" />
        </PaginationContent>
      </Pagination>

      <DialogOrder
        v-model="displayDialog.isDisplay"
        @orderCreated="handleOrderCreated"
      />
      <EditOrder
        v-model="editDisplay"
        :selectedRowOrder="selectedRowOrder"
        @orderCreated="handleOrderCreated"
      />
      <CancelOrder
        v-model="cancelDisplay"
        :selectname="selectname"
        @OrderCancelled="OrderCancelled"
      />
      <ReopenOrder
        v-model="reopenDisplay"
        :selectname="selectname"
        @OrderCancelled="OrderCancelled"
      />
    </div>
  </div>
</template>

<script setup>
import { DatePicker, Button, FormControl, FileUploader, Tabs } from 'frappe-ui'
import EditOrder from './EditOrder.vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'
import CreateNew from '../components/CreateNew.vue'
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { ListView, Badge, FeatherIcon } from 'frappe-ui'
import orderDetails from '../data/orderDetails'
import cancelledorderDetails from '../data/cancelledorderdetail'
import ordercount from '../data/ordercount'
import { displayDialog } from '../composables/displayDialog'
import DialogOrder from './DialogOrder.vue'
import CancelOrder from './CancelOrder.vue'
import ReopenOrder from './ReopenOrder.vue'
import BulkUpdate from './BulkUpdate.vue'
import PageLoader from './PageLoader.vue'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
const router = useRouter()

const open = () => {
  router.push('/order')
}

const ongoing = () => {
  router.push('/pickuplist')
}

const inputValue = ref('')
const totalPages = ref(1)
const orderonPages = ref('')
const rows = ref([])
const isLoading = ref(true)
const totalOrders = ref(0)
const openCount = ref(0)
const cancelledCount = ref(0)
const initiatedCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const editDisplay = ref(false)
const cancelDisplay = ref(false)
const reopenDisplay = ref(false)
const selectname = ref('')

let selectedRowOrder = reactive({
  customer_name: '',
  primary_mobile_no: '',
  secondary_mobile_no: '',
  name_of_city_area: '',
  location: '',
  destination_branch: '',
  cod_amount: '',
  delivery_amount: 0,
  is_paid_order: '',
  weight: '',
  order_description: '',
  instruction: '',
  enableGreen: '',
  order_type: '',
  pickup_branch: '',
  vendor_address: '',
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
const fetchCancelledOrderDetails = async () => {
  isLoading.value = true
  try {
    await cancelledorderDetails.fetch({
      limit_start: (currentPage.value - 1) * pageSize.value,
      limit_page_length: pageSize.value,
    })



    const mappedRows = cancelledorderDetails.data?.data?.orders
      .map((t) => ({
        ...t,
        creation: dayjs(t.creation).format('YYYY-MM-DD HH:mm:ss'),
        phone: t.secondary_mobile_no
          ? `${t.primary_mobile_no}, ${t.secondary_mobile_no}`
          : t.primary_mobile_no,
        cod_amount: `${t.cod_amount.toLocaleString('en-IN', options)}`,
        status: t.status === 'Open' ? 'Disabled' : t.status,
        modify: 'Edit',
        action: 'Cancel',
      }))
      .sort((a, b) => new Date(b.creation) - new Date(a.creation))

    rows.value = mappedRows.map((row, index) => ({
      ...row,
      sn: (currentPage.value - 1) * pageSize.value + index + 1,
    }))
   //  //console.log("rowsgfdsg", rows.value)
    const { current_page, total_pages, total_orders, orders_on_current_page } =
      cancelledorderDetails.data.data.pagination
    currentPage.value = current_page
    totalPages.value = total_pages
    totalOrders.value = total_orders
    orderonPages.value = orders_on_current_page

    const statusCounts = cancelledorderDetails.data?.data?.status_counts || {}
    openCount.value = statusCounts.open ?? 0
    cancelledCount.value = statusCounts.cancelled ?? 0
    initiatedCount.value = statusCounts.initiated ?? 0

    // Check if any order has a non-empty tracking number
    const hasTrackingNumber = rows.value.some(
      (order) => order.vendor_tracking_number,
    )
    if (!hasTrackingNumber) {
      // Remove the 'Reference No' column if all tracking numbers are empty
      const index = columns.findIndex(
        (column) => column.key === 'vendor_tracking_number',
      )
      if (index !== -1) {
        columns.splice(index, 1)
      }
    }
  } catch (e) {
    // console.error('Error fetching order details:', e);
  } finally {
    isLoading.value = false
  }
}

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

const getBadgeClass = (status) => {
  return status === 'Disabled'
    ? 'green'
    : status === 'Cancelled'
      ? 'red'
      : 'gray'
}
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

watch(currentPage, fetchCancelledOrderDetails)

onMounted(() => {
  fetchCancelledOrderDetails()
})

const columns = reactive([
  { label: 'SN', key: 'sn', width: '50px' },
  { label: 'Date', key: 'creation', width: '110px' },
  { label: 'Order ID', key: 'name', width: '150px' },
  { label: 'Customer Name', key: 'customer_name', width: '200px' },
  { label: 'Phone', key: 'phone', width: '100px' },
  { label: 'COD Amount', key: 'cod_amount', width: '100px' },
  { label: 'Delivery Amount', key: 'delivery_amount', width: '80px' },
  { label: 'Status', key: 'status', width: '100px' },
  { label: 'Modify', key: 'modify', width: '80px' },
  { label: 'Action', key: 'action', width: '80px' },
])

const handleRowClick = (row) => {
  selectedRowOrder = row
  editDisplay.value = true
}
// const handleCancelClick = (row) => {
//   selectedRowOrder = row;
//   cancelDisplay.value = true;
// };

const handleOrderCreated = () => {
  fetchCancelledOrderDetails()
}
const handleEditClick = (row) => {
  selectedRowOrder = row
  editDisplay.value = true
}

const handleCancelClick = (row) => {
  selectedRowOrder = row
 //  // console.log('selectedRowOrder', selectedRowOrder);
  selectname.value = row.name
  cancelDisplay.value = true
}
const handleReopenClick = (row) => {
  selectedRowOrder = row
 //  //console.log('selectedRowOrder', selectedRowOrder);
  selectname.value = row.name
  reopenDisplay.value = true
}
const OrderCancelled = () => {
  fetchCancelledOrderDetails()
  if (typeof ordercount.fetch === 'function') {
    ordercount.fetch().catch((err) =>
      console.error('Failed to refresh order counts after reopen:', err),
    )
  }
}

import html2pdf from 'html2pdf.js'
import JsBarcode from 'jsbarcode'
import QRCode from 'qrcode'
import { PRINT_FONT_FAMILY, waitForPrintFonts } from '../lib/printFonts'

const ticketListContainer = ref(null)
const printDetails = ref(null)

const getPrintDetails = async () => {
  const response = await cancelledorderDetails.fetch({
    limit_start: (currentPage.value - 1) * pageSize.value,
    limit_page_length: pageSize.value,
  })

  printDetails.value = cancelledorderDetails.data?.data?.orders.filter(
    (t) => t.status === 'Open',
  )
 //  // console.log("hvhf",printDetails.value)

  let allOrdersHtml = ''
  const printedTime = dayjs().format('YYYY-MM-DD HH:mm A')

  for (const order of printDetails.value) {
    order.creation = dayjs(order.creation).format('YYYY-MM-DD HH:mm A')

    const canvas = document.createElement('canvas')
    JsBarcode(canvas, order.name, { format: 'CODE39' })

    const barcodeDataUrl = canvas.toDataURL('image/png')
    const qrCodeDataUrl = await QRCode.toDataURL(order.name)

    const orderHtml = `
    <div class="order ">

      <div class="container" style="margin-bottom:0px; height:75mm; overflow:auto;">

        <table>
          <tr>
            <td colspan="3">
              <div class="barcode-container">
      <img src="${barcodeDataUrl}" alt="barcode" height="30px" width="160px" />

    </div>
     </td>
            </tr>
          <tr>
            <td rowspan="6" class="qr-code-cell">
              <strong style="padding-left: 5px;">From:</strong> ${order.pickup_branch}<br>
              <strong style="padding-left: 5px;">To:</strong> ${order.destination_branch}<br>
              <img src="${qrCodeDataUrl}" alt="qrcode" style="padding-top:5px;" width="130px"/>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom:10px;">
              <p"><strong style="padding-left: 5px;">Weight</strong></p>
              <p "><span style="padding-left: 5px;">${order.package_weight} Kg</span></p>
            </td>
            <td style="padding-bottom:10px;">
              <p ><strong style="padding-left: 5px;">COD Amount</strong></p>
              <p ><span style="padding-left: 5px;">${order.cod_amount}</span></p>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom:10px;"><strong style="padding-left: 5px;">Order ID</strong></td>
            <td style="padding-bottom:10px;"><span style="padding-left: 5px;">${order.name}</span></td>
          </tr>
          <tr>
            <td style="padding-bottom:10px;" colspan="2"><strong style="padding-left: 5px;">Sender: </strong><span style="padding-left: 5px;">${order.vendor_name}</span></td>
          </tr>
          <tr>
            <td style="padding-bottom:10px;" colspan="2">
              <p style="padding-left:5px;"><strong >Name: <span style="padding-left: 5px;font-size: 12px; text: bold;">${order.customer_name}</span></strong></p>
              <p style="padding-left: 5px;">${order.location}</p>
              <p style="padding-left: 5px;">${order.primary_mobile_no}</p>
            </td>
          </tr>
          <tr>
            <td colspan="3">
              <div class="phone-container">
          <p>Print Date: <br/> ${printedTime}</p>
          <p>Created Date: <br /> ${order.creation}</p>
        </div>
              </td>
            </tr>
        </table>

      </div>
    </div>

    `
    allOrdersHtml += orderHtml
  }

  ticketListContainer.value = `
  <html>
  <head>
    <meta charset="utf-8">
    <title>Barcode Generator</title>
    <style>
      p {
        line-height: 1;
        margin: 0;
        word-wrap: break-word;
        overflow-wrap: break-word;
      }
      table, th, td {
        border: 1px solid black;
        border-collapse: collapse;
        text-align: left;
        font-size: 10px;
        padding: 2px;
      }
      table {
        width: 100%;
      }
      .container {
        display: flex;
        flex-direction: column;
        padding: 2px;
        font-size: 8px;
        font-family: ${PRINT_FONT_FAMILY};


      }
      .barcode-container {
        display: flex;
        justify-content: center;
        align-items: center;
      }
      td[colspan="2"] {
        vertical-align: top;
      }
      td.qr-code-cell {
        width: 150px;
      }
      .phone-container {
        clear: both;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
      }
      .page-break {
        page-break-after: always;
      }

    </style>
  </head>
  <body>
    ${allOrdersHtml}
  </body>
  </html>
  `
}

// Call the function to fetch and log print details
getPrintDetails()

const openPDF = async () => {
  const element = ticketListContainer.value

  if (!element) {
    //  console.error('ticketListContainer element is not found or not rendered.')
    return
  }

  await waitForPrintFonts()

  const opt = {
    filename: 'ticket-list.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: [100, 75], orientation: 'landscape' },
  }

  try {
    const pdfBlob = await html2pdf().from(element).set(opt).outputPdf('blob')
    const pdfUrl = URL.createObjectURL(pdfBlob)
    window.open(pdfUrl, '_blank')
  } catch (err) {
    // console.error('PDF generation failed:', err)
  }
}

const singleticketListContainer = ref(null)
const singleprintDetails = ref(null)

const getSinglePrintDetails = async (row) => {
  await cancelledorderDetails.fetch()
  singleprintDetails.value = cancelledorderDetails.data.data.orders.filter(
    (order) => order.name == row.name,
  )

 //  // console.log(singleprintDetails.value);

  const printedTime = dayjs().format('YYYY-MM-DD HH:mm A')

  const creationDate = dayjs(singleprintDetails.value[0].creation).format(
    'YYYY-MM-DD',
  )
  singleprintDetails.value[0].creation = creationDate

  const canvas = document.createElement('canvas')
  JsBarcode(canvas, singleprintDetails.value[0].name, {
    format: 'CODE39',
    displayValue: false,
  })

  const barcodeDataUrl = canvas.toDataURL('image/png')

  const qrCodeDataUrl = await QRCode.toDataURL(singleprintDetails.value[0].name)

  singleticketListContainer.value = `
<html>
<head>
  <meta charset="utf-8">
  <title>Barcode Generator</title>
  <style>
    .container {
      width: 400px; /* Reduced container width */
      margin: auto;
      padding: 5px; /* Reduced padding */
      font-family: ${PRINT_FONT_FAMILY};
    }

    .header {

      display: flex;
     justify-content: flex-start;
     gap: 60px;
      align-items: center;
      font-size: 0.5rem; /* Reduced font size */

    }

    .header-info {
      line-height: 1;
      font-size: 0.6rem; /* Smaller font size */
       padding-bottom: 10px;
    }

    .header-right {
   padding-bottom: 10px;
      text-align: center;
      font-size: 0.6rem; /* Further reduced font size */
    }

    .barcode-section {
  display: flex;
  justify-content: flex-start; /* Align items to the left */
  gap: 10px; /* Add a small gap between the QR code and barcode */
  margin-top: 3px; /* Keep reduced margin */
}

    .qr-code img {
      width: 80px; /* Reduced QR code size */
      height: 80px;
    }

    .bar-code img {
      width: 180px; /* Reduced barcode size */
      height: 40px; /* Reduced height */
    }

    .instruction {
      font-size: 0.6rem; /* Smaller font size */
      text-align: start;
    }

    .branch-section {
      font-size: 0.9rem; /* Slightly reduced font size */
      font-weight: bold;
      text-align: start;
    }

    .details-row {
      display: flex;
      justify-content: space-between;
      font-size: 0.7rem; /* Reduced font size */
    }

    .details-column {
      flex: 1;
      margin-right: 0;
      padding: 3px; /* Reduced padding */
    }

    .details-column:last-child {
      margin-right: 0;
    }

    .label-field {
      margin: 1px 0; /* Reduced margin */
    }

    .label-field b {
      display: inline-block;
      width: 80px; /* Adjusted label width */
      font-weight: bold;
    }

    .footer {
      margin-top: 5px; /* Reduced margin */
      padding-top: 5px; /* Reduced padding */
      border-top: 1px solid #ccc;
      font-size: 0.5rem; /* Reduced font size */
      text-align: center;
    }

    .small-block {
      display: inline-block;
      border-radius: 5px;
      padding: 5px;
      margin: 1px;
      background-color: black;
      width: 45px; /* Reduced size */
      height: 15px; /* Reduced height */
      margin-top:5px;
    }

    /* Ensure no overflow on small screens */
    body {
      font-size: 0.7rem; /* Further reduced overall font size */
    }

  </style>
</head>
<body>
  <div class="container">
    <!-- Header Section -->
   <div class="header">
  <div class="header-info">
  <div>
    <h>
      Pick&Drop Nepal
      </h>
      </div>
  </div>
  <div class="header-right">
    <div>www.pickndropnepal.com | 9801235800 | ${singleprintDetails.value[0].creation}</div>
  </div>
</div>

    <!-- Barcode / QR Code Section -->
    <div class="barcode-section">
      <div class="qr-code">
        <img src="${qrCodeDataUrl}" alt="QR Code">
      </div>
      <div class="bar-code">
        <img src="${barcodeDataUrl}" alt="Barcode">
         <div class="instruction">
      <strong>Instruction:</strong>${singleprintDetails.value[0].instruction}
    </div>
      </div>
    </div>
    <!-- Branch Section -->
    <div class="branch-section">
      <span>${singleprintDetails.value[0].pickup_branch}</span> To <span>${singleprintDetails.value[0].destination_branch}</span>
    </div>

    <!-- Details Section -->
    <div class="details-row">
      <div class="details-column">
        <div class="label-field"><b>To:</b> ${singleprintDetails.value[0].customer_name}</div>
        <div class="label-field"><b>Phone:</b> ${singleprintDetails.value[0].primary_mobile_no}${singleprintDetails.value[0].secondary_mobile_no ? ` / ${singleprintDetails.value[0].secondary_mobile_no}` : ''}</div>
        <div class="label-field"><b>Address:</b> ${singleprintDetails.value[0].location}${singleprintDetails.value[0].name_of_city_area ? `, ${singleprintDetails.value[0].name_of_city_area}` : ''}</div>
        <div class="label-field"><b>COD:</b>${singleprintDetails.value[0].cod_amount} ${singleprintDetails.value[0].green_delivery ? `<img src="https://www.pickndropnepal.com/files/leaf (1).png" alt="Green Delivery" style="width: 20px; height: auto;">` : ''}</div>
      </div>

      <div class="details-column">
        <div class="label-field"><b>From:</b> ${singleprintDetails.value[0].vendor_name}</div>
        <div class="label-field"><b>Type:</b> ${singleprintDetails.value[0].order_type}</div>
        <div class="label-field"><b>Order ID:</b> <strong style="font-size: 1rem;">${singleprintDetails.value[0].name}</strong></div>
        ${singleprintDetails.value[0].vendor_tracking_number ? `<div class="label-field"><b>Reference ID:</b> ${singleprintDetails.value[0].vendor_tracking_number}</div>` : ''}

        ${
          singleprintDetails.value[0].location_type === 'Outside Valley' &&
          singleprintDetails.value[0].branch_owner === 'Self'
            ? `
          <div class="small-block"></div>
        `
            : ''
        }

        ${
          singleprintDetails.value[0].location_type === 'Outside Valley' &&
          singleprintDetails.value[0].branch_owner === 'Agent'
            ? `
          <div class="small-block"></div>
          <div class="small-block"></div>
        `
            : ''
        }

        ${
          singleprintDetails.value[0].location_type === 'Outside Valley' &&
          singleprintDetails.value[0].branch_owner === '3PL'
            ? `
          <div class="small-block"></div>
          <div class="small-block"></div>
          <div class="small-block"></div>
        `
            : ''
        }
      </div>
    </div>

    <!-- Footer Section -->
    <div class="footer">
      <em>Start selling online with Pick&Drop! We deliver across Nepal to help grow your business.</em>
    </div>
  </div>
</body>
</html>


  `
}

const openPDF1 = async (row) => {
  await getSinglePrintDetails(row)
  const element = singleticketListContainer.value

  if (!element) {
    // console.error('ticketListContainer element is not found or not rendered.');
    return
  }

  await waitForPrintFonts()

  const opt = {
    filename: 'ticket-list.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'mm', format: [100, 75], orientation: 'landscape' },
  }

  try {
    const pdfBlob = await html2pdf().from(element).set(opt).outputPdf('blob')
    const pdfUrl = URL.createObjectURL(pdfBlob)
    window.open(pdfUrl, '_blank')
  } catch (err) {
    // console.error('PDF generation failed:', err);
  }
}
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>
