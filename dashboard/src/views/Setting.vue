<template>
  <div class="p-2 mt-1 lg:bg-gray-200 h-[calc(100svh-5.5rem)] lg:h-[calc(100svh-5rem)] overflow-hidden">
    <div
      class="border-gray-200 rounded-lg bg-white h-full overflow-hidden grid grid-cols-1"
      :style="desktopSettingsGridStyle"
    >
      <div
        class="bg-white text-gray-900 flex flex-col border-r border-gray-200 min-h-0 rounded-lg"
        :class="isMobile && !showMenuMobile ? 'hidden' : 'flex'"
      >
        <div class="p-4 border-b border-gray-200 flex items-center justify-between">
          <div v-if="!isDesktopCollapsed">
            <p class="text-[11px] uppercase tracking-wide text-gray-800">
              Settings
            </p>
            <p class="font-semibold text-sm">Manage users and locations</p>
          </div>
          <button
            v-if="!isMobile"
            type="button"
            class="hidden md:inline-flex h-8 w-8 items-center justify-center rounded-lg text-gray-500 hover:bg-[#f7f7fb] hover:text-gray-800 transition-colors"
            @click="isSettingsSidebarOpen = !isSettingsSidebarOpen"
          >
            <PanelLeft class="h-4 w-4" />
          </button>
        </div>

        <div v-if="!isDesktopCollapsed" class="p-3">
          <div class="relative">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
              search
            </span>
            <input
              v-model="settingsSearch"
              type="text"
              placeholder="Search settings"
              class="w-full h-10 px-3 pl-10 text-sm text-gray-800 bg-gray-50 border border-gray-200 focus:outline-none focus:border-[#00a884] rounded-md"
            />
          </div>
        </div>

        <div v-if="!isDesktopCollapsed" class="px-4 pt-1">
          <p class="text-[13px] font-semibold text-black/70 ">
            Settings Menu
          </p>
        </div>

        <div
          class="flex-1 overflow-y-auto p-3 pt-2 space-y-1"
          :class="isDesktopCollapsed ? 'flex flex-col items-center' : ''"
        >
          <button
            v-for="tab in filteredSettingTabs"
            :key="tab.key"
            class="w-full text-left flex items-center gap-2 rounded-2xl px-3 py-2 transition-colors"
            :class="{
              'bg-[#e3eee6] text-[#2f9e62]': activeTab === tab.key,
              'hover:bg-[#f7f7fb] text-gray-800': activeTab !== tab.key,
              'justify-center !px-0': isDesktopCollapsed,
            }"
            @click="selectTab(tab.key)"
            :title="tab.label"
          >
            <SidebarIcon
              :name="tab.icon"
              size="sm"
              :class="activeTab === tab.key ? 'text-[#2f9e62]' : 'text-current'"
            />
            <span
              v-if="!isDesktopCollapsed"
              class="min-w-0 flex-1 truncate text-sm"
              :class="
                activeTab === tab.key
                  ? 'font-semibold text-[#2f9e62]'
                  : 'font-medium text-gray-800'
              "
            >
              {{ tab.label }}
            </span>
            <span
              v-if="!isDesktopCollapsed && tab.count !== ''"
              class="flex items-center justify-center text-[0.6rem] font-bold rounded px-2 py-1 min-w-8"
              :class="activeTab === tab.key ? 'bg-white text-[#09090b]' : 'bg-[#eee6e6] text-[#09090b]'"
            >
              {{ tab.count }}
            </span>
            <span
              v-if="!isDesktopCollapsed && activeTab === tab.key"
              class="material-symbols-outlined text-lg text-[#2f9e62]"
            >
              chevron_right
            </span>
            <span
              v-else-if="!isDesktopCollapsed"
              class="material-symbols-outlined text-lg text-gray-400"
            >
              chevron_right
            </span>
          </button>
        </div>
      </div>

      <div
        class="bg-white flex flex-col overflow-hidden min-h-0 h-full border border-gray-200 border-l-0"
        :class="isMobile && showMenuMobile ? 'hidden' : 'flex'"
      >
        <div class="h-14 px-4 flex items-center justify-between border-b border-gray-200 bg-gray-50 gap-3">
          <div class="space-y-0.5">
            <div class="text-sm text-gray-800 flex items-center gap-2">
              <button
                v-if="isMobile"
                class="md:hidden text-gray-600 hover:text-gray-800"
                @click="showMenuMobile = true"
              >
                <span class="material-symbols-outlined text-lg">arrow_back</span>
              </button>
              <span>{{ activeTabMeta.title }}</span>
            </div>
            <div class="text-sm text-gray-500">
              {{ activeTabMeta.subtitle }}
            </div>
          </div>

          <div class="shrink-0" v-if="activeTab === 'users' || activeTab === 'locations'">
            <Button
              v-if="activeTab === 'users'"
              variant="solid"
              @click="displayDialog.isDisplay = true"
            >
              + Add Team Member
            </Button>
            <Button
              v-else
              variant="solid"
              @click="displayAddress.isDisplay = true"
            >
              + Add Location
            </Button>
          </div>
        </div>

        <div class="flex-1 min-h-0 p-4 overflow-y-auto bg-gray-50">
          <div v-if="activeTab === 'users'" class="">
            <AppDataTable
              :columns="userTableColumns"
              :rows="userRows"
              row-key="email"
              empty-text="No records found"
              table-class="table-fixed min-w-[760px]"
              wrapper-class="rounded-lg border border-gray-200 shadow-none"
              :stack-on-mobile="false"
            >
              <template #cell-disable="{ row }">
                <span class="inline-flex items-center gap-2">
                  <Checkbox
                    v-if="!isCurrentUserRow(row)"
                    size="sm"
                    v-model="row.disable"
                    @change="() => toggleDisable(row)"
                  />
                  <span
                    v-else
                    class="text-xs text-gray-400"
                  >
                    --
                  </span>
                </span>
              </template>

              <template #cell-edit="{ row }">
                <button type="button" @click="openUserEdit(row)">
                  <FeatherIcon name="edit" class="h-3 w-3 text-black" />
                </button>
              </template>

              <template #mobile-row="{ row }">
                <div class="space-y-1 text-xs text-gray-700">
                  <p><span class="font-medium text-gray-500">Name:</span> {{ row.user_name }}</p>
                  <p><span class="font-medium text-gray-500">Email:</span> {{ row.email }}</p>
                  <p><span class="font-medium text-gray-500">Mobile Number:</span> {{ row.employee_phone || '-' }}</p>
                  <p class="flex items-center gap-2">
                    <span class="font-medium text-gray-500">Edit:</span>
                    <button type="button" @click="openUserEdit(row)">
                      <FeatherIcon name="edit" class="h-3 w-3 text-black" />
                    </button>
                  </p>
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-500">Disable:</span>
                    <Checkbox
                      v-if="!isCurrentUserRow(row)"
                      size="sm"
                      v-model="row.disable"
                      @change="() => toggleDisable(row)"
                    />
                    <span v-else class="text-xs text-gray-400">--</span>
                  </div>
                </div>
              </template>
            </AppDataTable>
          </div>

          <div v-else-if="activeTab === 'locations'" >
            <AppDataTable
              :columns="locationTableColumns"
              :rows="addressRows"
              row-key="name"
              empty-text="No records found"
              table-class="table-fixed min-w-[680px]"
              wrapper-class="rounded-lg border border-gray-200 shadow-none"
              :stack-on-mobile="false"
            >
              <template #cell-edit="{ row }">
                <button type="button" @click="openAddressEdit(row)">
                  <FeatherIcon name="edit" class="h-3 w-3 text-black" />
                </button>
              </template>

              <template #mobile-row="{ row }">
                <div class="space-y-1 text-xs text-gray-700">
                  <p><span class="font-medium text-gray-500">Address:</span> {{ row.address }}</p>
                  <p><span class="font-medium text-gray-500">Contact Person:</span> {{ row.contact_person || '-' }}</p>
                  <p><span class="font-medium text-gray-500">Mobile Number:</span> {{ row.phone || '-' }}</p>
                  <p class="flex items-center gap-2">
                    <span class="font-medium text-gray-500">Edit:</span>
                    <button type="button" @click="openAddressEdit(row)">
                      <FeatherIcon name="edit" class="h-3 w-3 text-black" />
                    </button>
                  </p>
                </div>
              </template>
            </AppDataTable>
          </div>
          <EditAccount v-else-if="activeTab === 'edit-profile'" embedded />
          <PasswordReset v-else-if="activeTab === 'reset-password'" embedded />
        </div>

        <DialogUser
          v-model="displayDialog.isDisplay"
          @userCreated="fetchnewuserinfo"
          :editData="selectedUser"
        />

        <DialogAddress
          v-model="displayAddress.isDisplay"
          @addressCreated="fetchaddressinfo"
          :editData="selectedAddress"
        />

        <Dialog
          v-model="showDisableDialog"
          :options="disableDialogOptions"
        >
          <template #body-content>
            <div class="p-2 text-sm text-gray-700">
              Are you sure you want to {{ pendingDisableAction }} this user?
            </div>
          </template>
        </Dialog>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Button, FeatherIcon, Checkbox, Dialog } from 'frappe-ui'
import { useToast } from 'vue-toastification'
import { displayAddress } from '../composables/displayAddress'
import { displayDialog } from '../composables/displayDialog'
import DialogUser from '../components/DialogUser.vue'
import DialogAddress from '../components/DialogAddress.vue'
import AppDataTable from '@/components/AppDataTable.vue'
import EditAccount from './EditAccount.vue'
import PasswordReset from './PasswordReset.vue'
import { ref, watch, onMounted, onBeforeUnmount, reactive, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import vendroaddressinfo from '/src/data/vendroaddressinfo.js'
import newuser from '/src/data/newuser.js'
import userInfo from '/src/data/userInfo.js'
import { PanelLeft } from 'lucide-vue-next'
import SidebarIcon from '@/components/SidebarIcon.vue'
import { useSidebar } from '@/components/ui/sidebar'
import {
  SIDEBAR_WIDTH,
  SIDEBAR_WIDTH_ICON,
} from '@/components/ui/sidebar/utils'

const toast = useToast()
const route = useRoute()
const router = useRouter()
const { setOpen } = useSidebar()
const SETTINGS_TAB_STORAGE_KEY = 'ecommerce.activeSettingsTab'
const userRows = ref([])

const addressRows = ref([])
const showDisableDialog = ref(false)
const pendingDisableRow = ref(null)
const pendingDisableState = ref(false)
const pendingDisableAction = ref('disable')
const currentUserEmail = computed(() => userInfo?.data?.message?.email || '')
const selectedUser = ref(null)
const selectedAddress = ref(null)
const activeTab = ref('users')
const settingsSearch = ref('')
const isMobile = ref(false)
const showMenuMobile = ref(true)
let handleResize = null
const isSettingsSidebarOpen = ref(true)
const isDesktopCollapsed = computed(
  () => !isMobile.value && !isSettingsSidebarOpen.value,
)
const desktopSettingsGridStyle = computed(() => {
  if (isMobile.value) {
    return {}
  }

  return {
    gridTemplateColumns: isDesktopCollapsed.value
      ? `${SIDEBAR_WIDTH_ICON} minmax(0, 1fr)`
      : `${SIDEBAR_WIDTH} minmax(0, 1fr)`,
  }
})

const fetchaddressinfo = async () => {
  try {
    await vendroaddressinfo.fetch()
   //  // console.log('vendroaddressinfo:',  vendroaddressinfo.data.data.vendor_address_info.address_info)
    if (
      vendroaddressinfo.data &&
      vendroaddressinfo.data.data.vendor_address_info &&
      vendroaddressinfo.data.data.vendor_address_info.address_info
    ) {
      addressRows.value =
        vendroaddressinfo.data.data.vendor_address_info.address_info.map(
          (t, index) => ({
            ...t,
            sn: index + 1,
          }),
        )

     //  //console.log('addressRows:', addressRows.value)
    } else {
      //   console.error('No data available in vendroaddressinfo')
    }
  } catch (error) {
    // console.error('Error fetching vendroaddressinfo:', error)
  }
}

const openUserEdit = (row) => {
  selectedUser.value = { ...row }
  displayDialog.isDisplay = true
}

const openAddressEdit = (row) => {
  selectedAddress.value = { ...row }
  displayAddress.isDisplay = true
}

const selectTab = (key) => {
  activeTab.value = key
  localStorage.setItem(SETTINGS_TAB_STORAGE_KEY, key)
  router.replace({
    name: 'setting',
    params: { settingsTab: key },
    query: route.query,
  })
  if (isMobile.value) {
    showMenuMobile.value = false
  }
}

const toggleDisable = async (row) => {
  if (
    Boolean(row.disable) &&
    currentUserEmail.value &&
    String(row.email || '').toLowerCase() === currentUserEmail.value.toLowerCase()
  ) {
    row.disable = false
    toast.error('You cannot disable your own user.')
    return
  }

  pendingDisableRow.value = row
  pendingDisableState.value = Boolean(row.disable)
  pendingDisableAction.value = pendingDisableState.value ? 'disable' : 'enable'
  showDisableDialog.value = true
}

const isCurrentUserRow = (row) => {
  return (
    currentUserEmail.value &&
    String(row?.email || '').toLowerCase() === currentUserEmail.value.toLowerCase()
  )
}

const confirmToggleDisable = async () => {
  const row = pendingDisableRow.value
  const nextDisableState = pendingDisableState.value

  if (!row) {
    showDisableDialog.value = false
    return
  }

  try {
    const response = await fetch(
      '/api/method/ecommerce.api.update_vendor_employee_status',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employee_email: row.email,
          disable: nextDisableState ? 1 : 0,
        }),
      },
    )

    const data = await response.json()
    // console.log('Server Response:', data) // Log the response

    if (!data.message || data.message.status !== 'success') {
      throw new Error(data.message?.message || 'Update failed')
    }

    await fetchnewuserinfo()
  } catch (err) {
    console.error('Error updating disable status:', err)
    toast.error(err.message || 'Failed to update user status')
    row.disable = !nextDisableState
  } finally {
    showDisableDialog.value = false
    pendingDisableRow.value = null
  }
}

const cancelToggleDisable = () => {
  if (pendingDisableRow.value) {
    pendingDisableRow.value.disable = !pendingDisableState.value
  }
  showDisableDialog.value = false
  pendingDisableRow.value = null
}

const fetchnewuserinfo = async () => {
  try {
    await newuser.fetch()
    if (
      newuser.data &&
      newuser.data.data.vendor_employee_info &&
      newuser.data.data.vendor_employee_info.employee_info
    ) {
      userRows.value = newuser.data.data.vendor_employee_info.employee_info.map(
        (t, index) => ({
          ...t,
          disable: Boolean(t.disable),
          sn: index + 1,
          action: 'Edit',
          editClicked: false,
        }),
      )

     //  // console.log('userRows:', userRows.value)
    } else {
      // console.error('No data available in newuser')
    }
  } catch (error) {
    //  console.error('Error fetching newuser:', error)
  }
}
onMounted(() => {
  handleResize = () => {
    isMobile.value = window.innerWidth < 768
    if (!isMobile.value) {
      showMenuMobile.value = true
    }
  }

  handleResize()
  window.addEventListener('resize', handleResize)
  fetchaddressinfo()
  fetchnewuserinfo()
})

onBeforeUnmount(() => {
  if (handleResize) {
    window.removeEventListener('resize', handleResize)
  }
  setOpen(true)
})

watch(
  [isMobile, isSettingsSidebarOpen],
  ([mobile, isOpen]) => {
    if (!mobile) {
      setOpen(!isOpen)
    }
  },
  { immediate: true },
)

const settingTabs = computed(() => [
  {
    key: 'users',
    label: 'Users',
    count: userRows.value.length,
    icon: 'users',
  },
  {
    key: 'locations',
    label: 'Locations',
    count: addressRows.value.length,
    icon: 'locations',
  },
  {
    key: 'edit-profile',
    label: 'Edit Profile',
    count: '',
    icon: 'edit-profile',
  },
  {
    key: 'reset-password',
    label: 'Reset Password',
    count: '',
    icon: 'reset-password',
  },
])

watch(
  () => route.params.settingsTab,
  (routeTab) => {
    const parameterTab = Array.isArray(routeTab) ? routeTab[0] : routeTab
    const storedTab = localStorage.getItem(SETTINGS_TAB_STORAGE_KEY)
    const requestedTab = parameterTab || storedTab
    const isValidTab = settingTabs.value.some(
      (tab) => tab.key === requestedTab,
    )

    activeTab.value = isValidTab ? requestedTab : 'users'
    localStorage.setItem(SETTINGS_TAB_STORAGE_KEY, activeTab.value)
  },
  { immediate: true },
)

const filteredSettingTabs = computed(() => {
  const term = settingsSearch.value.trim().toLowerCase()
  if (!term) return settingTabs.value

  return settingTabs.value.filter((tab) =>
    [tab.label, tab.description].some((value) =>
      value.toLowerCase().includes(term),
    ),
  )
})

const activeTabMeta = computed(() => {
  if (activeTab.value === 'locations') {
    return {
      title: 'Business Locations',
      subtitle: `${addressRows.value.length} location${addressRows.value.length === 1 ? '' : 's'}`,
    }
  }

  if (activeTab.value === 'edit-profile') {
    return {
      title: 'Edit Profile',
      subtitle: 'Update your business information',
    }
  }

  if (activeTab.value === 'reset-password') {
    return {
      title: 'Reset Password',
      subtitle: 'Update your account password',
    }
  }

  return {
    title: 'Team Member',
    subtitle: `${userRows.value.length} team member${userRows.value.length === 1 ? '' : 's'}`,
  }
})

watch(
  () => displayDialog.isDisplay,
  (isOpen) => {
    if (!isOpen) {
      selectedUser.value = null
    }
  },
)

watch(
  () => displayAddress.isDisplay,
  (isOpen) => {
    if (!isOpen) {
      selectedAddress.value = null
    }
  },
)

const locationTableColumns = [
  {
    key: 'sn',
    label: 'SN',
    headerClass: 'w-[10%]',
    cellClass: 'w-[10%] whitespace-nowrap',
  },
  {
    key: 'address',
    label: 'Address',
    headerClass: 'w-[40%]',
    cellClass: 'w-[40%]',
  },
  {
    key: 'contact_person',
    label: 'Contact Person',
    headerClass: 'w-[25%]',
    cellClass: 'w-[25%]',
  },
  {
    key: 'phone',
    label: 'Mobile Number',
    headerClass: 'w-[17%]',
    cellClass: 'w-[17%] whitespace-nowrap',
  },
  {
    key: 'edit',
    label: 'Edit',
    headerClass: 'w-[8%]',
    cellClass: 'w-[8%] whitespace-nowrap',
  },
]

const userTableColumns = [
  {
    key: 'sn',
    label: 'SN',
    headerClass: 'w-[8%]',
    cellClass: 'w-[8%] whitespace-nowrap',
  },
  {
    key: 'user_name',
    label: 'Name',
    headerClass: 'w-[24%]',
    cellClass: 'w-[24%]',
  },
  {
    key: 'email',
    label: 'Email',
    headerClass: 'w-[30%]',
    cellClass: 'w-[30%]',
  },
  {
    key: 'employee_phone',
    label: 'Mobile Number',
    headerClass: 'w-[20%]',
    cellClass: 'w-[20%] whitespace-nowrap',
  },
  {
    key: 'edit',
    label: 'Edit',
    headerClass: 'w-[9%]',
    cellClass: 'w-[9%] whitespace-nowrap',
  },
  {
    key: 'disable',
    label: 'Disable',
    headerClass: 'w-[9%]',
    cellClass: 'w-[9%] whitespace-nowrap',
  },
]

const disableDialogOptions = reactive({
  title: 'Confirm Status Change',
  size: 'md',
  actions: [
    {
      label: 'Cancel',
      variant: 'subtle',
      onClick: cancelToggleDisable,
    },
    {
      label: 'Confirm',
      variant: 'solid',
      onClick: confirmToggleDisable,
    },
  ],
})
</script>

<style scoped>
</style>
