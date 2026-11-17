<template>
  <li class="relative">
    <div
      class="flex h-9 cursor-pointer select-none items-center justify-between rounded-lg px-2.5 transition-colors"
      :class="{
        'bg-[#e8f5ee] font-semibold text-[#15803d]': isSelectedPage,
        'text-gray-600 hover:bg-gray-50 hover:text-gray-900': !isSelectedPage,
      }"
    >
      <!-- Expand/Collapse Toggle -->
      <button
        v-if="children.length > 0"
        @click="toggle()"
        class="mr-1.5 shrink-0 text-gray-500"
        aria-label="Toggle collapse"
        type="button"
      >
        <svg
          fill="#000000"
          viewBox="-6.5 0 32 32"
          xmlns="http://www.w3.org/2000/svg"
          class="h-3.5 w-3.5 transition-transform duration-200"
          :class="{ 'rotate-0': isExpanded, '-rotate-90': !isExpanded }"
        >
          <path
            d="M18.813 11.406l-7.906 9.906c-0.75 0.906-1.906 0.906-2.625 0l-7.906-9.906c-0.75-0.938-0.375-1.656 0.781-1.656h16.875c1.188 0 1.531 0.719 0.781 1.656z"
          />
        </svg>
      </button>

      <!-- Spacer so page names align when there's no arrow -->
      <span v-else class="mr-5"></span>

      <!-- Page Name with Icon -->
      <div class="flex min-w-0 flex-1 items-center space-x-2">
        <!-- Icon: Home for root -->
        <svg
          v-if="parentChain.length === 0"
          class="h-4 w-4 shrink-0"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill-rule="evenodd"
            clip-rule="evenodd"
            d="M8 0L0 6V8H1V15H4V10H7V15H15V8H16V6L14 4.5V1H11V2.25L8 0ZM9 10H12V13H9V10Z"
            fill="currentColor"
          />
        </svg>

        <!-- Icon: Building for children -->
        <svg
          v-else
          class="h-4 w-4 shrink-0"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path d="M13 11V1H9L9 11H13Z" fill="currentColor" />
          <path d="M15 15V13L1 13V15L15 15Z" fill="currentColor" />
          <path d="M7 5L7 11H3L3 5H7Z" fill="currentColor" />
        </svg>

        <!-- Page Name -->
        <button
          @click="navigateToPage"
          class="min-w-0 flex-1 truncate text-left focus:outline-none"
          :class="{ 'font-semibold text-green-700': isSelectedPage }"
          type="button"
        >
          {{ page.page }}
        </button>
      </div>

    </div>

    <div
      v-if="isPendingChild"
      class="ml-6 mt-1 flex items-center gap-2 rounded-md border border-green-300 bg-green-50 px-2 py-2 text-green-800"
    >
      <span class="material-symbols-outlined text-base">description</span>
      <span class="min-w-0 flex-1 truncate text-sm font-semibold">
        {{ pendingPage.title }}
      </span>
      <span
        class="shrink-0 rounded-full bg-white px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-green-700"
      >
        Not saved
      </span>
    </div>

    <!-- Recursive Children -->
    <ul
      v-if="isExpanded && children.length"
      class="list-none ml-3 mt-1 space-y-1"
    >
      <PageTreeItem
        v-for="child in children"
        :key="child.name"
        :page="child"
        :pages="pages"
        :parent-title="page.page"
        :parent-name="page.name"
        :parent-chain="[...parentChain, page]"
        :selected-page="selectedPage"
        :pending-page="pendingPage"
        @pageSelected="$emit('pageSelected', $event)"
        @openSidebar="$emit('openSidebar', $event)"
        @openIndependent="$emit('openIndependent')"
        @pageAction="$emit('pageAction', $event)"
      />
    </ul>
  </li>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageTreeItem from './PageTreeItem.vue'
import { confirmDiscardChanges } from '../composables/useUnsavedChanges'

const props = defineProps({
  page: Object,
  pages: Array,
  parentTitle: String,
  parentName: [String, Number],
  parentChain: {
    type: Array,
    default: () => [],
  },
  selectedPage: Object,
  pendingPage: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits([
  'openSidebar',
  'openIndependent',
  'pageSelected',
  'pageAction',
])

const router = useRouter()
const route = useRoute()
const isExpanded = ref(true)
function toggle() {
  isExpanded.value = !isExpanded.value
}

const children = computed(() => {
  return props.pages.filter(
    (p) =>
      p.parent1 == props.page.name &&
      (p.page_status === 'Archived') === isArchived.value,
  )
})

const isArchived = computed(() => props.page.page_status === 'Archived')
const isPendingChild = computed(
  () =>
    Boolean(props.pendingPage) &&
    String(props.pendingPage.parentName || '') ===
      String(props.page.name || ''),
)

function setBreadcrumbSession() {
  const breadcrumb = {
    parent: props.parentTitle,
    parent_name: props.parentName,
    parent_chain: Array.isArray(computedParentChain.value)
      ? computedParentChain.value.join(' / ')
      : computedParentChain.value,
  }
  sessionStorage.setItem('breadcrumbInfo', JSON.stringify(breadcrumb))
  //  // /console.log('Breadcrumb set in session:', breadcrumb)
}

async function navigateToPage() {
  if (!(await confirmDiscardChanges())) return false

  setBreadcrumbSession()
  emit('pageSelected', props.page)
  //  // console.log('Navigating to pagemncbs:', props.page)
  router.push({
    name: 'WebsitePageEdit',
    params: { page_name: props.page.name },
  })
  return true
}

const computedParentChain = computed(() => {
  return [...props.parentChain, props.page].map((p) => p.page).join(' > ')
})

const isSelectedPage = computed(() => {
  if (props.pendingPage) return false
  const selectedPageName = props.selectedPage?.name || route.params.page_name
  return String(selectedPageName || '') === String(props.page.name || '')
})
</script>
