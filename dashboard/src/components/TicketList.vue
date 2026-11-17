<template>
  <div class="grid grid-cols-1 gap-4 mb-4">
    <div class="flex items-center justify-between h-15 rounded bg-gray-50 px-2">
      <CreateNew
        supportTicketTitle="Support Ticket"
        addTicketLabel="+ Add Ticket"
      />
    </div>
  </div>
  <div class="overflow-x-hidden ">
    <ListView
      :options="options"
      :columns="columns"
      :rows="rows"
      class="text-sm font-regular"
    >
      <template #cell="{ item, row, column }">
        <!-- <router-link
          v-if="column.key !== 'action'"
          :to="{ name: 'TicketDetails', params: { name: row.name } }"
          class="block"
        >
          <div :class="getColumnBgColor(column.key)" class="p-2">
            <Badge
              v-if="column.key === 'status'"
              :variant="'subtle'"
              :theme="getStatusColor(row.status)"
              size="sm"
              :label="row.status"
            />
            <span v-else>
              {{ item }}
            </span>
          </div>
        </router-link> -->
        <div
          v-if="column.key !== 'action'"
          @click="goToTicket(row.name)"
          class="block cursor-pointer"
        >
          <div :class="getColumnBgColor(column.key)" class="p-2">
            <Badge
              v-if="column.key === 'status'"
              :variant="'subtle'"
              :theme="getStatusColor(row.status)"
              size="sm"
              :label="row.status"
            />
            <span v-else>
              {{ item }}
            </span>
          </div>
        </div>

        <div
          v-else
          :class="[
            getColumnBgColor(column.key),
            'flex items-center',
            { 'cursor-not-allowed opacity-50': row.status !== 'Open' },
          ]"
          class="p-2"
          @click="row.status === 'Open' ? handleEditClick(row) : null"
        >
          <FeatherIcon name="edit" class="w-4" /> {{ row.action }}
        </div>
      </template>
    </ListView>

    <DialogTicket
      v-model="displayDialog.isDisplay"
      @ticketCreated="handleTicketCreated"
    />
    <EditTicket
      v-model="showEditDialog"
      :selectedRow="selectedRow"
      @ticketCreated="handleTicketCreated"
    />
    <router-view />
  </div>
</template>

<script setup>
import CreateNew from '../components/CreateNew.vue'
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import { useRouter } from 'vue-router' // Import useRouter
import { ListView, Badge, FeatherIcon } from 'frappe-ui'
import { ticketDetails } from '../data/ticketDetails'
import { displayDialog } from '../composables/displayDialog'
import DialogTicket from './DialogTicket.vue'
import EditTicket from './EditTicket.vue'
import dayjs from 'dayjs'

const router = useRouter() // Use the router instance

//console.log(ticketDetails)

const rows = ref([])

const showEditDialog = ref(false)

function goToTicket(name) {
  window.open(`/helpdesk/my-tickets/${name}`, '_blank', 'noopener,noreferrer')
}

const selectedRow = reactive({
  name: null,
  subject: null,
  description: null,
})

const handleTicketCreated = async () => {
  await fetchTicketDetails()
}

const fetchTicketDetails = async () => {
  try {
    await ticketDetails.fetch()
   //  //console.log(ticketDetails.data)
    if (ticketDetails.data && ticketDetails.data.data) {
      let data = ticketDetails.data.data.map((t) => ({
        ...t,
        creation: dayjs(t.creation).format('YYYY-MM-DD HH:mm:ss'),
        action: 'Edit',
        editClicked: false,
      }))

      // Custom sorting function
      data.sort((a, b) => {
        const statusOrder = ['Open', 'Replied', 'Resolved', 'Closed']
        return statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status)
      })

      rows.value = data
    } else {
      // console.error('No data available in ticketDetails')
    }
  } catch (error) {
    // console.error('Error fetching ticket details:', error)
  }
}

onMounted(() => {
  fetchTicketDetails()
})

const columns = ref([
  { label: 'Subject', key: 'subject' },
  { label: 'Status', key: 'status' },
  { label: 'Create Date', key: 'creation' },
  { label: 'Priority', key: 'priority' },
  { label: 'Action', key: 'action' },
])

const options = ref({
  selectable: false,
  resizeColumn: false,
  showTooltip: true,
  emptyState: {
    title: 'No Tickets found',
    description: 'Create a new record to get started',
  },
})

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

const getColumnBgColor = (key) => {
  switch (key) {
    case 'subject':
      return ''
    case 'status':
      return ''
    case 'opening_date':
      return ''
    case 'priority':
      return ''
    case 'action':
      return ''
    default:
      return ''
  }
}

const getHeaderBgColor = (key) => {
  switch (key) {
    case 'subject':
      return 'bg-blue-300'
    case 'status':
      return 'bg-green-300'
    case 'opening_date':
      return 'bg-yellow-300'
    case 'priority':
      return 'bg-red-300'
    case 'action':
      return 'bg-gray-300'
    default:
      return ''
  }
}

const handleEditClick = (row) => {
  selectedRow.name = row.name
  selectedRow.subject = row.subject
  selectedRow.description = row.description
  showEditDialog.value = true
}
</script>
