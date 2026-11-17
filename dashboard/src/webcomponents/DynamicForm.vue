<template>
  <div
    v-if="config"
    ref="formRoot"
    class="builder-dynamic-form flex h-full min-h-0 flex-col"
  >
    <!-- Tabs -->

    <div
      v-if="config.tabs"
      class="z-20 w-full shrink-0 border-b bg-white py-2"
    >
      <AppTabNavigation
        :model-value="activeTab"
        :buttons="formTabButtons"
        min-width="680px"
        @update:model-value="setActiveTab"
      />
    </div>

    <div class="flex min-h-0 flex-1 flex-col overflow-hidden">
      <div class="flex min-h-0 flex-1 flex-col rounded-lg bg-white p-4 shadow">
        <!-- Active Tab Title -->
        <div v-if="activeTabObject" class="mb-2 mt-4 flex-shrink-0">
          <h2 class="text-lg font-semibold">
            {{ friendlyLabel(activeTabObject.title || activeTabObject.label) }}
          </h2>
        </div>

        <!-- Sections & Fields: scrollable area -->
        <div class="flex-1 min-h-0 overflow-y-auto pr-2">
          <template v-for="(field, i) in visibleFields" :key="i">
            <!-- Section Header -->
            <div v-if="field.type === 'section'" class="mt-6 mb-2">
              <h3 class="text-base font-semibold">{{ sanitize(field.label) }}</h3>
              <hr class="border-gray-300 mt-1" />
            </div>

            <!-- Field Wrapper -->
            <div
              v-else
              :data-editor-field="fieldKey(field)"
              :class="[
                field.layout?.startsWith('inline')
                  ? 'inline-field mb-4'
                  : 'mb-4',
                focusedFieldKey === fieldKey(field)
                  ? 'rounded-lg ring-2 ring-green-400 ring-offset-4'
                  : '',
              ]"
            >
              <!-- Text Field -->
              <div v-if="field.type === 'text'" class="flex gap-8 pt-6">
                <div>
                  <h1 class="pb-2 text-sm font-medium">
                    {{ friendlyFieldLabel(field) }}
                  </h1>
                  <div class="w-44">
                    <p class="text-sm break-words">
                      {{ sanitize(field.hint) }}
                    </p>
                  </div>
                </div>
                <div class="flex-1">
                  <template v-if="fieldKey(field) === 'grid_num'">
                    <select
                      v-model="form[field.model || field.name]"
                      class="w-full rounded border border-gray-300 bg-white px-3 py-2 focus:border-green-500 focus:outline-none"
                    >
                      <option value="">Automatic</option>
                      <option :value="1">1 per row</option>
                      <option :value="2">2 per row</option>
                      <option :value="3">3 per row</option>
                      <option :value="4">4 per row</option>
                    </select>
                    <p class="mt-1 text-xs text-gray-500">
                      Automatic is recommended and adapts to the screen size.
                    </p>
                  </template>
                  <template v-else>
                    <p class="text-sm text-right">
                      {{
                        String(form[field.model || field.name] || '').length
                      }}
                      / 60
                    </p>
                    <input
                      type="text"
                      v-model="form[field.model || field.name]"
                      :placeholder="sanitize(field.placeholder)"
                      class="border border-gray-300 px-2 py-1 w-full focus:outline-none"
                      maxlength="60"
                    />
                  </template>
                  <div class="flex justify-end">
                    <a
                      v-if="fieldKey(field) !== 'grid_num'"
                      href="https://writingcenter.uci.edu/2024/04/25/writing-strong-titles/"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="italic text-sm inline-flex items-center gap-1"
                    >
                      <span>How to write a good title</span>
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        class="w-4 h-4"
                        aria-hidden="true"
                      >
                        <path
                          d="M10 5H8.2c-1.12 0-1.68 0-2.11.218A1.8 1.8 0 0 0 5.218 6.092C5 6.52 5 7.08 5 8.2v7.6c0 1.12 0 1.68.218 2.108.192.376.498.682.874.874C6.52 19 7.08 19 8.197 19H15.803c1.118 0 1.677 0 2.105-.218.376-.192.683-.498.874-.874C19 17.48 19 16.921 19 15.803V14M20 9V4M20 4H15M20 4L13 11"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </a>
                  </div>
                </div>
              </div>

              <!-- normal text -->
              <div
                v-else-if="field.type === 'normaltext'"
                class="flex gap-8 pt-6"
              >
                <div>
                  <h1 class="pb-2 text-sm font-medium">
                    {{ sanitize(field.label) }}
                  </h1>
                  <div class="w-44">
                    <p class="text-sm break-words">
                      {{ sanitize(field.hint) }}
                    </p>
                  </div>
                </div>
                <div class="flex-1">
                  <input
                    type="text"
                    v-model="form[field.model || field.name]"
                    :placeholder="sanitize(field.placeholder)"
                    class="border border-gray-300 px-2 py-1 w-full focus:outline-none"
                    maxlength="60"
                  />
                </div>
              </div>

              <!-- Textarea -->
              <div
                v-else-if="field.type === 'textarea'"
                class="flex gap-8 pb-6 pt-5"
              >
                <div>
                  <h1 class="pb-2 text-sm font-medium">
                    {{ sanitize(field.label) }}
                  </h1>
                  <div class="w-44">
                    <p class="text-sm break-words">
                      {{ sanitize(field.hint) }}
                    </p>
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-sm text-right">
                    {{ sanitize(field.label).length }} / 160
                  </p>
                  <textarea
                    v-model="form[field.model || field.name]"
                    :placeholder="sanitize(field.placeholder)"
                    class="w-full border border-gray-300 rounded px-3 py-2"
                  />
                  <div class="flex justify-end">
                    <a
                      href="https://www.goodstorycompany.com/blog/writing-descriptions"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="italic text-sm inline-flex items-center gap-1"
                    >
                      <span>Write a compelling description</span>
                      <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        class="w-4 h-4"
                        aria-hidden="true"
                      >
                        <path
                          d="M10 5H8.2c-1.12 0-1.68 0-2.11.218A1.8 1.8 0 0 0 5.218 6.092C5 6.52 5 7.08 5 8.2v7.6c0 1.12 0 1.68.218 2.108.192.376.498.682.874.874C6.52 19 7.08 19 8.197 19H15.803c1.118 0 1.677 0 2.105-.218.376-.192.683-.498.874-.874C19 17.48 19 16.921 19 15.803V14M20 9V4M20 4H15M20 4L13 11"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </a>
                  </div>
                </div>
              </div>
              <!-- 📧 Email Field -->
              <!-- 📧 Email Field -->
              <div
                v-else-if="field.type === 'email'"
                class="flex gap-8 pb-6 pt-5"
              >
                <div>
                  <h1 class="pb-2 text-sm font-medium">
                    {{ sanitize(field.label) }}
                  </h1>
                  <div class="w-44">
                    <p class="text-sm break-words">
                      {{ sanitize(field.hint) }}
                    </p>
                  </div>
                </div>
                <div class="flex-1">
                  <input
                    type="email"
                    v-model="form[field.model || field.name]"
                    :placeholder="sanitize(field.placeholder)"
                    required
                    class="w-full border border-gray-300 rounded px-3 py-2"
                    @blur="validateEmail(field.model || field.name)"
                  />
                  <!-- Optional validation message -->
                  <p
                    v-if="emailErrors[field.model || field.name]"
                    class="text-red-500 text-sm mt-1"
                  >
                    {{ emailErrors[field.model || field.name] }}
                  </p>
                </div>
              </div>

              <!-- 📞 Phone Field -->
              <div
                v-else-if="field.type === 'phone'"
                class="flex gap-8 pb-6 pt-5"
              >
                <div>
                  <h1 class="pb-2 text-sm font-medium">
                    {{ sanitize(field.label) }}
                  </h1>
                  <div class="w-44">
                    <p class="text-sm break-words">
                      {{ sanitize(field.hint) }}
                    </p>
                  </div>
                </div>
                <div class="flex-1">
                  <input
                    type="tel"
                    v-model="form[field.model || field.name]"
                    :placeholder="sanitize(field.placeholder)"
                    maxlength="10"
                    pattern="[0-9]{10}"
                    required
                    class="w-full border border-gray-300 rounded px-3 py-2"
                    @input="
                      form[field.model || field.name] = form[
                        field.model || field.name
                      ].replace(/[^0-9]/g, '')
                    "
                  />
                  <!-- Optional validation message -->
                  <p
                    v-if="
                      form[field.model || field.name] &&
                      !/^[0-9]{10}$/.test(form[field.model || field.name])
                    "
                    class="text-red-500 text-sm mt-1"
                  >
                    Please enter a valid 10-digit phone number
                  </p>
                </div>
              </div>

              <!-- Repeatable Field -->
              <div v-else-if="field.type === 'repeatable'" class="pt-6">
                <h3 class="mb-2 text-sm font-medium">
                  {{ sanitize(field.label) }}
                </h3>

                <div
                  v-for="(item, idx) in Array.isArray(field.value)
                    ? field.value
                    : []"
                  :key="idx"
                  class="flex items-center gap-2 mb-2"
                >
                  <input
                    type="text"
                    v-model="field.value[idx]"
                    class="border rounded px-3 py-2 w-full"
                    :placeholder="field.placeholder || 'Enter value'"
                  />

                  <button
                    v-if="field.value.length > 1"
                    type="button"
                    class="px-2 py-1 bg-red-500 text-white rounded"
                    @click="field.value.splice(idx, 1)"
                  >
                    ✕
                  </button>
                </div>

                <!-- Add More button -->
                <button
                  type="button"
                  class="mt-2 rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-gray-700"
                  @click="openSidebar"
                >
                  ➕ Add More
                </button>

                <!-- Sidebar -->
                <Sidebar v-model="showSidebar" width="500px">
                  <template #title>
                    New Block - {{ props.fieldName }}
                  </template>

                  <!-- Block Content -->
                  <div class="grid grid-cols-1 gap-4 overflow-y-auto mt-4">
                    <p class="mt-2 font-medium text-center">URL List</p>

                    <!-- Text Input -->
                    <input
                      type="text"
                      v-model="newRepeatableValue"
                      class="border rounded px-3 py-2 w-full"
                      placeholder="Enter URL"
                    />

                    <!-- Actions -->
                    <div class="flex justify-end gap-2 mt-4">
                      <button
                        type="button"
                        class="rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50"
                        @click="showSidebar = false"
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        class="rounded-lg bg-gray-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-gray-700"
                        @click="addRepeatableValue(field)"
                      >
                        Save
                      </button>
                    </div>
                  </div>
                </Sidebar>
              </div>

              <!-- Toggle -->
              <div
                v-else-if="field.type === 'toggle'"
                class="flex items-center gap-6 pt-6"
              >
                <div class="flex w-64 flex-col">
                  <h3 class="text-sm font-medium text-gray-900">
                    {{ sanitize(field.label) }}
                  </h3>
                  <div v-if="field.hint" class="mt-1">
                    <p class="text-sm leading-5 text-gray-500">
                      {{ sanitize(field.hint) }}
                    </p>
                  </div>
                </div>

                <div class="shrink-0">
                  <input
                    type="checkbox"
                    :id="'toggle-' + i"
                    class="peer sr-only"
                    v-model="field.value"
                    @change="alertToggle(field)"
                  />

                  <label
                    :for="'toggle-' + i"
                    class="relative block h-6 w-11 cursor-pointer rounded-full border border-gray-300 bg-gray-200 transition-colors duration-200 after:absolute after:left-0.5 after:top-0.5 after:h-[18px] after:w-[18px] after:rounded-full after:bg-white after:shadow-sm after:transition-transform after:duration-200 hover:bg-gray-300 peer-checked:border-green-600 peer-checked:bg-green-600 peer-checked:after:translate-x-5 peer-focus-visible:ring-2 peer-focus-visible:ring-green-200 peer-focus-visible:ring-offset-2"
                    :aria-label="sanitize(field.label)"
                  >
                    <span class="sr-only">Toggle {{ sanitize(field.label) }}</span>
                  </label>
                </div>
              </div>
              <div
                v-else-if="field.type === 'select'"
                class="flex gap-8 pb-6 pt-5"
              >
                <div class="w-44 shrink-0">
                  <h2 class="font-semibold pb-2">
                    {{ sanitize(field.label) }}
                  </h2>
                  <p v-if="field.hint" class="text-sm text-gray-500">
                    {{ sanitize(field.hint) }}
                  </p>
                </div>
                <select
                  v-model="form[fieldKey(field)]"
                  class="min-w-0 flex-1 rounded border border-gray-300 bg-white px-3 py-2 focus:border-blue-500 focus:outline-none"
                >
                  <option value="">
                    {{ sanitize(field.placeholder) || 'Select an option' }}
                  </option>
                  <option
                    v-for="option in normalizeSelectOptions(field.options)"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
              </div>

              <div
                v-else-if="field.type === 'commerce_link'"
                class="flex gap-8 pb-6 pt-5"
              >
                <div class="w-44 shrink-0">
                  <h2 class="font-semibold pb-2">
                    {{ sanitize(field.label) }}
                  </h2>
                  <p class="text-sm text-gray-500">
                    Choose the linked brand, category, product, or page.
                  </p>
                </div>
                <div class="min-w-0 flex-1">
                  <select
                    v-model="form[fieldKey(field)]"
                    :disabled="
                      !commerceDestinationType(field) || commerceOptionsLoading
                    "
                    class="w-full rounded border border-gray-300 bg-white px-3 py-2 disabled:bg-gray-100"
                  >
                    <option value="">
                      {{
                        commerceOptionsLoading
                          ? 'Loading destinations...'
                          : 'Select destination'
                      }}
                    </option>
                    <option
                      v-for="option in commerceDestinationOptions(field)"
                      :key="option.value"
                      :value="option.value"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                </div>
              </div>

              <div
                v-else-if="field.type === 'commerce_links'"
                class="pb-6 pt-5"
              >
                <div class="mb-4">
                  <h2 class="font-semibold">{{ sanitize(field.label) }}</h2>
                  <p class="mt-1 text-sm text-gray-500">
                    {{
                      isMultipleCommerceDestinations(field)
                        ? 'Select any combination of products, brands, categories, and pages.'
                        : 'Choose one product, brand, category, or page.'
                    }}
                  </p>
                </div>
                <div
                  v-if="displayedCommerceDestinations(field).length"
                  class="mb-4 rounded-xl border border-gray-200 bg-gray-50 p-3"
                >
                  <p
                    class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500"
                  >
                    {{
                      isMultipleCommerceDestinations(field)
                        ? 'Selected link order'
                        : 'Selected link'
                    }}
                  </p>
                  <draggable
                    :model-value="displayedCommerceDestinations(field)"
                    :item-key="commerceDestinationKey"
                    :disabled="!isMultipleCommerceDestinations(field)"
                    handle=".selection-drag-handle"
                    ghost-class="selection-drag-ghost"
                    :animation="180"
                    class="space-y-2"
                    @update:model-value="
                      reorderCommerceDestinations(field, $event)
                    "
                  >
                    <template #item="{ element: destination }">
                      <div
                        class="flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2"
                      >
                        <button
                          v-if="isMultipleCommerceDestinations(field)"
                          type="button"
                          class="selection-drag-handle flex h-8 w-8 cursor-grab touch-none items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700 active:cursor-grabbing"
                          :aria-label="`Drag to reorder ${commerceDestinationLabel(destination)}`"
                          title="Drag to reorder"
                        >
                          <span class="material-symbols-outlined"
                            >drag_indicator</span
                          >
                        </button>
                        <span class="min-w-0 truncate text-sm font-medium">
                          {{ commerceDestinationLabel(destination) }}
                        </span>
                        <span class="ml-auto text-xs capitalize text-gray-400">
                          {{ destination.type }}
                        </span>
                        <button
                          v-if="!isMultipleCommerceDestinations(field)"
                          type="button"
                          class="ml-2 flex h-7 w-7 items-center justify-center rounded text-gray-400 hover:bg-red-50 hover:text-red-600"
                          aria-label="Remove selected link"
                          title="Remove selected link"
                          @click="clearCommerceDestinations(field)"
                        >
                          <span class="material-symbols-outlined text-lg">close</span>
                        </button>
                      </div>
                    </template>
                  </draggable>
                </div>
                <div
                  v-if="commerceOptionsLoading"
                  class="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-500"
                >
                  Loading destinations...
                </div>
                <div v-else class="overflow-hidden rounded-xl border border-gray-200 bg-white">
                  <div
                    class="flex overflow-x-auto border-b border-gray-200 bg-gray-50 px-2 pt-2"
                    role="tablist"
                    :aria-label="`${sanitize(field.label)} destination types`"
                  >
                    <button
                      v-for="group in commerceDestinationGroups"
                      :key="group.type"
                      type="button"
                      role="tab"
                      :aria-selected="activeCommerceDestinationType(field) === group.type"
                      class="inline-flex shrink-0 items-center gap-2 rounded-t-lg border-b-2 px-4 py-2.5 text-sm font-semibold transition-colors"
                      :class="
                        activeCommerceDestinationType(field) === group.type
                          ? 'border-green-600 bg-white text-green-700'
                          : 'border-transparent text-gray-500 hover:text-gray-800'
                      "
                      @click="setActiveCommerceDestinationType(field, group.type)"
                    >
                      {{ group.label }}
                      <span
                        v-if="selectedCommerceDestinationCount(field, group.type)"
                        class="rounded-full bg-green-100 px-1.5 py-0.5 text-[10px] leading-none text-green-700"
                      >
                        {{ selectedCommerceDestinationCount(field, group.type) }}
                      </span>
                    </button>
                  </div>

                  <template
                    v-for="group in commerceDestinationGroups"
                    :key="group.type"
                  >
                    <section
                      v-if="activeCommerceDestinationType(field) === group.type"
                      role="tabpanel"
                      class="p-4"
                    >
                      <div class="mb-3 flex items-center justify-between gap-2">
                        <h3 class="text-sm font-semibold text-gray-800">
                          Select {{ group.label }}
                        </h3>
                        <button
                          v-if="['product', 'brand', 'category'].includes(group.type)"
                          type="button"
                          class="text-xs font-semibold text-green-700 hover:text-green-900 hover:underline"
                          @click="openInlineCommerceDialog(group.type, field)"
                        >
                          + Add {{ group.singular }}
                        </button>
                      </div>
                      <div
                        v-if="!commerceOptions[group.type]?.length"
                        class="rounded-lg border border-dashed border-gray-200 p-5 text-center text-sm text-gray-400"
                      >
                        None available
                      </div>
                      <div
                        v-else
                        class="grid max-h-80 gap-1 overflow-y-auto pr-1 sm:grid-cols-2"
                      >
                        <label
                          v-for="option in commerceOptions[group.type] || []"
                          :key="`${group.type}-${option.value}`"
                          class="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm hover:bg-gray-50"
                        >
                          <input
                            :type="isMultipleCommerceDestinations(field) ? 'checkbox' : 'radio'"
                            :name="`commerce-destination-${commerceDestinationFieldKey(field)}`"
                            :checked="
                              isCommerceDestinationSelected(
                                field,
                                group.type,
                                option.value,
                              )
                            "
                            @change="
                              toggleCommerceDestination(field, group.type, option)
                            "
                          />
                          <span class="min-w-0 truncate">{{ option.label }}</span>
                        </label>
                      </div>
                    </section>
                  </template>
                </div>
              </div>

              <div v-else-if="field.type === 'repeater'" class="bg-white">
                <!-- Pass the field object and current form context -->
                <RepeaterField
                  :field="field"
                  :form="form"
                  :open-item-request="
                    focusedRepeaterItem?.fieldKey === fieldKey(field)
                      ? focusedRepeaterItem
                      : null
                  "
                  @update:value="(val) => (form[fieldKey(field)] = val)"
                />
              </div>

              <div v-else-if="field.type === 'categories'" class="pb-6 pt-5">
                <div class="mb-3 flex items-start justify-between gap-4">
                  <div>
                    <h2 class="font-semibold">{{ sanitize(field.label) }}</h2>
                    <p class="mt-1 text-sm text-gray-500">
                      {{
                        sanitize(field.hint) ||
                        'Choose which categories appear below the main navigation.'
                      }}
                    </p>
                  </div>
                  <button
                    type="button"
                    class="shrink-0 text-xs font-semibold text-green-700 hover:text-green-900 hover:underline"
                    @click="openInlineCategoryDialog(field)"
                  >
                    + Add Category
                  </button>
                </div>
                <div
                  v-if="commerceOptionsLoading"
                  class="rounded-lg border bg-gray-50 p-4 text-sm text-gray-500"
                >
                  Loading categories...
                </div>
                <div
                  v-else-if="!commerceOptions.category?.length"
                  class="rounded-lg border border-dashed p-4 text-sm text-gray-500"
                >
                  No categories available. Create a category first.
                </div>
                <template v-else>
                  <p class="mb-3 text-sm text-gray-500">
                    Click a category to select it, then drag the same row to set
                    its order.
                  </p>
                  <draggable
                    :model-value="orderedCategoryOptions(field)"
                    item-key="value"
                    handle=".selection-drag-handle"
                    ghost-class="selection-drag-ghost"
                    :animation="180"
                    class="space-y-2"
                    @update:model-value="reorderCategoryOptions(field, $event)"
                  >
                    <template #item="{ element: option }">
                      <div
                        class="flex cursor-pointer items-center gap-3 rounded-lg border px-3 py-2 transition"
                        :class="
                          selectedCategoryIds(field).includes(
                            String(option.value),
                          )
                            ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                            : 'border-gray-200 bg-white hover:border-gray-400'
                        "
                        @click="toggleMenuCategory(field, option.value)"
                      >
                        <button
                          type="button"
                          class="selection-drag-handle flex h-8 w-8 shrink-0 cursor-grab touch-none items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700 active:cursor-grabbing"
                          :aria-label="`Drag to reorder ${option.label}`"
                          title="Drag to reorder"
                          @click.stop
                        >
                          <span class="material-symbols-outlined"
                            >drag_indicator</span
                          >
                        </button>
                        <span
                          class="min-w-0 flex-1 truncate text-sm font-medium"
                        >
                          {{ option.label }}
                        </span>
                      </div>
                    </template>
                  </draggable>
                </template>
              </div>

              <!-- File Field -->
              <div v-else-if="field.type === 'file'" class="bg-white">
                <div class="grid grid-cols-[12rem_minmax(0,1fr)] gap-6 border-b border-gray-100 pb-8">
                  <div class="min-w-0">
                    <h2 class="pb-2 text-sm font-medium text-gray-900">
                      {{ sanitize(field.label) }}
                    </h2>
                    <div class="break-words">
                      <p class="text-sm leading-5 text-gray-500">
                        {{ fileFieldHint(field) }}
                      </p>
                    </div>
                  </div>

                  <div class="w-fit">
                    <button
                      type="button"
                      class="group relative flex h-24 w-36 items-center justify-center overflow-hidden rounded-lg border border-dashed border-gray-300 bg-gray-50 transition hover:border-green-500 hover:bg-green-50/40 focus:outline-none focus:ring-2 focus:ring-green-200 focus:ring-offset-2"
                      :disabled="uploadingFiles[fieldKey(field)]"
                      @click="openFileDialog(fieldKey(field))"
                    >
                      <img
                        v-if="previewUrls[fieldKey(field)] || form[fieldKey(field)]"
                        :src="previewUrls[fieldKey(field)] || form[fieldKey(field)]"
                        :alt="`${sanitize(field.label)} preview`"
                        class="h-full w-full object-cover"
                      />

                      <span
                        v-if="previewUrls[fieldKey(field)] || form[fieldKey(field)]"
                        class="absolute inset-0 flex items-center justify-center bg-black/0 text-sm font-medium text-white opacity-0 transition group-hover:bg-black/45 group-hover:opacity-100"
                      >
                        Replace image
                      </span>

                      <span v-else class="flex flex-col items-center gap-1 px-2 text-center">
                        <span class="material-symbols-outlined text-2xl text-gray-400 group-hover:text-green-700">add_photo_alternate</span>
                        <span class="text-xs font-medium text-gray-700">Upload image</span>
                      </span>

                      <span
                        v-if="uploadingFiles[fieldKey(field)]"
                        class="absolute inset-0 flex items-center justify-center bg-white/85 text-sm font-medium text-green-700"
                      >
                        Uploading…
                      </span>
                    </button>

                    <div
                      v-if="previewUrls[fieldKey(field)] || form[fieldKey(field)]"
                      class="mt-2 flex items-center gap-2"
                    >
                      <button
                        type="button"
                        class="rounded-lg bg-gray-900 px-3 py-2 text-sm font-medium text-white transition hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-50"
                        :disabled="uploadingFiles[fieldKey(field)]"
                        @click="openFileDialog(fieldKey(field))"
                      >
                        Replace image
                      </button>
                      <button
                        type="button"
                        class="rounded-lg px-3 py-2 text-sm font-medium text-red-600 transition hover:bg-red-50"
                        @click="removeFile(fieldKey(field))"
                      >
                        Remove
                      </button>
                    </div>
                    <p v-if="uploadErrors[fieldKey(field)]" class="mt-2 text-xs text-red-600">
                      {{ uploadErrors[fieldKey(field)] }}
                    </p>

                    <input
                      :ref="(el) => (fileInputs[fieldKey(field)] = el)"
                      type="file"
                      class="hidden"
                      accept="image/*"
                      @change="onFileChange($event, fieldKey(field))"
                    />
                  </div>
                </div>
              </div>

              <!-- <div v-else-if="field.type === 'product'" class="mt-4">
                <div class="flex flex-col-3 gap-4">
                  <div
                    v-for="product in products"
                    :key="product.name"
                    class="flex gap-4 items-center border p-3 rounded bg-gray-50"
                  >
                    <img
                      v-if="product.product_image"
                      :src="product.product_image"
                      alt="Product Image"
                      class="w-20 h-20 object-cover rounded"
                    />
                    <div>
                      <p class="font-medium">{{ product.product_name }}</p>
                      <p class="text-sm text-gray-600">
                        {{ product.product_description }}
                      </p>
                      <p class="text-sm font-bold">Rs {{ product.price }}</p>
                    </div>
                  </div>
                </div>
              </div> -->

              <div v-else-if="field.type === 'product'" class="mt-4">
                <div class="mb-4 flex justify-end">
                  <button
                    type="button"
                    class="inline-flex items-center rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-gray-700"
                    @click="openInlineProductDialog(field)"
                  >
                    + Add Product
                  </button>
                </div>
                <div
                  v-if="productsLoading"
                  class="rounded-lg border border-gray-200 bg-gray-50 p-5 text-center text-sm text-gray-500"
                >
                  Loading products...
                </div>
                <div
                  v-else-if="!products.length"
                  class="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-5 text-center"
                >
                  <p class="font-semibold text-gray-800">
                    No products available
                  </p>
                  <p class="mt-1 text-sm text-gray-500">
                    Use Add Product above to create and select one here.
                  </p>
                </div>
                <template v-else>
                  <p class="mb-3 text-sm text-gray-500">
                    Select products here, then drag the same cards to set their
                    display order.
                  </p>
                  <draggable
                    :model-value="orderedProductCards(field)"
                    item-key="name"
                    handle=".selection-drag-handle"
                    ghost-class="selection-drag-ghost"
                    :animation="180"
                    class="space-y-2"
                    @update:model-value="reorderProductCards(field, $event)"
                  >
                    <template #item="{ element: product }">
                      <div
                        @click="toggleProduct(field, product)"
                        class="flex cursor-pointer flex-wrap items-center gap-3 rounded-lg border px-3 py-2 transition"
                        :class="
                          isProductSelected(field, product.name)
                            ? 'border-blue-500 bg-blue-50 ring-1 ring-blue-500'
                            : 'border-gray-200 bg-white hover:border-gray-400'
                        "
                      >
                        <button
                          type="button"
                          class="selection-drag-handle flex h-8 w-8 shrink-0 cursor-grab touch-none items-center justify-center rounded text-gray-400 hover:bg-gray-100 hover:text-gray-700 active:cursor-grabbing"
                          :aria-label="`Drag to reorder ${product.product_name}`"
                          title="Drag to reorder"
                          @click.stop
                        >
                          <span class="material-symbols-outlined"
                            >drag_indicator</span
                          >
                        </button>
                        <img
                          v-if="product.product_image"
                          :src="product.product_image"
                          alt=""
                          class="h-10 w-10 shrink-0 rounded object-contain"
                        />
                        <p class="min-w-0 flex-1 truncate text-sm font-medium">
                          {{ product.product_name }}
                        </p>
                        <button
                          v-if="isProductSelected(field, product.name)"
                          type="button"
                          class="rounded bg-gray-900 px-2 py-1 text-xs font-medium text-white hover:bg-gray-700"
                          @click.stop="emit('edit-product-style', product)"
                        >
                          Card Style
                        </button>
                      </div>
                    </template>
                  </draggable>
                </template>
              </div>

              <div v-else-if="field.type === 'editor'" class="bg-white">
                <div class="flex gap-5 pb-6 pt-6">
                  <div>
                    <h2 class="font-semibold pb-3">
                      {{ sanitize(field.label) }}
                    </h2>
                    <div class="w-44 break-words">
                      <p class="text-sm">{{ sanitize(field.hint) }}</p>
                    </div>
                  </div>
                  <div class="flex-1 pr-8">
                    <div class="rounded-xl">
                      <QuillEditor
                        v-model:content="form[fieldKey(field)]"
                        contentType="html"
                        :options="editorOptions"
                        class="w-full min-h-14"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="field.type === 'draggable'" class="bg-white">
                <DraggableField
                  :field="field"
                  :block-names="templateBlockNames"
                  v-model="form[fieldKey(field)]"
                />
              </div>

              <div v-else-if="field.type === 'datetime'">
                <div class="flex gap-6 pb-4 pt-6">
                  <div>
                    <h2 class="font-semibold pb-3">
                      {{ field.label || 'Date & Time' }}
                    </h2>
                  </div>
                  <div>
                    <VueDatePicker
                      v-model="form[fieldKey(field)]"
                      :is-24="false"
                      :enable-time-picker="true"
                      format="MM/dd/yyyy hh:mm a"
                    />
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  computed,
  watch,
  reactive,
  onMounted,
  watchEffect,
  nextTick,
} from 'vue'
import draggable from 'vuedraggable'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { VueDatePicker } from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import AddBlock from '../components/AddBlock.vue'
import EditBlock from '../components/EditBlock.vue'
import Sidebar from '../components/Sidebar.vue'
import AppTabNavigation from '../components/AppTabNavigation.vue'
import RepeaterField from './RepeaterField.vue'
import DraggableField from './DraggableField.vue'
import { useRoute } from 'vue-router'
import {
  requestBuilderBrandCreation,
  requestBuilderCategoryCreation,
  requestBuilderProductCreation,
} from '@/composables/useBuilderCommerceCreator'

const props = defineProps({
  config: { type: Object, required: true },
  data: { type: Object, default: () => ({}) },
  form: { type: Object, required: true },
  productSettings: { type: Object, default: () => ({}) },
  focusedFieldKey: { type: String, default: '' },
  focusedRepeaterItem: { type: Object, default: null },
})
const emit = defineEmits([
  'edit-product-style',
  'edit-product-action-style',
  'toggle-product-add-to-cart',
])

const templateBlockNames = computed(() => {
  const starter = props.config?.starter_content || {}
  return ['header', 'main', 'footer'].flatMap((area) =>
    (Array.isArray(starter[area]) ? starter[area] : [])
      .map((block) => block?.name || block?.block_name)
      .filter(Boolean),
  )
})
const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token') || ''
const route = useRoute()
const editingBlock = ref(null)
const formRoot = ref(null)
const editingField = ref(null)
const showEditSidebar = ref(false)

function fileFieldHint(field) {
  const hint = sanitize(field?.hint)
  if (!hint || hint.includes('photo16x9.com')) {
    return 'Recommended: a 16:9 PNG, JPG, or WebP image.'
  }
  return hint
}

function handleClick(block) {
  editingBlock.value = block
  showEditSidebar.value = true
}

const products = ref([])
const productsLoading = ref(false)
const commerceOptions = ref({ brand: [], category: [], product: [], page: [] })
const commerceOptionsLoading = ref(false)
const commerceDestinationTabByField = reactive({})
const commerceDestinationGroups = [
  {
    type: 'product',
    label: 'Products',
    singular: 'Product',
  },
  { type: 'brand', label: 'Brands', singular: 'Brand' },
  {
    type: 'category',
    label: 'Categories',
    singular: 'Category',
  },
  { type: 'page', label: 'Builder Pages' },
]
const showSidebar = ref(false)
const newRepeatableValue = ref('')

const openSidebar = () => {
  newRepeatableValue.value = ''
  showSidebar.value = true
}

const newItem = ref('')

// Add a new top-level section
function addItem(field) {
  if (!field.value) field.value = []

  const newObj = {}
  for (const subField of field.fields || []) {
    // Initialize nested repeater fields as empty arrays
    newObj[subField.name] = subField.type === 'repeater' ? [] : ''
  }

  field.value.push(newObj)
}

const normalizedConfig = computed(() => {
  const cfg = props.config || {}

  // Case 1: normal fields
  if (cfg.fields) {
    return {
      type: 'fields',
      tabs: [],
      fields: cfg.fields,
    }
  }

  // Case 2: tab mode
  if (cfg.tabs) {
    const active = cfg.tabs.find((t) => t.active) ||
      cfg.tabs[0] || { fields: [] }
    return {
      type: 'tabs',
      tabs: cfg.tabs,
      fields: active.fields || [],
    }
  }

  return { type: 'none', tabs: [], fields: [] }
})

// Remove a top-level section
function removeItem(field, index) {
  field.value.splice(index, 1)
}

// Add a nested item inside a section
function addNestedItem(parentItem, subField) {
  if (!parentItem[subField.name]) parentItem[subField.name] = []

  const newNestedObj = {}
  for (const nestedField of subField.fields || []) {
    newNestedObj[nestedField.name] = ''
  }

  parentItem[subField.name].push(newNestedObj)
}

// Remove a nested item inside a section
function removeNestedItem(parentItem, subFieldName, index) {
  parentItem[subFieldName].splice(index, 1)
}

// const removeItem = (field, index) => {
//   if (field && Array.isArray(field.value)) {
//     field.value.splice(index, 1)
//   }
// }

const addRepeatableValue = (field) => {
  if (!Array.isArray(field.value)) field.value = []
  if (newRepeatableValue.value.trim()) {
    field.value.push(newRepeatableValue.value.trim())
  }
  showSidebar.value = false
}

function toggleProduct(field, product) {
  const currentValue = Array.isArray(field.value) ? [...field.value] : []
  const productId = String(product.name)
  const index = currentValue.findIndex((value) => String(value) === productId)
  if (index === -1) {
    currentValue.push(product.name)
  } else {
    currentValue.splice(index, 1)
  }

  field.value = currentValue
  const key = fieldKey(field)
  if (key) props.form[key] = currentValue

  //  //  console.log('Selected products:', field.value)
}

function isProductSelected(field, productId) {
  return (
    Array.isArray(field.value) &&
    field.value.some((value) => String(value) === String(productId))
  )
}

function orderedProductCards(field) {
  const productsById = new Map(
    products.value.map((product) => [String(product.name), product]),
  )
  const selectedProducts = (Array.isArray(field.value) ? field.value : [])
    .map((productId) => productsById.get(String(productId)))
    .filter(Boolean)
  const selectedIds = new Set(
    selectedProducts.map((product) => String(product.name)),
  )

  return [
    ...selectedProducts,
    ...products.value.filter(
      (product) => !selectedIds.has(String(product.name)),
    ),
  ]
}

function reorderProductCards(field, orderedProducts) {
  products.value = [...orderedProducts]
  const selectedIds = new Set(
    (Array.isArray(field.value) ? field.value : []).map(String),
  )
  const orderedIds = orderedProducts
    .filter((product) => selectedIds.has(String(product.name)))
    .map((product) => product.name)
  field.value = orderedIds
  const key = fieldKey(field)
  if (key) props.form[key] = orderedIds
}

function productShowsAddToCart(productId) {
  return props.productSettings?.[String(productId)]?.show_add_to_cart !== false
}

function toggleProductAddToCart(product, show) {
  emit('toggle-product-add-to-cart', {
    product,
    show: Boolean(show),
  })
}

function alertToggle(field) {
  const key = fieldKey(field)
  if (key) props.form[key] = Boolean(field.value)
}

function normalizeSelectOptions(options) {
  const values = Array.isArray(options)
    ? options
    : String(options || '').split(/\r?\n/)
  return values
    .map((option) => {
      if (option && typeof option === 'object') {
        return {
          value: String(option.value ?? option.label ?? ''),
          label: String(option.label ?? option.value ?? ''),
        }
      }
      return { value: String(option).trim(), label: String(option).trim() }
    })
    .filter((option) => option.value)
}

function commerceDestinationType(field) {
  const sourceField = field.destination_type_field || 'destination_type'
  return String(props.form[sourceField] || '').toLowerCase()
}

function commerceDestinationOptions(field) {
  return commerceOptions.value[commerceDestinationType(field)] || []
}

function normalizedCommerceDestinations(field) {
  const value = props.form[fieldKey(field)]
  return Array.isArray(value) ? value : []
}

function isMultipleCommerceDestinations(field) {
  if (typeof field?.multiple === 'boolean') return field.multiple
  return sanitize(field?.label).trim().toLowerCase() !== 'link'
}

function displayedCommerceDestinations(field) {
  const destinations = normalizedCommerceDestinations(field)
  return isMultipleCommerceDestinations(field)
    ? destinations
    : destinations.slice(0, 1)
}

function commerceDestinationFieldKey(field) {
  return fieldKey(field) || sanitize(field?.label) || 'commerce-links'
}

function activeCommerceDestinationType(field) {
  return (
    commerceDestinationTabByField[commerceDestinationFieldKey(field)] ||
    displayedCommerceDestinations(field)[0]?.type ||
    'product'
  )
}

function setActiveCommerceDestinationType(field, type) {
  commerceDestinationTabByField[commerceDestinationFieldKey(field)] = type
}

function selectedCommerceDestinationCount(field, type) {
  return displayedCommerceDestinations(field).filter(
    (destination) => String(destination?.type) === String(type),
  ).length
}

function commerceDestinationKey(destination) {
  return `${destination?.type || ''}:${destination?.value || ''}`
}

function commerceDestinationLabel(destination) {
  if (destination?.label) return destination.label
  const options = commerceOptions.value[destination?.type] || []
  return (
    options.find(
      (option) => String(option.value) === String(destination?.value),
    )?.label ||
    destination?.value ||
    'Linked item'
  )
}

function reorderCommerceDestinations(field, orderedDestinations) {
  const ordered = orderedDestinations.map((destination) => ({
    ...destination,
  }))
  const key = fieldKey(field)
  if (key) props.form[key] = ordered
  field.value = ordered
}

function clearCommerceDestinations(field) {
  const key = fieldKey(field)
  if (key) props.form[key] = []
  field.value = []
}

function selectedCategoryIds(field) {
  const value = props.form[fieldKey(field)]
  return Array.isArray(value) ? value.map((item) => String(item)) : []
}

function orderedCategoryOptions(field) {
  const categoriesById = new Map(
    (commerceOptions.value.category || []).map((option) => [
      String(option.value),
      option,
    ]),
  )
  const selectedCategories = selectedCategoryIds(field)
    .map((categoryId) => categoriesById.get(categoryId))
    .filter(Boolean)
  const selectedIds = new Set(
    selectedCategories.map((option) => String(option.value)),
  )

  return [
    ...selectedCategories,
    ...(commerceOptions.value.category || []).filter(
      (option) => !selectedIds.has(String(option.value)),
    ),
  ]
}

function reorderCategoryOptions(field, orderedCategories) {
  commerceOptions.value.category = [...orderedCategories]
  const selectedIds = new Set(selectedCategoryIds(field))
  const orderedIds = orderedCategories
    .filter((option) => selectedIds.has(String(option.value)))
    .map((option) => String(option.value))
  field.value = orderedIds
  const key = fieldKey(field)
  if (key) props.form[key] = orderedIds
}

function toggleMenuCategory(field, categoryId) {
  const key = fieldKey(field)
  const selected = selectedCategoryIds(field)
  const normalizedId = String(categoryId)
  const index = selected.indexOf(normalizedId)
  if (index >= 0) selected.splice(index, 1)
  else selected.push(normalizedId)
  props.form[key] = selected
  field.value = selected
}

function isCommerceDestinationSelected(field, type, value) {
  return displayedCommerceDestinations(field).some(
    (destination) =>
      String(destination?.type) === String(type) &&
      String(destination?.value) === String(value),
  )
}

function toggleCommerceDestination(field, type, option) {
  const key = fieldKey(field)
  if (!isMultipleCommerceDestinations(field)) {
    const selected = [{ type, value: option.value, label: option.label }]
    props.form[key] = selected
    field.value = selected
    return
  }
  const destinations = normalizedCommerceDestinations(field).map((item) => ({
    ...item,
  }))
  const index = destinations.findIndex(
    (destination) =>
      String(destination?.type) === String(type) &&
      String(destination?.value) === String(option.value),
  )
  if (index >= 0) {
    destinations.splice(index, 1)
  } else {
    destinations.push({ type, value: option.value, label: option.label })
  }
  props.form[key] = destinations
  field.value = destinations
}

function openInlineProductDialog(field) {
  requestBuilderProductCreation((product) =>
    handleInlineProductCreated(field, 'product-field', product),
  )
}

function openInlineCategoryDialog(field) {
  requestBuilderCategoryCreation((categoryId) =>
    handleInlineCategoryCreated(field, 'category-field', categoryId),
  )
}

function openInlineCommerceDialog(type, field) {
  if (type === 'product') {
    requestBuilderProductCreation((product) =>
      handleInlineProductCreated(field, 'commerce-links', product),
    )
    return
  }
  if (type === 'category') {
    requestBuilderCategoryCreation((categoryId) =>
      handleInlineCategoryCreated(field, 'commerce-links', categoryId),
    )
    return
  }
  if (type === 'brand') {
    requestBuilderBrandCreation((brandId) =>
      handleInlineBrandCreated(field, brandId),
    )
  }
}

async function handleInlineProductCreated(field, kind, savedProduct) {
  const savedId = savedProduct?.name || savedProduct?.id
  await Promise.all([fetchProducts(), fetchCommerceOptions()])
  if (!field || !savedId) return

  if (kind === 'product-field') {
    const product = products.value.find(
      (item) => String(item.name) === String(savedId),
    )
    if (product && !isProductSelected(field, savedId)) {
      toggleProduct(field, product)
    }
    return
  }

  const option = (commerceOptions.value.product || []).find(
    (item) => String(item.value) === String(savedId),
  )
  if (
    option &&
    !isCommerceDestinationSelected(field, 'product', savedId)
  ) {
    toggleCommerceDestination(field, 'product', option)
  }
}

async function handleInlineCategoryCreated(field, kind, savedId) {
  await fetchCommerceOptions()
  if (!field || !savedId) return

  if (kind === 'category-field') {
    if (!selectedCategoryIds(field).includes(String(savedId))) {
      toggleMenuCategory(field, savedId)
    }
    return
  }

  const option = (commerceOptions.value.category || []).find(
    (item) => String(item.value) === String(savedId),
  )
  if (
    option &&
    !isCommerceDestinationSelected(field, 'category', savedId)
  ) {
    toggleCommerceDestination(field, 'category', option)
  }
}

async function handleInlineBrandCreated(field, savedId) {
  await fetchCommerceOptions()
  if (!field || !savedId) return

  const option = (commerceOptions.value.brand || []).find(
    (item) => String(item.value) === String(savedId),
  )
  if (
    option &&
    !isCommerceDestinationSelected(field, 'brand', savedId)
  ) {
    toggleCommerceDestination(field, 'brand', option)
  }
}

function selectedWebsiteId() {
  try {
    const website = JSON.parse(localStorage.getItem('selectedWebsite') || '{}')
    return website.name || website.website_id || ''
  } catch {
    return ''
  }
}

async function fetchCommerceOptions() {
  commerceOptionsLoading.value = true
  try {
    const params = new URLSearchParams()
    const websiteId = selectedWebsiteId()
    if (websiteId) params.set('website_id', websiteId)
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_commerce_link_options?${params}`,
      {
        headers: {
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      },
    )
    const body = await response.json()
    const result = body?.message ?? body
    if (result?.status === 'success') {
      commerceOptions.value = result.data || commerceOptions.value
    }
  } catch (error) {
    console.error('Failed to load commerce destinations:', error)
  } finally {
    commerceOptionsLoading.value = false
  }
}

async function fetchProducts() {
  productsLoading.value = true
  try {
    const websiteId = selectedWebsiteId()
    const websiteQuery = websiteId
      ? `?website_id=${encodeURIComponent(websiteId)}`
      : ''
    const res = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_products${websiteQuery}`,
      {
        headers: {
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
          Authorization: `Bearer ${token}`,
        },
      },
    )
    const data = await res.json()
    const payload = data?.message
    if (payload?.status === 'success') {
      products.value = Array.isArray(payload.data) ? payload.data : []
    } else if (Array.isArray(payload?.message)) {
      // Compatibility with the previous get_products response shape.
      products.value = payload.message
    } else {
      products.value = []
      console.error('Failed to fetch products:', payload?.message || data)
    }
  } catch (err) {
    console.error('Failed to fetch products:', err)
    products.value = []
  } finally {
    productsLoading.value = false
  }
}

onMounted(() => {
  fetchProducts()
  fetchCommerceOptions()
})

const emailErrors = reactive({})

function validateEmail(fieldKey) {
  const value = props.form[fieldKey]
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/ // simple email regex
  if (!value) {
    emailErrors[fieldKey] = 'Email is required'
  } else if (!regex.test(value)) {
    emailErrors[fieldKey] = 'Please enter a valid email address'
  } else {
    emailErrors[fieldKey] = ''
  }
}

const fileInputs = reactive({}) // store ref for each input
const previewUrls = reactive({}) // store preview per field
const uploadingFiles = reactive({})
const uploadErrors = reactive({})

function openFileDialog(fieldName) {
  if (fileInputs[fieldName]) {
    fileInputs[fieldName].click()
  }
}

function removeFile(fieldName) {
  const preview = previewUrls[fieldName]
  if (preview?.startsWith('blob:')) URL.revokeObjectURL(preview)
  previewUrls[fieldName] = ''
  props.form[fieldName] = ''
  uploadErrors[fieldName] = ''
  if (fileInputs[fieldName]) fileInputs[fieldName].value = ''
}

// function onFileChange(event, fieldName) {
//   const file = event.target.files[0]
//   if (!file) return

//   console.log('Selected file:', file)

//   // Generate local preview
//   previewUrls[fieldName] = URL.createObjectURL(file)

//   // Convert file to base64
//   const reader = new FileReader()
//   reader.onload = () => {
//     const base64String = reader.result
//     props.form[fieldName] = base64String
//     console.log(
//       `Stored base64 in form[${fieldName}]:`,
//       base64String.substring(0, 100) + '...',
//     )
//   }
//   reader.readAsDataURL(file)
// }

async function onFileChange(event, fieldName) {
  const file = event.target.files[0]
  if (!file) return

  uploadErrors[fieldName] = ''
  uploadingFiles[fieldName] = true

  const previousPreview = previewUrls[fieldName]
  if (previousPreview?.startsWith('blob:')) URL.revokeObjectURL(previousPreview)

  // console.log('Selected file:', file)

  // Generate temporary local preview while uploading
  previewUrls[fieldName] = URL.createObjectURL(file)

  try {
    // Prepare FormData
    const formData = new FormData()
    formData.append('file', file)

    // Logos are stored as UUID-named File records attached to this page.
    // The returned File URL remains local to the block form until Block Save.
    const isLogoField = String(fieldName).toLowerCase().includes('logo')
    if (isLogoField) {
      formData.append('is_builder_logo', '1')
      formData.append('page_name', String(route.params.page_name || ''))
    }

    // Upload to backend
    const res = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.upload_file`,
      {
        method: 'POST',
        headers: {
          'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      },
    )

    const data = await res.json()
    if (data?.message?.file_url) {
      // Store the file URL in form
      props.form[fieldName] = data.message.file_url
      // Update preview to backend URL
      previewUrls[fieldName] = data.message.file_url
      // console.log(
      //   `Stored file URL in form[${fieldName}]:`,
      //   data.message.file_url,
      // )
    } else {
      console.error('File upload failed:', data)
      uploadErrors[fieldName] = 'The image could not be uploaded. Please try again.'
    }
  } catch (err) {
    console.error('File upload error:', err)
    uploadErrors[fieldName] = 'The image could not be uploaded. Please try again.'
  } finally {
    uploadingFiles[fieldName] = false
    event.target.value = ''
  }
}

const blocksForm = reactive({}) // store all block edits locally
function updateBlock(fieldName, { block, form }) {
  // Ensure the blocksForm entry exists
  if (!blocksForm[fieldName]) blocksForm[fieldName] = []

  // Make a deep copy of the block to preserve reactivity
  const newBlock = JSON.parse(JSON.stringify(block))

  // Update or push in blocksForm
  const index = blocksForm[fieldName].findIndex((b) => b.id === newBlock.id)
  if (index !== -1) {
    blocksForm[fieldName][index] = newBlock
  } else {
    blocksForm[fieldName].push(newBlock)
  }

  // Ensure the main form array exists
  if (!props.form[fieldName]) props.form[fieldName] = []

  // Update or push in the main form
  const mainIndex = props.form[fieldName].findIndex((b) => b.id === newBlock.id)
  if (mainIndex !== -1) {
    props.form[fieldName][mainIndex] = newBlock
  } else {
    props.form[fieldName].push(newBlock)
  }
}

// function updateBlock(fieldName, updatedBlock) {
//   const list = props.form[fieldName]
//   const index = list.findIndex((b) => b.id === updatedBlock.id)
//   if (index !== -1) list[index] = updatedBlock
// }

const activeTab = ref(null)
const formTabIcons = {
  SEO: 'search',
  Configuration: 'settings',
  'Page Info': 'file-text',
  Content: 'edit-3',
  Layout: 'layout',
}
const formTabButtons = computed(() =>
  (props.config?.tabs || []).map((tab) => ({
    label: friendlyLabel(tab.label),
    value: tab.label,
    icon: formTabIcons[tab.label],
  })),
)

// -----------------------
// Tabs: initialize & persist
// -----------------------
watch(
  () => props.config,
  (cfg) => {
    if (!cfg) return
    const savedTab =
      typeof window !== 'undefined' ? localStorage.getItem('activeTab') : null

    if (savedTab && cfg.tabs?.some((t) => t.label === savedTab)) {
      activeTab.value = savedTab
    } else {
      activeTab.value =
        cfg.tabs?.find((tab) => tab.active)?.label ||
        cfg.tabs?.[0]?.label ||
        null
      if (activeTab.value && typeof window !== 'undefined') {
        localStorage.setItem('activeTab', activeTab.value)
      }
    }
  },
  { immediate: true },
)

function setActiveTab(label) {
  activeTab.value = label
  if (typeof window !== 'undefined') localStorage.setItem('activeTab', label)
}

const activeTabObject = computed(
  () =>
    props.config?.tabs?.find((tab) => tab.label === activeTab.value) || null,
)
const visibleSections = computed(() => activeTabObject.value?.sections || [])

// -----------------------
// Fields: flatten & visible
// -----------------------
const flattenFields = (fields) => {
  let all = []
  fields?.forEach((f) => {
    if (!f || typeof f !== 'object') return
    if (f.type === 'section' && f.fields) {
      all.push({ type: 'section', label: f.label })
      all = all.concat(flattenFields(f.fields))
    } else {
      all.push(f)
    }
  })
  return all
}

const visibleFields = computed(() => {
  const config = props.config || {}
  let fields = []
  if (config.fields) fields = fields.concat(flattenFields(config.fields))
  visibleSections.value.forEach((section) => {
    if (!section || typeof section !== 'object') return
    fields.push({ type: 'section', label: section.label })
    if (section.fields) fields = fields.concat(flattenFields(section.fields))
  })
  return fields
})

function fieldKey(field) {
  return field?.model || field?.name || ''
}

function fieldsContainKey(fields, key) {
  return (fields || []).some((field) => {
    if (!field || typeof field !== 'object') return false
    if (fieldKey(field) === key) return true
    return fieldsContainKey(field.fields, key)
  })
}

async function focusEditorField(key) {
  if (!key) return
  const matchingTab = props.config?.tabs?.find(
    (tab) =>
      fieldsContainKey(tab.fields, key) ||
      (tab.sections || []).some((section) =>
        fieldsContainKey(section.fields, key),
      ),
  )
  if (matchingTab) setActiveTab(matchingTab.label)
  await nextTick()
  const wrapper = Array.from(
    formRoot.value?.querySelectorAll('[data-editor-field]') || [],
  ).find((element) => element.dataset.editorField === key)
  if (!wrapper) return
  wrapper.scrollIntoView({ behavior: 'smooth', block: 'center' })
  wrapper
    .querySelector('input, textarea, select, [contenteditable="true"]')
    ?.focus()
}

watch(() => props.focusedFieldKey, focusEditorField)

// -----------------------
// Form initialization & sync
// -----------------------
watch(
  [() => props.config, () => props.data],
  ([cfg, data]) => {
    if (!cfg) return

    let allFields = []

    if (cfg.fields) allFields = allFields.concat(flattenFields(cfg.fields))
    if (cfg.tabs) {
      cfg.tabs.forEach((tab) => {
        tab.sections?.forEach((section) => {
          allFields = allFields.concat(flattenFields(section.fields))
        })
      })
    }

    const hasOwn = (object, key) =>
      Object.prototype.hasOwnProperty.call(object || {}, key)

    if (!hasOwn(props.form, 'Page')) {
      props.form.Page = data?.Page || cfg.render_data?.Page || {}
    }

    allFields.forEach((f) => {
      const key = fieldKey(f)
      if (!key) return

      if (hasOwn(data, key)) {
        props.form[key] = data[key]
      } else if (!hasOwn(props.form, key)) {
        if (f.value !== undefined) props.form[key] = f.value
        else if (f.default !== undefined) props.form[key] = f.default
        else if (f.type === 'toggle') props.form[key] = false
        else if (
          f.type === 'repeatable' ||
          f.type === 'repeater' ||
          f.type === 'product' ||
          f.type === 'commerce_links' ||
          f.type === 'categories' ||
          f.type === 'draggable'
        ) {
          props.form[key] = []
        } else props.form[key] = ''
      }

      if (
        [
          'toggle',
          'repeatable',
          'repeater',
          'product',
          'commerce_links',
          'categories',
          'draggable',
        ].includes(f.type) &&
        !Object.is(f.value, props.form[key])
      ) {
        f.value = props.form[key]
      }
    })
  },
  { immediate: true },
)

// -----------------------
// Draggable handlers
// -----------------------
// function handleSubmit({ fieldName, block }) {
//   if (!props.form[fieldName]) props.form[fieldName] = []
//   props.form[fieldName].push(block)
// }
const handleSubmit = ({ fieldName, block }) => {
  // Ensure the form field array exists
  if (!props.form[fieldName]) {
    props.form[fieldName] = []
  }

  // Ensure it's an array
  if (!Array.isArray(props.form[fieldName])) {
    props.form[fieldName] = []
  }

  // Push the new block
  props.form[fieldName].push(block)
}

// function handleSubmit({ fieldName, block }) {
//   if (!form[fieldName]) form[fieldName] = []
//   form[fieldName].push(block)   // works because `form` is reactive
// }

function removeDraggableItem(fieldName, id) {
  if (!props.form[fieldName]) return
  props.form[fieldName] = props.form[fieldName].filter((item) => item.id !== id)
}

// -----------------------
// Utility: sanitize strings
// -----------------------
function sanitize(str) {
  if (!str) return ''
  return String(str)
    .replace(/<!--.*?-->/g, '')
    .replace(/[<>]/g, '')
}

function friendlyLabel(label) {
  const cleanLabel = sanitize(label)
  return (
    {
      SEO: 'Search appearance',
      Configuration: 'Store settings',
      'Page Info': 'Page details',
      Content: 'Content',
      Layout: 'Store design',
    }[cleanLabel] || cleanLabel
  )
}

function friendlyFieldLabel(field) {
  if (fieldKey(field) === 'grid_num') return 'Products per row'
  return sanitize(field?.label)
}

watch(
  () =>
    visibleFields.value.map((f) => ({
      name: fieldKey(f),
      value: f?.value,
    })),
  (updatedFields) => {
    updatedFields.forEach(({ name, value }) => {
      if (!name || Object.is(props.form[name], value)) return

      const currentValue = props.form[name]
      const bothObjects =
        currentValue !== null &&
        value !== null &&
        typeof currentValue === 'object' &&
        typeof value === 'object'

      if (bothObjects) {
        try {
          if (JSON.stringify(currentValue) === JSON.stringify(value)) return
        } catch {
          // Fall through and update non-serializable values by reference.
        }
      }

      props.form[name] = value
    })
  },
  { deep: true },
)
</script>

<style scoped>
.builder-dynamic-form
  :where(
    input:not([type='checkbox']):not([type='radio']):not([type='file']):not(
        [type='color']
      ),
    select,
    textarea
  ) {
  min-height: 44px !important;
  width: 100%;
  border: 1px solid #d1d5db !important;
  border-radius: 10px !important;
  background-color: #ffffff !important;
  padding: 0.625rem 0.875rem !important;
  color: #111827;
  transition:
    border-color 160ms ease,
    box-shadow 160ms ease,
    background-color 160ms ease;
}

.builder-dynamic-form
  :where(
    input:not([type='checkbox']):not([type='radio']):not([type='file']):not(
        [type='color']
      ),
    select,
    textarea
  ):focus {
  border-color: #22a263 !important;
  box-shadow: 0 0 0 3px rgba(34, 162, 99, 0.14) !important;
  outline: none !important;
}

.builder-dynamic-form :where(input, select, textarea):disabled {
  cursor: not-allowed;
  background-color: #f3f4f6 !important;
  color: #9ca3af;
}

.builder-dynamic-form textarea {
  min-height: 110px !important;
  resize: vertical;
}

.builder-dynamic-form [data-editor-field] {
  border-radius: 12px;
}

.builder-dynamic-form [data-editor-field] h1,
.builder-dynamic-form [data-editor-field] h2 {
  color: #111827;
  font-size: 0.875rem;
  font-weight: 500;
}

.inline-field {
  display: inline-block;
  width: 48%;
  margin-right: 4%;
}
.inline-field:last-child {
  margin-right: 0;
}

.ql-editor {
  word-break: break-all;
  white-space: normal;
}
.ql-container {
  border: none !important;
}
.ql-toolbar {
  border: none !important;
  border-bottom: 1px solid #e5e7eb !important;
  box-shadow: 0 1px 4px 0 rgba(0, 0, 0, 0.06);
}
.ql-toolbar.ql-snow .ql-formats {
  margin-right: 0px;
}

.selection-drag-ghost {
  opacity: 0.4;
}
</style>
