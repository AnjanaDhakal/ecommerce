<template>
  <div>
    <!-- Loading state -->

    <div
      v-if="loading"
      class="animate-pulse"
      :class="collapsed ? 'px-2' : 'px-2 '"
    >
      <div
        class="flex items-center"
        :class="collapsed ? 'justify-center mt-1 mb-3' : 'gap-2 mt-2 mb-2 rounded-2xl border border-gray-100 bg-gray-50 px-3 py-3'"
      >
        <div :class="collapsed ? 'h-10 w-10' : 'h-12 w-12'" class="rounded-full bg-gray-300 shrink-0"></div>
        <div v-if="!collapsed" class="min-w-0 flex-1">
          <div class="h-4 w-28 bg-gray-300 rounded mb-1.5"></div>
          <div class="h-3 w-36 bg-gray-300 rounded mb-1.5"></div>
          <div class="h-3 w-28 bg-gray-300 rounded"></div>
        </div>
      </div>
    </div>

    <!-- Vendor info available -->
    <div v-else-if="hasVendorData">
      <div :class="collapsed ? '' : 'px-3'">
        <div
          :role="canEditProfile ? 'button' : undefined"
          :tabindex="canEditProfile ? 0 : undefined"
          class="flex items-center rounded-md"
          :class="
            collapsed
              ? 'justify-center p-2'
              : `gap-3 rounded-2xl border border-gray-200 bg-gray-50 ${canEditProfile ? 'cursor-pointer' : ''}`
          "
          @click="openEditProfile"
        >
        <div
          class="relative shrink-0"
          :class="collapsed ? 'h-11 w-11' : 'h-16 w-16'"
        >
          <svg
            class="absolute inset-0 -rotate-90"
            viewBox="0 0 64 64"
            width="100%"
            height="100%"
          >
            <circle
              cx="32"
              cy="32"
              r="24"
              fill="none"
              stroke="#E5E7EB"
              stroke-width="2"
            />
            <circle
              cx="32"
              cy="32"
              r="24"
              fill="none"
              stroke="#22C55E"
              stroke-width="2"
              stroke-linecap="round"
              :stroke-dasharray="2 * Math.PI * 24"
              :stroke-dashoffset="2 * Math.PI * 24 * (1 - profileCompletion / 100)"
              class="transition-all duration-500"
            />
          </svg>

          <div
            class="absolute left-1/2 top-1/2 flex items-center justify-center overflow-hidden rounded-full bg-gray-300 -translate-x-1/2 -translate-y-1/2"
            :class="collapsed ? 'h-7 w-7' : 'h-10 w-10'"
          >
            <div
              v-if="!vendorLogo"
              class="flex items-center justify-center h-full w-full"
            >
              <p :class="collapsed ? 'text-base' : 'text-2xl'" class="font-semibold text-gray-600">
                {{ vendorInitial }}
              </p>
            </div>

            <img
              v-else
              class="h-full w-full object-cover"
              :src="vendorLogo"
              @error="setDefaultImage"
              alt="Store Logo"
            />
          </div>

          <span
            v-if="!collapsed"
            class="absolute bottom-1 left-1/2 z-10 -translate-x-1/2 rounded-full bg-white px-1.5 py-0.5 text-[10px] font-semibold leading-none text-green-600 shadow-sm ring-1 ring-gray-200"
          >
            {{ profileCompletion }}%
          </span>
        </div>

        <div
          v-if="!collapsed"
          class="min-w-0 flex-1 self-center"
        >
          <div class="flex items-center gap-2 group cursor-pointer">
            <p class="text-base leading-tight text-gray-800 font-bold truncate">
              {{ vendorName }}
            </p>

            <span
              style="
                font-variation-settings:
                  'FILL' 1,
                  'wght' 700,
                  'GRAD' 0,
                  'opsz' 48;
              "
              class="material-symbols-outlined text-green-600 text-base shrink-0"
            >
              new_releases
            </span>

          </div>
          <p class="text-gray-800 font-pmedium text-xs leading-tight truncate">{{ vendorEmail }}</p>
          <p class="text-gray-800 font-pmedium text-xs leading-tight truncate">{{ vendorPhone }}</p>
        </div>
      </div>
      </div>

    </div>
    <!-- Vendor data not available -->
    <div v-else class="my-8 flex items-center justify-center">
      <Button
        :variant="'solid'"
        theme="gray"
        size="sm"
        label="Verify KYC"
        :loading="false"
        :disabled="!canEditProfile"
        @click="openEditProfile"
      >
        Verify KYC
      </Button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'
import editaccount from '../data/editaccount'
import userInfo from '../data/userInfo'

import { Button } from 'frappe-ui'
import { useRouter } from 'vue-router'

defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})

const router = useRouter()

const vendorName = ref('')
const vendorLogo = ref('')
const vendorEmail = ref('')
const vendorPhone = ref('')
const hasVendorData = ref(false)
const loading = ref(true)
const profileCompletion = ref(0)

const canEditProfile = computed(() => {
  const payload = userInfo?.data?.message || userInfo?.data || {}
  return String(payload?.role || '').toUpperCase() === 'ADMIN'
})

const openEditProfile = () => {
  if (!canEditProfile.value) return
  router.push('/editprofile')
}

const vendorInitial = computed(() => {
  return vendorName.value ? vendorName.value.charAt(0) : ''
})

const setDefaultImage = (event) => {
  event.target.src = `https://via.placeholder.com/150?text=${vendorInitial.value || 'G'}`
}

onMounted(async () => {
  try {
    const response = await editaccount.fetch()
    const data = editaccount?.data?.data?.[0] || editaccount?.data?.[0]


    if (data && data.vendor_name) {
      vendorName.value = data.vendor_name
      vendorLogo.value = data.logo
      vendorEmail.value = data.primary_email
      vendorPhone.value = data.primary_phone
      const fields = [
        data.vendor_name,
        data.pan_number,
        data.primary_email,
        data.contact_person,
        data.primary_phone,
        data.secondary_phone,
        data.secondary_email,
        data.vendor_address,
        data.website,
        data.facebook,
        data.instagram,
        data.logo,
        data.pan,
        data.citizenship,
      ]
      const filledFields = fields.filter(
        (field) => field !== null && field !== undefined && String(field).trim() !== '',
      ).length
      profileCompletion.value = Math.round((filledFields / fields.length) * 100)
      hasVendorData.value = true
    } else {
      hasVendorData.value = false
    }
  } catch (error) {
    console.error('Top vendor profile fetch error:', error)
    hasVendorData.value = false
  } finally {
    loading.value = false
  }

  await nextTick(() => {
    const tooltip = document.getElementById('tooltip')
    const groupElement = document.querySelector('.group')
    if (tooltip && groupElement) {
      groupElement.addEventListener('mousemove', (event) => {
        tooltip.style.left = `${event.pageX + 10}px`
        tooltip.style.top = `${event.pageY + 10}px`
      })
    }
  })
})
</script>

<style scoped>
.pointer-events-none {
  pointer-events: none;
}

.absolute {
  position: absolute;
}

.hidden {
  display: none;
}

.group-hover\:block:hover .hidden {
  display: block;
}
</style>
