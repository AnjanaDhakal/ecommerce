<template>
  <div ref="wrapperRef" class="relative w-full">
    <button
      type="button"
      class="flex h-[32px] w-full items-center justify-between gap-1.5 rounded-md border border-gray-200 bg-gray-100 px-2.5 py-1 text-left transition focus:border-green-400 focus:outline-none focus:ring-2 focus:ring-green-300"
      @click="toggleDropdown"
    >
      <div class="flex min-w-0 flex-1 items-center justify-between gap-2 leading-none">
        <div class="min-w-0 truncate text-[12px] font-semibold leading-tight text-gray-900">
          {{ selectedBranchLabel }}
        </div>
        <div
          v-if="props.showSelectedArea && selectedAreaLabel"
          class="max-w-[45%] truncate text-right text-[10px] leading-tight text-gray-500"
        >
          {{ selectedAreaLabel }}
        </div>
      </div>

      <svg
        class="h-3.5 w-3.5 flex-shrink-0 text-gray-500 transition-transform"
        :class="{ 'rotate-180': isOpen }"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <Portal>
      <div
        v-if="isOpen"
        ref="dropdownRef"
        class="fixed z-[160] flex flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl"
        :style="dropdownStyle"
      >
      <div class="border-b border-gray-100 bg-white p-2">
        <div class="relative">
          <svg
            class="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-gray-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="7" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35" />
          </svg>

          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            :placeholder="placeholder"
            autocomplete="off"
            class="h-9 w-full rounded-lg border border-gray-200 bg-gray-50 pl-8 pr-2 text-base outline-none transition focus:border-green-400 focus:bg-white focus:ring-2 focus:ring-green-300 sm:h-8 sm:text-[12px]"
            @input="handleSearchInput"
          />
        </div>
      </div>

      <div
        v-if="filteredBranches.length"
        ref="resultBoxRef"
        class="min-h-0 flex-1 overflow-y-auto p-1"
      >
        <div
          v-for="(branch, branchIndex) in filteredBranches"
          :key="branch.value"
          :data-active="branchIndex === activeIndex ? 'true' : 'false'"
          class="mb-1 overflow-hidden rounded-lg border"
          :class="
            isSelected(branch)
              ? 'border-green-500 bg-green-50'
              : branchIndex === activeIndex
                ? 'border-green-400 bg-green-50/80'
              : 'border-gray-100 bg-white'
          "
        >
          <button
            type="button"
            class="flex w-full items-start justify-between gap-2 px-2.5 py-1.5 text-left transition hover:bg-gray-50"
            @click="selectBranch(branch)"
          >
            <div class="min-w-0 flex-1">
              <div class="truncate text-[12px] font-semibold leading-tight text-gray-800">
                <template
                  v-for="(part, index) in getHighlightedParts(branch.label, searchQuery)"
                  :key="`${branch.value}-label-${index}`"
                >
                  <mark
                    v-if="part.match"
                    class="rounded-[2px] bg-yellow-300 px-0.5 text-gray-900"
                  >
                    {{ part.text }}
                  </mark>
                  <template v-else>{{ part.text }}</template>
                </template>
              </div>

              <div class="mt-0.5 flex items-start justify-between gap-2 text-[10px] leading-tight text-black">
                <template v-if="branch.district || branch.municipality">
                  <div
                    v-if="branch.municipality"
                    class="min-w-0 flex-1 truncate text-left"
                  >
                    <template
                      v-for="(part, index) in getHighlightedParts(branch.municipality, searchQuery)"
                      :key="`${branch.value}-municipality-${index}`"
                    >
                      <mark
                        v-if="part.match"
                        class="rounded-[2px] bg-orange-300 px-0.5 text-gray-900"
                      >
                        {{ part.text }}
                      </mark>
                      <template v-else>{{ part.text }}</template>
                    </template>
                  </div>
                  <div
                    v-if="branch.district"
                    class="min-w-0 flex-1 truncate text-right"
                  >
                    <template
                      v-for="(part, index) in getHighlightedParts(branch.district, searchQuery)"
                      :key="`${branch.value}-district-${index}`"
                    >
                      <mark
                        v-if="part.match"
                        class="rounded-[2px] bg-orange-300 px-0.5 text-gray-900"
                      >
                        {{ part.text }}
                      </mark>
                      <template v-else>{{ part.text }}</template>
                    </template>
                  </div>
                </template>
              </div>
            </div>

            <span
              class="mt-0 rounded-full px-1.5 py-0.5 text-[10px] leading-tight"
              :class="
                isSelected(branch)
                  ? 'bg-green-100 font-semibold text-green-700'
                  : branchIndex === activeIndex
                    ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-500'
              "
            >
              {{ isSelected(branch) ? 'Selected' : branchIndex === activeIndex ? 'Enter' : 'Select' }}
            </span>
          </button>

          <div v-if="branch.matchedAreas.length" class="px-2.5 pb-1.5 pt-0">
            <div class="flex flex-wrap gap-1">
              <button
                v-for="(area, areaIndex) in branch.matchedAreas"
                :key="`${branch.value}-${area}`"
                type="button"
                :data-active-area="
                  branchIndex === activeIndex && areaIndex === activeAreaIndex
                    ? 'true'
                    : 'false'
                "
                class="whitespace-nowrap rounded-md border px-1.5 py-[3px] text-[10px] leading-none transition"
                :class="
                  selectedAreaMatches(branch, area)
                    ? 'border-green-600 bg-green-600 text-white'
                    : branchIndex === activeIndex && areaIndex === activeAreaIndex
                      ? 'border-gray-800 bg-gray-800 text-white ring-1 ring-gray-400 shadow-sm'
                    : 'border-gray-200 bg-gray-50 text-gray-600 hover:border-green-300 hover:bg-green-50 hover:text-green-700'
                "
                @click="selectBranch(branch, area)"
              >
                <template
                  v-for="(part, index) in getHighlightedParts(area, searchQuery)"
                  :key="`${branch.value}-${area}-part-${index}`"
                >
                  <mark
                    v-if="part.match"
                    class="rounded-[2px] bg-yellow-300 px-0.5 text-gray-900"
                  >
                    {{ part.text }}
                  </mark>
                  <template v-else>{{ part.text }}</template>
                </template>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="px-3 py-5 text-center">
        <div class="text-[13px] font-medium text-gray-600">No result found</div>
        <div class="mt-0.5 text-[11px] text-gray-400">
          Try branch, area, district or municipality
        </div>
      </div>
      </div>
    </Portal>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Portal } from '@headlessui/vue'

const props = defineProps({
  modelValue: {
    type: [String, Object, null],
    default: '',
  },
  options: {
    type: Array,
    default: () => [],
  },
  placeholder: {
    type: String,
    default: 'Search branch, area, district or municipality...',
  },
  showSelectedArea: {
    type: Boolean,
    default: false,
  },
  autoSelectFirstArea: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const searchQuery = ref('')
const wrapperRef = ref(null)
const searchInputRef = ref(null)
const resultBoxRef = ref(null)
const dropdownRef = ref(null)
const selectedArea = ref('')
const dropdownStyle = ref({})
const activeIndex = ref(0)
const activeAreaIndex = ref(0)
let dialogScrollElement = null

const allowDialogTouchScroll = (event) => {
  if (!isOpen.value) event.stopPropagation()
}

const blurActiveElement = () => {
  if (document.activeElement instanceof HTMLElement) {
    document.activeElement.blur()
  }
}

const normalizeText = (value) =>
  String(value || '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim()

const alphabeticalCollator = new Intl.Collator(undefined, {
  numeric: true,
  sensitivity: 'base',
})

const sortAlphabetically = (firstValue, secondValue) =>
  alphabeticalCollator.compare(
    String(firstValue || '').trim(),
    String(secondValue || '').trim(),
  )

const getHighlightedParts = (text, query) => {
  const source = String(text || '')
  const normalizedQuery = String(query || '').trim()

  if (!source || !normalizedQuery) {
    return [{ text: source, match: false }]
  }

  const lowerSource = source.toLowerCase()
  const lowerQuery = normalizedQuery.toLowerCase()
  const parts = []
  let cursor = 0

  while (cursor < source.length) {
    const matchIndex = lowerSource.indexOf(lowerQuery, cursor)

    if (matchIndex === -1) {
      parts.push({ text: source.slice(cursor), match: false })
      break
    }

    if (matchIndex > cursor) {
      parts.push({ text: source.slice(cursor, matchIndex), match: false })
    }

    parts.push({
      text: source.slice(matchIndex, matchIndex + normalizedQuery.length),
      match: true,
    })
    cursor = matchIndex + normalizedQuery.length
  }

  return parts.length ? parts : [{ text: source, match: false }]
}

const normalizeAreas = (areas) => {
  if (!Array.isArray(areas)) {
    return []
  }

  return areas
    .flatMap((area) => String(area || '').split(','))
    .map((area) => area.trim())
    .filter((area) => area && area.toLowerCase() !== 'default description')
    .sort(sortAlphabetically)
}

const normalizedOptions = computed(() =>
  (props.options || [])
    .map((branch) => ({
      ...branch,
      label: branch.label || branch.branch_name || branch.name || '',
      value: branch.value || branch.branch_name || branch.name || '',
      district: branch.district || '',
      municipality: branch.municipality || '',
      areas: normalizeAreas(branch.areas || branch.area || []),
    }))
    .sort((firstBranch, secondBranch) =>
      sortAlphabetically(firstBranch.label, secondBranch.label),
    ),
)

const selectedValue = computed(() =>
  typeof props.modelValue === 'object'
    ? props.modelValue?.value || props.modelValue?.label || ''
    : props.modelValue || '',
)

const selectedBranch = computed(() => {
  const currentValue = normalizeText(selectedValue.value)
  return normalizedOptions.value.find((branch) => {
    return (
      normalizeText(branch.value) === currentValue ||
      normalizeText(branch.label) === currentValue
    )
  })
})

const selectedBranchLabel = computed(
  () => selectedBranch.value?.label || selectedValue.value || 'Select Branch',
)

const selectedAreaLabel = computed(() => {
  if (selectedArea.value) {
    return selectedArea.value
  }

  return selectedBranch.value?.areas?.[0] || ''
})

const filteredBranches = computed(() => {
  const query = normalizeText(searchQuery.value)

  if (!query) {
    return normalizedOptions.value.map((branch) => ({
      ...branch,
      matchedAreas: branch.areas,
    }))
  }

  return normalizedOptions.value
    .map((branch) => {
      const branchLabel = normalizeText(branch.label)
      const branchValue = normalizeText(branch.value)
      const district = normalizeText(branch.district)
      const municipality = normalizeText(branch.municipality)
      const branchStartsWithQuery =
        branchLabel.startsWith(query) || branchValue.startsWith(query)
      const isBranchMatch =
        branchLabel.includes(query) || branchValue.includes(query)
      const districtStartsWithQuery = district.startsWith(query)
      const municipalityStartsWithQuery = municipality.startsWith(query)
      const isDistrictMatch = district.includes(query)
      const isMunicipalityMatch = municipality.includes(query)
      const matchedAreas = branch.areas
        .filter((area) => normalizeText(area).includes(query))
        .sort((firstArea, secondArea) => {
          const firstStartsWithQuery = normalizeText(firstArea).startsWith(query)
          const secondStartsWithQuery =
            normalizeText(secondArea).startsWith(query)

          if (firstStartsWithQuery !== secondStartsWithQuery) {
            return firstStartsWithQuery ? -1 : 1
          }

          return sortAlphabetically(firstArea, secondArea)
        })

      if (
        !isBranchMatch &&
        !isDistrictMatch &&
        !isMunicipalityMatch &&
        matchedAreas.length === 0
      ) {
        return null
      }

      let matchPriority = 5
      if (branchStartsWithQuery) {
        matchPriority = 0
      } else if (isBranchMatch) {
        matchPriority = 1
      } else if (
        matchedAreas.some((area) => normalizeText(area).startsWith(query))
      ) {
        matchPriority = 2
      } else if (matchedAreas.length) {
        matchPriority = 3
      } else if (districtStartsWithQuery || municipalityStartsWithQuery) {
        matchPriority = 4
      }

      return {
        ...branch,
        matchPriority,
        matchedAreas:
          isBranchMatch
            ? branch.areas
            : matchedAreas.length
              ? matchedAreas
              : isDistrictMatch || isMunicipalityMatch
                ? branch.areas
                : [],
      }
    })
    .filter(Boolean)
    .sort(
      (firstBranch, secondBranch) =>
        firstBranch.matchPriority - secondBranch.matchPriority ||
        sortAlphabetically(firstBranch.label, secondBranch.label),
    )
})

const isSelected = (branch) =>
  normalizeText(branch.value) === normalizeText(selectedValue.value) ||
  normalizeText(branch.label) === normalizeText(selectedValue.value)

const selectedAreaMatches = (branch, area) =>
  isSelected(branch) && normalizeText(selectedArea.value) === normalizeText(area)

const openDropdown = async () => {
  updateDropdownPosition()
  activeIndex.value = 0
  activeAreaIndex.value = 0
  isOpen.value = true
  await nextTick()
  searchInputRef.value?.focus?.()
  window.setTimeout(updateDropdownPosition, 0)
  scrollActiveIntoView()
}

const closeDropdown = () => {
  searchInputRef.value?.blur?.()
  blurActiveElement()
  isOpen.value = false
  searchQuery.value = ''
}

const restoreDialogScroll = () => {
  const dialog = wrapperRef.value?.closest?.('[role="dialog"]')
  if (!(dialog instanceof HTMLElement)) return

  if (dialogScrollElement !== dialog) {
    dialogScrollElement?.removeEventListener(
      'touchmove',
      allowDialogTouchScroll,
    )
    dialogScrollElement = dialog
    dialogScrollElement.addEventListener(
      'touchmove',
      allowDialogTouchScroll,
      { passive: true },
    )
  }

  dialog.style.overflowY = 'auto'
  dialog.style.touchAction = 'pan-y'
  dialog.style.webkitOverflowScrolling = 'touch'
}

const toggleDropdown = () => {
  if (isOpen.value) {
    closeDropdown()
    return
  }

  openDropdown()
}

const updateDropdownPosition = () => {
  const trigger = wrapperRef.value

  if (!(trigger instanceof HTMLElement)) {
    return
  }

  const rect = trigger.getBoundingClientRect()
  const visualViewport = window.visualViewport
  const viewportWidth = visualViewport?.width || window.innerWidth
  const viewportHeight = visualViewport?.height || window.innerHeight
  const viewportLeft = visualViewport?.offsetLeft || 0
  const viewportTop = visualViewport?.offsetTop || 0
  const viewportRight = viewportLeft + viewportWidth
  const viewportBottom = viewportTop + viewportHeight
  const preferredWidth = 320
  const maxWidth = Math.min(preferredWidth, viewportWidth - 16)
  const left = Math.min(rect.left, viewportRight - maxWidth - 8)
  const gap = 6
  const minimumUsefulSpace = 180
  const spaceBelow = viewportBottom - rect.bottom - gap - 8
  const spaceAbove = rect.top - viewportTop - gap - 8
  const placeBelow =
    spaceBelow >= minimumUsefulSpace || spaceBelow >= spaceAbove
  const availableSpace = placeBelow ? spaceBelow : spaceAbove
  const dropdownHeight = Math.max(
    96,
    Math.min(320, viewportHeight - 16, availableSpace),
  )
  const top = placeBelow
    ? rect.bottom + gap
    : Math.max(viewportTop + 8, rect.top - gap - dropdownHeight)

  dropdownStyle.value = {
    top: `${top}px`,
    left: `${Math.max(viewportLeft + 8, left)}px`,
    width: `${maxWidth}px`,
    height: `${dropdownHeight}px`,
    maxWidth: 'calc(100vw - 16px)',
  }
}

const handleSearchInput = () => {
  activeIndex.value = 0
  activeAreaIndex.value = 0
}

const moveActiveBranch = (step) => {
  if (!filteredBranches.value.length) {
    return
  }

  activeIndex.value += step
  activeAreaIndex.value = 0

  if (activeIndex.value < 0) {
    activeIndex.value = filteredBranches.value.length - 1
  }

  if (activeIndex.value >= filteredBranches.value.length) {
    activeIndex.value = 0
  }

  scrollActiveIntoView()
}

const moveActiveArea = (step) => {
  const branch = filteredBranches.value[activeIndex.value]
  const areas = branch?.matchedAreas || []

  if (!areas.length) {
    return
  }

  activeAreaIndex.value += step

  if (activeAreaIndex.value < 0) {
    activeAreaIndex.value = areas.length - 1
  }

  if (activeAreaIndex.value >= areas.length) {
    activeAreaIndex.value = 0
  }

  scrollActiveAreaIntoView()
}

const selectActiveResult = () => {
  const branch = filteredBranches.value[activeIndex.value]

  if (!branch) {
    return
  }

  const selectedAreaValue = props.autoSelectFirstArea
    ? branch.matchedAreas?.[activeAreaIndex.value] || ''
    : ''
  selectBranch(branch, selectedAreaValue)
}

const scrollActiveIntoView = async () => {
  await nextTick()
  const activeCard = resultBoxRef.value?.querySelector('[data-active="true"]')
  activeCard?.scrollIntoView?.({ block: 'nearest' })
}

const scrollActiveAreaIntoView = async () => {
  await nextTick()
  const activeArea = resultBoxRef.value?.querySelector('[data-active-area="true"]')
  activeArea?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' })
}

const selectBranch = async (branch, area = '') => {
  selectedArea.value =
    area || (props.autoSelectFirstArea ? branch.areas?.[0] || '' : '')

  const selection = {
    branch: branch.value,
    branch_name: branch.label,
    branch_code: branch.branch_code || '',
    district: branch.district || '',
    municipality: branch.municipality || '',
    area: selectedArea.value,
  }

  closeDropdown()
  await nextTick()
  restoreDialogScroll()

  emit('update:modelValue', branch.value)
  emit('change', selection)

  window.requestAnimationFrame(restoreDialogScroll)
  window.setTimeout(restoreDialogScroll, 150)
}

const handleDocumentPointerDown = (event) => {
  const target = event.target

  if (
    !wrapperRef.value?.contains(target) &&
    !dropdownRef.value?.contains?.(target)
  ) {
    closeDropdown()
  }
}

const handleDocumentKeydown = (event) => {
  const isInsideSelect = wrapperRef.value?.contains(document.activeElement)

  if (!isInsideSelect && !isOpen.value) {
    return
  }

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    event.stopPropagation()

    if (!isOpen.value) {
      openDropdown()
      return
    }

    moveActiveBranch(1)
    return
  }

  if (event.key === 'ArrowUp') {
    event.preventDefault()
    event.stopPropagation()

    if (!isOpen.value) {
      openDropdown()
      return
    }

    moveActiveBranch(-1)
    return
  }

  if (event.key === 'ArrowRight') {
    event.preventDefault()
    event.stopPropagation()

    if (!isOpen.value) {
      openDropdown()
      return
    }

    moveActiveArea(1)
    return
  }

  if (event.key === 'ArrowLeft') {
    event.preventDefault()
    event.stopPropagation()

    if (!isOpen.value) {
      openDropdown()
      return
    }

    moveActiveArea(-1)
    return
  }

  if (event.key === 'Enter') {
    event.preventDefault()
    event.stopPropagation()

    if (!isOpen.value) {
      openDropdown()
      return
    }

    selectActiveResult()
    return
  }

  if (event.key === 'Escape' && isOpen.value) {
    event.preventDefault()
    event.stopPropagation()
    closeDropdown()
    wrapperRef.value?.querySelector('button')?.focus?.()
  }
}

watch(filteredBranches, (branches) => {
  if (!branches.length) {
    activeIndex.value = 0
    activeAreaIndex.value = 0
    return
  }

  if (activeIndex.value >= branches.length) {
    activeIndex.value = 0
  }

  const areas = branches[activeIndex.value]?.matchedAreas || []
  if (activeAreaIndex.value >= areas.length) {
    activeAreaIndex.value = 0
  }
})

onMounted(() => {
  document.addEventListener('pointerdown', handleDocumentPointerDown, true)
  document.addEventListener('keydown', handleDocumentKeydown, true)
  window.addEventListener('resize', updateDropdownPosition)
  window.addEventListener('scroll', updateDropdownPosition, true)
  window.visualViewport?.addEventListener('resize', updateDropdownPosition)
  window.visualViewport?.addEventListener('scroll', updateDropdownPosition)
})

onBeforeUnmount(() => {
  dialogScrollElement?.removeEventListener(
    'touchmove',
    allowDialogTouchScroll,
  )
  dialogScrollElement = null
  document.removeEventListener('pointerdown', handleDocumentPointerDown, true)
  document.removeEventListener('keydown', handleDocumentKeydown, true)
  window.removeEventListener('resize', updateDropdownPosition)
  window.removeEventListener('scroll', updateDropdownPosition, true)
  window.visualViewport?.removeEventListener('resize', updateDropdownPosition)
  window.visualViewport?.removeEventListener('scroll', updateDropdownPosition)
})
</script>
