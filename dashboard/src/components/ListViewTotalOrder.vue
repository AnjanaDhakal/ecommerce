<template>
  <div>
    <div class="mb-4">
      <div class="bg-white">
        <!-- <div
          class="flex items-center justify-between h-15 rounded bg-gray-50 p-2"
        >
          <CreateNew
            supportTicketTitle="My Orders List"
            addTicketLabel="+ Add Order"
          />
        </div> -->
        <!-- <div class="flex  h-15 rounded  p-2">
          <div class="">
            <FormControl class="w-36" type="search" size="sm" variant="subtle" placeholder="Search" :disabled="false"
              label="Search" v-model="inputValue" />
          </div>
          <div class="flex">
            <div class="pl-4 mt-4
              <BulkUpdate />
            </div>
            <div class="pl-4 mt-4 ">
              <Button @click="openPDF" variant="solid" aria-label="Print All">
                <div class="flex justify-around items-center space-x-2 flex-row">
                  <FeatherIcon name="printer" class="text-white h-5 " />
                  <span class="hidden sm:block">Print All</span>
                </div>
              </Button>
            </div>
          </div>

        </div> -->
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
            <div class="mt-4 sm:mt-0">
              <Button @click="openPDF" variant="solid" aria-label="Print">
                <div
                  class="flex justify-around items-center space-x-2 flex-row"
                >
                  <FeatherIcon name="printer" class="text-white h-5" />
                  <span class="">Print</span>
                </div>
              </Button>
            </div>
          </div>
        </div>

        <div class="mt-3">
          <div class="flex border-b">
            <div
              class="py-1 px-4 border-b-2 border-transparent rounded-tl-md rounded-tr-md text-white bg-green-500 transition-all duration-300 ease-in-out transform hover:scale-y-110 hover:translate-y-1"
            >
              <p class="text-center font-pregular text-xs">
                Open Orders
                <span class="inline-flex items-center justify-center
            min-w-[18px] h-[14px] mx-2 px-1
            rounded-full
            text-[10px] font-medium
            bg-white text-green-600">
{{ openCount }}
                </span>
              </p>
            </div>
            <div
              class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
              @click="cancel"
            >
              <p class="text-center pt-1 font-pregular text-xs">
                Cancel Orders     <span class="inline-flex items-center justify-center
            min-w-[18px] h-[14px] mx-2 px-1
            rounded-full
            text-[10px] font-medium
            bg-green-600 text-white"> {{ cancelledCount }} </span>
              </p>
            </div>
            <div
              class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
              @click="ongoing"
            >
              <p class="text-center pt-1 font-pregular text-xs">
                Ongoing Pickups <span class="inline-flex items-center justify-center
            min-w-[18px] h-[14px] mx-2 px-1
            rounded-full
            text-[10px] font-medium
            bg-green-600 text-white"> {{ initiatedCount }} </span>
              </p>
            </div>
          </div>

          <div class="">
            <ListView
              class="text-sm !font-light listview-min-height listview-padding"
              :columns="columns"
              :rows="filteredRows"
              :options="options"
              row-key="name"
              @row-click="handleRowClick"
              @update:selections="updateSelections"
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
                v-else-if="column.key === 'customer_name'"
                class="block whitespace-normal break-words"
              >
                {{ item }}
              </span>
              <span
                v-else-if="column.key === 'destination_branch'"
                class="block whitespace-normal break-words"
              >
                {{ item }}
              </span>
              <span
                v-else-if="column.key === 'order_description'"
                class="block whitespace-normal break-words text-xs text-black"
              >
                {{ item }}
              </span>
              <span v-else-if="column.key !== 'name'">{{ item }}</span>
              <span
                v-else
                class="flex flex-col gap-1"
                :title="
                  row.express_delivery === 1
                    ? 'Express delivery'
                    : row.order_type === 'Return'
                      ? 'Return order'
                      : ''
                "
              >
                <span class="flex items-center gap-1">
                  <span class="whitespace-normal break-words font-bold">{{
                    item
                  }}</span>
                  <span
                    v-if="Number(row.express_delivery) === 1"
                    class="material-symbols-outlined text-rose-600 text-sm leading-none"
                  >
                    rocket_launch
                  </span>
                  <span
                    v-if="row.order_type === 'Return'"
                    class="material-symbols-outlined text-amber-600 text-sm leading-none"
                  >
                    undo
                  </span>
                </span>
                <span
                  v-if="row.vendor_tracking_number"
                  class="text-xs text-black whitespace-normal break-words"
                >
                  {{ row.vendor_tracking_number }}
                </span>
                <span
                  v-else
                  class="text-xs text-transparent"
                >
                  &nbsp;
                </span>
              </span>
            </router-link>

            <div
              @click="
                row.status === 'Open' || row.status === 'Cancelled'
                      ? handleEditClick(row)
                      : null
                  "
                  v-if="column.key === 'modify'"
                  title="Edit order"
                  :class="[
                    'flex items-center justify-center cursor-pointer',
                    {
                      'cursor-not-allowed opacity-50':
                        row.status !== 'Open' && row.status !== 'Cancelled',
                    },
                  ]"
                >
                  <FeatherIcon
                    name="edit"
                    class="w-4 text-blue-500 cursor-pointer"
                  />
                </div>
                <div
                  @click="
                    row.status === 'Open' || row.status === 'Cancelled'
                      ? openPDF1(row)
                      : null
                  "
                  v-if="column.key === 'print'"
                  title="Print order"
                  :class="[
                    'flex items-center justify-center cursor-pointer',
                    {
                      'cursor-not-allowed opacity-50':
                        row.status !== 'Open' && row.status !== 'Cancelled',
                    },
                  ]"
                >
                  <FeatherIcon
                    name="printer"
                    class="text-blue-500 h-5 cursor-pointer"
                  />
                </div>

                <div
                  v-if="column.key === 'action'"
                  title="Cancel order"
                  :class="[
                    'flex items-center justify-center',
                    {
                      'cursor-not-allowed opacity-50':
                        row.status !== 'Open' && row.status !== 'Cancelled',
                    },
                  ]"
                >
                  <template v-if="row.status === 'Open'">
                    <div
                      class="flex items-center justify-center"
                      @click="handleCancelClick(row)"
                    >
                      <FeatherIcon
                        name="x-circle"
                        class="w-4 text-red-500 cursor-pointer"
                      />
                    </div>
                  </template>
                </div>
              </template>
            </ListView>
            <div class="bg-gray-50 p-4 rounded-lg mt-6">
              <div
                class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
              >
                <h3
                  class="text-lg font-semibold text-gray-800 border-b sm:border-none pb-2 sm:pb-0"
                >
                  Total Value
                </h3>
                <div
                  class="text-sm font-medium flex flex-col sm:flex-row gap-4"
                >
                  <div class="flex items-center gap-2">
                    <span class="text-gray-700">Total COD Amount:</span>
                    <span class="text-blue-600 font-bold">{{ totalCOD }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="text-gray-700">Total Delivery Charge:</span>
                    <span class="text-green-600 font-bold">{{
                      totalDelivery
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        class="flex flex-col sm:flex-row p-6 space-y-4 sm:space-y-0 sm:space-x-2"
      >
        <!-- Pagination Info -->
        <!-- <div
          class="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4"
        >
          <span class="block text-sm text-gray-500"
            >Total Orders: {{ totalOrders }}</span
          >
          <span class="block text-sm text-gray-500"
            >Current Orders: {{ orderonPages }}</span
          >
          <span class="block text-sm text-gray-500"
            >Page {{ currentPage }} of {{ totalPages }}</span
          >
        </div> -->

        <!-- Pagination Buttons -->
        <!-- <div class="flex space-x-2 justify-center sm:justify-start">
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
        </div> -->

        <Pagination
          v-slot="{ page }"
          :items-per-page="pageSize"
          :total="totalOrders"
          :default-page="currentPage"
          class=""
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
      </div>

      <!-- <div class="flex p-6">

        <div class="flex space-x-2">
          <span class="block text-sm text-gray-500">Total Orders: {{ totalOrders }}</span>
          <span class="block text-sm text-gray-500">Current Orders: {{ orderonPages }}</span>
          <span class="block text-sm text-gray-500">Page {{ currentPage }} of {{ totalPages }}</span>

          <Button variant="outline"
            class="px-6 py-2 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-200 transition-all duration-300 disabled:bg-gray-100"
            :disabled="currentPage <= 1" @click="changePage(currentPage - 1)">
            Previous
          </Button>
          <Button variant="outline"
            class="px-6 py-2 border border-gray-300 rounded-sm text-gray-700 hover:bg-gray-200 transition-all duration-300 disabled:bg-gray-100"
            :disabled="currentPage >= totalPages" @click="changePage(currentPage + 1)">
            Next
          </Button>
        </div>
      </div> -->

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
    <div class="inline-block lg:hidden fixed bottom-24 right-4">
      <DialogPickup />
    </div>
  </div>
</template>

<script setup>
import { DatePicker, Button, FormControl, FileUploader, Tabs } from 'frappe-ui'
import EditOrder from './EditOrder.vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'
import DialogPickup from './DialogPickup.vue'
import CreateNew from '../components/CreateNew.vue'
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { ListView, Badge, FeatherIcon } from 'frappe-ui'
import orderDetails from '../data/orderDetails'
import openorderDetails from '../data/openorderdetail'
import ordercount from '../data/ordercount'
import { displayDialog } from '../composables/displayDialog'
import DialogOrder from './DialogOrder.vue'
import CancelOrder from './CancelOrder.vue'
import ReopenOrder from './ReopenOrder.vue'
import BulkUpdate from './BulkUpdate.vue'
import PageLoader from './PageLoader.vue'
import logo from '../assets/logo.png'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'
const router = useRouter()

const cancel = () => {
  router.push('/cancelorder')
}

const ongoing = () => {
  router.push('/pickuplist')
}

// const state = reactive({
//   index: 0,
//   tabs_without_icon: [
//     { label: 'Open Order', content: 'Displaying Open Orders', color: 'green' },
//     { label: 'Cancelled Order', content: 'Displaying Cancelled Orders', color: 'red', route: '/cancelorder' },
//   ],
// });
const state = reactive({
  index: 0,
  tabs_without_icon: [
    {
      label: 'Open Order',
      content: 'Displaying Open Orders',
      color: 'green',
      route: '/order',
    },
    // { label: 'Cancelled Order', content: 'Displaying Cancelled Orders', color: 'red', route: '/cancelorder' },
  ],
})

const handleTabChange = (index) => {
  router.push(state.tabs_without_icon[index].route)
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
const pageSize = ref(40)
const editDisplay = ref(false)
const cancelDisplay = ref(false)
const reopenDisplay = ref(false)
const selectname = ref('')
const openrows = ref([])
const totalCOD = ref(0)
const totalDelivery = ref(0)

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
  selectable: true,
  showTooltip: false,
  resizeColumn: true,
  rowHeight: 'auto',
  emptyState: {
    title: 'No records found',
    description: 'Create a new record to get started',
  },
})

const columns = reactive([
  { label: 'SN', key: 'sn', width: '50px' },
  { label: 'Date', key: 'creation', width: '110px' },
  { label: 'Order ID', key: 'name', width: '120px' },
  { label: 'Customer Name', key: 'customer_name', width: '140px' },
  { label: 'Destination Branch', key: 'destination_branch', width: '130px' },
  { label: 'Description', key: 'order_description', width: '120px' },
  { label: 'Phone', key: 'phone', width: '100px' },
  { label: 'COD Amount', key: 'cod_amount', width: '100px' },
  { label: 'Delivery Amount', key: 'delivery_amount', width: '80px' },
  { label: 'Modify', key: 'modify', width: '60px' },
  { label: 'Print', key: 'print', width: '60px' },
  { label: 'Action', key: 'action', width: '60px' },
])

const fetchOpenOrderDetails = async () => {
  isLoading.value = true
  try {
    await openorderDetails.fetch({
      limit_start: (currentPage.value - 1) * pageSize.value,
      limit_page_length: pageSize.value,
    })
  //  // console.log('openorderDetails', openorderDetails.data)

    const mappedRows = Array.from(openorderDetails.data?.data?.orders || [])
      .map((t) => ({
        ...t,
        creation: dayjs(t.creation).format('YYYY-MM-DD HH:mm:ss'),
        phone: t.secondary_mobile_no
          ? `${t.primary_mobile_no}, ${t.secondary_mobile_no}`
          : t.primary_mobile_no,
        cod_amount: `${t.cod_amount.toLocaleString('en-IN', options)}`,
        modify: 'Edit',
        action: 'Cancel',
        print: '',
      }))
      .sort((a, b) => new Date(b.creation) - new Date(a.creation))

    openrows.value = mappedRows.map((row, index) => ({
      ...row,
      sn: (currentPage.value - 1) * pageSize.value + index + 1,
    }))

   //  // console.log("rowsopen", openrows.value);
    const { current_page, total_pages, total_orders, orders_on_current_page } =
      openorderDetails.data.data.pagination
    currentPage.value = current_page
    totalPages.value = total_pages
    totalOrders.value = total_orders
    orderonPages.value = orders_on_current_page

    const statusCounts = openorderDetails?.data?.data?.status_counts || {}
    openCount.value = statusCounts.open ?? total_orders
    cancelledCount.value = statusCounts.cancelled ?? 0
    initiatedCount.value = statusCounts.initiated ?? 0

    // Extract total COD and delivery amounts
    totalCOD.value = openorderDetails?.data?.data?.total_cod_amount || 0
    totalDelivery.value =
      openorderDetails?.data?.data?.total_delivery_amount || 0

   //  // console.log('Total COD:', totalCOD.value);
   //  // console.log('Total Delivery:', totalDelivery.value);

    // Keep columns stable even if some fields are empty
  } catch (e) {
    //console.error('Error fetching open order details:', e);
  } finally {
    isLoading.value = false
  }
}

const filteredRows = computed(() => {
  let result = openrows.value
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
  return status === 'Open' ? 'green' : status === 'Cancelled' ? 'red' : 'gray'
}
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
}

watch(currentPage, fetchOpenOrderDetails)

onMounted(() => {
  fetchOpenOrderDetails()
})

const handleRowClick = (row) => {
  selectedRowOrder = row
  editDisplay.value = true
}
// const handleCancelClick = (row) => {
//   selectedRowOrder = row;
//   cancelDisplay.value = true;
// };

const handleOrderCreated = () => {
  fetchOpenOrderDetails()
}
const handleEditClick = (row) => {
  selectedRowOrder = row
 //  // console.log('selectedRowOrdermngdcjfhgds', selectedRowOrder.name)
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
  fetchOpenOrderDetails()
  if (typeof ordercount.fetch === 'function') {
    ordercount.fetch().catch((err) =>
      console.error('Failed to refresh order counts after cancel:', err),
    )
  }
}

import html2pdf from 'html2pdf.js'
import JsBarcode from 'jsbarcode'
import QRCode from 'qrcode'
import { PRINT_FONT_FAMILY, waitForPrintFonts } from '../lib/printFonts'

const ticketListContainer = ref(null)
const printDetails = ref(null)
const selectedKeys = ref(new Set())
const selectedCount = computed(
  () => Array.from(selectedKeys.value || []).length,
)

const updateSelections = (selections) => {
  selectedKeys.value = selections || new Set()
}

const getExpressStampHtml = (isExpress) =>
  Number(isExpress) === 1
    ? `
      <div class="express-stamp-wrapper">
        <img
          class="express-stamp-image"
          src="/express-delivery-stamp.jpg"
          alt="Express Delivery"
        >
      </div>
    `
    : ''

const getContainerClass = (isExpress) =>
  Number(isExpress) === 1 ? 'container express-order' : 'container'

const ticketPrintStyles = `
 .container {
  width: 400px;
  margin: auto;
  padding: 5px;
  box-sizing: border-box;
  position: relative;
  overflow: hidden;
  font-family: ${PRINT_FONT_FAMILY};
  page-break-after: always;
  page-break-inside: avoid;
  margin-top: 8px;
}

@media print {
  .container:last-child {
    page-break-after: auto;
  }
}

  .header {
    display: flex;
    justify-content: flex-start;
    gap: 60px;
    align-items: center;
    font-size: 0.5rem;
  }

  .header-info {
    line-height: 1;
    font-size: 0.6rem;
    padding-bottom: 10px;
  }

  .header-right {
    padding-bottom: 10px;
    text-align: center;
    font-size: 0.6rem;
  }

  .barcode-section {
    display: flex;
    justify-content: flex-start;
    gap: 10px;
    margin-top: 3px;
  }

  .qr-code img {
    width: 80px;
    height: 80px;
  }

  .bar-code img {
    width: 180px;
    height: 40px;
  }

  .instruction {
    font-size: 0.6rem;
    text-align: start;
  }

  .branch-section {
    font-size: 0.9rem;
    font-weight: bold;
    text-align: center;
    margin-top: -20px;
  }

  .details-row {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
  }

  .details-column {
    flex: 1;
    margin-right: 0;
    padding: 3px;
  }

  .details-column:last-child {
    margin-right: 0;
  }

  .label-field {
    margin: 1px 0;
  }

  .label-field b {
    display: inline-block;
    width: 80px;
    font-weight: bold;
  }

  .footer {
    margin-top: 5px;
    padding-top: 5px;
    border-top: 1px solid #ccc;
    font-size: 0.5rem;
    text-align: center;
  }

  .small-block {
    display: inline-block;
    border-radius: 5px;
    padding: 5px;
    margin: 1px;
    background-color: black;
    width: 45px;
    height: 15px;
    margin-top: 5px;
  }

  .express-order .details-column:last-child {
    box-sizing: border-box;
    padding-right: 98px;
  }

  .express-stamp-wrapper {
    position: absolute;
    right: 4px;
    bottom: 0;
    width: 102px;
    height: 58px;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    overflow: visible;
    pointer-events: none;
  }

  .express-stamp-image {
    display: block;
    width: 82px;
    height: auto;
    margin-right: 6px;
    transform: rotate(-7deg);
    transform-origin: bottom right;
  }

  body {
    font-size: 0.7rem;
  }
`

const buildOrderHtml = async (order) => {
  const creationDate = dayjs(order.creation).format('YYYY-MM-DD')

  const canvas = document.createElement('canvas')
  JsBarcode(canvas, order.name, { format: 'CODE39', displayValue: false })

  const barcodeDataUrl = canvas.toDataURL('image/png')
  const qrCodeDataUrl = await QRCode.toDataURL(order.name)

  return `
  <div class="${getContainerClass(order.express_delivery)}">
    <!-- Header Section -->
   <div class="header">
  <div class="header-info">
  <div>
    <h>
      Pick & Drop
      </h>
      </div>
  </div>
  <div class="header-right">
    <div>www.pickndropnepal.com | 015971511 | ${creationDate}</div>
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
      <strong>Instruction:</strong>${order.instruction || ''}
    </div>
      </div>
    </div>
    <!-- Branch Section -->
    <div class="branch-section">
      <span>${order.pickup_branch}</span> To <span>${order.destination_branch}</span>
    </div>

    <!-- Details Section -->
    <div class="details-row">
      <div class="details-column">
        <div class="label-field"><b>To:</b> ${order.customer_name}</div>
        <div class="label-field"><b>Phone:</b> ${order.primary_mobile_no}${order.secondary_mobile_no ? ` / ${order.secondary_mobile_no}` : ''}</div>
        <div class="label-field"><b>Address:</b> ${order.location}${order.name_of_city_area ? `, ${order.name_of_city_area}` : ''}</div>
        <div class="label-field"><b>COD:</b>${order.cod_amount} ${order.green_delivery ? `<img src="https://www.pickndropnepal.com/files/leaf (1).png" alt="Green Delivery" style="width: 20px; height: auto;">` : ''}</div>
      </div>

      <div class="details-column">
        <div class="label-field"><b>From:</b> ${order.vendor_name}</div>
        <div class="label-field"><b>Type:</b> ${order.order_type}</div>
        <div class="label-field"><b>Order ID:</b> <strong style="font-size: 1rem;">${order.name}</strong></div>
        ${order.vendor_tracking_number ? `<div class="label-field"><b>Reference ID:</b> ${order.vendor_tracking_number}</div>` : ''}

        ${
          order.location_type === 'Outside Valley' &&
          order.branch_owner === 'Self'
            ? `
          <div class="small-block"></div>
        `
            : ''
        }

        ${
          order.location_type === 'Outside Valley' &&
          order.branch_owner === 'Agent'
            ? `
          <div class="small-block"></div>
          <div class="small-block"></div>
        `
            : ''
        }

        ${
          order.location_type === 'Outside Valley' &&
          order.branch_owner === '3PL'
            ? `
          <div class="small-block"></div>
          <div class="small-block"></div>
          <div class="small-block"></div>
        `
            : ''
        }
      </div>
    </div>

    ${getExpressStampHtml(order.express_delivery)}
  </div>

    `
}

const getSelectedPrintDetails = async () => {
  const selectedOrders = openrows.value.filter(
    (row) => selectedKeys.value.has(row.name) && row.status === 'Open',
  )
  if (!selectedOrders.length) {
    ticketListContainer.value = null
    return
  }

  let allOrdersHtml = ''

  for (const order of selectedOrders) {
    allOrdersHtml += await buildOrderHtml(order)
  }

  ticketListContainer.value = `
  <html>
  <head>
    <meta charset="utf-8">
    <title>Barcode Generator</title>
<style>
${ticketPrintStyles}
</style>

  </head>
  <body>
    ${allOrdersHtml}
  </body>
  </html>
  `
  await waitForPrintFonts()
}

const getPrintDetails = async () => {
  const response = await openorderDetails.fetch({
    limit_start: (currentPage.value - 1) * pageSize.value,
    limit_page_length: pageSize.value,
  })

  printDetails.value = openorderDetails.data?.data?.orders.filter(
    (t) => t.status === 'Open',
  )
 //  // console.log("hvhf",printDetails.value)

  let allOrdersHtml = ''
  for (const order of printDetails.value) {
    allOrdersHtml += await buildOrderHtml(order)
  }

  ticketListContainer.value = `
  <html>
  <head>
    <meta charset="utf-8">
    <title>Barcode Generator</title>
<style>
${ticketPrintStyles}
</style>

  </head>
  <body>
    ${allOrdersHtml}
  </body>
  </html>
  `
  await waitForPrintFonts()
}

// Call the function to fetch and log print details

getPrintDetails()
// Call your printing logic after fetching the data

watch(currentPage, (newPage) => {
  getPrintDetails() // Re-fetch for printing on page change
})

const openPDF = async () => {
  if (selectedCount.value > 0) {
    await openPDFSelected()
    return
  }
  await getPrintDetails()

  const element = ticketListContainer.value

  if (!element) {
    // console.error('ticketListContainer element is not found or not rendered.')
    return
  }

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
    //   console.error('PDF generation failed:', err)
  }
}

const openPDFSelected = async () => {
  await getSelectedPrintDetails()
  const element = ticketListContainer.value

  if (!element) {
    return
  }

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
    //   console.error('PDF generation failed:', err)
  }
}

const singleticketListContainer = ref(null)
const singleprintDetails = ref(null)

const getSinglePrintDetails = async (row) => {
  await openorderDetails.fetch()
  singleprintDetails.value = openorderDetails.data.data.orders.filter(
    (order) => order.name == row.name,
  )

 //  // console.log(singleprintDetails.value);

  const creationDate = dayjs(singleprintDetails.value[0].creation).format(
    'YYYY-MM-DD',
  )
  singleprintDetails.value[0].creation = creationDate

  const canvas = document.createElement('canvas')
  JsBarcode(canvas, singleprintDetails.value[0].name, {
    format: 'CODE39',
    displayValue: false,
  })
  const imageUrl =
    'https://www.pickndropnepal.com/files/Screenshot%20from%202024-03-29%2000-29-54.png'

  const barcodeDataUrl = canvas.toDataURL('image/png')

  const qrCodeDataUrl = await QRCode.toDataURL(singleprintDetails.value[0].name)

  singleticketListContainer.value = `
<html>
<head>
  <meta charset="utf-8">
  <title>Barcode Generator</title>
  <style>
${ticketPrintStyles}
  </style>
</head>
<body>
  <div class="${getContainerClass(singleprintDetails.value[0].express_delivery)}">
    <!-- Header Section -->
   <div class="header">
  <div class="header-info">
  <div>
    <h>
      Pick & Drop
      </h>
      </div>
  </div>
  <div class="header-right">
    <div>www.pickndropnepal.com | 015971511 | ${singleprintDetails.value[0].creation}</div>
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
        <div class="label-field "><b>Address:</b> ${singleprintDetails.value[0].location}${singleprintDetails.value[0].name_of_city_area ? `, ${singleprintDetails.value[0].name_of_city_area}` : ''}</div>
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

    ${getExpressStampHtml(singleprintDetails.value[0].express_delivery)}
  </div>
</body>
</html>


  `
}

const openPDF1 = async (row) => {
  await getSinglePrintDetails(row)
  const element = singleticketListContainer.value

  if (!element) {
    //console.error('ticketListContainer element is not found or not rendered.');
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
    //  console.error('PDF generation failed:', err);
  }
}
</script>

<style scoped>
:deep(.listview-min-height .grid.items-center) {
  min-height: 40px;
  height: auto !important;
}

:deep(.listview-padding .grid.items-center) {
  padding-top: 6px;
  padding-bottom: 6px;
}
</style>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
</style>
