import { readonly, ref } from 'vue'

const hasUnsavedChanges = ref(false)
const showUnsavedDialog = ref(false)
const isSavingUnsavedChanges = ref(false)
let pendingDecision = null
let activeSaveHandler = null
let activeDiscardHandler = null

export function setUnsavedChanges(value, handlers = {}) {
  hasUnsavedChanges.value = Boolean(value)
  if (hasUnsavedChanges.value) {
    if (handlers.save) activeSaveHandler = handlers.save
    if (handlers.discard) activeDiscardHandler = handlers.discard
  } else {
    activeSaveHandler = null
    activeDiscardHandler = null
  }
}

export function clearUnsavedChanges() {
  hasUnsavedChanges.value = false
  activeSaveHandler = null
  activeDiscardHandler = null
}

export function confirmDiscardChanges() {
  if (!hasUnsavedChanges.value) return Promise.resolve(true)
  if (pendingDecision) return pendingDecision.promise

  let resolveDecision
  const promise = new Promise((resolve) => {
    resolveDecision = resolve
  })
  pendingDecision = { promise, resolve: resolveDecision }
  showUnsavedDialog.value = true
  return promise
}

function finishDecision(shouldContinue) {
  showUnsavedDialog.value = false
  pendingDecision?.resolve(shouldContinue)
  pendingDecision = null
}

export function stayOnCurrentPage() {
  finishDecision(false)
}

export async function discardUnsavedChanges() {
  await activeDiscardHandler?.()
  clearUnsavedChanges()
  finishDecision(true)
}

export async function saveUnsavedChanges() {
  if (!activeSaveHandler || isSavingUnsavedChanges.value) return
  isSavingUnsavedChanges.value = true
  try {
    const saved = await activeSaveHandler()
    if (saved) {
      clearUnsavedChanges()
      finishDecision(true)
    }
  } finally {
    isSavingUnsavedChanges.value = false
  }
}

export function useUnsavedChanges() {
  return {
    hasUnsavedChanges: readonly(hasUnsavedChanges),
    showUnsavedDialog: readonly(showUnsavedDialog),
    isSavingUnsavedChanges: readonly(isSavingUnsavedChanges),
    setUnsavedChanges,
    clearUnsavedChanges,
  }
}
