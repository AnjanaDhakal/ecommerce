<template>
  <section class="mt-5 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
    <button
      type="button"
      class="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition hover:bg-slate-50"
      :aria-expanded="!isCollapsed"
      @click="isCollapsed = !isCollapsed"
    >
      <span class="flex min-w-0 items-center gap-3">
        <span class="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-700">
          <span class="material-symbols-outlined text-[20px]">{{ areaIcon }}</span>
        </span>
        <span class="min-w-0">
          <span class="flex flex-wrap items-center gap-2">
            <span class="block text-sm font-semibold text-slate-900">{{ sectionAreaLabel }}</span>
            <span
              v-if="isHeaderArea"
              class="rounded-full bg-violet-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-violet-700"
            >
              Every page
            </span>
          </span>
          <span class="mt-0.5 block text-xs text-slate-500">
            {{ sectionCountLabel }} · Drag to reorder, click to edit
          </span>
        </span>
      </span>
      <span
        class="material-symbols-outlined shrink-0 text-[20px] text-slate-400 transition-transform"
        :class="{ 'rotate-180': !isCollapsed }"
      >
        expand_more
      </span>
    </button>

    <div v-show="!isCollapsed" class="border-t border-slate-100 bg-slate-50/70 p-3">
      <draggable
        v-model="localValue"
        item-key="id"
        handle=".section-drag-handle"
        ghost-class="section-ghost"
        chosen-class="section-chosen"
        :animation="180"
        class="space-y-2"
        @start="handleDragStart"
      >
        <template #item="{ element, index }">
          <article
            class="section-row group flex min-h-[62px] cursor-pointer items-center gap-2 rounded-xl border bg-white px-2.5 py-2 transition"
            :class="isSelected(index)
              ? 'border-emerald-500 bg-emerald-50/60 ring-2 ring-emerald-100'
              : 'border-slate-200 hover:border-slate-300 hover:shadow-sm'"
            @click="openEdit(element, index)"
          >
            <button
              type="button"
              class="section-drag-handle grid h-9 w-7 shrink-0 cursor-grab place-items-center rounded-lg text-slate-300 transition hover:bg-slate-100 hover:text-slate-500 active:cursor-grabbing"
              title="Drag to reorder"
              aria-label="Drag section to reorder"
              @click.stop
            >
              <span class="material-symbols-outlined text-[20px]">drag_indicator</span>
            </button>

            <img
              v-if="previewFor(element)"
              :src="previewFor(element)"
              alt=""
              class="h-10 w-14 shrink-0 rounded-lg border border-slate-200 bg-slate-100 object-cover"
            />
            <span
              v-else
              class="grid h-10 w-14 shrink-0 place-items-center rounded-lg bg-slate-100 text-slate-600"
              :class="{ 'bg-emerald-100 text-emerald-700': isSelected(index) }"
            >
              <span class="material-symbols-outlined text-[19px]">
                {{ sectionIcon(element.block_name) }}
              </span>
            </span>

            <span class="min-w-0 flex-1">
              <span class="block truncate text-sm font-semibold text-slate-800">
                {{ friendlySectionName(element.block_name) }}
              </span>
              <span class="mt-0.5 block truncate text-[11px] font-medium uppercase tracking-wide text-slate-400">
                {{ sectionTypeLabel(element.block_name) }}
              </span>
            </span>

            <span class="flex shrink-0 items-center gap-1">
              <button
                type="button"
                class="section-action"
                title="Duplicate section"
                aria-label="Duplicate section"
                @click.stop="duplicate(index)"
              >
                <span class="material-symbols-outlined text-[18px]">content_copy</span>
              </button>
              <button
                type="button"
                class="section-action hover:!bg-red-50 hover:!text-red-600"
                title="Remove section"
                aria-label="Remove section"
                @click.stop="remove(index)"
              >
                <span class="material-symbols-outlined text-[19px]">delete</span>
              </button>
              <span class="material-symbols-outlined ml-0.5 text-[19px] text-slate-300 transition group-hover:text-slate-500">
                chevron_right
              </span>
            </span>
          </article>
        </template>
      </draggable>

      <div
        v-if="!localValue.length"
        class="mb-2 rounded-xl border border-dashed border-slate-300 bg-white px-4 py-6 text-center"
      >
        <span class="material-symbols-outlined text-3xl text-slate-300">dashboard_customize</span>
        <p class="mt-1 text-sm font-semibold text-slate-700">No sections yet</p>
        <p class="mt-0.5 text-xs text-slate-500">Add a section to start building this area.</p>
      </div>

      <AddBlock
        :fieldName="field.name"
        :block-names="blockNames"
        @submitted="addBlock"
      />
    </div>

    <!-- 🛠 Edit Sidebar -->
    <EditBlock
      :block="editingBlock || emptyEditingBlock"
      :show="showEdit"
      @update="updateBlock"
      @close="closeEdit"
    />
  </section>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue"
import draggable from "vuedraggable"
import AddBlock from "@/components/AddBlock.vue"
import EditBlock from "@/components/EditBlock.vue"
import { getBuilderBlocks } from "@/utils/builderBlocks"

const props = defineProps({
  field: Object,
  modelValue: { type: Array, default: () => [] },
  blockNames: { type: Array, default: () => [] },
})
const emit = defineEmits(["update:modelValue"])

const fieldArea = computed(() => String(props.field?.name || '').toLowerCase())
const sectionAreaLabel = computed(() => ({
  header: 'Store header',
  main: 'Page content',
  footer: 'Store footer',
}[fieldArea.value] || props.field?.label || 'Page content'))
const isHeaderArea = computed(() => fieldArea.value === 'header')
const areaIcon = computed(() => ({
  header: 'web_asset',
  main: 'view_quilt',
  footer: 'bottom_panel_open',
}[fieldArea.value] || 'view_quilt'))

function friendlySectionName(name) {
  return {
    'Navbar 1': 'Contact bar',
    'Navbar 2': 'Main navigation',
    'Product Card': 'Products',
    'Image Gallery': 'Image gallery',
  }[name] || name
}

function sectionIcon(name) {
  const normalized = String(name || '').toLowerCase()
  if (normalized.includes('announcement') || normalized.includes('bar')) return 'campaign'
  if (normalized.includes('navigation') || normalized.includes('navbar')) return 'menu'
  if (normalized.includes('hero') || normalized.includes('banner')) return 'panorama'
  if (normalized.includes('product') || normalized.includes('commerce')) return 'shopping_bag'
  if (normalized.includes('collection') || normalized.includes('gallery')) return 'grid_view'
  if (normalized.includes('story') || normalized.includes('split')) return 'view_column_2'
  if (normalized.includes('footer')) return 'bottom_panel_open'
  return 'dashboard_customize'
}

function sectionTypeLabel(name) {
  return String(name || 'Section')
}

// local copy for draggable
const localValue = ref([...props.modelValue])
const isCollapsed = ref(false)
const blockPreviewByName = ref({})
const sectionCountLabel = computed(() => {
  const count = localValue.value.length
  return `${count} ${count === 1 ? 'section' : 'sections'}`
})

function previewFor(block) {
  return (
    blockPreviewByName.value[block?.name] ||
    blockPreviewByName.value[block?.block_name] ||
    ''
  )
}

onMounted(async () => {
  try {
    const blocks = await getBuilderBlocks()
    const previews = {}
    blocks.forEach((block) => {
      const preview = block.block_image_base64 || block.block_image
      if (!preview) return
      if (block.name) previews[block.name] = preview
      if (block.block_name && !previews[block.block_name]) {
        previews[block.block_name] = preview
      }
    })
    blockPreviewByName.value = previews
  } catch (error) {
    console.error('Failed to load section previews:', error)
  }
})

function valuesMatch(left, right) {
  if (Object.is(left, right)) return true
  try {
    return JSON.stringify(left) === JSON.stringify(right)
  } catch {
    return false
  }
}

// sync when v-model changes externally
watch(
  () => props.modelValue,
  (val) => {
    const nextValue = Array.isArray(val) ? val : []
    if (!valuesMatch(localValue.value, nextValue)) {
      localValue.value = [...nextValue]
    }
  },
  { deep: true }
)

// emit back to parent when order or values change
watch(
  () => localValue.value,
  (val) => {
    if (!valuesMatch(val, props.modelValue)) {
      emit("update:modelValue", val)
    }
  },
  { deep: true }
)

const editingBlock = ref(null)
const editingIndex = ref(null)
const showEdit = ref(false)
const emptyEditingBlock = Object.freeze({})

function addBlock(payload) {
  // payload = { fieldName, block }
  const block = payload.block

  // ensure unique ID for draggable
  const blockToAdd = {
    id: block.id ?? Date.now(),
    block_name: block.block_name || "New Block",
    ...block
  }

  localValue.value.push(blockToAdd)
  openEdit(blockToAdd, localValue.value.length - 1)
}


async function openEdit(block, index) {
  showEdit.value = false
  editingBlock.value = JSON.parse(JSON.stringify(block))
  editingIndex.value = index
  await nextTick()
  showEdit.value = true
}

function updateBlock(updatedData) {
  if (editingIndex.value === null || !localValue.value[editingIndex.value]) {
    closeEdit()
    return
  }

  const existingId = localValue.value[editingIndex.value].id
  const updatedBlock = {
    ...updatedData.block,
    id: existingId // preserve ID
  }

  localValue.value.splice(editingIndex.value, 1, updatedBlock)

  if (updatedData.keepOpen) {
    editingBlock.value = JSON.parse(JSON.stringify(updatedBlock))
    showEdit.value = true
    return
  }

  closeEdit()
}

function closeEdit() {
  showEdit.value = false
  editingBlock.value = null
  editingIndex.value = null
}

function isSelected(index) {
  return showEdit.value && editingIndex.value === index
}

function handleDragStart() {
  closeEdit()
}

function duplicate(index) {
  const source = localValue.value[index]
  if (!source) return

  const copy = JSON.parse(JSON.stringify(source))
  copy.id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  localValue.value.splice(index + 1, 0, copy)
  openEdit(copy, index + 1)
}

function remove(index) {
  if (editingIndex.value === index) {
    closeEdit()
  } else if (editingIndex.value !== null && editingIndex.value > index) {
    editingIndex.value -= 1
  }
  localValue.value.splice(index, 1)
}
</script>

<style scoped>
.section-action {
  display: grid;
  height: 2rem;
  width: 2rem;
  place-items: center;
  border-radius: 0.5rem;
  color: rgb(148 163 184);
  transition: background-color 150ms ease, color 150ms ease;
}

.section-action:hover {
  background: rgb(241 245 249);
  color: rgb(71 85 105);
}

.section-ghost {
  border-color: rgb(52 211 153) !important;
  background: rgb(236 253 245) !important;
  opacity: 0.55;
}

.section-chosen {
  box-shadow: 0 12px 24px -12px rgb(15 23 42 / 0.28);
}
</style>
