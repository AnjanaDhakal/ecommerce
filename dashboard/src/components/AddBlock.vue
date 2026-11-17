<template>
  <!-- Trigger Button -->
  <button
    type="button"
    class="mt-2 flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-dashed border-emerald-300 bg-emerald-50/60 px-4 py-2.5 text-sm font-semibold text-emerald-700 transition hover:border-emerald-500 hover:bg-emerald-50 focus:outline-none focus:ring-2 focus:ring-emerald-200"
    @click="openSidebar"
  >
    <span class="material-symbols-outlined text-[20px]">add</span>
    Add section
  </button>

  <!-- Sidebar -->
  <Sidebar v-model="showSidebar" width="600px">
    <template #title>Add to {{ sectionAreaLabel }}</template>

    <!-- Block List -->
    <div class="mt-4 grid grid-cols-1 gap-3 overflow-y-auto sm:grid-cols-2">
      <div class="text-center sm:col-span-2">
        <p class="mt-2 font-medium">Choose a section</p>
        <p class="mt-1 text-sm text-gray-500">You can edit its content and design after adding it.</p>
      </div>
      <div
        v-for="block in filteredBlocks"
        :key="block.name"
        class="flex cursor-pointer flex-col overflow-hidden rounded-xl border border-slate-200 bg-white p-2 transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md"
        :class="{ 'border-emerald-400 bg-emerald-50': selectedBlock === block }"
        @click="selectBlock(block)"
      >
        <!-- Block Name -->
        <p class="px-1 py-2 text-left text-sm font-semibold text-slate-800">{{ friendlySectionName(block.block_name) }}</p>

        <!-- Block Image -->
        <img
          v-if="block.block_image_base64"
          :src="block.block_image_base64"
          class="order-first aspect-video w-full rounded-lg border border-slate-100 bg-slate-50 object-cover"
        />
      </div>
    </div>
  </Sidebar>
</template>

<script setup>
import { computed, ref } from 'vue'
import Sidebar from './Sidebar.vue'
import { getBuilderBlocks } from '@/utils/builderBlocks'

// Props: draggable field name
const props = defineProps({
  fieldName: { type: String, required: true },
  blockNames: { type: Array, default: () => [] },
})

// Emit new block to parent
const emit = defineEmits(['submitted'])

const sectionAreaLabel = computed(() => ({
  header: 'store header',
  main: 'page',
  footer: 'store footer',
}[String(props.fieldName || '').toLowerCase()] || 'page'))

function friendlySectionName(name) {
  return {
    'Navbar 1': 'Contact bar',
    'Navbar 2': 'Main navigation',
    'Product Card': 'Products',
    'Image Gallery': 'Image gallery',
  }[name] || name
}

// Sidebar state
const showSidebar = ref(false)
const blocks = ref([])
const filteredBlocks = ref([])
const selectedBlock = ref(null)

function hydrateBlockDefaults(value) {
  if (Array.isArray(value)) return value.map(hydrateBlockDefaults)
  if (!value || typeof value !== 'object') return value

  const hydrated = Object.fromEntries(
    Object.entries(value).map(([key, item]) => [key, hydrateBlockDefaults(item)]),
  )
  if (
    Object.prototype.hasOwnProperty.call(hydrated, 'default') &&
    !Object.prototype.hasOwnProperty.call(hydrated, 'value')
  ) {
    hydrated.value = structuredClone(hydrated.default)
  }
  return hydrated
}

function blocksForCurrentTemplate(allBlocks) {
  return allBlocks.filter(
    (block) => block.type.toLowerCase() === props.fieldName.toLowerCase(),
  )
}

// Fetch blocks and open sidebar
async function openSidebar() {
  showSidebar.value = true
  try {
    blocks.value = await getBuilderBlocks()
    filteredBlocks.value = blocksForCurrentTemplate(blocks.value)
  } catch (err) {
    console.error('Failed to fetch blocks:', err)
  }
}

// // Auto-add block when clicked
// function selectBlock(block) {
//   const newBlock = {
//     id: Date.now(), // temporary unique id
//     name: block.name, // original name from API
//     block_name: block.block_name,
//     type: block.type,
//   }

//   emit('submitted', { fieldName: props.fieldName, block: newBlock })
//   showSidebar.value = false
//   selectedBlock.value = block
// }

// Auto-add block when clicked
function selectBlock(block) {
  let parsedModel = {}
  try {
    parsedModel = hydrateBlockDefaults(
      block.model ? JSON.parse(block.model) : {},
    )
  } catch (e) {
    console.error('Failed to parse block.model:', e)
  }

  const newBlock = {
    id: Date.now(), // temporary unique id
    name: block.name,
    block_name: block.block_name,
    type: block.type,
    block_details: {
      name: block.name,
      model: parsedModel, // ✅ parsed JSON model
    },
  }

 //  //console.log("New Block JSON:", JSON.stringify(newBlock, null, 2))

  emit('submitted', { fieldName: props.fieldName, block: newBlock })
  showSidebar.value = false
  selectedBlock.value = newBlock
}
</script>

<style scoped>
/* Optional: make block selection more obvious */
.bg-green-100 {
  border-color: #22c55e;
}
</style>
