<template>
  <Teleport to="body">
    <div
      v-if="showUnsavedDialog"
      class="fixed inset-0 z-[10000] flex items-center justify-center bg-black/45 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="unsaved-changes-title"
    >
      <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h2 id="unsaved-changes-title" class="text-xl font-semibold text-gray-900">
          Unsaved changes
        </h2>
        <p class="mt-2 text-sm leading-6 text-gray-600">
          You have unsaved changes. Do you want to save them before continuing?
        </p>

        <div class="mt-6 flex flex-wrap justify-end gap-2">
          <button
            type="button"
            class="rounded-lg border border-red-200 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
            :disabled="isSavingUnsavedChanges"
            @click="discardUnsavedChanges"
          >
            Undo changes
          </button>
          <button
            type="button"
            class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            :disabled="isSavingUnsavedChanges"
            @click="stayOnCurrentPage"
          >
            Stay here
          </button>
          <button
            type="button"
            class="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-60"
            :disabled="isSavingUnsavedChanges"
            @click="saveUnsavedChanges"
          >
            {{ isSavingUnsavedChanges ? 'Saving...' : 'Save changes' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {
  discardUnsavedChanges,
  saveUnsavedChanges,
  stayOnCurrentPage,
  useUnsavedChanges,
} from '../composables/useUnsavedChanges'

const { showUnsavedDialog, isSavingUnsavedChanges } = useUnsavedChanges()
</script>
