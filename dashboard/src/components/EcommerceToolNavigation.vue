<template>
  <div class="shrink-0 md:h-full md:w-52">
    <label class="sr-only" :for="mobileSelectId">ECommerce section</label>
    <select
      :id="mobileSelectId"
      :value="modelValue"
      class="h-11 w-full rounded-xl border border-gray-200 bg-white px-3 text-sm font-medium text-gray-900 shadow-sm md:hidden"
      @change="select($event.target.value)"
    >
      <option
        v-for="item in flatItems"
        :key="item.value"
        :value="item.value"
      >
        {{ item.label }}
      </option>
    </select>

    <aside
      class="hidden h-full min-h-[28rem] flex-col rounded-xl border border-gray-200 bg-white p-3 shadow-sm md:flex"
      aria-label="ECommerce workspace"
    >
      <router-link
        v-if="showAccountChrome"
        to="/main"
        class="mb-3 flex h-12 items-center border-b border-gray-100 px-2 pb-3"
        title="Ecommerce dashboard"
      >
        <img
          :src="companyLogo"
          alt="Ecommerce"
          class="max-h-9 w-full object-contain object-left"
        />
      </router-link>

      <div class="flex items-center gap-3 border-b border-gray-100 px-2 pb-3">
        <img
          :src="ecommerceIcon"
          alt=""
          class="h-9 w-9 shrink-0 rounded-lg object-cover"
        />
        <div class="min-w-0">
          <p class="truncate text-sm font-semibold text-gray-900">ECommerce</p>
          <p class="text-[11px] text-gray-500">Store workspace</p>
        </div>
      </div>

      <div class="mt-3 space-y-4">
        <section v-for="group in groups" :key="group.label || 'main'">
          <p
            v-if="group.label"
            class="mb-1 px-2 text-[10px] font-semibold uppercase tracking-[0.12em] text-gray-400"
          >
            {{ group.label }}
          </p>

          <div class="space-y-1">
            <button
              v-for="item in group.items"
              :key="item.value"
              type="button"
              class="flex h-9 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-sm font-medium transition-colors"
              :class="itemClass(item.value)"
              @click="select(item.value)"
            >
              <span class="material-symbols-outlined text-[18px]">
                {{ item.icon }}
              </span>
              <span class="min-w-0 flex-1 truncate">{{ item.label }}</span>
              <span
                v-if="modelValue === item.value"
                class="h-1.5 w-1.5 rounded-full bg-[#15803d]"
              ></span>
            </button>
          </div>
        </section>
      </div>

      <button
        v-if="showAllApps"
        type="button"
        class="mt-auto flex h-9 w-full items-center gap-2 rounded-lg border-t border-gray-100 px-2.5 pt-3 text-left text-xs font-medium text-gray-500 transition-colors hover:text-gray-900"
        @click="emit('allApps')"
      >
        <span class="material-symbols-outlined text-[17px]">apps</span>
        All integrations
      </button>

      <div
        v-if="showAccountChrome"
        class="mt-3 flex items-center gap-2.5 border-t border-gray-100 px-2 pt-3"
      >
        <UserAvatar class="shrink-0" />
        <router-link to="/editprofile" class="min-w-0 flex-1">
          <p class="truncate text-sm font-semibold text-gray-800">
            {{ userName }}
          </p>
          <p
            v-if="userRole"
            class="mt-0.5 truncate text-[10px] font-medium uppercase tracking-wide text-gray-500"
          >
            {{ userRole }}
          </p>
        </router-link>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import UserAvatar from './Avatar.vue'
import userInfo from '@/data/userInfo'
import companyLogo from '@/assets/apps-menu/ecommerce.png'
import ecommerceIcon from '@/assets/apps-menu/ecommerce.png'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'overview',
  },
  showAllApps: {
    type: Boolean,
    default: false,
  },
  showAccountChrome: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue', 'allApps'])
const mobileSelectId = 'ecommerce-workspace-section'

const groups = [
  {
    label: '',
    items: [
      { label: 'Website', value: 'overview', icon: 'home' },
      { label: 'Orders', value: 'orders', icon: 'shopping_bag' },
    ],
  },
  {
    label: 'Catalogue',
    items: [
      { label: 'Products', value: 'add-product', icon: 'inventory_2' },
      { label: 'Categories', value: 'categories', icon: 'category' },
      { label: 'Brands', value: 'brands', icon: 'sell' },
    ],
  },
  {
    label: 'Insights',
    items: [
      { label: 'Analytics', value: 'analytics', icon: 'monitoring' },
      { label: 'Extensions', value: 'plugins', icon: 'extension' },
      { label: 'Archive', value: 'archive', icon: 'archive' },
    ],
  },
]

const flatItems = computed(() => groups.flatMap((group) => group.items))
const userPayload = computed(
  () => userInfo?.data?.message || userInfo?.data || {},
)
const userName = computed(
  () =>
    userPayload.value.full_name ||
    userPayload.value.fullName ||
    userPayload.value.name ||
    'User',
)
const userRole = computed(() => userPayload.value.role || '')

function itemClass(value) {
  return props.modelValue === value
    ? 'bg-[#e8f5ee] text-[#15803d]'
    : 'text-gray-800 hover:bg-gray-50 hover:text-gray-900'
}

function select(value) {
  emit('update:modelValue', value)
}
</script>
