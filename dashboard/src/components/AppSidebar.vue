<template>
  <Sidebar class="h-svh" collapsible="icon">
    <SidebarContent class="overflow-y-auto bg-white">
      <SidebarGroup>
        <div
          class=""
          :class="isCollapsed ? 'relative px-2  mt-1' : 'relative px-3 py-3'"
        >
          <div
            class="flex"
            :class="
              isCollapsed
                ? 'flex-col items-center gap-2'
                : 'items-center justify-between gap-3'
            "
          >
            <div :class="isCollapsed ? 'inline-flex' : 'contents'">
              <router-link
                to="/main"
                class="flex overflow-hidden"
                :class="
                  isCollapsed
                    ? 'h-10 w-12 items-center justify-center p-2'
                    : 'h-10 w-full items-center object-contain object-left'
                "
              >
                <div
                  v-if="!isCollapsed"
                  class="flex h-full w-full items-center justify-start p-1"
                >
                  <img
                    :src="sidebarLogoExpanded"
                    class="max-h-full w-full object-contain object-left"
                    alt="Pickndrop Logo"
                  />
                </div>
                <img
                  v-else
                  :src="sidebarLogoCollapsed"
                  class="h-10 w-12 object-contain"
                  alt="Pickndrop Logo"
                />
              </router-link>
            </div>

            <button
              v-if="isCollapsed"
              type="button"
              class="hidden h-9 w-9 items-center justify-center rounded-2xl text-gray-500 transition-colors hover:bg-[#f7f7fb] hover:text-gray-800 md:inline-flex"
              @click="toggleSidebar"
            >
              <PanelLeft class="h-5 w-5 text-current" />
            </button>

          </div>
        </div>

        <VendorProfile :collapsed="isCollapsed" />
        <SidebarGroupContent>
          <SidebarMenu
            class="px-3 pt-2 space-y-1"
            :class="isCollapsed ? 'overflow-visible' : ''"
          >
            <!-- Items up to and including Comments (excluding Account) -->
            <SidebarMenuItem
              v-for="item in itemsBeforeComments"
              :key="item.title"
            >
              <SidebarMenuButton
                asChild
                :class="isCollapsed ? 'min-h-0 overflow-visible p-0' : 'p-0'"
                :tooltip="item.title"
              >
                <RouterLink
                  :to="getRouteFor(item.title)"
                  @click="handleNavigationClick"
                  class="w-full rounded-xl transition-colors"
                  :class="[
                    isCollapsed
                      ? 'flex flex-col items-center justify-center gap-1 py-2'
                      : 'flex items-center gap-2 px-3 py-2',
                    isActiveItem(item.title)
                      ? 'bg-[#eaf5ef] text-[#111827]'
                      : 'hover:bg-[#f7f7fb]',
                  ]"
                >
                  <span
                    v-if="isCollapsed && getSidebarBadgeCount(item.title) > 0"
                    class="absolute -right-1 top-0 flex min-w-4 h-4 max-w-[2rem] items-center justify-center overflow-hidden rounded-full bg-[#111827] px-1 text-[9px] font-semibold leading-none text-white"
                  >
                    {{ getSidebarBadgeCount(item.title) }}
                  </span>
                  <SidebarIcon
                    :name="item.icon"
                    size="sm"
                    :class="
                      isActiveItem(item.title)
                        ? 'text-[#111827]'
                        : 'text-current'
                    "
                  />
                  <span
                    v-if="!isCollapsed"
                    class="min-w-0 flex-1 truncate text-sm"
                    :class="isActiveItem(item.title) ? 'font-semibold' : 'font-medium'"
                  >{{
                    item.title
                  }}</span>
                  <span
                    v-if="
                      !isCollapsed &&
                      item.title === 'Live Updates' &&
                      processingOrdersCount > 0
                    "
                    class="ml-auto flex items-center justify-center text-[0.6rem] font-bold rounded px-2 py-1 min-w-8"
                    :class="isActiveItem(item.title) ? 'bg-[#2f9e62] text-white' : 'bg-[#eee6e6] text-[#09090b]'"
                  >
                    {{ processingOrdersCount }}
                  </span>
                  <span
                    v-if="
                      !isCollapsed &&
                      item.title === 'My Orders' &&
                      openOrdersCount > 0
                    "
                    class="ml-auto flex items-center justify-center text-[0.6rem] font-bold rounded px-2 py-1 min-w-8"
                    :class="isActiveItem(item.title) ? 'bg-[#2f9e62] text-white' : 'bg-[#eee6e6] text-[#09090b]'"
                  >
                    {{ openOrdersCount }}
                  </span>
                  <span
                    v-if="
                      !isCollapsed &&
                      item.title === 'Comments' &&
                      unreadCommentsCount > 0
                    "
                    class="ml-auto flex items-center justify-center text-[0.6rem] font-bold rounded px-2 py-1 min-w-8"
                    :class="isActiveItem(item.title) ? 'bg-[#2f9e62] text-white' : 'bg-[#eee6e6] text-[#09090b]'"
                  >
                    {{ unreadCommentsCount }}
                  </span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>

            <!-- Collapsible: Account -->
            <SidebarMenuItem>
              <SidebarMenuButton
                as="button"
                @click="handleAccountClick"
                class="w-full text-left flex items-center gap-2 rounded-2xl px-3 py-2 transition-colors"
                :tooltip="'Account'"
                :class="[
                  isAccountSectionActive()
                    ? 'bg-[#eaf5ef] text-[#111827]'
                    : 'hover:bg-[#f7f7fb]',
                  isCollapsed ? 'min-h-0 justify-center' : '',
                ]"
              >
                <SidebarIcon
                  name="account"
                  size="sm"
                  :class="
                    isAccountSectionActive() ? 'text-[#111827]' : 'text-current'
                  "
                />
                <span
                  v-if="!isCollapsed"
                  class="min-w-0 flex-1 truncate text-sm"
                  :class="isAccountSectionActive() ? 'font-semibold' : 'font-medium'"
                >Account</span>
                <span
                  v-if="!isCollapsed"
                  class="material-symbols-outlined text-lg"
                  :class="isAccountSectionActive() ? 'text-[#111827]' : 'text-gray-400'"
                >
                  chevron_right
                </span>
              </SidebarMenuButton>

              <SidebarMenuSub
                v-if="(open.account || isAnyAccountSectionOpen()) && !isCollapsed"
              >
                <SidebarMenuSubItem>
                  <SidebarMenuSubButton asChild>
                    <RouterLink
                      to="/account/orderpayment"
                      @click="handleNavigationClick"
                      class="block w-full rounded-xl px-3 py-2 transition-colors"
                      :class="
                        isExactPathActive('/account/orderpayment')
                          ? 'bg-[#eaf5ef] text-[#111827] font-semibold'
                          : 'hover:bg-[#f7f7fb]'
                      "
                    >
                      <span>Order-wise Payment</span>
                    </RouterLink>
                  </SidebarMenuSubButton>
                </SidebarMenuSubItem>
                <SidebarMenuSubItem>
                  <SidebarMenuSubButton asChild>
                    <RouterLink
                      to="/account/cod"
                      @click="handleNavigationClick"
                      class="block w-full rounded-xl px-3 py-2 transition-colors"
                      :class="
                        isCodSectionActive()
                          ? 'bg-[#eaf5ef] text-[#111827] font-semibold'
                          : 'hover:bg-[#f7f7fb]'
                      "
                    >
                      <span>COD Transfer Amount</span>
                    </RouterLink>
                  </SidebarMenuSubButton>
                </SidebarMenuSubItem>
              </SidebarMenuSub>
            </SidebarMenuItem>

            <!-- Collapsible: Settings -->
            <SidebarMenuItem>
              <SidebarMenuButton
                asChild
                class="rounded-2xl p-0 transition-colors"
                :tooltip="'Settings'"
                :class="[
                  isSettingsSectionActive()
                    ? 'bg-[#eaf5ef] text-[#111827]'
                    : 'hover:bg-[#f7f7fb]',
                  isCollapsed ? 'min-h-0 py-2 justify-center' : '',
                ]"
              >
                <RouterLink
                  to="/setting"
                  @click="handleNavigationClick"
                  class="w-full text-left flex items-center gap-2 rounded-2xl px-3 py-2"
                  :class="isCollapsed ? 'justify-center' : ''"
                >
                  <SidebarIcon
                    name="settings"
                    size="sm"
                    :class="
                      isSettingsSectionActive()
                        ? 'text-[#111827]'
                        : 'text-current'
                    "
                  />
                  <span
                    v-if="!isCollapsed"
                    class="min-w-0 flex-1 truncate text-sm"
                    :class="isSettingsSectionActive() ? 'font-semibold' : 'font-medium'"
                  >Settings</span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>

            <!-- Items after Comments (excluding Account and Settings) -->
            <SidebarMenuItem
              v-for="item in itemsAfterComments"
              :key="item.title"
            >
              <SidebarMenuButton
                asChild
                :class="isCollapsed ? 'min-h-0 p-0' : 'p-0'"
                :tooltip="item.title"
              >
                <RouterLink
                  :to="getRouteFor(item.title)"
                  @click="handleNavigationClick"
                  class="w-full text-left flex items-center gap-2 rounded-2xl px-3 py-2 transition-colors"
                  :class="[
                    isActiveItem(item.title)
                      ? 'bg-[#eaf5ef] text-[#111827]'
                      : 'hover:bg-[#f7f7fb]',
                    isCollapsed ? 'justify-center' : '',
                  ]"
                >
                  <SidebarIcon
                    :name="item.icon"
                    size="sm"
                    :class="
                      isActiveItem(item.title)
                        ? 'text-[#111827]'
                        : 'text-current'
                    "
                  />
                  <span
                    v-if="!isCollapsed"
                    class="min-w-0 flex-1 truncate text-sm"
                    :class="isActiveItem(item.title) ? 'font-semibold' : 'font-medium'"
                  >{{ item.title }}</span>
                  <SidebarMenuBadge
                    v-if="!isCollapsed && item.title === 'Apps'"
                    class="bg-[#E4F5E9] text-[#278F5E] p-2 font-bold rounded-xl"
                    >NEW</SidebarMenuBadge
                  >
                  <span
                    v-if="!isCollapsed"
                    class="material-symbols-outlined text-lg"
                    :class="isActiveItem(item.title) ? 'text-[#111827]' : 'text-gray-400'"
                    v-show="item.title !== 'Refer Offer' && item.title !== 'Branch Details / Charges'"
                  >
                    chevron_right
                  </span>
                </RouterLink>
              </SidebarMenuButton>
            </SidebarMenuItem>

          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter
      class="relative overflow-visible border-t border-gray-200 bg-white px-3"
    >
      <div
        ref="profileActionsContainer"
        class="flex items-center rounded-2xl px-3 py-2 transition-colors hover:bg-[#f7f7fb]"
        :class="isCollapsed ? 'justify-center' : 'gap-3'"
      >
        <div
          role="button"
          tabindex="0"
          class="flex min-w-0 items-center"
          :class="isCollapsed ? 'justify-center' : 'flex-1 gap-3'"
          @click="toggleSidebar"
        >
          <div class="relative h-11 w-11 shrink-0">
            <div
              class="absolute inset-0 overflow-hidden rounded-full bg-gray-100"
            >
              <img
                v-if="userImage"
                :src="userImage"
                alt="User profile"
                class="h-full w-full object-cover"
              />
              <div
                v-else
                class="flex h-full w-full items-center justify-center text-sm font-semibold text-gray-700"
              >
                {{ userInitials }}
              </div>
            </div>
          </div>

          <div v-if="!isCollapsed" class="min-w-0 flex-1">
            <div class="flex items-center gap-2">
              <p class="min-w-0 truncate text-sm font-semibold text-gray-800">
                {{ userName }}
              </p>

            </div>
            <div class="mt-0.5 space-y-1">

               <span
                v-if="userRole"
                class="shrink-0 rounded-full bg-gray-100 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide text-gray-600"
              >
                {{ userRole }}
              </span>
            </div>
          </div>
        </div>
        <div v-if="!isCollapsed" class="relative shrink-0">
          <button
            type="button"
            class="inline-flex shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium text-gray-800 transition-colors hover:bg-white"
            @click.stop="showProfileActions = !showProfileActions"
          >
            <LogOut class="h-4 w-4 shrink-0" :stroke-width="1.75" />
          </button>

          <div
            v-if="showProfileActions"
            class="absolute bottom-full right-0 z-20 mb-2 w-40 rounded-xl border border-gray-200 bg-white p-1 shadow-lg"
          >
            <button
              type="button"
              class="flex w-full rounded-lg px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50"
              @click="openResetPassword"
            >
              Reset Password
            </button>
            <button
              type="button"
              class="flex w-full rounded-lg px-3 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50"
              @click="openLogoutConfirm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
      <button
        v-if="isCollapsed"
        type="button"
        class="flex w-full items-center justify-center rounded-2xl px-3 py-2 text-left transition-colors hover:bg-[#f7f7fb]"
        @click.stop="showProfileActions = !showProfileActions"
      >
        <LogOut class="h-4 w-4 shrink-0" :stroke-width="1.75" />
      </button>
      <div
        v-if="isCollapsed && showProfileActions"
        class="absolute bottom-2 left-[calc(100%+0.5rem)] z-50 w-56 rounded-xl border border-gray-200 bg-white p-2 shadow-lg"
        @pointerdown.stop
      >
        <button
          type="button"
          class="flex w-full whitespace-nowrap rounded-lg px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-50"
          @click="openResetPassword"
        >
          Reset Password
        </button>
        <button
          type="button"
          class="flex w-full whitespace-nowrap rounded-lg px-3 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50"
          @click="openLogoutConfirm"
        >
          Logout
        </button>
      </div>
    </SidebarFooter>

  </Sidebar>

  <Dialog v-model="showLogoutConfirm" :options="{ title: 'Confirm Logout' }">
    <template #body-content>
      <p class="text-sm text-gray-600">Are you sure you want to logout?</p>
    </template>
    <template #actions>
      <button
        type="button"
        class="rounded-lg px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100"
        @click="showLogoutConfirm = false"
      >
        Cancel
      </button>
      <button
        type="button"
        class="rounded-lg bg-red-600 px-3 py-2 text-sm text-white transition-colors hover:bg-red-700"
        @click="confirmLogout"
      >
        Logout
      </button>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { RouteLocationRaw } from 'vue-router'
import { useRoute, useRouter } from 'vue-router'
import editaccount from '../data/editaccount'
import {
  PanelLeft,
  LogOut,
} from 'lucide-vue-next'
import { Dialog } from 'frappe-ui'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
  SidebarMenuBadge,
  useSidebar,
} from '../components/ui/sidebar'

import VendorProfile from './VendorProfile.vue'
import SidebarIcon from './SidebarIcon.vue'
import ordercount from '@/data/ordercount'
import comments from '@/data/comments'
import userInfo from '@/data/userInfo'
import { session } from '@/data/session'
import sidebarLogoCollapsed from '@/assets/PickDrop_Logo_Full_Light.png'
import sidebarLogoExpanded from '@/assets/PickDrop_Logo_Full_Dark.png'

const profileData = ref(null)
const showProfileActions = ref(false)
const showLogoutConfirm = ref(false)
const profileActionsContainer = ref<HTMLElement | null>(null)

onMounted(async () => {
  const res = await editaccount.fetch()
 //  //console.log('Profile Data:', res?.data[0])
  profileData.value = res?.data[0] || null
})

const profileCompletion = computed(() => {
  const profile = profileData.value
  if (!profile) return 0

  const fields = [
    profile.vendor_name,
    profile.pan_number,
    profile.primary_email,
    profile.contact_person,
    profile.primary_phone,
    profile.secondary_phone,
    profile.secondary_email,
    profile.vendor_address,
    profile.website,
    profile.facebook,
    profile.instagram,
    profile.logo,
    profile.pan,
    profile.citizenship,
  ]

  const totalFields = fields.length
  const filledFields = fields.filter(
    (f) => f !== null && f !== undefined && String(f).trim() !== '',
  ).length

  return Math.round((filledFields / totalFields) * 100)
})

// check if production
const isMySite =
  window.location.hostname === 'pickndropnepal.com' ||
  window.location.hostname === 'app-t.pickndropnepal.com'
//|| window.location.hostname === 'app-t.pickndropnepal.com'
// add your production hostnames here
const isProduction = isMySite

// close sidebar on mobile
const { isMobile, setOpenMobile, toggleSidebar, state } = useSidebar()
const route = useRoute()
const router = useRouter()

function handleProfileActionsPointerDown(event: PointerEvent) {
  const container = profileActionsContainer.value
  const target = event.target

  if (
    showProfileActions.value &&
    container &&
    target instanceof Node &&
    !container.contains(target)
  ) {
    showProfileActions.value = false
  }
}
const isCollapsed = computed(
  () => state.value === 'collapsed' && !isMobile.value,
)
const handleNavigationClick = () => {
  if (isMobile.value) setOpenMobile(false)
}

function handleAccountClick() {
  open.value.account = true

  if (route.path !== '/account/orderpayment') {
    router.push('/account/orderpayment')
  }

  handleNavigationClick()
}

function handleSettingsClick() {
  open.value.settings = true

  if (route.path !== '/setting') {
    router.push('/setting')
  }

  handleNavigationClick()
}

// menu items
const items = [
  { title: 'Dashboard', icon: 'dashboard' },
  { title: 'Live Updates', icon: 'live-updates' },
  { title: 'My Orders', icon: 'my-orders' },
  { title: 'Ticket', icon: 'ticket' },
  { title: 'Inbox', icon: 'inbox' },
  { title: 'Comments', icon: 'comments' },
  { title: 'Account', icon: 'account' },
  { title: 'Settings', icon: 'settings' },
  { title: 'Apps', icon: 'integration' },
  { title: 'Branch Details / Charges', icon: 'branch-details' },
  { title: 'Refer Offer', icon: 'refer-offer' },
]

const open = ref({
  account: false,
  settings: false,
})

const commentsIndex = computed(() =>
  items.findIndex((i) => i.title === 'Comments'),
)

const extractOrderCount = (
  key: 'processing_orders' | 'open_and_initiated' | 'open_orders',
) => {
  // frappe-ui resources place the server payload in `data`
  // which in our API shape is { status, message, data: { ...counts } }
  const payload = (ordercount as any)?.data
  const data = payload?.data ?? payload?.message?.data ?? {}
  return Number(data?.[key]) || 0
}

const processingOrdersCount = computed(() =>
  extractOrderCount('processing_orders'),
)
const openOrdersCount = computed(() =>
  extractOrderCount('open_orders'),
)
const unreadCommentsCount = computed(() => {
  const payload = (comments as any)?.data
  const commentGroups =
    payload?.data?.comments || payload?.message?.comments || []

  return commentGroups.reduce((total: number, group: any) => {
    const details = Array.isArray(group?.details) ? group.details : []
    return (
      total +
      details.filter(
        (detail: any) => (Number(detail?.unseen_comment_count) || 0) > 0,
      ).length
    )
  }, 0)
})

function getSidebarBadgeCount(title: string): number {
  if (title === 'Live Updates') return processingOrdersCount.value
  if (title === 'My Orders') return openOrdersCount.value
  if (title === 'Comments') return unreadCommentsCount.value
  return 0
}

onMounted(async () => {
  const refreshCounts = async () => {
    try {
      const tasks = []
      if (typeof ordercount.fetch === 'function') {
        tasks.push(ordercount.fetch())
      }
      if (typeof comments.fetch === 'function') {
        tasks.push(comments.fetch())
      }
      await Promise.all(tasks)
    } catch (error) {
      console.error('Failed to fetch sidebar counts:', error)
    }
  }

  await refreshCounts()

  // lightweight polling to keep counts fresh without full page reload
  const intervalId = window.setInterval(refreshCounts, 15000)
  const handleVisibility = () => {
    if (!document.hidden) refreshCounts()
  }
  document.addEventListener('visibilitychange', handleVisibility)
  document.addEventListener('pointerdown', handleProfileActionsPointerDown)

  onUnmounted(() => {
    window.clearInterval(intervalId)
    document.removeEventListener('visibilitychange', handleVisibility)
    document.removeEventListener('pointerdown', handleProfileActionsPointerDown)
  })
})

// const itemsBeforeComments = computed(() => {
//   const idx = commentsIndex.value
//   return idx >= 0 ? items.slice(0, idx + 1) : items
// })

const itemsBeforeComments = computed(() => {
  const idx = commentsIndex.value
  const arr = idx >= 0 ? items.slice(0, idx + 1) : items
  // hide Account always, hide Dashboard only in production
  return arr.filter((i) =>
    isProduction ? !['Account'].includes(i.title) : i.title !== 'Account',
  )
})

const itemsAfterComments = computed(() => {
  const idx = commentsIndex.value
  const arr = idx >= 0 ? items.slice(idx + 1) : []
  return arr.filter((i) => !['Account', 'Settings'].includes(i.title))
})

const userPayload = computed(() => {
  return (userInfo as any)?.data?.message || (userInfo as any)?.data || {}
})

const userName = computed(() => {
  const fullName =
    userPayload.value?.full_name ||
    userPayload.value?.fullName ||
    userPayload.value?.name
  return fullName || 'User'
})

const userImage = computed(() => {
  return userPayload.value?.user_image || userPayload.value?.image || ''
})

const userRole = computed(() => {
  return userPayload.value?.role || ''
})

const userInitials = computed(() => {
  const fullName = userName.value.trim()
  if (!fullName) return 'U'
  return fullName
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('')
})

function logout() {
  return session.logout.submit()
}

function openResetPassword() {
  showProfileActions.value = false
  router.push('/passwordreset')
}

function openLogoutConfirm() {
  showProfileActions.value = false
  if (isMobile.value) setOpenMobile(false)
  showLogoutConfirm.value = true
}

async function confirmLogout() {
  showLogoutConfirm.value = false
  try {
    await logout()
  } finally {
    window.location.replace(
      `${window.location.origin}/login?redirect-to=/dashboard`,
    )
  }
}

const routeMap: Record<string, RouteLocationRaw> = {
  Dashboard: { name: 'dashboard' },
  'Live Updates': { name: 'main' },
  'My Orders': { name: 'order' },
  Ticket: '/tickets',
  Inbox: '/inbox',
  Comments: '/comment',
  Settings: '/setting',
  'Refer Offer': '/refer',
  Apps: '/apiintegration',
  'Branch Details / Charges': '/branch',
}

function getRouteFor(title: string): RouteLocationRaw {
  return routeMap[title] ?? '#'
}

function isActiveItem(title: string): boolean {
  if (title === 'Apps') {
    return route.name === 'apiintegration'
  }

  const routeTarget = routeMap[title]
  if (!routeTarget) return false

  if (typeof routeTarget === 'string') {
    return route.path === routeTarget
  }

  if ('name' in routeTarget && routeTarget.name) {
    return route.name === routeTarget.name
  }

  if ('path' in routeTarget && routeTarget.path) {
    return route.path === routeTarget.path
  }

  return false
}

function isExactPathActive(path: string): boolean {
  return route.path === path
}

function isCodSectionActive(): boolean {
  return route.path === '/account/cod' || route.path.startsWith('/account/cod/')
}

function isAccountSectionActive(): boolean {
  return route.path === '/account'
}

function isAnyAccountSectionOpen(): boolean {
  return (
    route.path === '/account' ||
    route.path === '/account/orderpayment' ||
    isCodSectionActive()
  )
}

function isSettingsSectionActive(): boolean {
  return (
    route.path === '/setting' ||
    route.path.startsWith('/setting/') ||
    route.path === '/editprofile' ||
    route.path === '/passwordreset'
  )
}

</script>

<style scoped>
.count-pill {
  background: #dcdcdc;
  color: #09090b;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 8px;
  min-width: 2.6rem;
  height: 1.8rem;
  padding: 0 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
</style>
