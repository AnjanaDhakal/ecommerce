<template>
  <div class="flex h-full w-full flex-col bg-white">
    <SelectedPageDetails
      v-if="selectedPage"
      :form="form"
      :selectedPage="selectedPage"
      :isFromNewPage="isFromNewPage"
      :parsedDataJson="parsedDataJson"
      :handleClick="handleClick"
      :handleClickandPublish="handleClickandPublish"
      :breadcrumb="fullBreadcrumb"
      :main_page_name="pageId"
    />

    <PageDataDetails :pageData="pageData" :breadcrumb="fullBreadcrumb" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, watchEffect } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SelectedPageDetails from '@/components/SelectedPageDetails.vue'
import PageDataDetails from '@/components/PageDataDetails.vue'
import { clearUnsavedChanges } from '@/composables/useUnsavedChanges'

import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const form = ref({
  title: '',
})
const toast = useToast()

const pageData = ref(null)
const websiteObj = ref(
  JSON.parse(localStorage.getItem('selectedWebsite') || '{}'),
)
const pageId = ref(
  JSON.parse(localStorage.getItem('mainpage') || '{}').name || null,
)
//console.log('Loaded hrashfdh name:', pageId.value)

const allWebsitesWithPages = ref([]) // fill this from API or inject globally

// Fetch all websites and their pages
const loading = ref(true)

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''

const fetchdata = async () => {
  const token = localStorage.getItem('access_token') || ''
  try {
    loading.value = true
    const pageId = route.params.page_name // Or however you're storing it
    //  //console.log('Fetching data for pageId:', pageId)
    const url = pageId
      ? `${Frappe_URL}/api/method/ecommerce.api.get_pagetemplatedata?page_id=${encodeURIComponent(pageId)}`
      : `${Frappe_URL}/api/method/ecommerce.api.get_pagetemplatedata`

    const res = await fetch(url, {
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })
    const json = await res.json()
    // console.log('Fetched pagetemplatedata:', json)

    if (pageId) {
      pageData.value = res.ok ? json?.message?.data || null : null
    } else {
      allWebsitesWithPages.value = json.message.data || []
    }
  } catch (err) {
    console.error('❌ Failed to fetch websites/pages:', err)
  } finally {
    loading.value = false
  }
}

const pageName = computed(() => route.params.page_name || null)

const isFromNewPage = computed(() => route.query.source === 'newpage')
const pages = ref([])
const selectedPage = ref(null)
const parsedDataJson = ref(null)
const fullBreadcrumb = ref('')

async function applyParentLayout(config, token) {
  let parentPage = {}
  try {
    parentPage = JSON.parse(localStorage.getItem('mainpage') || '{}')
  } catch {
    localStorage.removeItem('mainpage')
  }

  const parentName =
    String(route.query.parent || '') ||
    parentPage.name ||
    parentPage.main_page_name
  if (!parentName || !config) return config

  const response = await fetch(
    `${Frappe_URL}/api/method/ecommerce.api.get_pagetemplatedata?page_id=${encodeURIComponent(parentName)}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    },
  )
  const result = await response.json()
  const parentData = result?.message?.data
  const parentValues = parentData?.field_value
  if (!response.ok || !parentValues) return config

  const mergedConfig = deepCopy(config)
  mergedConfig.starter_content = mergedConfig.starter_content || {}
  mergedConfig.starter_content.header = deepCopy(parentValues.header || [])
  mergedConfig.starter_content.footer = deepCopy(parentValues.footer || [])
  mergedConfig.inherits_layout = true
  mergedConfig.layout_source = parentData.layout_source || parentName
  return mergedConfig
}

// Load breadcrumb from sessionStorage
function loadBreadcrumbFromSession() {
  const stored = sessionStorage.getItem('breadcrumbInfo')
  if (stored) {
    try {
      const { parent_chain } = JSON.parse(stored)
      fullBreadcrumb.value = parent_chain
        ? parent_chain.replace(/>/g, ' / ')
        : ''
    } catch (e) {
      fullBreadcrumb.value = ''
    }
  }
}

// function handleClick() {
//   // Get selected website
//   const websiteJson = sessionStorage.getItem('selectedWebsite')
//   const websiteObj = websiteJson ? JSON.parse(websiteJson) : null

//   const mainPage = JSON.parse(sessionStorage.getItem('mainpage') || '{}')

//   // Get current route page name
//   const routePageName = route.params.page_name || null
//   //console.log('Creating page:', routePageName)

//   const payload = {
//     title: form.value.title,
//     website_name: websiteObj?.name,
//     route_page_name: routePageName,
//     main_page_name: mainPage?.name,
//     field_value: { ...form.value },
//   }
//   //console.log('Submitting 1 payload:', payload)
//   fetch('/api/method/ecommerce.api.post_page_data', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
//     },
//     body: JSON.stringify(payload),
//   })
//   toast
//     .success('Order created successfully')
//     .then((res) => res.json())
//     .then((data) => {
//       console.log('✅ Page created successfully:', data)

//       if (data?.message?.status === 'success') {
//         const newPageId = data.message.data.name

//         //   First navigate to the new page
//         router.push({
//           name: 'WebsitePageEdit',
//           params: { page_name: newPageId },
//         })

//         setTimeout(() => {
//           window.location.reload()
//         }, 100) // 100ms is usually enough, adjust if needed
//       }
//     })
//     .catch((err) => {
//       console.error('❌ API Error:', err)
//     })
// }
function deepCopy(obj) {
  return JSON.parse(JSON.stringify(obj))
}
function handleClick({ navigateAfterSave = true } = {}) {
  const token = localStorage.getItem('access_token') || ''
  const routePageName = route.params.page_name || null
  let mainPage = {}
  let currentWebsite = websiteObj.value
  try {
    mainPage = JSON.parse(localStorage.getItem('mainpage') || '{}')
    currentWebsite =
      JSON.parse(localStorage.getItem('selectedWebsite') || '{}') ||
      currentWebsite
  } catch {
    // The explicit route parent remains authoritative if cached state is invalid.
  }

  const parentName =
    String(route.query.parent || '') ||
    mainPage?.name ||
    mainPage?.main_page_name ||
    null

  const payload = {
    title: form.value.title,
    website_name: currentWebsite?.name,
    route_page_name: routePageName,
    main_page_name: parentName,
    field_value: deepCopy(form.value),
    blocks: deepCopy(form.value.header || []),
  }

  // console.log('Submitting payload:', payload)

  return fetch(`${Frappe_URL}/api/method/ecommerce.api.post_page_data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then(async (data) => {
      if (data?.message?.status === 'success') {
        toast.success('Page created successfully ✅')
        clearUnsavedChanges()

        const newPageId = data.message.data.name
        window.dispatchEvent(
          new CustomEvent('ecommerce:website-updated', {
            detail: { pageName: newPageId, action: 'created' },
          }),
        )

        if (navigateAfterSave) {
          await router.push({
            name: 'WebsitePageEdit',
            params: { page_name: newPageId },
          })
        }
        return newPageId
      } else {
        toast.error(data?.message || 'Failed to create page ❌')
        return null
      }
    })
    .catch((err) => {
      toast.error('API Error ❌')
      console.error('❌ API Error:', err)
      return null
    })
}

// function handleClick() {
//   // Website selection from sessionStorage
//   const websiteJson = sessionStorage.getItem('selectedWebsite')
//   const websiteObj = websiteJson ? JSON.parse(websiteJson) : null
//   const mainPage = JSON.parse(sessionStorage.getItem('mainpage') || '{}')

//   const routePageName = route.params.page_name || null

//   const payload = {
//     title: form.value.title,
//     website_name: websiteObj?.name,
//     route_page_name: routePageName,
//     main_page_name: mainPage?.name,
//     // field_value: { ...form.value },
//     field_value: deepCopy(form.value),
//     blocks: deepCopy(form.value.header || []),
//   }

//   console.log('Submitting payload:', payload)

//   fetch('/api/method/ecommerce.api.post_page_data', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
//     },
//     body: JSON.stringify(payload),
//   })
//     .then((res) => res.json())
//     .then((data) => {
//      // console.log('✅ Page created successfully:', data)

//       if (data?.message?.status === 'success') {
//         toast.success('Page created successfully ✅')

//         const newPageId = data.message.data.name

//         router.push({
//           name: 'WebsitePageEdit',
//           params: { page_name: newPageId },
//         })

//         // setTimeout(() => {
//         //   window.location.reload()
//         // }, 100)
//       } else {
//         toast.error(data?.message || 'Failed to create page ❌')
//       }
//     })
//     .catch((err) => {
//       toast.error('API Error ❌')
//       console.error('❌ API Error:', err)
//     })
// }

// Fetch pages and find selected page
const fetchPages = async () => {
  const token = localStorage.getItem('access_token') || ''
  try {
    const res = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_pages`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )
    const result = await res.json()
    //  // console.log('Fetched pages:', result)
    pages.value = result?.message?.data || []

    selectedPage.value =
      pages.value.find((p) => p.name === pageName.value) || null

    if (selectedPage.value?.data_json && isFromNewPage.value) {
      try {
        const templateConfig = JSON.parse(selectedPage.value.data_json)
        parsedDataJson.value = await applyParentLayout(templateConfig, token)
      } catch (e) {
        console.error('Unable to load the parent page layout:', e)
        parsedDataJson.value = null
      }
    } else {
      parsedDataJson.value = null
    }
  } catch (err) {
    console.error('Error fetching pages:', err)
  }
}

// Load breadcrumb initially
onMounted(loadBreadcrumbFromSession)
watch(() => route.fullPath, loadBreadcrumbFromSession)

onMounted(() => {
  fetchPages()
  fetchdata()
  window.addEventListener('ecommerce:page-template-changed', refreshChangedPage)
})

async function refreshChangedPage(event) {
  if (
    String(event?.detail?.pageName || '') ===
    String(route.params.page_name || '')
  ) {
    await fetchdata()
  }
}

onBeforeUnmount(() => {
  window.removeEventListener('ecommerce:page-template-changed', refreshChangedPage)
})

watch(() => route.params.page_name, fetchPages)
watch(() => route.params.page_name, fetchdata, { immediate: true })
</script>
