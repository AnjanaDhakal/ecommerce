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

        <div class="flex border-b mt-3">
          <div
            class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
            @click="open"
          >
            <p class="text-center pt-1 font-pregular text-xs">
              Open Orders
              <span
                class="inline-flex items-center justify-center min-w-[18px] mx-2 h-[14px] px-1 rounded-full text-[10px] font-medium bg-green-600 text-white"
              >
                {{ openCount }}
              </span>
            </p>
          </div>
          <div
            class="cursor-pointer px-4 border-t-2 rounded-tl-md rounded-tr-md hover:border-gray-500 hover:text-gray-500"
            @click="cancel"
          >
            <p class="text-center pt-1 font-pregular text-xs">
              Cancel Orders
              <span
                class="inline-flex items-center justify-center min-w-[18px] mx-2 h-[14px] px-1 rounded-full text-[10px] font-medium bg-green-600 text-white"
              >
                {{ cancelledCount }}
              </span>
            </p>
          </div>
          <div
            class="py-1 px-4 border-b-2 border-transparent rounded-tl-md rounded-tr-md text-white bg-green-500 transition-all duration-300 ease-in-out transform hover:scale-y-110 hover:translate-y-1"
          >
            <p class="text-center font-pregular text-xs">
              Ongoing Pickups
              <span
                class="inline-flex items-center justify-center min-w-[18px] mx-2 h-[14px] px-1 rounded-full text-[10px] font-medium bg-white text-green-600"
              >
                {{ initiatedCount }}
              </span>
            </p>
          </div>
        </div>

        <ListView
          :options="options"
          :columns="columns"
          :rows="rows"
          class="text-sm !font-light"
        >
          <PageLoader v-if="isLoading" />
          <template #cell="{ item, row, column }">
            <span v-if="column.key === 'sn'">{{ row.sn }}</span>
            <router-link v-else :to="`/main/${row.name}`" target="_blank">
              <Badge
                v-if="column.key === 'status'"
                :variant="'subtle'"
                :theme="getBadgeClass(item)"
                size="sm"
                :label="item"
              />
              <span v-else-if="column.key === 'action'">
                <FeatherIcon name="eye" class="h-5 w-5 text-blue-500" />
              </span>
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
          </template>
        </ListView>
        <DialogOrder
          v-model="displayDialog.isDisplay"
          @orderCreated="handleOrderCreated"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { displayDialog } from '../composables/displayDialog'

import PageLoader from './PageLoader.vue'
import { DatePicker, Button, FormControl } from 'frappe-ui'
import { ref, onMounted } from 'vue'
import { computed } from 'vue'
import { reactive } from 'vue'
import { ListView, Badge, FeatherIcon } from 'frappe-ui'
import { useRouter } from 'vue-router'
import Pickup from '../data/pickup'
import BulkUpdate from './BulkUpdate.vue'
import CreateNew from '../components/CreateNew.vue'
import DialogOrder from './DialogOrder.vue'

const router = useRouter()
const dateValue = ref('')
const dateValue1 = ref('')
//console.log(Pickup)

const inputValue = ref('')

let isLoading = ref(true)
const openCount = ref(0)
const cancelledCount = ref(0)
const initiatedCount = ref(0)

const fetchPickup = async () => {
  isLoading.value = true
  try {
    await Pickup.fetch()
   //  // console.log('Pickup data:', Pickup.data)
    if (
      Pickup.data &&
      Pickup.data.data &&
      Pickup.data.data.orders &&
      Array.isArray(Pickup.data.data.orders)
    ) {
      rows.value = Pickup.data.data.orders
        .filter((t) => t.status === 'Initiated')
        .map((t, index) => {
          // Create a new Date object from the creation field
          const creationDate = new Date(t.creation)

          //   const orderId = t.vendor_tracking_number
          // ? `${t.name} / ${t.vendor_tracking_number}`
          // : t.name;
          // Format the date and time
          const formattedDate = creationDate.toLocaleDateString()
          const formattedTime = creationDate.toLocaleTimeString()

          // Return the new object
          return {
            ...t,
            sn: index + 1,
            creation: `${formattedDate} ${formattedTime}`,
            action: 'Edit',
            editClicked: false,
          }
        })
      const statusCounts = Pickup.data?.data?.status_counts || {}
      openCount.value = statusCounts.open ?? 0
      cancelledCount.value = statusCounts.cancelled ?? 0
      initiatedCount.value = statusCounts.initiated ?? 0
    } else {
      //  console.error('No data available or data is not an array')
    }
  } catch (error) {
    // console.error('Error fetching :', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchPickup()
})

const cancel = () => {
  router.push('/cancelorder')
}

const open = () => {
  router.push('/order')
}

// const filteredRows = computed(() => {
//   if (!inputValue.value) {
//     return rows.value;
//   }
//   return rows.value.filter(row =>
//     Object.values(row).some(val =>
//       val && val.toString().toLowerCase().includes(inputValue.value.toLowerCase())
//     )
//   );
// });
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

// const fetchFilteredData = async (startDate, endDate) => {
//   try {
//     const params = new URLSearchParams({
//       start_date: startDate,
//       end_date: endDate,
//     });

//     const url = `/api/method/ecommerce.api.filter_by_dateinitiated?${params.toString()}`;
//    // console.log('API Request URL:', url); // Log the URL

//     const response = await fetch(url, {
//       method: 'GET',
//     });

//     const data = await response.json();
//     //console.log(data);

//     if (data?.message?.data && Array.isArray(data.message.data.orders)) {
//   rows.value = data.message.data.orders.map((t) => {
//     const creationDate = new Date(t.creation);
//     const formattedDate = creationDate.toLocaleDateString();
//     const formattedTime = creationDate.toLocaleTimeString();
//     const orderId = orders.vendor_tracking_number
//           ? `${orders.name} / ${orders.vendor_tracking_number}`
//           : orders.name;
//     return {
//       ...t,
//       name: orderId,
//       creation: `${formattedDate} ${formattedTime}`,
//       action: 'Edit',
//       editClicked: false,
//     };
//       });
//     } else {
//       console.error('No data available or data is not an array');
//     }
//   } catch (error) {
//     console.error('Error fetching filtered data:', error);
//   }
// };

const onFilterClick = async () => {
  const startDate = dateValue.value
    ? new Date(dateValue.value).toISOString().split('T')[0]
    : null
  const endDate = dateValue1.value
    ? new Date(dateValue1.value).toISOString().split('T')[0]
    : null

  if (!startDate || !endDate) {
    //  console.error('Both start date and end date are required for filtering.');
    return
  }

  if (new Date(startDate) > new Date(endDate)) {
    //console.error('Start date should be earlier than end date');
    return
  }

  try {
    await fetchFilteredData(startDate, endDate)
  } catch (error) {
    // console.error('Error during filtering:', error);
  }
}

const getBadgeClass = (status) => {
  switch (status) {
    case 'Initiated':
      return 'blue'

    default:
      return 'gray'
  }
}

const columns = reactive([
  {
    label: 'SN',
    key: 'sn',
    width: '60px',
  },
  {
    label: 'Date',
    key: 'creation',
    width: '100px',
    getLabel: ({ row }) => row.date,
  },
  {
    label: 'Order Code',
    key: 'name',
    width: '150px',
  },
  {
    label: 'Customer Name',
    key: 'customer_name',
    width: '150px',
  },
  {
    label: 'Phone',
    key: 'primary_mobile_no',
    width: '100px',
  },
  {
    label: 'COD Amount',
    key: 'cod_amount',
    width: '80px',
  },

  {
    label: 'Delivery Amount',
    key: 'delivery_amount',
    width: '80px',
  },

  { label: 'Pickup Branch', key: 'pickup_branch', width: '100px' },
  { label: 'Destination Branch', key: 'destination_branch', width: '100px' },

  {
    label: 'Action',
    key: 'action',
    width: '90px',
  },
])

const rows = ref([])
const options = reactive({
  selectable: false,
  showTooltip: false,
  resizeColumn: true,
  emptyState: {
    title: 'No records found',
    //description: 'Create a new record to get started',
  },
})
</script>
