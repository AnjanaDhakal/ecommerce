<template>
  <div v-if="pageData" class="flex h-full min-h-0 flex-col">
    <!-- Page Title -->
    <div class="z-30 shrink-0 bg-white shadow-sm">
      <TextField
        v-model="pageTitle"
        label="Name"
        placeholder="Enter page title"
      />
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="min-h-0 flex-1 overflow-y-auto">
      <PageLoader />
    </div>

    <!-- Only show DynamicForm if template exists -->
    <div v-else class="min-h-0 flex-1 overflow-hidden">
      <template v-if="hasTemplate">
        <DynamicForm :config="formConfig" :form="formState" />
      </template>
      <template v-else>
        <p class="text-gray-500 italic">No template available</p>
      </template>
    </div>

    <!-- Fixed Footer with Breadcrumb + Actions -->
    <div
      class="z-40 flex w-full shrink-0 items-center justify-between border-t border-gray-200 bg-white px-4 py-2"
    >
      <!-- Breadcrumb -->
      <p class="text-sm text-gray-500 truncate">{{ breadcrumb }}</p>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <span
          v-if="hasUnsavedChanges"
          class="self-center rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800"
        >
          Unsaved changes
        </span>
        <button
          type="button"
          @click="handlePreview"
          :disabled="previewLoading"
          class="px-3 py-1.5 bg-gray-100 text-gray-800 rounded shadow hover:bg-gray-200 text-sm disabled:opacity-50"
        >
          {{ previewLoading ? 'Loading...' : 'Preview' }}
        </button>
        <button
          @click="handleUpdate"
          :disabled="loadings"
          class="px-3 py-1.5 bg-gray-400 text-white rounded shadow hover:bg-gray-500 text-sm disabled:opacity-50"
        >
          <span v-if="loadings">Saving...</span>
          <span v-else>Save</span>
        </button>
        <button
          @click="handleSaveAndPublish"
          :disabled="loadings"
          class="px-3 py-1.5 bg-green-600 text-white rounded shadow hover:bg-green-700 text-sm disabled:opacity-50"
        >
          Save and Publish
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  watch,
  nextTick,
  onMounted,
  onBeforeUnmount,
  toRaw,
} from 'vue'
import { useToast } from 'vue-toastification'
import DynamicForm from '../webcomponents/DynamicForm.vue'
import TextField from '../webcomponents/TextField.vue'
import PageLoader from '../components/PageLoader.vue'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'

const props = defineProps({
  pageData: { type: Object, default: null },
  breadcrumb: { type: String, default: '' },
})

//console.log('PageDataDetails props.pageData:', props.pageData)
const toast = useToast()
const formConfig = ref(null)
const formState = ref({})
const pageTitle = ref('')
const loading = ref(false)
const previewLoading = ref(false)
const { hasUnsavedChanges, setUnsavedChanges, clearUnsavedChanges } =
  useUnsavedChanges()
const savedSnapshot = ref('')
const isInitializing = ref(true)

function currentSnapshot() {
  return JSON.stringify({
    title: pageTitle.value || '',
    field_value: JSON.parse(JSON.stringify(toRaw(formState.value || {}))),
  })
}

function markCurrentStateSaved() {
  savedSnapshot.value = currentSnapshot()
  clearUnsavedChanges()
}

async function restoreSavedState() {
  if (!savedSnapshot.value) return
  isInitializing.value = true
  const saved = JSON.parse(savedSnapshot.value)
  pageTitle.value = saved.title
  formState.value = saved.field_value
  await nextTick()
  isInitializing.value = false
}

function handleBeforeUnload(event) {
  if (!hasUnsavedChanges.value) return
  event.preventDefault()
  event.returnValue = ''
}

onMounted(() => window.addEventListener('beforeunload', handleBeforeUnload))
onBeforeUnmount(() =>
  window.removeEventListener('beforeunload', handleBeforeUnload),
)

const handlePreview = async () => {
  const pageName = props.pageData?.name
  if (!pageName) {
    toast.error('Page preview is not available')
    return
  }

  const previewWindow = window.open('', '_blank')
  if (!previewWindow) {
    toast.error('Please allow pop-ups to open the preview')
    return
  }

  previewWindow.opener = null
  previewWindow.document.write(
    '<!doctype html><title>Loading preview...</title><p style="font-family:sans-serif;padding:24px">Loading preview...</p>',
  )
  previewWindow.document.close()

  previewLoading.value = true

  try {
    const token = localStorage.getItem('access_token') || ''
    const plainFieldValue = JSON.parse(JSON.stringify(toRaw(formState.value)))
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.update_publish_data`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
        },
        body: JSON.stringify({
          name: pageName,
          title: pageTitle.value || props.pageData?.title,
          field_value: plainFieldValue,
          preview_only: true,
        }),
      },
    )
    const responseData = await response.json()
    const result = responseData?.message

    if (!response.ok || result?.status !== 'success') {
      throw new Error(result?.message || 'Unable to load page preview')
    }

    const previewHtml = result?.data?.preview || result?.data?.block_render
    if (!previewHtml) {
      throw new Error('No rendered preview is available')
    }

    const previewUrl = result?.data?.preview_url
    if (!previewUrl) throw new Error('No preview URL is available')

    const previewKey = `ecommerce-page-preview-${Date.now()}-${Math.random().toString(36).slice(2)}`
    localStorage.setItem(previewKey, previewHtml)
    const destination = new URL(previewUrl, window.location.origin)
    destination.searchParams.set('preview_key', previewKey)
    previewWindow.location.replace(destination.toString())
  } catch (error) {
    previewWindow.close()
    toast.error(error?.message || 'Unable to load page preview')
  } finally {
    previewLoading.value = false
  }
}

// -------------------
// Build payload + update
// -------------------

const loadings = ref(false)

// function handleUpdate() {
//   console.log('Updating page:', props.pageData?.name)

//   const payload = {
//     name: props.pageData?.name,
//     title: pageTitle.value || props.pageData?.title,
//     field_value: { ...formState.value }, // full form state
//   }

//   console.log('Submitting payload:', payload)

//   loadings.value = true

//   fetch('/api/method/ecommerce.api.update_page_data', {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
//     },
//     body: JSON.stringify(payload),
//   })
//     .then((r) => r.json())
//     .then((data) => {
//       if (data?.message?.status === 'success') {
//         toast.success(data.message.message || '✅ Page updated successfully')
//       } else {
//         toast.error(data?.message?.message || '❌ Update failed')
//       }
//       console.log('🔔 API Response:', data)
//     })
//     .catch((err) => {
//       toast.error('❌ Update failed')
//       console.error('❌ Update failed:', err)
//     })
//     .finally(() => {
//       loadings.value = false
//     })
// }

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
async function handleUpdate() {
  //  // console.log('Updating page:', props.pageData?.name)
  const token = localStorage.getItem('access_token') || ''
  // Convert reactive state → plain JSON
  const plainFieldValue = JSON.parse(JSON.stringify(toRaw(formState.value)))

  const payload = {
    name: props.pageData?.name,
    title: pageTitle.value || props.pageData?.title,
    field_value: plainFieldValue, // 👈 clean object, no Proxy
  }

  // console.log('Submitting payload:', payload)

  loadings.value = true

  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.update_page_data`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      },
    )
    const data = await response.json()
    if (data?.message?.status === 'success') {
      markCurrentStateSaved()
      toast.success(data.message.message || '✅ Page updated successfully')
      return true
    }
    toast.error(data?.message?.message || '❌ Update failed')
    return false
  } catch (err) {
    toast.error('❌ Update failed')
    console.error('❌ Update failed:', err)
    return false
  } finally {
    loadings.value = false
  }
}

function handleSaveAndPublish() {
  //  //  console.log('Updating page:', props.pageData?.name)
  const token = localStorage.getItem('access_token') || ''
  // ✅ Clean state before sending
  const plainFieldValue = JSON.parse(JSON.stringify(toRaw(formState.value)))

  const payload = {
    name: props.pageData?.name,
    title: pageTitle.value || props.pageData?.title,
    field_value: plainFieldValue,
  }

  // console.log('Submitting payload 2:', payload)

  loadings.value = true

  fetch(`${Frappe_URL}/api/method/ecommerce.api.update_publish_data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  })
    .then((r) => r.json())
    .then((data) => {
      if (data?.message?.status === 'success') {
        markCurrentStateSaved()
        toast.success(data.message.message || '✅ Page updated successfully')
      } else {
        toast.error(data?.message?.message || '❌ Update failed')
      }
      //  //  console.log('🔔 API Response:', data)
    })
    .catch((err) => {
      toast.error('❌ Update failed')
      console.error('❌ Update failed:', err)
    })
    .finally(() => {
      loadings.value = false
    })
}

// -------------------
// Watch pageData and init form
// -------------------
watch(
  () => props.pageData,
  (newVal) => {
    if (!newVal) return
    isInitializing.value = true
    clearUnsavedChanges()
    loading.value = true

    // set page title
    pageTitle.value = newVal.page || newVal.title || newVal.name || ''

    const rd = newVal.render_data
    if (!rd) {
      formConfig.value = null
      formState.value = {}
      loading.value = false
      nextTick(() => {
        markCurrentStateSaved()
        isInitializing.value = false
      })
      return
    }

    // Build config
    formConfig.value = {
      title: rd.title,
      tabs: rd.tabs || null,
      sections: rd.sections || null,
      fields: rd.fields || null,
      starter_content: rd.starter_content || null,
    }

    // Flatten all fields
    let allFields = []
    if (rd.fields) allFields = allFields.concat(rd.fields)
    if (rd.sections) {
      rd.sections.forEach((section) => {
        if (section.fields) allFields = allFields.concat(section.fields)
      })
    }
    if (rd.tabs) {
      rd.tabs.forEach((tab) => {
        tab.sections?.forEach((section) => {
          if (section.fields) allFields = allFields.concat(section.fields)
        })
      })
    }

    // Set state
    const savedValues =
      typeof newVal.field_value === 'string'
        ? JSON.parse(newVal.field_value)
        : newVal.field_value || {}

    const state = {}
    allFields.forEach((f) => {
      const key = f.model || f.name
      if (!key) return
      if (savedValues[key] !== undefined) state[key] = savedValues[key]
      else if (f.value !== undefined) state[key] = f.value
      else if (f.default !== undefined) state[key] = f.default
      else state[key] = f.type === 'toggle' ? false : ''
    })

    formState.value = state
    loading.value = false
    nextTick(() => {
      markCurrentStateSaved()
      isInitializing.value = false
    })
  },
  { immediate: true },
)

watch(
  [pageTitle, formState],
  () => {
    if (isInitializing.value || !savedSnapshot.value) return
    const isDirty = currentSnapshot() !== savedSnapshot.value
    setUnsavedChanges(isDirty, {
      save: handleUpdate,
      discard: restoreSavedState,
    })
  },
  { deep: true },
)

// -------------------
// Template existence
// -------------------
const hasTemplate = computed(() => {
  const rd = props.pageData?.render_data
  if (!rd) return false
  if (Array.isArray(rd.fields) && rd.fields.length > 0) return true
  if (rd.sections?.some((s) => s.fields?.length)) return true
  if (rd.tabs?.some((t) => t.sections?.some((s) => s.fields?.length)))
    return true
  return false
})
</script>
