<template>
  <div class="h-full min-w-0">
    <aside
      class="flex h-full min-h-[28rem] w-full flex-col overflow-y-auto rounded-xl border border-gray-200 bg-white p-3 shadow-sm"
    >
      <RouterLink
        to="/website"
        class="mb-3 flex h-10 items-center justify-between border-b border-gray-100 px-2 pb-3 hover:text-green-600"
      >
        <strong class="text-sm font-semibold text-gray-900">Content</strong>

        <!-- Edit icon SVG -->
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 text-gray-500 hover:text-green-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            d="M15.232 5.232l3.536 3.536M4 20h4.586l11-11-4.586-4.586L4 15.414V20z"
          />
        </svg>
      </RouterLink>

      <div v-if="isLoading" class="rounded-lg bg-gray-50 p-4 text-center">
        <p class="text-sm text-gray-500">Loading websites...</p>
      </div>

      <div v-else-if="websites.length" class="mb-4 px-0.5">
        <label for="summaryType" class="mb-1 block px-1 text-xs font-medium text-gray-600">
          Website</label
        >
        <select
          id="summaryType"
          :value="selectedSummary"
          @change="handleWebsiteChange"
          class="h-9 w-full rounded-lg border px-2.5 text-sm font-medium shadow-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
          :class="
            isWebsiteOverview
              ? 'border-green-500 bg-green-50 font-semibold text-green-700'
              : 'border-gray-300 bg-white'
          "
        >
          <option
            v-for="site in websites"
            :key="site.website_link"
            :value="site.website_link"
          >
            {{ site.website_link }}
          </option>
        </select>

        <div
          v-if="topLevelPages.length"
          class="mt-3 text-sm text-gray-700"
        >
          <ul class="list-inside list-none space-y-1">
            <PageTreeItem
              v-for="page in topLevelPages"
              :key="page.name"
              :page="page"
              :pages="selectedWebsitePages"
              :parent-chain="[]"
              :selected-page="selectedPage"
              :pending-page="pendingPage"
              @pageSelected="(page) => (selectedPage = page)"
              @openSidebar="openSidebar"
              @openIndependent="openIndependentPageCreator"
              @pageAction="handlePageAction"
            />
          </ul>
        </div>
        <div v-else class="mt-2 text-sm text-gray-500">
          No pages found for this website.
        </div>

      </div>

      <div
        v-else
        class="flex flex-col items-center rounded-xl border border-dashed border-gray-300 bg-gray-50 px-4 py-6 text-center"
      >
        <span
          class="material-symbols-outlined mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-xl text-green-700"
        >
          language
        </span>
        <p class="text-sm font-semibold text-gray-800">
          No website created yet
        </p>
        <p class="mt-1 text-xs leading-5 text-gray-500">
          Create your first website to start building pages and explore the
          website builder.
        </p>
        <button
          type="button"
          class="app-btn-primary mt-4 w-full"
          @click="createWebsite"
        >
          Add New Website
        </button>
      </div>

      <div
        v-if="websites.length && preferredParentPage"
        class="sticky bottom-0 mt-auto border-t border-gray-100 bg-white pt-3"
      >
        <button
          type="button"
          class="group relative flex w-full items-center justify-center rounded-lg bg-gray-900 px-10 py-3 text-center text-white shadow-sm transition hover:bg-black focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          @click="openSidebar(preferredParentPage)"
        >
          <span class="material-symbols-outlined absolute left-3 text-lg">
            account_tree
          </span>
          <span class="min-w-0">
            <span class="block truncate text-sm font-semibold">
              Add subpages
            </span>
          </span>
        </button>
      </div>
    </aside>

    <Sidebar v-model="showSidebar" width="560px">
      <template #title>{{ pageCreatorTitle }}</template>
      <div class="space-y-5">
        <label v-if="templateChooserMode === 'create'" class="block">
          <span class="text-sm font-semibold text-gray-900">
            Where should this page appear?
          </span>
          <select
            :value="creationParentName"
            class="mt-2 w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-sm focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500"
            @change="handleCreationParentChange"
          >
            <option value="">Separate page — not inside another page</option>
            <option
              v-for="page in availableParentPages"
              :key="page.name"
              :value="page.name"
            >
              {{ page.page }}
            </option>
          </select>
          <span class="mt-1 block text-xs leading-5 text-gray-500">
            {{ pagePlacementHelp }}
          </span>
        </label>

        <div>
          <h3 class="text-base font-semibold text-gray-900">
            {{ templateChooserMode === 'change'
              ? 'Choose the new design'
              : 'Choose a starting point' }}
          </h3>
          <p class="mt-1 text-sm leading-5 text-gray-500">
            {{ templateChooserMode === 'change'
              ? templateChangeSummary
              : 'Start with a ready-made layout, then edit, reorder, add, or remove any section.' }}
          </p>
        </div>

        <div
          v-if="templateChooserMode === 'change'"
          class="flex gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-amber-900"
        >
          <span class="material-symbols-outlined shrink-0 text-xl">warning</span>
          <p class="text-sm leading-5">
            {{ templateChangeWarning }}
          </p>
        </div>

        <div
          v-if="isLoadingTemplates"
          class="grid grid-cols-1 gap-4 sm:grid-cols-2"
        >
          <div
            v-for="index in 4"
            :key="index"
            class="h-48 animate-pulse rounded-xl bg-gray-100"
          ></div>
        </div>

        <div
          v-else-if="pages.length"
          class="grid grid-cols-1 gap-4 sm:grid-cols-2"
        >
          <button
            v-for="page in pages"
            :key="page.name"
            type="button"
            class="group overflow-hidden rounded-xl border bg-white text-left shadow-sm transition hover:-translate-y-0.5 hover:border-green-500 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:cursor-wait disabled:opacity-60"
            :class="isCurrentTemplate(page) ? 'border-green-500 ring-1 ring-green-500' : 'border-gray-200'"
            :disabled="templateChangeLoading"
            @click="selectTemplate(page)"
          >
            <div
              class="relative h-32 overflow-hidden bg-gradient-to-br from-gray-50 to-gray-200"
            >
              <div
                v-if="page.preview_image && !failedPreviewImages.has(page.preview_image)"
                class="h-full bg-white"
              >
                <div
                  v-if="page.preview_layout === 'split'"
                  class="grid h-full grid-cols-[0.9fr_1.1fr]"
                >
                  <div class="flex min-w-0 flex-col justify-center p-3">
                    <span class="text-[7px] font-bold uppercase tracking-[0.16em] text-green-700">
                      {{ page.preview_eyebrow }}
                    </span>
                    <strong class="mt-1 line-clamp-3 font-serif text-[15px] leading-[1.05] text-gray-900">
                      {{ page.preview_heading }}
                    </strong>
                    <span class="mt-2 h-1.5 w-10 rounded-full bg-gray-900"></span>
                  </div>
                  <img
                    :src="page.preview_image"
                    alt=""
                    class="h-full min-h-0 w-full object-cover"
                    @error="markPreviewImageFailed(page.preview_image)"
                  />
                </div>
                <div
                  v-else-if="page.preview_layout === 'editorial'"
                  class="grid h-full grid-cols-[1.35fr_0.65fr]"
                >
                  <img
                    :src="page.preview_image"
                    alt=""
                    class="h-full min-h-0 w-full object-cover"
                    @error="markPreviewImageFailed(page.preview_image)"
                  />
                  <div class="flex min-w-0 flex-col justify-center bg-stone-50 p-2.5">
                    <span class="text-[6px] font-bold uppercase tracking-wider text-amber-700">
                      {{ page.preview_eyebrow }}
                    </span>
                    <strong class="mt-1 line-clamp-4 font-serif text-[12px] leading-[1.05] text-gray-900">
                      {{ page.preview_heading }}
                    </strong>
                  </div>
                </div>
                <div v-else class="relative h-full">
                  <img
                    :src="page.preview_image"
                    alt=""
                    class="h-full min-h-0 w-full object-cover"
                    @error="markPreviewImageFailed(page.preview_image)"
                  />
                  <div class="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/75 via-black/20 to-transparent p-3 text-white">
                    <span class="text-[7px] font-bold uppercase tracking-[0.16em] text-white/80">
                      {{ page.preview_eyebrow }}
                    </span>
                    <strong class="mt-1 line-clamp-2 font-serif text-base leading-none">
                      {{ page.preview_heading }}
                    </strong>
                  </div>
                </div>
              </div>
              <div
                v-else-if="page.preview_images?.length"
                class="grid h-full gap-1 p-2"
                :class="
                  page.preview_images.length > 1 ? 'grid-cols-2' : 'grid-cols-1'
                "
              >
                <div
                  v-for="(image, index) in page.preview_images.slice(0, 4)"
                  :key="`${page.name}-${index}`"
                  class="relative grid min-h-0 place-items-center overflow-hidden rounded-md bg-white"
                >
                  <span
                    class="material-symbols-outlined absolute text-2xl text-gray-300"
                    aria-hidden="true"
                  >
                    image
                  </span>
                  <img
                    v-if="!failedPreviewImages.has(image)"
                    :src="image"
                    alt=""
                    class="relative z-10 h-full min-h-0 w-full bg-white object-cover object-top"
                    @error="markPreviewImageFailed(image)"
                  />
                </div>
              </div>
              <div v-else class="flex h-full items-center justify-center">
                <span class="material-symbols-outlined text-4xl text-gray-400">
                  {{ page.block_count ? 'dashboard' : 'note_add' }}
                </span>
              </div>
              <span
                v-if="page.block_count"
                class="absolute bottom-2 right-2 rounded-full bg-gray-900/80 px-2 py-1 text-[11px] font-medium text-white"
              >
                {{ page.block_count }} sections
              </span>
              <span
                v-if="isCurrentTemplate(page)"
                class="absolute left-2 top-2 rounded-full bg-green-600 px-2 py-1 text-[11px] font-semibold text-white shadow"
              >
                Current template
              </span>
            </div>

            <div class="p-4">
              <div class="flex items-start justify-between gap-3">
                <h4
                  class="font-semibold text-gray-900 group-hover:text-green-700"
                >
                  {{ page.page_name }}
                </h4>
                <span
                  class="material-symbols-outlined text-lg text-gray-400 group-hover:text-green-600"
                >
                  arrow_forward
                </span>
              </div>
              <p class="mt-1 line-clamp-2 text-xs leading-5 text-gray-500">
                {{ page.description }}
              </p>
            </div>
          </button>
        </div>

        <div
          v-else
          class="rounded-xl border border-dashed border-gray-300 p-6 text-center text-sm text-gray-500"
        >
          No page templates are available.
        </div>
      </div>
    </Sidebar>

    <Dialog
      v-model="showConfirmationDialog"
      :options="{ title: confirmationDialog.title, size: 'md' }"
    >
      <template #body-content>
        <div class="flex gap-3">
          <span
            class="material-symbols-outlined mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-50 text-xl text-amber-600"
          >
            {{ confirmationDialog.icon }}
          </span>
          <div>
            <p class="text-sm leading-6 text-gray-700">
              {{ confirmationDialog.message }}
            </p>
            <p v-if="confirmationDialog.help" class="mt-1 text-xs leading-5 text-gray-500">
              {{ confirmationDialog.help }}
            </p>
          </div>
        </div>
      </template>
      <template #actions>
        <button
          type="button"
          class="rounded-lg px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100"
          :disabled="confirmationLoading"
          @click="closeConfirmationDialog"
        >
          Cancel
        </button>
        <button
          type="button"
          class="rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-black disabled:cursor-wait disabled:opacity-60"
          :disabled="confirmationLoading"
          @click="confirmDialogAction"
        >
          {{ confirmationLoading ? 'Please wait…' : confirmationDialog.confirmLabel }}
        </button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import { Dialog } from 'frappe-ui'
import Sidebar from './Sidebar.vue'
import PageTreeItem from './PageTreeItem.vue'
import { confirmDiscardChanges } from '../composables/useUnsavedChanges'

const websites = ref([])
const selectedSummary = ref('')
const selectedWebsitePages = ref([])
const showSidebar = ref(false)
const selectedPage = ref(null)
const selectedPageFromSidebar = ref(null)
const isLoading = ref(true)
const pageActionLoading = ref(false)

const pages = ref([])
const isLoadingTemplates = ref(false)
const creationParentName = ref('')
const failedPreviewImages = ref(new Set())
const templateChooserMode = ref('create')
const templateChangePage = ref(null)
const templateChangeLoading = ref(false)
const showConfirmationDialog = ref(false)
const confirmationLoading = ref(false)
const confirmationDialog = ref({
  title: '',
  message: '',
  help: '',
  icon: 'help',
  confirmLabel: 'Confirm',
  onConfirm: null,
})

function requestConfirmation(options) {
  confirmationDialog.value = {
    title: options.title || 'Confirm action',
    message: options.message || '',
    help: options.help || '',
    icon: options.icon || 'help',
    confirmLabel: options.confirmLabel || 'Confirm',
    onConfirm: options.onConfirm || null,
  }
  showConfirmationDialog.value = true
}

function closeConfirmationDialog() {
  if (confirmationLoading.value) return
  showConfirmationDialog.value = false
}

async function confirmDialogAction() {
  if (confirmationLoading.value || !confirmationDialog.value.onConfirm) return
  confirmationLoading.value = true
  try {
    await confirmationDialog.value.onConfirm()
    showConfirmationDialog.value = false
  } finally {
    confirmationLoading.value = false
  }
}

function markPreviewImageFailed(image) {
  failedPreviewImages.value = new Set([
    ...failedPreviewImages.value,
    image,
  ])
}

// watch(selectedPageFromSidebar, (newVal) => {
//   if (newVal) {
//     mainPageId(newVal)
//   }
// })
// console.log('Selected page from sidebar:', selectedPageFromSidebar)

// function mainPageId(page) {
//   const pageId = {
//     name: page.name,
//   }
//   localStorage.setItem('mainpage', JSON.stringify(pageId))
// }

watch(selectedPageFromSidebar, (newVal) => {
  if (newVal) {
    //  // console.log('Selected page from sidebar:', newVal) // ✅ log actual new value
    mainPageId(newVal)
  }
})

// // function mainPageId(page) {
// //   const pageData = {
// //     main_page_name: page.name,
// //     website_name: page.website_name || '', // ✅ make sure to include website_name
// //   }
// //   console.log('Saving to localStorage:', pageData) // ✅ confirm what’s being saved
// //   localStorage.setItem('mainpage', JSON.stringify(pageData))
// // }

// function mainPageId(page) {
//   const pageData = {
//     main_page_name: page.name,
//     website_name: page.website_name || '',
//     ...page, // ✅ keep the rest of the page object too
//   }
//   console.log('Saving to localStorage:', pageData)
//   localStorage.setItem('mainpage', JSON.stringify(pageData))
// }

const mainPage = ref(JSON.parse(localStorage.getItem('mainpage') || '{}'))
const websiteObj = ref(
  JSON.parse(localStorage.getItem('selectedWebsite') || '{}'),
)

function mainPageId(page) {
  const pageData = {
    main_page_name: page.name,
    website_name: page.website_name || '',
    ...page,
  }
  localStorage.setItem('mainpage', JSON.stringify(pageData))
  //  //  console.log('Saving to localStorage:', pageData)
  mainPage.value = pageData // ✅ reactive sync
}

const router = useRouter()
const route = useRoute()
const toast = useToast()
const isWebsiteOverview = computed(() => route.name === 'WebsiteHome')

function applyWebsiteSelection(websiteLink) {
  const selectedWebsiteObj = websites.value.find(
    (website) => website.website_link === websiteLink,
  )
  selectedSummary.value = websiteLink
  localStorage.setItem('selectedWebsite', JSON.stringify(selectedWebsiteObj))
  websiteObj.value = selectedWebsiteObj
  selectedWebsitePages.value = selectedWebsiteObj?.pages || []
  selectCurrentOrHomePage()
}

function selectCurrentOrHomePage() {
  const activePages = selectedWebsitePages.value.filter(
    (page) => page.page_status !== 'Archived',
  )
  const routePageName = String(route.params.page_name || '')
  const routePage = activePages.find(
    (page) => String(page.name) === routePageName,
  )
  const homePage = activePages.find((page) => !page.parent1)
  const nextPage = routePage || homePage || activePages[0] || null

  selectedPage.value = nextPage
  selectedPageFromSidebar.value = nextPage
  if (nextPage) mainPageId(nextPage)
}

async function handleWebsiteChange(event) {
  const nextWebsite = event.target.value
  if (nextWebsite === selectedSummary.value) return

  if (!(await confirmDiscardChanges())) {
    event.target.value = selectedSummary.value
    return
  }

  applyWebsiteSelection(nextWebsite)
  if (route.name !== 'WebsiteHome' && selectedPage.value?.name) {
    await router.push({
      name: 'WebsitePageEdit',
      params: { page_name: selectedPage.value.name },
    })
  }
}

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')
const fetchWebsites = async () => {
  //  // console.log('🔗 Frappe URL:', Frappe_URL)
  //  // console.log('🔑 Using token:', token)

  try {
    const url = `${Frappe_URL}/api/method/ecommerce.api.get_vendor_websites`
    //  //console.log('🌐 Fetching from:', url)

    const res = await fetch(url, {
      method: 'GET',
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    const result = await res.json()
    const data = result?.message

    //  // console.log('📥 Fetched websites data:', result)
    if (data?.status === 'success') {
      websites.value = Array.isArray(data.data) ? data.data : []

      const saved = localStorage.getItem('selectedWebsite')
      //  //  console.log('Saved website from localStorage:', saved)
      if (saved) {
        try {
          const parsed = JSON.parse(saved)
          const found = websites.value.find(
            (w) => w.website_link === parsed.website_link,
          )
          if (found) {
            applyWebsiteSelection(parsed.website_link)
          }
          //  // console.log('Restored selected website:', found)
        } catch (e) {
          console.error('Error parsing saved website:', e)
        }
      }

      // If nothing restored, pick the first website
      if (!selectedSummary.value && websites.value.length) {
        applyWebsiteSelection(websites.value[0].website_link)
      }
    }
  } catch (err) {
    console.error('Error fetching websites:', err)
    websites.value = []
  } finally {
    isLoading.value = false
  }
}

const topLevelPages = computed(() =>
  selectedWebsitePages.value.filter(
    (page) => !page.parent1 && page.page_status !== 'Archived',
  ),
)

const preferredParentPage = computed(() => {
  if (selectedPage.value && selectedPage.value.page_status !== 'Archived') {
    return selectedPage.value
  }

  const routePage = selectedWebsitePages.value.find(
    (page) => String(page.name) === String(route.params.page_name || ''),
  )
  if (routePage?.page_status !== 'Archived') return routePage

  return topLevelPages.value[0] || null
})

const selectedCreationParent = computed(() =>
  selectedWebsitePages.value.find(
    (page) => String(page.name) === String(creationParentName.value || ''),
  ),
)

const pageCreatorTitle = computed(() =>
  templateChooserMode.value === 'change'
    ? `Change template for “${templateChangePage.value?.page || 'page'}”`
    : selectedCreationParent.value
      ? `Add page under “${selectedCreationParent.value.page}”`
      : 'Create a separate page',
)

const templateChangeIsChild = computed(() =>
  Boolean(templateChangePage.value?.parent1),
)

const templateChangeSummary = computed(() =>
  templateChangeIsChild.value
    ? `Only the body of “${templateChangePage.value?.page || 'this page'}” will change.`
    : `The header, body, and footer of “${templateChangePage.value?.page || 'this page'}” will change.`,
)

const templateChangeWarning = computed(() =>
  templateChangeIsChild.value
    ? 'This child page’s main sections will be replaced. Its inherited header and footer will stay unchanged.'
    : 'This parent page’s header, main sections, and footer will be replaced. Its new header and footer will also be applied to every child page.',
)

const pagePlacementHelp = computed(() =>
  selectedCreationParent.value
    ? `This page will appear under “${selectedCreationParent.value.page}” and share its header and footer.`
    : 'This page will not appear inside another page and will use its own header and footer.',
)

const pendingPage = computed(() => {
  if (route.query.source !== 'newpage') return null

  const template = pages.value.find(
    (page) => String(page.name) === String(route.params.page_name || ''),
  )
  const storedParent = mainPage.value || {}

  return {
    title: template?.page_name || 'New page',
    parentName:
      String(route.query.parent || '') ||
      creationParentName.value ||
      storedParent.name ||
      storedParent.main_page_name ||
      preferredParentPage.value?.name ||
      '',
  }
})

const availableParentPages = computed(() =>
  selectedWebsitePages.value.filter((page) => page.page_status !== 'Archived'),
)

async function handlePageAction({ action, page }) {
  if (pageActionLoading.value || !page?.name) return
  if (!(await confirmDiscardChanges())) return

  if (action === 'archive') {
    requestConfirmation({
      title: 'Archive page?',
      message: `Archive “${page.page}”? Its child pages will also be archived.`,
      help: 'Archived pages are hidden from the website and can be restored from Archive.',
      icon: 'archive',
      confirmLabel: 'Archive page',
      onConfirm: () => updatePageArchiveStatus({ action, page }),
    })
    return
  }

  if (!['archive', 'restore'].includes(action)) return

  await updatePageArchiveStatus({ action, page })
}

async function updatePageArchiveStatus({ action, page }) {
  if (pageActionLoading.value || !page?.name) return

  pageActionLoading.value = true
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.set_builder_page_archived`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
        },
        body: JSON.stringify({
          page_name: page.name,
          archived: action === 'archive',
        }),
      },
    )
    const result = await response.json()
    const message = result?.message
    if (!response.ok || message?.status !== 'success') {
      throw new Error(message?.message || 'Unable to update the page.')
    }

    const affectedPages = (message.data?.page_names || []).map(String)
    const currentPageName = String(route.params.page_name || '')
    let savedMainPage = {}
    try {
      savedMainPage = JSON.parse(localStorage.getItem('mainpage') || '{}')
    } catch {
      localStorage.removeItem('mainpage')
    }
    const savedMainPageName = String(
      savedMainPage.name || savedMainPage.main_page_name || '',
    )

    if (affectedPages.includes(savedMainPageName)) {
      localStorage.removeItem('mainpage')
      mainPage.value = {}
    }

    showSidebar.value = false
    await fetchWebsites()

    if (affectedPages.includes(currentPageName)) {
      const refreshedPage = selectedWebsitePages.value.find(
        (candidate) => String(candidate.name) === currentPageName,
      )
      if (refreshedPage) {
        selectedPage.value = refreshedPage
        selectedPageFromSidebar.value = refreshedPage
        mainPageId(refreshedPage)
      }
    }

    window.dispatchEvent(new CustomEvent('ecommerce:page-status-updated'))

    toast.success(message.message)
  } catch (error) {
    toast.error(error?.message || 'Unable to update the page.')
  } finally {
    pageActionLoading.value = false
  }
}

function currentToolbarPage() {
  const routePage = selectedWebsitePages.value.find(
    (page) => String(page.name) === String(route.params.page_name || ''),
  )
  return routePage || selectedPage.value || preferredParentPage.value || null
}

function handleToolbarPageAction(event) {
  const action = event?.detail?.action
  const page = currentToolbarPage()

  if (action === 'create-child') {
    if (page) openSidebar(page)
    return
  }
  if (action === 'create-independent') {
    openIndependentPageCreator()
    return
  }
  if (action === 'change-template') {
    if (page) openTemplateChanger(page)
    return
  }
  if (['archive', 'restore'].includes(action) && page) {
    handlePageAction({ action, page })
  }
}

function setCreationParent(page) {
  if (!page?.name) {
    creationParentName.value = ''
    localStorage.removeItem('mainpage')
    sessionStorage.removeItem('breadcrumbInfo')
    mainPage.value = {}
    return
  }

  creationParentName.value = String(page.name)
  mainPageId(page)
}

function handleCreationParentChange(event) {
  const parentName = String(event.target.value || '')
  const parentPage = selectedWebsitePages.value.find(
    (page) => String(page.name) === parentName,
  )
  setCreationParent(parentPage)
}

function openIndependentPageCreator() {
  templateChooserMode.value = 'create'
  templateChangePage.value = null
  selectedPage.value = null
  selectedPageFromSidebar.value = null
  setCreationParent(null)
  showSidebar.value = true
}

const openSidebar = (page) => {
  templateChooserMode.value = 'create'
  templateChangePage.value = null
  selectedPage.value = page
  selectedPageFromSidebar.value = page
  setCreationParent(page)
  showSidebar.value = true
}

async function openTemplateChanger(page) {
  if (!(await confirmDiscardChanges())) return
  templateChooserMode.value = 'change'
  templateChangePage.value = page
  showSidebar.value = true
}

const fetchPages = async () => {
  isLoadingTemplates.value = true
  try {
    const url = `${Frappe_URL}/api/method/ecommerce.api.get_pages`
    //  // console.log('🌐 Fetching from:', url)

    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    })
    //  //console.log('Response status:', res)
    const result = await res.json()
    pages.value = result?.message?.data || []
  } catch (err) {
    console.error('Error fetching pages:', err)
    pages.value = []
  } finally {
    isLoadingTemplates.value = false
  }
}

function isCurrentTemplate(template) {
  return templateChooserMode.value === 'change' &&
    String(templateChangePage.value?.template || '') === String(template.name || '')
}

async function changePageTemplate(template) {
  const targetPage = templateChangePage.value
  if (!targetPage?.name || !template?.name || isCurrentTemplate(template)) return

  const isChildPage = Boolean(targetPage.parent1)
  const replacementDescription = isChildPage
    ? 'Only this child page\'s main sections will be replaced. Its inherited header and footer will stay unchanged.'
    : 'This parent page\'s header, main sections, and footer will be replaced. The new header and footer will be applied to all child pages.'
  requestConfirmation({
    title: 'Change page template?',
    message: `Change “${targetPage.page}” to “${template.page_name}”?`,
    help: replacementDescription,
    icon: 'dashboard_customize',
    confirmLabel: 'Change template',
    onConfirm: () => applyPageTemplateChange(template, targetPage, isChildPage),
  })
}

async function applyPageTemplateChange(template, targetPage, isChildPage) {

  templateChangeLoading.value = true
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.change_builder_page_template`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
        },
        body: JSON.stringify({
          page_name: targetPage.name,
          template_name: template.name,
        }),
      },
    )
    const result = (await response.json())?.message
    if (!response.ok || result?.status !== 'success') {
      throw new Error(result?.message || 'Unable to change the page template.')
    }

    showSidebar.value = false
    templateChangePage.value = null
    templateChooserMode.value = 'create'
    await fetchWebsites()
    window.dispatchEvent(
      new CustomEvent('ecommerce:page-template-changed', {
        detail: { pageName: targetPage.name, templateName: template.name },
      }),
    )
    toast.success(
      isChildPage
        ? `Only “${targetPage.page}” main sections changed to ${template.page_name}`
        : `“${targetPage.page}” design changed and its child layouts were updated`,
    )
  } catch (error) {
    toast.error(error?.message || 'Unable to change the page template.')
  } finally {
    templateChangeLoading.value = false
  }
}

function selectTemplate(page) {
  if (templateChooserMode.value === 'change') {
    changePageTemplate(page)
    return
  }
  navigateToPage(page)
}

const navigateToPage = (page) => {
  // Navigate to edit page
  router.push({
    name: 'WebsitePageEdit',
    params: { page_name: page.name },
    query: {
      source: 'newpage',
      ...(creationParentName.value && {
        parent: creationParentName.value,
      }),
    },
  })

  showSidebar.value = false
}

const createWebsite = () => {
  router.push({
    name: 'WebsiteHome',
    query: { create: '1' },
  })
}

// On mount
onMounted(() => {
  fetchWebsites()
  fetchPages()
  window.addEventListener('ecommerce:website-updated', fetchWebsites)
  window.addEventListener(
    'ecommerce:website-page-action',
    handleToolbarPageAction,
  )
})

watch(
  () => route.params.page_name,
  (pageName, previousPageName) => {
    if (pageName !== previousPageName) fetchWebsites()
  },
)

onBeforeUnmount(() => {
  window.removeEventListener('ecommerce:website-updated', fetchWebsites)
  window.removeEventListener(
    'ecommerce:website-page-action',
    handleToolbarPageAction,
  )
})
</script>
