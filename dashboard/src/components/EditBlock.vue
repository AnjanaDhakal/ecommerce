<template>
  <Sidebar
    :modelValue="show"
    @update:modelValue="() => emit('close')"
    title="Edit section"
    width="min(1400px, 96vw)"
  >
    <div v-if="localBlock.name" class="section-editor-shell flex h-full flex-col">
      <div class="flex flex-row justify-between items-center gap-3 border-b pb-3 mb-3 shrink-0">
        <div>
          <h2 class="text-lg font-semibold">{{ friendlySectionName(localBlock.block_name) }}</h2>
          <p class="mt-0.5 text-xs text-gray-500">Edit the section while previewing changes live.</p>
        </div>
        <button
          v-if="!editorPanelVisible"
          type="button"
          class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-semibold text-gray-700 transition-colors hover:border-green-500 hover:text-green-700"
          @click="openContentPanel"
        >
          <span class="material-symbols-outlined text-lg" aria-hidden="true">tune</span>
          Show settings
        </button>
      </div>

      <div
        class="grid min-h-0 flex-1 gap-5"
        :class="editorPanelVisible
          ? 'lg:grid-cols-[minmax(0,1.15fr)_minmax(430px,.85fr)]'
          : 'grid-cols-1'"
      >
        <section class="flex w-full min-h-0 max-h-[calc(100vh-10rem)] self-start flex-col overflow-hidden rounded-xl border border-gray-200 bg-gray-50 p-3 lg:sticky lg:top-0">
          <div class="mb-3 flex shrink-0 items-center justify-between gap-3">
            <div>
              <h3 class="font-semibold text-gray-900">Live preview</h3>
              <p class="text-xs text-gray-500">
                {{ hasLinkedProductContent
                  ? 'Edit highlighted section text here. Product details are managed in Ecommerce Products.'
                  : 'Edit highlighted text directly. Click an image to replace it.' }}
              </p>
            </div>
            <span v-if="previewLoading || inlineImageUploading" class="text-xs text-gray-400">
              {{ inlineImageUploading ? 'Uploading image…' : 'Updating…' }}
            </span>
          </div>
          <div
            ref="previewViewport"
            class="min-h-0 flex-1 overflow-y-auto overflow-x-hidden rounded-lg border border-gray-200 bg-white"
          >
            <component :is="'style'" v-if="previewStyle">{{ previewStyle }}</component>
            <div
              v-if="previewHtml"
              ref="previewContainer"
              class="visual-block-preview min-h-[420px] w-full bg-white"
              :class="previewBlockClasses"
              :style="previewCanvasStyle"
              @click="handlePreviewClick"
              @focusin="handlePreviewFocusIn"
              @focusout="handlePreviewFocusOut"
              @input="handlePreviewInput"
              @keydown="handlePreviewKeydown"
              v-html="previewHtml"
            />
            <div
              v-else-if="!previewLoading && !previewError"
              class="grid min-h-[420px] place-items-center text-sm text-gray-400"
            >
              Start entering content to see this section.
            </div>
            <input
              ref="inlineFileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleInlineFileChange"
            />
          </div>
          <p v-if="previewError" class="mt-2 text-xs text-red-600">{{ previewError }}</p>
        </section>

        <section
          v-if="editorPanelVisible"
          class="flex w-full min-h-0 max-h-[calc(100vh-10rem)] self-start flex-col overflow-hidden rounded-xl border border-gray-200 bg-white lg:sticky lg:top-0"
        >

      <div role="tablist" aria-label="Section editor" class="flex h-12 shrink-0 items-center border-b border-gray-200 bg-white px-3">
        <button
          type="button"
          role="tab"
          :aria-selected="activeEditorTab === 'content'"
          class="relative flex h-12 items-center px-4 text-sm font-medium transition-colors after:absolute after:inset-x-3 after:bottom-0 after:h-0.5"
          :class="activeEditorTab === 'content'
            ? 'text-green-700 after:bg-green-600'
            : 'text-gray-500 after:bg-transparent hover:text-gray-900'"
          @click="openContentPanel"
        >
          Content
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="activeEditorTab === 'style'"
          class="relative flex h-12 items-center px-4 text-sm font-medium transition-colors after:absolute after:inset-x-3 after:bottom-0 after:h-0.5"
          :class="activeEditorTab === 'style'
            ? 'text-green-700 after:bg-green-600'
            : 'text-gray-500 after:bg-transparent hover:text-gray-900'"
          @click="openDesignPanel"
        >
          Advance Design
        </button>
        <button
          type="button"
          class="ml-auto inline-flex h-8 w-8 items-center justify-center rounded-md text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-900"
          title="Hide settings panel"
          aria-label="Hide settings panel"
          @click="closeEditorPanel"
        >
          <span class="material-symbols-outlined text-xl" aria-hidden="true">close</span>
        </button>
      </div>

      <div ref="settingsScrollContainer" class="flex-1 overflow-y-auto p-5">
        <div
          v-if="activeEditorTab === 'style'"
          class="figma-style-panel -m-5 bg-white"
        >
          <div class="mb-4">
            <div class="flex items-center justify-between gap-3">
              <h3 class="font-semibold text-gray-900">
                {{ styleTargetLabel }}
              </h3>
              <button
                v-if="selectedStyleProduct || selectedStyleElement"
                type="button"
                class="text-xs font-medium text-green-700 hover:text-green-900"
                @click="selectedStyleElement ? returnToProductCardStyle() : clearStyleTarget()"
              >
                {{ selectedStyleElement ? 'Back to card style' : 'Design whole section' }}
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500">
              Leave a value empty to use the
              {{ selectedStyleProduct
                ? 'product card'
                : selectedStyleElement
                  ? selectedStyleElement.label
                  : 'section' }}'s original design.
            </p>
          </div>

          <div
            v-if="selectedStyleProduct"
            class="mb-4 flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-white p-3"
          >
            <label class="flex items-center gap-2 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                :checked="productSettings[String(selectedStyleProduct.name)]?.show_add_to_cart !== false"
                @change="toggleProductAddToCart({
                  product: selectedStyleProduct,
                  show: $event.target.checked,
                })"
              />
              Show Add to Cart
            </label>
            <button
              v-if="productSettings[String(selectedStyleProduct.name)]?.show_add_to_cart !== false"
              type="button"
              class="ml-auto rounded-lg bg-gray-900 px-3 py-2 text-xs font-semibold text-white hover:bg-gray-700"
              @click="editProductActionStyle({
                product: selectedStyleProduct,
                key: 'add_to_cart',
                label: 'Add to Cart',
              })"
            >
              Button Style
            </button>
          </div>

          <div class="grid grid-cols-2 gap-0">
            <label class="col-span-2 text-sm font-medium text-gray-700">
              Background
              <select
                v-model="activeStyle.background_type"
                class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
                @change="handleBackgroundTypeChange"
              >
                <option value="">Use section default</option>
                <option value="solid">Solid color</option>
                <option value="gradient">Gradient</option>
              </select>
            </label>

            <label
              v-if="activeStyle.background_type === 'solid'"
              class="col-span-2 text-sm font-medium text-gray-700"
            >
              Background source
              <select
                v-model="activeStyle.background_theme"
                class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
              >
                <option value="">Custom color</option>
                <option v-for="option in themeColorOptions" :key="`background-${option.value}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <div v-if="!activeStyle.background_theme" class="mt-2 flex items-center gap-2">
                <input
                  type="color"
                  :value="activeStyle.background_color || '#ffffff'"
                  class="h-10 w-12 cursor-pointer rounded border border-gray-300 bg-white p-1"
                  @input="activeStyle.background_color = $event.target.value"
                />
                <input
                  v-model.trim="activeStyle.background_color"
                  type="text"
                  placeholder="Default"
                  class="h-10 min-w-0 flex-1 rounded border border-gray-300 px-3"
                />
                <button
                  v-if="activeStyle.background_color"
                  type="button"
                  class="text-xs text-gray-500 hover:text-red-600"
                  @click="activeStyle.background_color = ''"
                >
                  Clear
                </button>
              </div>
            </label>

            <template v-if="activeStyle.background_type === 'gradient'">
              <label class="text-sm font-medium text-gray-700">
                Gradient start source
                <select
                  v-model="activeStyle.gradient_from_theme"
                  class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
                >
                  <option value="">Custom color</option>
                  <option v-for="option in themeColorOptions" :key="`gradient-from-${option.value}`" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <div v-if="!activeStyle.gradient_from_theme" class="mt-2 flex items-center gap-2">
                  <input
                    type="color"
                    :value="activeStyle.gradient_from || '#7e51a2'"
                    class="h-10 w-12 cursor-pointer rounded border border-gray-300 bg-white p-1"
                    @input="activeStyle.gradient_from = $event.target.value"
                  />
                  <input
                    v-model.trim="activeStyle.gradient_from"
                    type="text"
                    placeholder="#7e51a2"
                    class="h-10 min-w-0 flex-1 rounded border border-gray-300 px-3"
                  />
                </div>
              </label>

              <label class="text-sm font-medium text-gray-700">
                Gradient end source
                <select
                  v-model="activeStyle.gradient_to_theme"
                  class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
                >
                  <option value="">Custom color</option>
                  <option v-for="option in themeColorOptions" :key="`gradient-to-${option.value}`" :value="option.value">
                    {{ option.label }}
                  </option>
                </select>
                <div v-if="!activeStyle.gradient_to_theme" class="mt-2 flex items-center gap-2">
                  <input
                    type="color"
                    :value="activeStyle.gradient_to || '#d62b90'"
                    class="h-10 w-12 cursor-pointer rounded border border-gray-300 bg-white p-1"
                    @input="activeStyle.gradient_to = $event.target.value"
                  />
                  <input
                    v-model.trim="activeStyle.gradient_to"
                    type="text"
                    placeholder="#d62b90"
                    class="h-10 min-w-0 flex-1 rounded border border-gray-300 px-3"
                  />
                </div>
              </label>

              <label class="col-span-2 text-sm font-medium text-gray-700">
                Gradient Direction
                <select
                  v-model="activeStyle.gradient_direction"
                  class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
                >
                  <option value="to right">Left to right</option>
                  <option value="to left">Right to left</option>
                  <option value="to bottom">Top to bottom</option>
                  <option value="to top">Bottom to top</option>
                  <option value="to bottom right">Top-left to bottom-right</option>
                  <option value="to bottom left">Top-right to bottom-left</option>
                </select>
              </label>
            </template>

            <label class="text-sm font-medium text-gray-700">
              Text source
              <select
                v-model="activeStyle.text_theme"
                class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
              >
                <option value="">Custom color</option>
                <option v-for="option in themeColorOptions" :key="`text-${option.value}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <div v-if="!activeStyle.text_theme" class="mt-2 flex items-center gap-2">
                <input
                  type="color"
                  :value="activeStyle.text_color || '#111827'"
                  class="h-10 w-12 cursor-pointer rounded border border-gray-300 bg-white p-1"
                  @input="activeStyle.text_color = $event.target.value"
                />
                <input
                  v-model.trim="activeStyle.text_color"
                  type="text"
                  placeholder="Default"
                  class="h-10 min-w-0 flex-1 rounded border border-gray-300 px-3"
                />
                <button
                  v-if="activeStyle.text_color"
                  type="button"
                  class="text-xs text-gray-500 hover:text-red-600"
                  @click="activeStyle.text_color = ''"
                >
                  Clear
                </button>
              </div>
            </label>

            <label class="col-span-2 text-sm font-medium text-gray-700">
              Action / button source
              <select
                v-model="actionSourceValue"
                class="mt-1 h-10 w-full rounded border border-gray-300 bg-white px-3"
              >
                <option value="default">Website default</option>
                <option value="custom">Custom color</option>
                <option v-for="option in themeColorOptions" :key="`action-${option.value}`" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <div v-if="actionSourceValue === 'custom'" class="mt-2 flex items-center gap-2">
                <input
                  type="color"
                  :value="activeStyle.action_color || '#111827'"
                  class="h-10 w-12 cursor-pointer rounded border border-gray-300 bg-white p-1"
                  @input="activeStyle.action_color = $event.target.value"
                />
                <input
                  v-model.trim="activeStyle.action_color"
                  type="text"
                  placeholder="Additional 1 when set, otherwise #111827"
                  class="h-10 min-w-0 flex-1 rounded border border-gray-300 px-3"
                />
                <button
                  v-if="activeStyle.action_color"
                  type="button"
                  class="text-xs text-gray-500 hover:text-red-600"
                  @click="activeStyle.action_color = ''"
                >
                  Use default
                </button>
              </div>
            </label>

            <label class="text-sm font-medium text-gray-700">
              Text Size
              <input
                v-model.trim="activeStyle.font_size"
                type="text"
                placeholder="Default, e.g. 16px"
                class="mt-1 h-10 w-full rounded border border-gray-300 px-3"
              />
            </label>

            <fieldset class="col-span-2">
              <legend class="text-sm font-medium text-gray-700">Margin</legend>
              <label class="mt-1 block text-xs text-gray-500">
                All sides
                <input
                  v-model.trim="activeStyle.margin"
                  type="text"
                  placeholder="Default, e.g. 16px"
                  class="mt-1 h-10 w-full rounded border border-gray-300 px-3 text-sm text-gray-900"
                />
              </label>
              <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
                <label
                  v-for="side in spacingSides"
                  :key="`margin-${side.key}`"
                  class="text-xs text-gray-500"
                >
                  {{ side.label }}
                  <input
                    v-model.trim="activeStyle[`margin_${side.key}`]"
                    type="text"
                    placeholder="Default"
                    class="mt-1 h-10 w-full rounded border border-gray-300 px-2 text-sm text-gray-900"
                  />
                </label>
              </div>
            </fieldset>

            <fieldset class="col-span-2">
              <legend class="text-sm font-medium text-gray-700">Padding</legend>
              <label class="mt-1 block text-xs text-gray-500">
                All sides
                <input
                  v-model.trim="activeStyle.padding"
                  type="text"
                  placeholder="Default, e.g. 12px"
                  class="mt-1 h-10 w-full rounded border border-gray-300 px-3 text-sm text-gray-900"
                />
              </label>
              <div class="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
                <label
                  v-for="side in spacingSides"
                  :key="`padding-${side.key}`"
                  class="text-xs text-gray-500"
                >
                  {{ side.label }}
                  <input
                    v-model.trim="activeStyle[`padding_${side.key}`]"
                    type="text"
                    placeholder="Default"
                    class="mt-1 h-10 w-full rounded border border-gray-300 px-2 text-sm text-gray-900"
                  />
                </label>
              </div>
            </fieldset>
          </div>
        </div>

        <DynamicForm
          v-if="activeEditorTab === 'content' && dynamicConfig"
          :config="dynamicConfig"
          :form="form"
          :product-settings="productSettings"
          :focused-field-key="focusedFieldKey"
          :focused-repeater-item="focusedRepeaterItem"
          @edit-product-style="editProductStyle"
          @edit-product-action-style="editProductActionStyle"
          @toggle-product-add-to-cart="toggleProductAddToCart"
        />
        <p
          v-else-if="activeEditorTab === 'content' && !dynamicConfig"
          class="py-8 text-center text-sm text-gray-500"
        >
          This block has no editable content fields.
        </p>
        <p v-if="validationError" class="mt-3 text-sm text-red-600">
          {{ validationError }}
        </p>
      </div>

      <div class="flex shrink-0 justify-end border-t border-gray-200 bg-white px-4 py-2.5">
        <button
          class="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-gray-700"
          @click="save"
        >
          {{ activeEditorTab === 'style' ? 'Apply design' : 'Save changes' }}
        </button>
      </div>

        </section>
      </div>
      <div v-if="!editorPanelVisible" class="fixed bottom-5 right-[3vw] z-[30] flex justify-end gap-2">
        <button
          class="rounded-lg bg-gray-900 px-6 py-3 text-sm font-semibold text-white shadow-xl ring-1 ring-white/70 transition-colors hover:bg-gray-700"
          @click="save"
        >
          Save changes
        </button>
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import { ref, watch, computed, onBeforeUnmount, nextTick } from "vue"
import { useRoute } from "vue-router"
import Sidebar from "./Sidebar.vue"
import DynamicForm from "../webcomponents/DynamicForm.vue"

const props = defineProps({
  block: { type: Object, required: true },
  show: { type: Boolean, default: false }
})
const emit = defineEmits(["update", "close"])

function friendlySectionName(name) {
  return {
    'Navbar 1': 'Contact bar',
    'Navbar 2': 'Main navigation',
    'Product Card': 'Products',
    'Image Gallery': 'Image gallery',
  }[name] || name
}

const localBlock = ref({ model: {} })
const form = ref({})
const previewContainer = ref(null)
const previewViewport = ref(null)
const settingsScrollContainer = ref(null)
const inlineFileInput = ref(null)
const previewHtml = ref("")
const previewStyle = ref("")
const previewSampleValues = ref({})
const previewLoading = ref(false)
const previewError = ref("")
const focusedFieldKey = ref("")
const focusedRepeaterItem = ref(null)
const editorPanelOpen = ref(true)
const inlineImageUploading = ref(false)
const pendingInlineFileTarget = ref(null)
let repeaterFocusRequest = 0
let previewTimer = null
let previewRequest = 0
let inlinePreviewEditing = false
let previewResizeObserver = null
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ""
const token = localStorage.getItem("access_token") || ""
const route = useRoute()
const editorPanelVisible = computed(() => editorPanelOpen.value)
const DESKTOP_PREVIEW_WIDTH = 1440
const previewViewportWidth = ref(DESKTOP_PREVIEW_WIDTH)
const previewScale = computed(() =>
  Math.min(1, Math.max(0.1, previewViewportWidth.value / DESKTOP_PREVIEW_WIDTH)),
)

function openContentPanel() {
  activeEditorTab.value = "content"
  editorPanelOpen.value = true
}

async function openDesignPanel() {
  activeEditorTab.value = "style"
  editorPanelOpen.value = true
  await scrollSettingsToTop()
}

async function scrollSettingsToTop() {
  await nextTick()
  if (settingsScrollContainer.value) {
    settingsScrollContainer.value.scrollTop = 0
  }
}

function closeEditorPanel() {
  editorPanelOpen.value = false
  activeEditorTab.value = "content"
  selectedStyleProduct.value = null
  selectedStyleElement.value = null
}

function selectedWebsiteId() {
  try {
    const website = JSON.parse(localStorage.getItem("selectedWebsite") || "{}")
    return website.name || website.website_id || ""
  } catch {
    return ""
  }
}

async function refreshPreview() {
  if (!props.show || !localBlock.value.block_name) return
  const requestId = ++previewRequest
  previewLoading.value = true
  previewError.value = ""
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.preview_builder_block`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          block_name: localBlock.value.block_name,
          website_id: selectedWebsiteId(),
          values: form.value,
        }),
      },
    )
    const body = await response.json()
    const result = body?.message ?? body
    if (!response.ok || result?.status !== "success") {
      throw new Error(result?.message || "Unable to load section preview.")
    }
    if (requestId !== previewRequest) return
    previewHtml.value = result.data?.html || ""
    previewStyle.value = result.data?.style || ""
    previewSampleValues.value = result.data?.sample_values || {}
    await nextTick()
    markEditablePreviewContent()
  } catch (error) {
    if (requestId !== previewRequest) return
    previewError.value = error.message || "Unable to load section preview."
  } finally {
    if (requestId === previewRequest) previewLoading.value = false
  }
}

function schedulePreview() {
  window.clearTimeout(previewTimer)
  if (inlinePreviewEditing) return
  previewTimer = window.setTimeout(refreshPreview, 250)
}

function editablePreviewEntries() {
  const values = { ...previewSampleValues.value }
  Object.entries(form.value || {}).forEach(([key, value]) => {
    const hasValue = Array.isArray(value)
      ? value.length > 0
      : value !== null && value !== undefined && String(value).trim() !== ""
    if (hasValue) {
      values[key] = value
    }
  })
  const inlineTextFieldTypes = new Set([
    "text",
    "normaltext",
    "textarea",
    "email",
    "phone",
    "editor",
  ])
  const inlineTextKeys = new Set(
    builderModelFields()
      .filter((field) => inlineTextFieldTypes.has(field.type))
      .map((field) => field.key || field.name)
      .filter(Boolean),
  )
  const entries = Object.entries(values)
    .filter(([key, value]) =>
      inlineTextKeys.has(key) && ["string", "number"].includes(typeof value),
    )
    .map(([key, value]) => [key, String(value).trim()])
  return entries
    .filter(([, value]) => value.length > 1)
    .sort((left, right) => right[1].length - left[1].length)
}

function builderModelFields() {
  const model = localBlock.value.block_details?.model || {}
  const fields = [...(model.fields || [])]
  ;(model.tabs || []).forEach((tab) => {
    fields.push(...(tab.fields || []))
    ;(tab.sections || []).forEach((section) => fields.push(...(section.fields || [])))
  })
  return fields
}

const hasLinkedProductContent = computed(() =>
  builderModelFields().some((field) => field.type === "product"),
)

function markEditablePreviewContent() {
  const root = previewContainer.value
  if (!root) return
  // Header templates commonly hide their desktop layout until Tailwind's
  // responsive runtime applies `md:block` or `md:flex`. The editor preview is
  // desktop-sized, so make that intended state explicit and reliable.
  root.querySelectorAll(".hidden").forEach((element) => {
    const display = element.classList.contains("md:flex") ? "flex" : "block"
    element.style.setProperty("display", display, "important")
  })
  // Builder templates are stored in the database, so Tailwind cannot discover
  // every arbitrary colour class at build time. Recreate the small set of
  // colour utilities used by those templates so live values remain visible.
  root.querySelectorAll("[class]").forEach((element) => {
    const classes = Array.from(element.classList).map((name) => name.replace(/^md:/, ""))
    const arbitraryValue = (prefix) => {
      const token = classes.find((name) => name.startsWith(`${prefix}-[`) && name.endsWith("]"))
      return token ? token.slice(prefix.length + 2, -1) : ""
    }
    const gradientDirections = {
      "bg-gradient-to-r": "to right",
      "bg-gradient-to-l": "to left",
      "bg-gradient-to-b": "to bottom",
      "bg-gradient-to-t": "to top",
      "bg-gradient-to-br": "to bottom right",
      "bg-gradient-to-bl": "to bottom left",
      "bg-gradient-to-tr": "to top right",
      "bg-gradient-to-tl": "to top left",
    }
    const gradientClass = classes.find((name) => gradientDirections[name])
    const from = arbitraryValue("from")
    const to = arbitraryValue("to")
    if (gradientClass && from && to) {
      element.style.setProperty(
        "background-image",
        `linear-gradient(${gradientDirections[gradientClass]}, ${from}, ${to})`,
        "important",
      )
    }
    const background = arbitraryValue("bg")
    if (background) element.style.setProperty("background-color", background, "important")
    const textColor = arbitraryValue("text")
    if (textColor) element.style.setProperty("color", textColor, "important")
    if (classes.includes("text-white")) element.style.setProperty("color", "#ffffff", "important")
    if (classes.includes("text-black")) element.style.setProperty("color", "#000000", "important")
  })
  if (localBlock.value.block_name === "Product Card") {
    const cards = Array.from(root.querySelectorAll(".ecommerce-product-style"))
    const productGrid = cards[0]?.parentElement
    if (productGrid) {
      const requestedColumns = Number.parseInt(form.value.grid_num, 10)
      const columns = Number.isInteger(requestedColumns) && requestedColumns >= 1
        ? Math.min(requestedColumns, 4)
        : Math.min(Math.max(cards.length, 1), 3)
      productGrid.style.setProperty("display", "grid", "important")
      productGrid.style.setProperty(
        "grid-template-columns",
        `repeat(${columns}, minmax(0, 1fr))`,
        "important",
      )
      productGrid.style.setProperty("gap", "1.5rem", "important")
    }
    cards.forEach((card) => {
      card.style.setProperty("min-width", "0", "important")
      const image = card.querySelector("img")
      if (!image) return
      image.style.setProperty("display", "block", "important")
      image.style.setProperty("width", "100%", "important")
      image.style.setProperty("max-width", "100%", "important")
      image.style.setProperty("height", "18rem", "important")
      image.style.setProperty("object-fit", "contain", "important")
      image.style.setProperty("padding", "1rem", "important")
      image.style.setProperty("box-sizing", "border-box", "important")
    })
  }
  const entries = editablePreviewEntries()
  root.querySelectorAll("[data-builder-field]").forEach((element) => {
    delete element.dataset.builderField
    delete element.dataset.builderItemIndex
    delete element.dataset.builderSubfield
    delete element.dataset.builderInlineEdit
    delete element.dataset.builderInlineFile
    element.removeAttribute("contenteditable")
    element.removeAttribute("spellcheck")
    element.removeAttribute("role")
    element.removeAttribute("title")
  })

  const assignField = (element, key, metadata = {}) => {
    if (!element || element.closest("[data-builder-field]")) return
    element.dataset.builderField = key
    if (Number.isInteger(metadata.itemIndex)) {
      element.dataset.builderItemIndex = String(metadata.itemIndex)
    }
    if (metadata.subfield) element.dataset.builderSubfield = metadata.subfield
    if (metadata.inline) {
      element.dataset.builderInlineEdit = "true"
      element.setAttribute("contenteditable", "plaintext-only")
      element.setAttribute("spellcheck", "true")
      element.setAttribute("role", "textbox")
    }
    element.title = `Click to edit ${key.replaceAll("_", " ")}`
  }

  const assignTextNode = (node, key, metadata = {}) => {
    if (!node?.parentElement) return null
    let element = node.parentElement
    if (element.childNodes.length > 1) {
      const wrapper = document.createElement("span")
      element.replaceChild(wrapper, node)
      wrapper.appendChild(node)
      element = wrapper
    }
    assignField(element, key, { ...metadata, inline: true })
    return element
  }

  root.querySelectorAll("a[href]").forEach((link) => {
    const href = decodeURIComponent(link.getAttribute("href") || "")
    const match = entries.find(([, value]) => href.includes(value))
    if (match) assignField(link, match[0])
  })
  root.querySelectorAll("[src]").forEach((element) => {
    const source = element.getAttribute("src") || ""
    const match = entries.find(([, value]) => source === value)
    if (match) assignField(element, match[0])
  })
  root.querySelectorAll("[placeholder]").forEach((element) => {
    const placeholder = element.getAttribute("placeholder") || ""
    const match = entries.find(([, value]) => placeholder.includes(value))
    if (match) assignField(element, match[0])
  })
  root.querySelectorAll(".ecommerce-category-menu__link, .ecommerce-category-menu__submenu a").forEach((element) => {
    assignField(element, "menu_categories")
  })

  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT)
  const nodes = []
  while (walker.nextNode()) nodes.push(walker.currentNode)
  nodes.forEach((node) => {
    const text = String(node.textContent || "").trim()
    const match = entries.find(([, value]) => text.includes(value))
    if (match) assignTextNode(node, match[0])
  })

  // Map rendered repeater text back to its exact item and nested field.
  const modelFields = builderModelFields()
  const previewImages = Array.from(root.querySelectorAll("img[src]"))
  const usedImages = new Set()
  const markInlineFile = (element, key, itemIndex = null, subfield = "") => {
    if (!element) return
    element.dataset.builderField = key
    element.dataset.builderInlineFile = "true"
    if (Number.isInteger(itemIndex)) element.dataset.builderItemIndex = String(itemIndex)
    if (subfield) element.dataset.builderSubfield = subfield
    element.title = "Click to replace image"
  }

  modelFields
    .filter((field) => field.type === "file")
    .forEach((field) => {
      const key = field.key || field.name
      const source = String(form.value[key] || previewSampleValues.value[key] || "")
      const image = previewImages.find(
        (candidate) => !usedImages.has(candidate) && candidate.getAttribute("src") === source,
      )
      if (!image) return
      usedImages.add(image)
      markInlineFile(image, key)
    })

  modelFields
    .filter((field) => field.type === "repeater")
    .forEach((field) => {
      const key = field.key || field.name
      const items = Array.isArray(form.value[key]) && form.value[key].length
        ? form.value[key]
        : Array.isArray(previewSampleValues.value[key])
          ? previewSampleValues.value[key]
          : []
      const usedNodes = new Set()
      const subfields = field.fields || []
      items.forEach((item, index) => {
        subfields.forEach((subfield) => {
          if (!["text", "normaltext", "textarea", "email", "phone"].includes(subfield.type)) return
          const subfieldKey = subfield.key || subfield.name
          const value = String(item?.[subfieldKey] ?? "").trim()
          if (!value || value === "#") return
          const node = nodes.find(
            (candidate) =>
              !usedNodes.has(candidate) && String(candidate.textContent || "").trim() === value,
          )
          if (!node) return
          usedNodes.add(node)
          const element = node.parentElement?.closest("[data-builder-inline-edit]") || node.parentElement
          if (!element) return
          element.dataset.builderField = key
          element.dataset.builderItemIndex = String(index)
          element.dataset.builderSubfield = subfieldKey
          element.dataset.builderInlineEdit = "true"
          element.setAttribute("contenteditable", "plaintext-only")
          element.setAttribute("spellcheck", "true")
          element.setAttribute("role", "textbox")
          element.title = `Click to edit ${subfield.label || subfieldKey}`
        })
        subfields
          .filter((subfield) => subfield.type === "file")
          .forEach((subfield) => {
            const subfieldKey = subfield.key || subfield.name
            const source = String(item?.[subfieldKey] || "")
            const image = previewImages.find(
              (candidate) =>
                !usedImages.has(candidate) && candidate.getAttribute("src") === source,
            )
            if (!image) return
            usedImages.add(image)
            markInlineFile(image, key, index, subfieldKey)
          })
      })

      addRepeaterControlToPreview(root, field, key)
    })
}

function addRepeaterControlToPreview(root, field, key) {
  const itemElements = Array.from(
    root.querySelectorAll(`[data-builder-field="${CSS.escape(key)}"]`),
  )
  const indexedElements = itemElements.filter((element) =>
    Number.isInteger(Number.parseInt(element.dataset.builderItemIndex, 10)),
  )
  const firstElement = indexedElements[0]
  const firstIndex = firstElement?.dataset.builderItemIndex
  const elementsFromOtherItems = indexedElements.filter(
    (element) => element.dataset.builderItemIndex !== firstIndex,
  )

  // Walk from one rendered value toward the shared list. The first parent
  // containing a different item is the repeatable collection container.
  let container = null
  let referenceCard = null
  let candidate = firstElement
  while (candidate?.parentElement && candidate.parentElement !== root) {
    const parent = candidate.parentElement
    if (elementsFromOtherItems.some((element) => parent.contains(element))) {
      container = parent
      referenceCard = candidate
      break
    }
    candidate = parent
  }

  // A one-item collection has no sibling marker to compare, so use common
  // semantic card elements as a safe fallback.
  if (!container) {
    const itemCard = itemElements
      .map((element) => element.closest("a, article, li"))
      .find((element) => element?.parentElement && element !== root)
    container = itemCard?.parentElement || null
    referenceCard = itemCard || null
  }
  if (!container) return

  const button = document.createElement("button")
  button.type = "button"
  button.dataset.builderAddRepeater = key
  button.className = "ecommerce-preview-add-repeater"
  button.textContent = `+ Add ${String(field.label || "Item")}`
  button.title = `Add ${String(field.label || "item").toLowerCase()}`

  // Match compact tiles such as brands, while preventing tall editorial or
  // testimonial cards from stretching the add action into a mostly empty box.
  const referenceHeight = referenceCard?.getBoundingClientRect().height || 0
  if (referenceHeight > 0) {
    button.style.setProperty(
      "--ecommerce-preview-add-height",
      `${Math.min(Math.max(Math.round(referenceHeight), 128), 320)}px`,
    )
  }
  container.appendChild(button)
}

async function addRepeaterItemFromPreview(key) {
  const modelField = builderModelFields().find(
    (field) => field.type === "repeater" && (field.key || field.name) === key,
  )
  if (!modelField) return

  const newItem = { _id: `_${Math.random().toString(36).slice(2, 11)}` }
  ;(modelField.fields || []).forEach((field) => {
    const subfieldKey = field.key || field.name
    if (!subfieldKey) return
    newItem[subfieldKey] = field.type === "repeater"
      ? []
      : JSON.parse(JSON.stringify(field.default ?? ""))
  })

  const items = JSON.parse(JSON.stringify(Array.isArray(form.value[key]) ? form.value[key] : []))
  items.push(newItem)
  form.value[key] = items
  modelField.value = items

  openContentPanel()
  await nextTick()
  focusedRepeaterItem.value = {
    fieldKey: key,
    index: items.length - 1,
    request: ++repeaterFocusRequest,
  }
  focusedFieldKey.value = key
}

function handlePreviewFocusIn(event) {
  if (!event.target.closest("[data-builder-inline-edit]")) return
  inlinePreviewEditing = true
  window.clearTimeout(previewTimer)
}

function handlePreviewFocusOut(event) {
  if (!event.target.closest("[data-builder-inline-edit]")) return
  window.setTimeout(() => {
    const activeElement = document.activeElement
    if (activeElement?.closest?.("[data-builder-inline-edit]")) return
    inlinePreviewEditing = false
    schedulePreview()
  }, 0)
}

function handlePreviewInput(event) {
  const editable = event.target.closest("[data-builder-inline-edit]")
  if (!editable || !previewContainer.value?.contains(editable)) return
  const key = editable.dataset.builderField
  if (!key) return
  const value = String(editable.innerText ?? editable.textContent ?? "").replace(/\n+$/g, "")
  const itemIndex = Number.parseInt(editable.dataset.builderItemIndex, 10)
  const subfield = editable.dataset.builderSubfield
  if (Number.isInteger(itemIndex) && subfield) {
    const source = Array.isArray(form.value[key]) && form.value[key].length
      ? form.value[key]
      : previewSampleValues.value[key]
    const items = JSON.parse(JSON.stringify(Array.isArray(source) ? source : []))
    if (!items[itemIndex] || typeof items[itemIndex] !== "object") items[itemIndex] = {}
    items[itemIndex][subfield] = value
    form.value[key] = items
    const modelField = builderModelFields().find(
      (field) => (field.key || field.name) === key,
    )
    if (modelField) modelField.value = items
    return
  }
  form.value[key] = value
}

function handlePreviewKeydown(event) {
  if (event.key !== "Enter" || !event.target.closest("[data-builder-inline-edit]")) return
  event.preventDefault()
  event.target.blur()
}

function triggerInlineFileUpload(element) {
  pendingInlineFileTarget.value = {
    key: element.dataset.builderField,
    itemIndex: Number.parseInt(element.dataset.builderItemIndex, 10),
    subfield: element.dataset.builderSubfield || "",
    element,
  }
  inlineFileInput.value?.click()
}

async function handleInlineFileChange(event) {
  const file = event.target.files?.[0]
  const target = pendingInlineFileTarget.value
  if (!file || !target?.key) return

  const temporaryUrl = URL.createObjectURL(file)
  if (target.element) target.element.src = temporaryUrl
  inlineImageUploading.value = true
  previewError.value = ""
  try {
    const uploadData = new FormData()
    uploadData.append("file", file)
    const pageName = String(route.params.page_name || route.params.pageId || "")
    if (target.key.toLowerCase().includes("logo") && pageName) {
      uploadData.append("is_builder_logo", "1")
      uploadData.append("page_name", pageName)
    }
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.upload_file`,
      {
        method: "POST",
        headers: {
          "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: uploadData,
      },
    )
    const body = await response.json()
    const result = body?.message ?? body
    if (!response.ok || result?.status !== "success" || !result.file_url) {
      throw new Error(result?.message || "Unable to upload image.")
    }

    if (Number.isInteger(target.itemIndex) && target.subfield) {
      const source = Array.isArray(form.value[target.key]) && form.value[target.key].length
        ? form.value[target.key]
        : previewSampleValues.value[target.key]
      const items = JSON.parse(JSON.stringify(Array.isArray(source) ? source : []))
      if (!items[target.itemIndex] || typeof items[target.itemIndex] !== "object") {
        items[target.itemIndex] = {}
      }
      items[target.itemIndex][target.subfield] = result.file_url
      form.value[target.key] = items
      const modelField = builderModelFields().find(
        (field) => (field.key || field.name) === target.key,
      )
      if (modelField) modelField.value = items
    } else {
      form.value[target.key] = result.file_url
    }
    schedulePreview()
  } catch (error) {
    previewError.value = error.message || "Unable to upload image."
    schedulePreview()
  } finally {
    inlineImageUploading.value = false
    pendingInlineFileTarget.value = null
    event.target.value = ""
    window.setTimeout(() => URL.revokeObjectURL(temporaryUrl), 1000)
  }
}

async function handlePreviewClick(event) {
  const addRepeaterButton = event.target.closest("[data-builder-add-repeater]")
  if (addRepeaterButton && previewContainer.value?.contains(addRepeaterButton)) {
    event.preventDefault()
    event.stopPropagation()
    await addRepeaterItemFromPreview(addRepeaterButton.dataset.builderAddRepeater)
    return
  }
  const inlineFile = event.target.closest("[data-builder-inline-file]")
  if (inlineFile && previewContainer.value?.contains(inlineFile)) {
    event.preventDefault()
    event.stopPropagation()
    triggerInlineFileUpload(inlineFile)
    return
  }
  const previewLink = event.target.closest("a[href]")
  if (previewLink && previewContainer.value?.contains(previewLink)) {
    event.preventDefault()
    event.stopPropagation()
  }
  const editable = event.target.closest("[data-builder-field]")
  if (!editable || !previewContainer.value?.contains(editable)) return
  if (editable.dataset.builderInlineEdit === "true") return
  event.preventDefault()
  event.stopPropagation()
  openContentPanel()
  const itemIndex = Number.parseInt(editable.dataset.builderItemIndex, 10)
  focusedRepeaterItem.value = Number.isInteger(itemIndex)
    ? {
        fieldKey: editable.dataset.builderField,
        index: itemIndex,
        request: ++repeaterFocusRequest,
      }
    : null
  focusedFieldKey.value = ""
  await nextTick()
  focusedFieldKey.value = editable.dataset.builderField
}
const validationError = ref("")
const activeEditorTab = ref("content")
const spacingSides = [
  { key: "top", label: "Top" },
  { key: "right", label: "Right" },
  { key: "bottom", label: "Bottom" },
  { key: "left", label: "Left" },
]
const themeColorOptions = [
  { value: "primary", label: "Website primary" },
  { value: "secondary", label: "Website secondary" },
  { value: "additional_1", label: "Website additional 1" },
  { value: "additional_2", label: "Website additional 2" },
]
const emptyBlockStyle = () => ({
  background_type: "",
  background_theme: "",
  background_color: "",
  gradient_from_theme: "",
  gradient_from: "",
  gradient_to_theme: "",
  gradient_to: "",
  gradient_direction: "to right",
  text_theme: "",
  text_color: "",
  action_theme: "",
  action_color: "",
  font_size: "",
  margin: "",
  margin_top: "",
  margin_right: "",
  margin_bottom: "",
  margin_left: "",
  padding: "",
  padding_top: "",
  padding_right: "",
  padding_bottom: "",
  padding_left: "",
})
const blockStyle = ref(emptyBlockStyle())
const productStyles = ref({})
const productSettings = ref({})
const selectedStyleProduct = ref(null)
const selectedStyleElement = ref(null)
const activeStyle = computed(() => {
  const productId = selectedStyleProduct.value?.name
  if (productId) {
    const key = String(productId)
    return productStyles.value[key] || blockStyle.value
  }

  const elementKey = selectedStyleElement.value?.key
  const elementProductId = selectedStyleElement.value?.productId
  if (elementKey && elementProductId) {
    const productKey = String(elementProductId)
    return productSettings.value[productKey]?.[`${elementKey}_style`] || blockStyle.value
  }

  return blockStyle.value
})
const themeStyleValue = (theme, customValue) => {
  const tokens = {
    primary: "var(--store-primary)",
    secondary: "var(--store-secondary)",
    additional_1: "var(--store-additional-1)",
    additional_2: "var(--store-additional-2)",
  }
  return tokens[theme] || customValue || ""
}
const actionSourceValue = computed({
  get() {
    if (activeStyle.value.action_theme) return activeStyle.value.action_theme
    return activeStyle.value.action_color ? "custom" : "default"
  },
  set(value) {
    if (value === "default") {
      activeStyle.value.action_theme = ""
      activeStyle.value.action_color = ""
    } else if (value === "custom") {
      activeStyle.value.action_theme = ""
      if (!activeStyle.value.action_color) activeStyle.value.action_color = "#111827"
    } else {
      activeStyle.value.action_theme = value
      activeStyle.value.action_color = ""
    }
  },
})
const previewBlockClasses = computed(() => ({
  "ecommerce-preview-custom-background": Boolean(
    blockStyle.value.background_type && (
      blockStyle.value.background_theme ||
      blockStyle.value.background_color ||
      blockStyle.value.gradient_from_theme ||
      blockStyle.value.gradient_from
    )
  ),
  "ecommerce-preview-custom-text": Boolean(
    blockStyle.value.text_theme || blockStyle.value.text_color
  ),
}))
const previewBlockStyle = computed(() => {
  const style = {}
  if (blockStyle.value.background_type === "solid") {
    style["--ecommerce-preview-background"] = themeStyleValue(
      blockStyle.value.background_theme,
      blockStyle.value.background_color,
    )
  } else if (blockStyle.value.background_type === "gradient") {
    const from = themeStyleValue(
      blockStyle.value.gradient_from_theme,
      blockStyle.value.gradient_from,
    )
    const to = themeStyleValue(
      blockStyle.value.gradient_to_theme,
      blockStyle.value.gradient_to,
    )
    if (from && to) {
      style["--ecommerce-preview-background"] = `linear-gradient(${blockStyle.value.gradient_direction || "to right"}, ${from}, ${to})`
    }
  }
  const textColor = themeStyleValue(
    blockStyle.value.text_theme,
    blockStyle.value.text_color,
  )
  if (textColor) style["--ecommerce-preview-text"] = textColor
  const actionColor = themeStyleValue(
    blockStyle.value.action_theme,
    blockStyle.value.action_color,
  )
  if (actionColor) style["--ecommerce-action-background"] = actionColor
  return style
})
const previewCanvasStyle = computed(() => ({
  ...previewBlockStyle.value,
  width: `${DESKTOP_PREVIEW_WIDTH}px`,
  maxWidth: "none",
  zoom: previewScale.value,
}))
const styleTargetLabel = computed(() => {
  if (selectedStyleProduct.value) {
    return `${selectedStyleProduct.value.product_name || selectedStyleProduct.value.name} Style`
  }
  if (selectedStyleElement.value) {
    return `${selectedStyleElement.value.productName} — ${selectedStyleElement.value.label} Style`
  }
  return "Block Style"
})

// dynamic form config
const dynamicConfig = computed(() => {
  const model = localBlock.value.block_details?.model
  if (!model) return null
  if (model.tabs?.length) return { tabs: model.tabs }
  if (model.fields?.length) return { fields: model.fields }
  return null
})

// initialize form
function initForm() {
  form.value = {}
  activeEditorTab.value = "content"
  editorPanelOpen.value = true
  const savedStyle = localBlock.value.block_style || {}
  productStyles.value = JSON.parse(
    JSON.stringify(localBlock.value.product_styles || {}),
  )
  productSettings.value = JSON.parse(
    JSON.stringify(localBlock.value.product_settings || {}),
  )
  selectedStyleProduct.value = null
  selectedStyleElement.value = null
  blockStyle.value = {
    ...emptyBlockStyle(),
    ...savedStyle,
    background_type:
      savedStyle.background_type ||
      (savedStyle.background_color ? "solid" : ""),
  }
  validationError.value = ""
  const model = localBlock.value.block_details?.model
  if (!model) return

  // Older in-progress Product Card data may still contain the temporary
  // block-level toggle. Add to Cart is configured separately per product.
  if (
    localBlock.value.block_name === "Product Card" &&
    Array.isArray(model.fields)
  ) {
    model.fields = model.fields.filter(
      field => (field.key || field.name) !== "show_add_to_cart",
    )
  }

  const collect = []

  if (Array.isArray(model.fields)) collect.push(...model.fields)
  if (Array.isArray(model.tabs)) {
    model.tabs.forEach(tab => {
      if (Array.isArray(tab.fields)) collect.push(...tab.fields)
    })
  }

  collect.forEach(f => {
    const key = f.key || f.name
    const arrayFieldTypes = ["product", "repeatable", "repeater", "draggable", "commerce_links", "categories"]
    const fallbackValue = arrayFieldTypes.includes(f.type) ? [] : ""
    form.value[key] = f.value ?? f.default ?? fallbackValue

    if (arrayFieldTypes.includes(f.type) && !Array.isArray(form.value[key])) {
      form.value[key] = []
    }
  })
}

function handleBackgroundTypeChange() {
  if (activeStyle.value.background_type === "solid") {
    if (!activeStyle.value.background_color) {
      activeStyle.value.background_color = "#ffffff"
    }
    return
  }

  if (activeStyle.value.background_type === "gradient") {
    if (!activeStyle.value.gradient_from) {
      activeStyle.value.gradient_from = "#7e51a2"
    }
    if (!activeStyle.value.gradient_to) {
      activeStyle.value.gradient_to = "#d62b90"
    }
    if (!activeStyle.value.gradient_direction) {
      activeStyle.value.gradient_direction = "to right"
    }
  }
}

function editProductStyle(product) {
  if (!product?.name) return
  const productId = String(product.name)
  if (!productStyles.value[productId]) {
    productStyles.value[productId] = emptyBlockStyle()
  }
  selectedStyleProduct.value = product
  selectedStyleElement.value = null
  openDesignPanel()
}

function editProductActionStyle({ product, key, label }) {
  if (!product?.name || !key) return
  const productId = String(product.name)
  if (!productSettings.value[productId]) {
    productSettings.value[productId] = { show_add_to_cart: true }
  }
  if (!productSettings.value[productId][`${key}_style`]) {
    productSettings.value[productId][`${key}_style`] = emptyBlockStyle()
  }
  selectedStyleElement.value = {
    key,
    label,
    productId: product.name,
    productName: product.product_name || product.name,
  }
  selectedStyleProduct.value = null
  openDesignPanel()
}

function toggleProductAddToCart({ product, show }) {
  if (!product?.name) return
  const productId = String(product.name)
  if (!productSettings.value[productId]) {
    productSettings.value[productId] = {}
  }
  productSettings.value[productId].show_add_to_cart = Boolean(show)
}

function returnToProductCardStyle() {
  if (!selectedStyleElement.value) return
  selectedStyleProduct.value = {
    name: selectedStyleElement.value.productId,
    product_name: selectedStyleElement.value.productName,
  }
  selectedStyleElement.value = null
  scrollSettingsToTop()
}

function clearStyleTarget() {
  selectedStyleProduct.value = null
  selectedStyleElement.value = null
  scrollSettingsToTop()
}

// watchers
watch(() => props.block, (val) => {
  if (!val) return

  // Keep form edits isolated from the watched prop. Mutating a nested model
  // shared with props.block causes this watcher to trigger itself recursively.
  const clonedValue = JSON.parse(JSON.stringify(val))

  const model =
    (clonedValue.block_details && clonedValue.block_details.model) ||
    (typeof clonedValue.model === "object" ? clonedValue.model : {})

  localBlock.value = {
    ...clonedValue,
    block_details: { ...clonedValue.block_details, model },
  }

  initForm()
}, { immediate: true })


watch(() => props.show, (v) => v && initForm())

watch(previewViewport, (element) => {
  previewResizeObserver?.disconnect()
  previewResizeObserver = null
  if (!element) return

  const updatePreviewWidth = () => {
    previewViewportWidth.value = element.clientWidth || DESKTOP_PREVIEW_WIDTH
  }
  updatePreviewWidth()
  previewResizeObserver = new ResizeObserver(updatePreviewWidth)
  previewResizeObserver.observe(element)
})

watch(
  [() => props.show, () => localBlock.value.block_name, form],
  schedulePreview,
  { deep: true, immediate: true },
)

onBeforeUnmount(() => {
  window.clearTimeout(previewTimer)
  previewResizeObserver?.disconnect()
})

// save
function save() {
  const model = localBlock.value.block_details?.model
  if (!model) return

  const modelFields = []
  if (Array.isArray(model.fields)) modelFields.push(...model.fields)
  if (Array.isArray(model.tabs)) {
    model.tabs.forEach(tab => {
      if (Array.isArray(tab.fields)) modelFields.push(...tab.fields)
      tab.sections?.forEach(section => {
        if (Array.isArray(section.fields)) modelFields.push(...section.fields)
      })
    })
  }

  const emptyProductField = modelFields.find(field => {
    if (field.type !== "product") return false
    const key = field.key || field.name
    return !Array.isArray(form.value[key]) || form.value[key].length === 0
  })

  if (emptyProductField) {
    validationError.value = "Select at least one product before saving this block."
    openContentPanel()
    return
  }

  validationError.value = ""

  if (Array.isArray(model.fields)) {
    model.fields.forEach(f => {
      const key = f.key || f.name
      if (key in form.value) f.value = form.value[key]
    })
  }

  if (Array.isArray(model.tabs)) {
    model.tabs.forEach(tab => {
      if (Array.isArray(tab.sections)) {
        tab.sections.forEach(section => {
          if (Array.isArray(section.fields)) {
            section.fields.forEach(f => {
              const key = f.key || f.name
              if (key in form.value) f.value = form.value[key]
            })
          }
        })
      }

      if (Array.isArray(tab.fields)) {
        tab.fields.forEach(f => {
          const key = f.key || f.name
          if (key in form.value) f.value = form.value[key]
        })
      }
    })
  }

  let cleanedBlock = JSON.parse(JSON.stringify(localBlock.value))
  const cleanedForm = JSON.parse(JSON.stringify(form.value))
  const cleanedStyle = Object.fromEntries(
    Object.entries(blockStyle.value).filter(([, value]) => value !== ""),
  )
  if (cleanedStyle.background_type !== "solid") {
    delete cleanedStyle.background_color
    delete cleanedStyle.background_theme
  }
  if (cleanedStyle.background_type !== "gradient") {
    delete cleanedStyle.gradient_from_theme
    delete cleanedStyle.gradient_from
    delete cleanedStyle.gradient_to_theme
    delete cleanedStyle.gradient_to
    delete cleanedStyle.gradient_direction
  }
  if (Object.keys(cleanedStyle).length) cleanedBlock.block_style = cleanedStyle
  else delete cleanedBlock.block_style

  const selectedProductIds = new Set()
  modelFields.forEach(field => {
    if (field.type !== "product") return
    const key = field.key || field.name
    const values = form.value[key]
    if (Array.isArray(values)) {
      values.forEach(value => selectedProductIds.add(String(value)))
    }
  })
  const cleanedProductStyles = {}
  Object.entries(productStyles.value).forEach(([productId, style]) => {
    if (!selectedProductIds.has(String(productId))) return
    const cleanedProductStyle = Object.fromEntries(
      Object.entries(style || {}).filter(([, value]) => value !== ""),
    )
    if (cleanedProductStyle.background_type !== "solid") {
      delete cleanedProductStyle.background_color
      delete cleanedProductStyle.background_theme
    }
    if (cleanedProductStyle.background_type !== "gradient") {
      delete cleanedProductStyle.gradient_from_theme
      delete cleanedProductStyle.gradient_from
      delete cleanedProductStyle.gradient_to_theme
      delete cleanedProductStyle.gradient_to
      delete cleanedProductStyle.gradient_direction
    }
    if (Object.keys(cleanedProductStyle).length) {
      cleanedProductStyles[productId] = cleanedProductStyle
    }
  })
  if (Object.keys(cleanedProductStyles).length) {
    cleanedBlock.product_styles = cleanedProductStyles
  } else {
    delete cleanedBlock.product_styles
  }

  const cleanedProductSettings = {}
  Object.entries(productSettings.value).forEach(([productId, settings]) => {
    if (!selectedProductIds.has(String(productId))) return
    const cleanedSettings = {
      show_add_to_cart: settings?.show_add_to_cart !== false,
    }
    const actionStyle = { ...(settings?.add_to_cart_style || {}) }
    Object.keys(actionStyle).forEach(key => {
      if (actionStyle[key] === "") delete actionStyle[key]
    })
    if (actionStyle.background_type !== "solid") {
      delete actionStyle.background_color
      delete actionStyle.background_theme
    }
    if (actionStyle.background_type !== "gradient") {
      delete actionStyle.gradient_from_theme
      delete actionStyle.gradient_from
      delete actionStyle.gradient_to_theme
      delete actionStyle.gradient_to
      delete actionStyle.gradient_direction
    }
    if (Object.keys(actionStyle).length) {
      cleanedSettings.add_to_cart_style = actionStyle
    }
    if (!cleanedSettings.show_add_to_cart || cleanedSettings.add_to_cart_style) {
      cleanedProductSettings[productId] = cleanedSettings
    }
  })
  if (Object.keys(cleanedProductSettings).length) {
    cleanedBlock.product_settings = cleanedProductSettings
  } else {
    delete cleanedBlock.product_settings
  }
  if (cleanedBlock.model && cleanedBlock.block_details?.model) delete cleanedBlock.model

  // console.log("🚀 Emitting updated block:", cleanedBlock)

  if (activeEditorTab.value === "style") {
    activeEditorTab.value = "content"
    selectedStyleProduct.value = null
    selectedStyleElement.value = null
    emit("update", {
      block: cleanedBlock,
      form: cleanedForm,
      keepOpen: true,
    })
    return
  }

  emit("update", { block: cleanedBlock, form: cleanedForm })
  emit("close")
}


</script>

<style scoped>
.figma-style-panel > .mb-4 {
  margin: 0;
  padding: 14px 16px 12px;
  border-bottom: 1px solid #e5e7eb;
}

.figma-style-panel > .mb-4 h3 {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.figma-style-panel > .mb-4 p {
  margin-top: 3px;
  font-size: 12px;
  line-height: 1.4;
}

.figma-style-panel > .grid > label,
.figma-style-panel > .grid > fieldset,
.figma-style-panel > .grid > template + label {
  min-width: 0;
  padding: 12px 16px;
  border-bottom: 1px solid #eef0f2;
}

.figma-style-panel :is(label, legend) {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
  color: #4b5563;
}

.figma-style-panel :is(select, input[type='text']) {
  height: 34px !important;
  margin-top: 5px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: #ffffff;
  padding-left: 10px;
  padding-right: 10px;
  font-size: 14px;
  font-weight: 400;
  color: #111827;
  outline: none;
}

.figma-style-panel :is(select, input[type='text']):focus {
  border-color: #22a263;
  box-shadow: 0 0 0 2px rgba(34, 162, 99, 0.12);
}

.figma-style-panel input[type='color'] {
  width: 34px;
  height: 34px;
  margin-top: 5px;
  border-radius: 6px;
  padding: 3px;
}

.figma-style-panel fieldset > label {
  font-size: 12px;
}

.figma-style-panel fieldset .grid {
  gap: 6px;
}

.section-editor-shell {
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
  font-size: 14px;
  color: #111827;
}

.section-editor-shell :is(button, input, select, textarea) {
  font-family: inherit;
}

.section-editor-shell :deep(.builder-dynamic-form) {
  font-family: inherit;
  font-size: 14px;
}

.section-editor-shell :deep(.builder-dynamic-form [data-editor-field] h1),
.section-editor-shell :deep(.builder-dynamic-form [data-editor-field] h2),
.section-editor-shell :deep(.builder-dynamic-form [data-editor-field] h3) {
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
}

.section-editor-shell :deep(.builder-dynamic-form [data-editor-field] p) {
  font-size: 12px;
  line-height: 1.5;
}

.section-editor-shell :deep(.builder-dynamic-form input),
.section-editor-shell :deep(.builder-dynamic-form select),
.section-editor-shell :deep(.builder-dynamic-form textarea),
.section-editor-shell :deep(.builder-dynamic-form button) {
  font-size: 14px;
}

.visual-block-preview,
.visual-block-preview :deep(button),
.visual-block-preview :deep(input),
.visual-block-preview :deep(select),
.visual-block-preview :deep(textarea) {
  font-family: var(--store-font, Inter, sans-serif);
}

.visual-block-preview {
  container-name: visual-block-preview;
  container-type: inline-size;
}

/*
 * Builder blocks normally respond to the storefront viewport. Inside the
 * editor, however, the preview can be much narrower than the browser window.
 * Use its container width for fluid sizing and responsive layout so desktop
 * hero styles do not overflow the editor column.
 */
.visual-block-preview :deep(.pc-hero__copy),
.visual-block-preview :deep(.pc-editorial > div) {
  padding: clamp(2rem, 6cqw, 6rem);
}

.visual-block-preview :deep(.pc-hero h1) {
  font-size: clamp(2.5rem, 5cqw, 5.2rem);
}

.visual-block-preview :deep(.pc-editorial h2) {
  font-size: clamp(2.2rem, 4cqw, 4.5rem);
}

.visual-block-preview :deep(.pc-hero > *),
.visual-block-preview :deep(.pc-editorial > *) {
  min-width: 0;
}

.visual-block-preview :deep(.pc-hero h1),
.visual-block-preview :deep(.pc-editorial h2) {
  overflow-wrap: break-word;
}

.visual-block-preview :deep(.pc-section),
.visual-block-preview :deep(.pc-article-section) {
  padding-left: clamp(1rem, 4cqw, 4rem);
  padding-right: clamp(1rem, 4cqw, 4rem);
}

.visual-block-preview :deep(.pc-heading),
.visual-block-preview :deep(.pc-section__header h2),
.visual-block-preview :deep(.pc-article-header h2) {
  font-size: clamp(2rem, 3cqw, 3.25rem);
}

@container visual-block-preview (max-width: 1000px) {
  .visual-block-preview :deep(.pc-products) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@container visual-block-preview (max-width: 800px) {
  .visual-block-preview :deep(.pc-brands),
  .visual-block-preview :deep(.pc-footer__main) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }

  .visual-block-preview :deep(.pc-articles) {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  .visual-block-preview :deep(.pc-article-header) {
    align-items: flex-start;
  }

  .visual-block-preview :deep(.pc-article-description) {
    min-height: 0;
  }
}

@container visual-block-preview (max-width: 560px) {
  .visual-block-preview :deep(.pc-products) {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  .visual-block-preview :deep(.pc-categories) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }
}

@container visual-block-preview (max-width: 520px) {
  .visual-block-preview :deep(.pc-hero),
  .visual-block-preview :deep(.pc-editorial) {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  .visual-block-preview :deep(.pc-hero__copy),
  .visual-block-preview :deep(.pc-editorial > div) {
    padding: 2.5rem 1.5rem;
  }

  .visual-block-preview :deep(.pc-hero img) {
    min-height: 320px;
  }

  .visual-block-preview :deep(.pc-editorial > img) {
    height: 360px;
  }
}

.visual-block-preview.ecommerce-preview-custom-background :deep(> :first-child),
.visual-block-preview.ecommerce-preview-custom-background :deep(> :first-child > :first-child) {
  background: var(--ecommerce-preview-background) !important;
  background-image: var(--ecommerce-preview-background) !important;
}

.visual-block-preview.ecommerce-preview-custom-text,
.visual-block-preview.ecommerce-preview-custom-text :deep(*) {
  color: var(--ecommerce-preview-text) !important;
}

.visual-block-preview :deep([data-builder-field]) {
  cursor: pointer !important;
  outline: 2px dashed rgba(34, 197, 94, 0.6);
  outline-offset: 3px;
  border-radius: 3px;
}

.visual-block-preview :deep([data-builder-field]:hover) {
  outline: 3px solid #22c55e;
  background: rgba(220, 252, 231, 0.45);
}

.visual-block-preview :deep([data-builder-inline-edit]:focus) {
  outline: 3px solid #22c55e;
  background: rgba(240, 253, 244, 0.8);
}

.visual-block-preview :deep([data-builder-inline-file]) {
  cursor: copy !important;
}

.visual-block-preview :deep(.ecommerce-preview-add-repeater) {
  display: grid !important;
  align-self: start;
  min-height: var(--ecommerce-preview-add-height, 8rem);
  height: var(--ecommerce-preview-add-height, auto);
  width: 100%;
  place-items: center;
  border: 2px dashed rgba(34, 197, 94, 0.7) !important;
  background: rgba(240, 253, 244, 0.65) !important;
  padding: 1rem;
  color: #15803d !important;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}

.visual-block-preview :deep(.ecommerce-preview-add-repeater:hover) {
  border-color: #16a34a !important;
  background: #dcfce7 !important;
}
</style>
