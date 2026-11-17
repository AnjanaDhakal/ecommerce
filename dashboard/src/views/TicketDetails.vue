<template>
  <div>
    <div v-if="isLoading" class="mt-40 text-center">
      <PageLoader />
    </div>
    <div v-if="viewTicket" class="p-4 lg:bg-gray-200 min-h-screen">
      <div class="p-3 lg:p-4 selection:rounded-lg min-h-screen">
        <div class="grid grid-cols-1 gap-4 mb-4">
          <div
            class="flex items-center justify-between h-15 rounded bg-gray-50 p-5"
          >
            <BreadCrums />
          </div>
        </div>
        <div class="mb-4 rounded bg-gray-50 p-5">
          <div
            class="flex flex-col sm:flex-row justify-between items-start sm:items-center"
          >
            <div
              class="flex flex-col sm:flex-row justify-between gap-2 items-start sm:items-center"
            >
              <h2 class="font-bold text-2xl text-gray-600">
                # {{ viewTicket.subject }}
              </h2>
              <Badge
                :variant="'subtle'"
                :theme="getStatusColor(viewTicket.status)"
                size="sm"
                :label="viewTicket.status"
              />
            </div>
            <div class="mt-4 sm:mt-0">
              <Button
                :variant="'solid'"
                @click="markAsResolved"
                :disabled="viewTicket.status === 'Resolved'"
              >
                Mark as Resolved
              </Button>
            </div>
          </div>
          <!-- Divider -->
          <div class="my-4">
            <hr class="border-t-2 border-gray-300" />
          </div>
          <!-- Description -->
          <div class="flex flex-col sm:flex-row justify-between">
            <div>
              <h2 class="mb-3 font-bold text-lg">Description</h2>
              <span v-html="viewTicket.description"></span>
            </div>
            <!-- Summary -->
            <div
              class="mt-4 sm:mt-0 sm:mr-40 flex flex-col sm:flex-row justify-end"
            >
              <!-- Vertical divider -->
              <p
                class="border-l-2 border-gray-300 mx-4 h-24 hidden sm:block"
              ></p>
              <div>
                <h3 class="text-lg font-bold">Priority</h3>
                <Badge
                  class="text-lg"
                  :variant="'outline'"
                  theme="blue"
                  size="sm"
                  :label="viewTicket.priority"
                />
                <h3 class="text-lg font-bold">Created Date</h3>
                <p class="text-sm">
                  {{ getFormattedDate(viewTicket.creation) }}
                </p>
              </div>
            </div>
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
import { useRoute } from 'vue-router'
import BreadCrums from '../components/BreadCrums.vue'
import { Badge, Button } from 'frappe-ui'
import { onMounted, ref, reactive } from 'vue'
import { ticketDetails } from '../data/ticketDetails'
import dayjs from 'dayjs'
import FoundNot from '../components/FoundNot.vue'
import PageLoader from '../components/PageLoader.vue'

const route = useRoute()
let viewTicket = ref(null)

let isLoading = ref(true)
const fetchTicket = async () => {
  isLoading.value = true
  await ticketDetails.fetch()
  viewTicket.value =
    ticketDetails.data.data.find((t) => t.name === Number(route.params.name)) ||
    null
 //  //console.log(viewTicket.value.name);
  isLoading.value = false
}

onMounted(() => {
  fetchTicket()
})

const status = ref(viewTicket.value ? viewTicket.value.status : '')

const getStatusColor = (status) => {
  switch (status) {
    case 'Open':
      return 'red'
    case 'Resolved':
      return 'blue'
    case 'Closed':
      return 'green'
    default:
      return 'gray'
  }
}

function getFormattedDate(date) {
  return dayjs(date).format('MMMM DD, YYYY')
}

const updateIssueData = ref({
  name: '',
  status: '',
  feedback: '',
})

const apiUrl = '/api/method/ecommerce.api.update_ticket'

const markAsResolved = async () => {
  if (viewTicket.value) {
    updateIssueData.value = {
      name: viewTicket.value.name,
      status: 'Resolved',
      feedback: 'Quick and precise solutions',
    }

    await updateTicket()
    await fetchTicket()
  }
}

const updateTicket = async () => {
 //  //console.log(updateIssueData.value);
  try {
    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updateIssueData.value),
    })
    const responseData = await response.json()

    if (response.ok) {
      status.value = 'Resolved'
     //  //console.log('Ticket updated successfully',responseData);
    } else {
      //console.error(`Error updating issue: ${responseData.message}`);
    }
  } catch (error) {
    //console.error('Error updating issue:', error);
  }
}
</script>
