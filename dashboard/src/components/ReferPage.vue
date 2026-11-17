<template>
  <section class="h-full overflow-y-auto space-y-4 pr-1">
    <div class="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <img
        :src="referImage"
        alt="Refer and earn"
        class="h-auto w-full object-cover"
      />
    </div>

    <div class="grid gap-4 lg:grid-cols-2">
      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <h2 class="text-base font-semibold text-gray-800">Share your link</h2>
        <p class="mt-2 max-w-md text-sm leading-6 text-gray-600">
          Invite your business partners to join Pick & Drop and earn rewards together.
        </p>

        <div class="mt-4 space-y-4">
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-600">
              Referral Link
            </label>
            <div class="referral-input-shell flex overflow-hidden rounded-md bg-white">
              <input
                class="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-sm text-gray-800 outline-none"
                :value="referralLink"
                readonly
              />
              <button
                type="button"
                @click="copyLink"
                class="inline-flex items-center gap-2 rounded-none bg-green-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-emerald-600"
              >
                <Copy :size="16" />
                Copy
              </button>
            </div>
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-gray-600">
              Referral Code
            </label>
            <div class="referral-input-shell flex overflow-hidden rounded-md bg-white">
              <input
                class="min-w-0 flex-1 bg-transparent px-3 py-2.5 text-sm font-semibold tracking-[0.12em] text-emerald-700 outline-none"
                style="color: #047857;"
                :value="referralCode"
                readonly
              />
              <button
                type="button"
                @click="copyCode"
                class="inline-flex items-center gap-2 rounded-none bg-green-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-emerald-600"
              >
                <Copy :size="16" />
                Copy
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-gray-200 bg-white p-4">
        <h2 class="text-center text-base font-semibold text-gray-800">Spread the word</h2>

        <div class="mx-auto mt-4 grid max-w-[250px] grid-cols-5 justify-items-center gap-x-0 gap-y-2 text-center">
          <a
            v-for="item in shareItems"
            :key="item.label"
            :href="item.href"
            target="_blank"
            rel="noopener noreferrer"
            class="group flex w-full max-w-[60px] flex-col items-center justify-center gap-1 text-center text-sm text-gray-700"
          >
            <span
              class="inline-flex h-9 w-9 items-center justify-center rounded-full text-white shadow-sm transition group-hover:-translate-y-0.5"
              :style="{ backgroundColor: item.color, color: '#ffffff' }"
            >
              <component :is="item.icon" :size="16" v-if="item.icon" />
              <svg
                v-else-if="item.iconName === 'twitter'"
                viewBox="0 0 24 24"
                class="h-4 w-4"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817-5.967 6.817H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231 5.45-6.231Zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77Z" />
              </svg>
              <svg
                v-else-if="item.iconName === 'telegram'"
                viewBox="0 0 24 24"
                class="h-4 w-4"
                fill="currentColor"
                aria-hidden="true"
              >
                <path d="M21.94 4.16a1.5 1.5 0 0 0-1.96-1.43L2.9 9.45c-1.21.47-1.2 2.18.02 2.62l4.28 1.54 1.67 5.2c.36 1.13 1.8 1.45 2.6.58l2.43-2.65 4.35 3.18c1.01.74 2.45.18 2.68-1.05l3.01-14.71ZM8.1 12.44l9.52-5.86-7.3 7.6-.3 3.23-1.07-3.35a1.5 1.5 0 0 0-.85-.92l-.01-.7Zm2.74 4.13.13-1.4 1.38.99-1.51.41Z" />
              </svg>
            </span>
            <span class="w-full text-center text-[11px] leading-tight">{{ item.label }}</span>
          </a>
        </div>

        <div class="mt-5 border-t border-gray-200 pt-4">
          <div class="flex items-center justify-between gap-4">
            <p class="text-sm font-medium text-gray-600">Total Referrals Shared</p>
            <p class="text-base font-semibold text-emerald-600">
              {{ formattedTotalReferrals }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <div class="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <div class="flex flex-col gap-2 border-b border-gray-200 px-6 py-2.5 sm:flex-row sm:items-center sm:justify-between">
        <h2 class="text-base font-semibold text-gray-800">Referral History</h2>
        <div class="flex gap-3">
          <button
            type="button"
            @click="exportCsv"
            class="inline-flex items-center justify-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50"
          >
            <Download :size="16" />
            Export CSV
          </button>
          <!-- <button
            type="button"
            @click="reloadReferral"
            class="rounded-md bg-green-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-green-600"
          >
            View All
          </button> -->
        </div>
      </div>

      <AppDataTable
        :columns="referralTableColumns"
        :rows="paginatedReferralRows"
        row-key="id"
        empty-text="No referrals found."
        table-class="table-fixed text-left"
        wrapper-class="rounded-none border-0 shadow-none"
      >
        <template #cell-name="{ row }">
          <span class="text-sm font-semibold text-gray-800">{{ row.name }}</span>
        </template>

        <template #cell-joinDate="{ row }">
          <span class="whitespace-nowrap text-sm text-gray-800">{{ row.joinDate }}</span>
        </template>

        <template #cell-progress="{ row }">
          <div>
            <div class="mb-3 flex items-center justify-between gap-3 text-xs font-semibold text-gray-700">
              <span>{{ row.progressLabel }}</span>
            </div>
            <div
              class="relative h-3.5 w-full max-w-[320px] overflow-hidden rounded-full"
              style="background-color: #e2e8f0; box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.08);"
            >
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="row.progressBarStyle"
              />
            </div>
          </div>
        </template>

        <template #cell-status="{ row }">
          <span
            class="inline-flex rounded-full px-3 py-1 text-xs font-bold"
            :class="row.statusClass"
          >
            {{ row.status }}
          </span>
        </template>

        <template #cell-rewardStatus="{ row }">
          <span
            class="inline-flex items-center gap-2 text-sm font-semibold"
            :class="row.rewardClass"
          >
            <CheckCircle v-if="row.rewardSent" :size="16" />
            {{ row.rewardStatus }}
          </span>
        </template>

        <template #mobile-row="{ row }">
          <div class="space-y-2 text-sm text-gray-700">
            <p><span class="font-medium text-gray-500">Name:</span> {{ row.name }}</p>
            <p><span class="font-medium text-gray-500">Join Date:</span> {{ row.joinDate }}</p>
            <div>
              <p class="mb-2 text-xs font-medium uppercase tracking-wide text-gray-400">Order Progress</p>
              <p class="mb-2 text-sm font-semibold text-gray-700">{{ row.progressLabel }}</p>
              <div
                class="relative h-3.5 w-full overflow-hidden rounded-full"
                style="background-color: #e2e8f0; box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.08);"
              >
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :style="row.progressBarStyle"
                />
              </div>
            </div>
            <p>
              <span class="font-medium text-gray-500">Registration Status:</span>
              <span
                class="ml-2 inline-flex rounded-full px-3 py-1 text-xs font-bold"
                :class="row.statusClass"
              >
                {{ row.status }}
              </span>
            </p>
            <p>
              <span class="font-medium text-gray-500">Reward Status:</span>
              <span class="ml-2 inline-flex items-center gap-2 text-sm font-semibold" :class="row.rewardClass">
                <CheckCircle v-if="row.rewardSent" :size="16" />
                {{ row.rewardStatus }}
              </span>
            </p>
          </div>
        </template>
      </AppDataTable>

      <div class="flex flex-col gap-4 border-t border-gray-200 bg-gray-50 px-6 py-1 text-sm text-gray-600 sm:flex-row sm:items-center sm:justify-between">
        <p>Showing {{ showingFrom }}-{{ showingTo }} of {{ totalReferrals }} referrals</p>
        <div v-if="pageCount > 1" class="flex items-center gap-3">
          <button
            class="rounded-md p-2 text-gray-700 hover:bg-white disabled:cursor-not-allowed disabled:opacity-40"
            type="button"
            :disabled="activePage === 1"
            @click="goToPage(activePage - 1)"
          >
            <ChevronLeft :size="20" />
          </button>
          <button
            v-for="page in visiblePages"
            :key="page"
            type="button"
            class="rounded-md px-4 py-2 font-medium"
            :class="page === activePage ? 'text-white' : 'text-gray-700 hover:bg-white'"
            :style="page === activePage ? { backgroundColor: '#22c55e' } : null"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
          <button
            class="rounded-md p-2 text-gray-700 hover:bg-white disabled:cursor-not-allowed disabled:opacity-40"
            type="button"
            :disabled="activePage === pageCount"
            @click="goToPage(activePage + 1)"
          >
            <ChevronRight :size="20" />
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import AppDataTable from './AppDataTable.vue'
import vendorProfile from '../data/vendorProfile'
import referral from '../data/referral'
import { useToast } from 'vue-toastification'
import {
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Copy,
  Download,
  Facebook,
  MessageCircle,
  MessageSquareText,
} from 'lucide-vue-next'

const toast = useToast()
const referImage = 'https://pickndropnepal.com/files/refer%20and%20earn.png'
const currentPage = ref(1)
const pageSize = 10

const referralData = computed(() => {
  return referral.data?.referrals || referral.data?.message?.referrals || []
})

const totalReferrals = computed(() => {
  return referralData.value.length
})

const formattedTotalReferrals = computed(() => {
  return Number(totalReferrals.value || 0).toLocaleString()
})

const referralCode = computed(() => {
  const apiCode = referral.data?.referral_code || referral.data?.message?.referral_code
  if (apiCode) return apiCode

  const name = vendorProfile?.data?.vendor_info?.name || ''
  const parts = name.split('-')

  if (parts.length > 1 && parts[1]) {
    return parts[1].trim()
  }

  return ''
})

const referralLink = computed(() => {
  return `https://pickndropnepal.com/dashboard/register?utm_campaign=referral&utm_source=${encodeURIComponent(
    referralCode.value,
  )}`
})

const message = computed(() => {
  return `Join me on Pick & Drop! Use code ${referralCode.value}: ${referralLink.value}`
})

const whatsappLink = computed(() => `https://wa.me/?text=${encodeURIComponent(message.value)}`)
const viberLink = computed(() => `viber://forward?text=${encodeURIComponent(message.value)}`)
const facebookLink = computed(() => {
  return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(referralLink.value)}`
})
const xLink = computed(() => `https://twitter.com/intent/tweet?text=${encodeURIComponent(message.value)}`)
const telegramLink = computed(() => `https://t.me/share/url?url=${encodeURIComponent(referralLink.value)}&text=${encodeURIComponent(message.value)}`)

const shareItems = computed(() => [
  { label: 'WhatsApp', href: whatsappLink.value, icon: MessageCircle, color: '#22c55e' },
  { label: 'Viber', href: viberLink.value, icon: MessageSquareText, color: '#6d3fe0' },
  { label: 'Facebook', href: facebookLink.value, icon: Facebook, color: '#087de0' },
  { label: 'Twitter', href: xLink.value, iconName: 'twitter', color: '#1d9bf0' },
  { label: 'Telegram', href: telegramLink.value, iconName: 'telegram', color: '#229ed9' },
])

const referralRows = computed(() => {
  return referralData.value.map((item, index) => {
    const name = item.store_name || item.vendor_name || item.name || 'Referral'
    const orders = Number(
      item.delivered_orders ||
      item.completed_orders ||
      item.orders_delivered ||
      item.order_count ||
      item.delivered_count ||
      0,
    )
    const target = Number(item.target_orders || item.milestone_orders || 50) || 50
    const status = normalizeStatus(item.registration_status || item.status || 'In Progress')
    const referralPercentage = Number(item.referral_percentage || 0)
    const rewardStatus =
      item.reward_status || rewardLabel(status, orders, target, referralPercentage)
    const progressPercent = Math.min(Math.round((orders / target) * 100), 100)

    return {
      id: item.name || item.email || `${name}-${index}`,
      name,
      joinDate: formatDate(item.creation || item.join_date || item.created_at),
      progressLabel: `${orders}/${target} Orders`,
      progressPercent,
      progressBarStyle: {
        width: `${Math.max(progressPercent, orders > 0 ? 6 : 0)}%`,
        backgroundColor: status === 'Idle' ? '#dc2626' : '#22c55e',
      },
      status,
      statusClass: statusClass(status),
      rewardStatus,
      rewardClass: rewardClass(rewardStatus),
      rewardSent: /sent|reward/i.test(rewardStatus),
    }
  })
})

const pageCount = computed(() => {
  return Math.ceil(referralRows.value.length / pageSize)
})

const activePage = computed(() => {
  if (!pageCount.value) return 1
  return Math.min(currentPage.value, pageCount.value)
})

const paginatedReferralRows = computed(() => {
  const start = (activePage.value - 1) * pageSize
  return referralRows.value.slice(start, start + pageSize)
})

const showingFrom = computed(() => {
  if (!referralRows.value.length) return 0
  return (activePage.value - 1) * pageSize + 1
})

const showingTo = computed(() => {
  return Math.min(activePage.value * pageSize, referralRows.value.length)
})

const visiblePages = computed(() => {
  return Array.from({ length: pageCount.value }, (_, index) => index + 1)
})

const referralTableColumns = [
  {
    key: 'name',
    label: 'Name',
    headerClass: 'w-[26%]',
    cellClass: 'w-[26%] py-6',
  },
  {
    key: 'joinDate',
    label: 'Join Date',
    headerClass: 'w-[18%]',
    cellClass: 'w-[18%] py-6',
  },
  {
    key: 'progress',
    label: 'Order Progress',
    headerClass: 'w-[24%]',
    cellClass: 'w-[24%] py-6',
  },
  {
    key: 'status',
    label: 'Registration Status',
    headerClass: 'w-[20%]',
    cellClass: 'w-[20%] py-6 whitespace-nowrap',
  },
  {
    key: 'rewardStatus',
    label: 'Reward Status',
    headerClass: 'w-[30%]',
    cellClass: 'w-[30%] py-6 whitespace-nowrap',
  },
]

const goToPage = (page) => {
  currentPage.value = Math.min(Math.max(page, 1), pageCount.value || 1)
}

const normalizeStatus = (status) => {
  const value = String(status || '').trim().toLowerCase()
  if (['success', 'completed', 'approved', 'registered'].includes(value)) return 'Registered'
  if (['rejected', 'idle', 'expired'].includes(value)) return 'Idle'
  return 'Pending'
}

const statusClass = (status) => {
  if (status === 'Registered') return 'bg-green-700 text-white'
  if (status === 'Idle') return 'bg-red-100 text-red-700'
  return 'bg-emerald-100 text-emerald-800'
}

const rewardLabel = (status, orders, target, referralPercentage = 0) => {
  if (status === 'Registered' || orders >= target) {
    return `${referralPercentage}% Reward Sent`
  }
  if (status === 'Idle') return 'Expiring Soon'
  return orders > 0 ? 'Pending Milestone' : 'Not Eligible'
}

const rewardClass = (rewardStatus) => {
  if (/sent|reward/i.test(rewardStatus)) return 'text-emerald-500'
  if (/expir|idle/i.test(rewardStatus)) return 'text-red-700'
  return 'text-gray-700'
}

const formatDate = (value) => {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'

  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

const copyToClipboard = async (text) => {
  try {
    if (navigator?.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }

    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'

    document.body.appendChild(textarea)
    textarea.select()

    const success = document.execCommand('copy')
    document.body.removeChild(textarea)

    return success
  } catch (err) {
    console.error('Copy failed:', err)
    return false
  }
}

const copyCode = async () => {
  const ok = await copyToClipboard(referralCode.value)
  if (ok) toast.success('Referral code copied!')
}

const copyLink = async () => {
  const ok = await copyToClipboard(referralLink.value)
  if (ok) toast.success('Link copied!')
}

const reloadReferral = async () => {
  try {
    await referral.reload()
  } catch (err) {
    console.error(err)
    toast.error('Failed to refresh referral data')
  }
}

const exportCsv = () => {
  const header = ['Name', 'Join Date', 'Progress', 'Registeration Status', 'Reward Status']
  const rows = referralRows.value.map((item) => [
    item.name,
    item.joinDate,
    item.progressLabel,
    item.status,
    item.rewardStatus,
  ])

  const csv = [header, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = 'referrals.csv'
  link.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.referral-input-shell {
  box-shadow: inset 0 0 0 1px rgb(209 213 219);
  background-clip: padding-box;
}
</style>
