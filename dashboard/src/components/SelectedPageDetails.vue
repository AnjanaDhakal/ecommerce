<template>
  <div class="flex h-full min-h-0 flex-col">
    <div class="z-30 shrink-0 bg-white shadow-sm">
      <TextField
        v-model="form.title"
        label="Name"
        placeholder="Enter page title"
        id="page-title"
      />
    </div>

    <div class="min-h-0 flex-1 overflow-hidden">
      <DynamicForm :config="parsedDataJson" :form="form" />
    </div>

    <div
      class="z-40 flex w-full shrink-0 items-center justify-between border-t border-gray-200 bg-white px-4 py-2"
    >
      <!-- Breadcrumb on the left -->
      <p class="text-sm text-gray-500 truncate">{{ breadcrumb }}</p>

      <!-- Submit Button on the right -->
      <div class="flex gap-2">
        <span
          v-if="hasUnsavedChanges"
          class="self-center rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800"
        >
          Unsaved changes
        </span>
        <button
          type="button"
          @click="previewPage"
          :disabled="previewLoading"
          class="px-3 py-1.5 bg-gray-100 text-gray-800 rounded shadow hover:bg-gray-200 text-sm disabled:cursor-not-allowed disabled:opacity-50"
        >
          {{ previewLoading ? 'Preparing preview...' : 'Preview' }}
        </button>
        <button
          @click="savePage()"
          :disabled="previewLoading"
          class="px-3 py-1.5 bg-green-600 text-white rounded shadow hover:bg-green-700 text-sm"
        >
          Save
        </button>
        <!-- <button
         @click="handleClickandPublish"
          class="px-3 py-1.5 bg-green-600 text-white rounded shadow hover:bg-green-700 text-sm"
        >
          Save and Publish A
        </button> -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { watch, ref, onMounted, onBeforeUnmount, nextTick, toRaw } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import DynamicForm from '../webcomponents/DynamicForm.vue'
import TextField from '../webcomponents/TextField.vue'
import { useUnsavedChanges } from '../composables/useUnsavedChanges'

const props = defineProps({
  form: {
    type: Object, // Expect a reactive object (e.g., ref({}))
    required: true,
  },
  selectedPage: Object,
  isFromNewPage: Boolean,
  parsedDataJson: Object,
  handleClick: Function,
  handleClickandPublish: Function,
  breadcrumb: String,
  main_page_name: [String, Number, null],
})

const router = useRouter()
const toast = useToast()
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const previewLoading = ref(false)

function deepCopy(value) {
  return JSON.parse(JSON.stringify(value))
}

function getAllFields(config) {
  const fields = []

  function visit(node) {
    if (!node || typeof node !== 'object') return
    if (Array.isArray(node)) {
      node.forEach(visit)
      return
    }

    if (node.type && (node.name || node.model || node.key)) fields.push(node)
    visit(node.fields)
    visit(node.sections)
    visit(node.tabs)
  }

  visit(config)
  return fields
}

const mainPageData = ref({})
const { hasUnsavedChanges, setUnsavedChanges, clearUnsavedChanges } =
  useUnsavedChanges()
const savedSnapshot = ref('')
const isInitializing = ref(true)
const pageCreated = ref(false)

function currentSnapshot() {
  return JSON.stringify(JSON.parse(JSON.stringify(toRaw(props.form || {}))))
}

function markCurrentStateSaved() {
  savedSnapshot.value = currentSnapshot()
  clearUnsavedChanges()
}

async function restoreSavedState() {
  if (!savedSnapshot.value) return
  isInitializing.value = true
  const saved = JSON.parse(savedSnapshot.value)
  Object.keys(props.form).forEach((key) => delete props.form[key])
  Object.assign(props.form, saved)
  await nextTick()
  isInitializing.value = false
}

async function savePage(navigateAfterSave = true) {
  const pageName = await props.handleClick?.({ navigateAfterSave })
  if (pageName) {
    pageCreated.value = true
    markCurrentStateSaved()
  }
  return pageName || null
}

async function previewPage() {
  const previewWindow = window.open('', '_blank')
  if (!previewWindow) {
    toast.error('Please allow pop-ups to open the preview')
    return
  }

  previewWindow.opener = null
  previewWindow.document.write(
    '<!doctype html><title>Preparing preview...</title><p style="font-family:sans-serif;padding:24px">Preparing your page preview...</p>',
  )
  previewWindow.document.close()
  previewLoading.value = true

  try {
    const title = props.form.title
    const fieldValue = deepCopy(toRaw(props.form))

    // A preview needs a page identifier for permission checks and template
    // resolution. Create the draft once, then open its rendered preview.
    const pageName = await savePage(false)
    if (!pageName) throw new Error('Unable to prepare the page preview')

    // The draft already exists at this point. Move to its real editor route
    // immediately so a later preview error cannot leave a hidden page behind.
    await router.replace({
      name: 'WebsitePageEdit',
      params: { page_name: pageName },
    })

    const token = localStorage.getItem('access_token') || ''
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
          title,
          field_value: fieldValue,
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
    const previewUrl = result?.data?.preview_url
    if (!previewHtml || !previewUrl) {
      throw new Error('No rendered preview is available')
    }

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

function handleBeforeUnload(event) {
  if (!hasUnsavedChanges.value) return
  event.preventDefault()
  event.returnValue = ''
}

onMounted(() => {
  const savedPage = localStorage.getItem('mainpage')
  if (savedPage) {
    try {
      mainPageData.value = JSON.parse(savedPage)
      // console.log('Loaded save data:', savedPage)
    } catch (e) {
      console.error('Error parsing mainpage:', e)
    }
  }
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onBeforeUnmount(() =>
  window.removeEventListener('beforeunload', handleBeforeUnload),
)

// Watch for changes on parsedDataJson or isFromNewPage to initialize form for new pages
watch(
  () => [props.parsedDataJson, props.isFromNewPage],
  ([config, isNew]) => {
    if (!config) return

    if (isNew) {
      isInitializing.value = true
      pageCreated.value = false
      clearUnsavedChanges()
      // Start from the template's editable sample content, then fill any
      // remaining fields from their schema defaults.
      const allFields = getAllFields(config)
      const newForm = deepCopy(config.starter_content || {})

      allFields.forEach((field) => {
        const key = field.model || field.name || field.key
        if (key && newForm[key] === undefined) {
          if (field.type === 'toggle') {
            newForm[key] =
              field.default !== undefined ? deepCopy(field.default) : false
          } else if (field.value !== undefined) {
            newForm[key] = deepCopy(field.value)
          } else if (field.default !== undefined) {
            newForm[key] = deepCopy(field.default)
          } else if (field.type === 'draggable') {
            newForm[key] = []
          } else {
            newForm[key] = ''
          }
        }
      })

      // Use the selected template name as a useful, editable page title.
      if (!newForm.title) {
        newForm.title =
          config.default_page_title ||
          props.selectedPage?.page_name ||
          'Untitled page'
      }

      // Replace entire form object reactively
      Object.keys(props.form).forEach((k) => delete props.form[k]) // clear old keys
      Object.assign(props.form, newForm)
      nextTick(() => {
        savedSnapshot.value = currentSnapshot()
        isInitializing.value = false
        setUnsavedChanges(true, {
          save: () => savePage(false),
          discard: restoreSavedState,
        })
      })
    } else {
      // For existing page, keep form as is (likely loaded from outside)
      // You can optionally populate the form here if you want, depending on your flow
    }
  },
  { immediate: true },
)

watch(
  () => props.form,
  () => {
    if (isInitializing.value || !savedSnapshot.value) return
    const isDirty =
      !pageCreated.value || currentSnapshot() !== savedSnapshot.value
    setUnsavedChanges(isDirty, {
      save: () => savePage(false),
      discard: restoreSavedState,
    })
  },
  { deep: true },
)
</script>
