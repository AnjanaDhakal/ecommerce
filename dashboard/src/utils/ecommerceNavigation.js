const ECOMMERCE_TOOL_STORAGE_KEY = 'ecommerce.pendingEcommerceTool'
export const ECOMMERCE_TOOL_EVENT = 'ecommerce:open-ecommerce-tool'
export const ECOMMERCE_FEATURE_EVENT = 'ecommerce:ecommerce-feature-changed'

export const ecommerceRoute = {
  name: 'apiintegration',
  params: { integrationTab: 'ecommerce' },
}

export function requestEcommerceTool(tool) {
  if (!tool) return
  window.sessionStorage.setItem(ECOMMERCE_TOOL_STORAGE_KEY, tool)
  window.dispatchEvent(
    new CustomEvent(ECOMMERCE_TOOL_EVENT, { detail: { tool } }),
  )
}

export function consumeRequestedEcommerceTool() {
  const tool = window.sessionStorage.getItem(ECOMMERCE_TOOL_STORAGE_KEY) || ''
  window.sessionStorage.removeItem(ECOMMERCE_TOOL_STORAGE_KEY)
  return tool
}

export function notifyEcommerceFeatureChange(enabled) {
  window.dispatchEvent(
    new CustomEvent(ECOMMERCE_FEATURE_EVENT, {
      detail: { enabled: Boolean(enabled) },
    }),
  )
}
