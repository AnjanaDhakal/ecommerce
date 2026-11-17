<template>
  <div class="h-full min-h-0">
    <div v-if="loading" class="flex min-h-[420px] items-center justify-center">
      <p class="text-sm text-gray-500">Loading {{ title.toLowerCase() }}...</p>
    </div>

    <div
      v-else-if="!items.length"
      class="flex min-h-[480px] flex-col items-center justify-center px-6 text-center"
    >
      <div class="relative mb-7 h-40 w-44">
        <div
          class="absolute inset-x-3 bottom-0 h-32 rounded-full bg-gray-100"
        ></div>
        <div
          class="absolute bottom-0 left-1/2 h-28 w-28 -translate-x-1/2 rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
        >
          <div class="space-y-3 pt-2">
            <div class="h-2 w-12 rounded-full bg-gray-300"></div>
            <div class="h-2 w-16 rounded-full bg-gray-200"></div>
            <div class="h-2 w-10 rounded-full bg-gray-300"></div>
            <div class="h-2 w-14 rounded-full bg-gray-200"></div>
          </div>
        </div>
        <div
          class="absolute left-1/2 top-0 flex h-14 w-28 -translate-x-1/2 items-center rounded-xl bg-gray-400 px-4 shadow"
        >
          <span class="material-symbols-outlined text-2xl text-white">
            {{ emptyIcon }}
          </span>
        </div>
      </div>

      <h3 class="text-xl font-semibold text-gray-900">{{ emptyTitle }}</h3>
      <p class="mt-2 max-w-md text-sm leading-6 text-gray-500">
        {{ emptyDescription }}
      </p>
      <Button
        class="mt-6"
        theme="green"
        variant="solid"
        @click="$emit('create')"
      >
        + {{ createLabel }}
      </Button>
    </div>

    <div
      v-else
      class="grid h-full min-h-0 overflow-hidden rounded-xl border border-gray-200 bg-white lg:grid-cols-[13rem_minmax(0,1fr)]"
    >
      <aside class="flex min-h-0 flex-col border-b border-gray-200 lg:border-b-0 lg:border-r">
        <div class="shrink-0 border-b border-gray-200 p-4">
          <div class="flex flex-col items-stretch gap-3">
            <h3 class="font-semibold text-gray-900">
              {{ title }} ({{ items.length }})
            </h3>
            <Button
              class="w-full justify-center"
              theme="green"
              variant="solid"
              @click="$emit('create')"
            >
              + {{ shortCreateLabel }}
            </Button>
          </div>
          <div class="relative mt-4">
            <span
              class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-gray-400"
            >
              search
            </span>
            <input
              v-model="search"
              type="search"
              :placeholder="`Search ${title.toLowerCase()}...`"
              class="h-10 w-full rounded-lg border border-gray-200 bg-gray-50 pl-10 pr-3 text-sm outline-none transition-colors focus:border-green-500"
            />
          </div>
        </div>

        <div class="min-h-0 flex-1 overflow-y-auto">
          <button
            v-for="item in filteredItems"
            :key="item.key"
            type="button"
            class="flex w-full items-center gap-2.5 border-b border-gray-100 px-3 py-3 text-left transition-colors"
            :class="
              selectedKey === item.key
                ? 'bg-green-50 text-green-900'
                : 'hover:bg-gray-50'
            "
            @click="$emit('select', item.key)"
          >
            <div
              class="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-md border border-gray-200 bg-white"
            >
              <img
                v-if="item.image"
                :src="item.image"
                :alt="item.title"
                class="h-full w-full object-contain"
              />
              <span v-else class="text-sm font-semibold text-green-700">
                {{ item.title.charAt(0).toUpperCase() }}
              </span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium">{{ item.title }}</p>
              <p
                v-if="item.status"
                class="mt-0.5 truncate text-[11px] font-medium"
                :class="
                  item.status === 'Published'
                    ? 'text-green-700'
                    : 'text-gray-500'
                "
              >
                {{ item.status }}
              </p>
            </div>
          </button>

          <p
            v-if="!filteredItems.length"
            class="p-6 text-center text-sm text-gray-500"
          >
            No matching {{ title.toLowerCase() }}.
          </p>
        </div>
      </aside>

      <main class="min-h-0 min-w-0 overflow-y-auto p-5 sm:p-6">
        <slot name="detail" :item="selectedItem?.raw">
          <div class="flex h-full items-center justify-center text-sm text-gray-500">
            Select an item to view its details.
          </div>
        </slot>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Button } from 'frappe-ui'

const props = defineProps({
  title: { type: String, required: true },
  items: { type: Array, default: () => [] },
  selectedKey: { type: [String, Number], default: '' },
  loading: { type: Boolean, default: false },
  createLabel: { type: String, required: true },
  shortCreateLabel: { type: String, required: true },
  emptyTitle: { type: String, required: true },
  emptyDescription: { type: String, required: true },
  emptyIcon: { type: String, default: 'inventory_2' },
})

defineEmits(['create', 'select'])

const search = ref('')
const filteredItems = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return props.items
  return props.items.filter((item) =>
    `${item.title} ${item.subtitle || ''}`.toLowerCase().includes(term),
  )
})
const selectedItem = computed(
  () =>
    props.items.find((item) => item.key === props.selectedKey) || props.items[0],
)
</script>
