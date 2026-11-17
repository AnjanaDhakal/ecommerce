<template>
  <div class="rounded-xl border border-gray-200 bg-white p-4">
    <!-- Label -->
    <label class="block text-gray-700 font-medium mb-2">{{
      field.label
    }}</label>

    <!-- List of Repeater Items -->
    <draggable
      v-model="localItems"
      :item-key="repeaterItemKey"
      handle=".repeater-drag-handle"
      ghost-class="repeater-drag-ghost"
      drag-class="repeater-drag-active"
      :animation="180"
    >
      <template #item="{ element: item, index }">
        <div
          class="mb-3 flex items-center justify-between gap-3 rounded-xl border border-gray-200 bg-gray-50 p-3"
        >
          <div class="flex min-w-0 items-center gap-3">
            <button
              type="button"
              class="repeater-drag-handle flex h-9 w-9 shrink-0 cursor-grab touch-none items-center justify-center rounded-lg text-gray-400 hover:bg-gray-200 hover:text-gray-700 active:cursor-grabbing"
              :aria-label="`Drag to reorder ${getItemLabel(item, index)}`"
              title="Drag to reorder"
            >
              <span class="material-symbols-outlined">drag_indicator</span>
            </button>
            <p class="truncate font-medium">
              {{ getItemLabel(item, index) }}
            </p>

            <!-- <p v-if="Object.keys(item).length > 1" class="text-sm text-gray-500 truncate">
              {{ summarizeItem(item) }}
            </p> -->
          </div>

          <div class="flex shrink-0 gap-2">
            <button
              type="button"
              @click="openEditor(index)"
              class="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-sm font-semibold text-gray-700 hover:bg-gray-100"
            >
              Edit
            </button>
            <button
              type="button"
              @click="removeItem(index)"
              class="rounded-lg px-3 py-1.5 text-sm font-semibold text-red-600 hover:bg-red-50"
            >
              Remove
            </button>
          </div>
        </div>
      </template>
    </draggable>

    <!-- Add Button -->
    <button
      type="button"
      @click="addItem"
      class="mt-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-gray-700"
    >
      + Add {{ field.label }}
    </button>

    <!-- Sidebar Drawer -->
    <transition name="slide">
      <div
        v-if="showSidebar"
        class="fixed top-0 right-0 h-full max-w-[96vw] bg-white shadow-lg z-50 flex flex-col"
        style="width: min(700px, 96vw)"
      >
        <!-- Header -->
        <div class="flex justify-between items-center border-b p-4">
          <h2 class="text-lg font-semibold">Edit {{ field.label }}</h2>
          <button @click="closeEditor" class="text-gray-500 hover:text-black">
            ✕
          </button>
        </div>

        <!-- Dynamic Form Body -->
        <div class="flex-1 overflow-auto p-4">
          <DynamicForm
            v-if="activeItem"
            :config="{
              fields: field.fields.map((f) => ({
                ...f,
                value: activeItem[f.name],
              })),
            }"
            :form="activeItem"
          />
        </div>

        <!-- Footer -->
        <div class="border-t p-4 flex justify-end gap-3">
          <button
            @click="closeEditor"
            class="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="saveEditor"
            class="rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-gray-700"
          >
            Save
          </button>
        </div>
      </div>
    </transition>

    <!-- Overlay -->
    <div
      v-if="showSidebar"
      class="fixed inset-0 bg-black bg-opacity-40 z-40"
      @click="closeEditor"
    ></div>
  </div>
</template>

<script setup>
import { ref, watch, toRaw } from 'vue'
import draggable from 'vuedraggable'
import DynamicForm from './DynamicForm.vue'

/* -----------------------------
   PROPS & EMITS
------------------------------ */
const props = defineProps({
  field: { type: Object, required: true },
  form: { type: Object, required: true },
  openItemRequest: { type: Object, default: null },
})
const emit = defineEmits(['update:value'])

/* -----------------------------
   STATE
------------------------------ */
const localItems = ref([])
const showSidebar = ref(false)
const activeItem = ref(null)
const activeIndex = ref(null)

/* -----------------------------
   UTILITIES
------------------------------ */
function safeClone(obj) {
  try {
    return JSON.parse(JSON.stringify(toRaw(obj ?? {})))
  } catch {
    return structuredClone
      ? structuredClone(toRaw(obj ?? {}))
      : { ...toRaw(obj ?? {}) }
  }
}

function initializeNested(item, fields) {
  fields.forEach((f) => {
    // Initialize missing field
    if (!(f.name in item)) {
      if (f.type === 'repeater') {
        item[f.name] = []
      } else {
        item[f.name] = f.default ?? ''
      }
    }

    // Recursive init for nested repeaters
    if (f.type === 'repeater' && Array.isArray(item[f.name])) {
      item[f.name].forEach((nested) => initializeNested(nested, f.fields || []))
    }
  })
}

function deepMerge(target = {}, source = {}) {
  for (const key of Object.keys(source)) {
    const src = source[key]
    const tgt = target[key]

    if (Array.isArray(src)) {
      // Replace arrays entirely (important for nested repeaters)
      target[key] = src
    } else if (src && typeof src === 'object') {
      if (!tgt || typeof tgt !== 'object' || Array.isArray(tgt))
        target[key] = {}
      deepMerge(target[key], src)
    } else {
      target[key] = src
    }
  }
  return target
}

/* -----------------------------
   INITIALIZATION
------------------------------ */
if (!Array.isArray(props.field.value)) {
  props.field.value = []
}

function normalizeItems(items) {
  return (Array.isArray(items) ? items : []).map((item) => {
    const clonedValue = safeClone(item)
    const cloned =
      clonedValue &&
      typeof clonedValue === 'object' &&
      !Array.isArray(clonedValue)
        ? clonedValue
        : { value: clonedValue }
    if (!cloned._id) {
      Object.defineProperty(cloned, '__dragId', {
        value: generateId(),
        enumerable: false,
      })
    }
    return cloned
  })
}

function repeaterItemKey(item) {
  return item?._id || item?.__dragId
}

function syncLocal() {
  localItems.value = normalizeItems(props.field.value)
}
syncLocal()

// Watch parent → local
watch(
  () => props.field.value,
  (newVal) => {
    const normalized = normalizeItems(newVal)
    if (JSON.stringify(normalized) !== JSON.stringify(localItems.value)) {
      localItems.value = normalized
    }
  },
  { deep: true },
)

// Watch local → emit to parent
watch(
  localItems,
  (newVal) => {
    emit(
      'update:value',
      newVal.map((i) => toRaw(i)),
    )
  },
  { deep: true },
)

/* -----------------------------
   REPEATER ACTIONS
------------------------------ */
function generateId() {
  return '_' + Math.random().toString(36).substr(2, 9)
}

function addItem() {
  const fields = Array.isArray(props.field.fields) ? props.field.fields : []
  const newItem = { _id: generateId() }

  fields.forEach((f) => {
    if (f.type === 'repeater') newItem[f.name] = []
    else newItem[f.name] = f.default ?? ''
  })

  localItems.value.push(newItem)
  openEditor(localItems.value.length - 1)
}

function removeItem(index) {
  localItems.value.splice(index, 1)
}

function summarizeItem(item) {
  const keys = Object.keys(item).filter((k) => !['_id', 'Page'].includes(k))

  const summary = keys
    .map((key) => {
      const value = item[key]

      // 🧩 Handle nested repeater arrays
      if (Array.isArray(value)) {
        if (value.length === 0) return `${key}: [empty]`

        // Try to pick a readable label from each child item
        const labelKeys = ['title', 'name', 'label']
        const labels = value
          .map((child) => {
            if (typeof child !== 'object') return child
            const labelKey = labelKeys.find((k) => child[k])
            return labelKey ? child[labelKey] : '(item)'
          })
          .filter(Boolean)
          .slice(0, 3) // show first 3 items

        const labelPreview = labels.join(', ')
        return `${key}: [${value.length} ${value.length === 1 ? 'item' : 'items'}: ${labelPreview}]`
      }

      // 🧩 Handle nested object (like Page)
      else if (value && typeof value === 'object') {
        const labelKey = ['title', 'name', 'label', 'slug', 'id'].find(
          (k) => value[k],
        )
        if (labelKey) {
          return `${key}: { ${labelKey}: ${value[labelKey]} }`
        } else if (Object.keys(value).length > 0) {
          const previewKey = Object.keys(value)[0]
          return `${key}: { ${previewKey}: ${value[previewKey]} }`
        } else {
          return `${key}: {empty}`
        }
      }

      // 🧩 Plain string or number
      else {
        return `${key}: ${value ?? ''}`
      }
    })
    .join(', ')

  return summary.length > 100 ? summary.slice(0, 100) + '...' : summary
}

function getItemLabel(item, index) {
  const title = item.title || item.keyword || item.name || `Item ${index + 1}`
  const links = Array.isArray(item.destinations) ? item.destinations : item.links
  const linksCount = Array.isArray(links) ? links.length : 0
  return linksCount > 0
    ? `${title} (${linksCount} ${linksCount === 1 ? 'link' : 'links'})`
    : title
}

/* -----------------------------
   SIDEBAR HANDLERS
------------------------------ */
function openEditor(index) {
  activeIndex.value = index
  activeItem.value = safeClone(localItems.value[index])

  // ✅ Initialize all nested fields before showing DynamicForm
  initializeNested(activeItem.value, props.field.fields || [])

  showSidebar.value = true
}

watch(
  () => props.openItemRequest?.request,
  () => {
    const index = Number(props.openItemRequest?.index)
    if (Number.isInteger(index) && index >= 0 && index < localItems.value.length) {
      openEditor(index)
    }
  },
  { immediate: true },
)

function closeEditor() {
  showSidebar.value = false
  activeItem.value = null
  activeIndex.value = null
}

function saveEditor() {
  if (activeIndex.value !== null) {
    const existing = safeClone(localItems.value[activeIndex.value])
    const updated = safeClone(activeItem.value)
    const merged = deepMerge(existing, updated)
    localItems.value.splice(activeIndex.value, 1, merged)
  }
  closeEditor()
}
</script>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.repeater-drag-ghost {
  opacity: 0.4;
}

.repeater-drag-active {
  cursor: grabbing;
}
</style>
