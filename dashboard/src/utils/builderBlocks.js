const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''

let cachedBlocks = null
let pendingRequest = null

export async function getBuilderBlocks() {
  if (cachedBlocks) return cachedBlocks
  if (pendingRequest) return pendingRequest

  const token = localStorage.getItem('access_token') || ''
  pendingRequest = fetch(
    `${Frappe_URL}/api/method/ecommerce.api.get_block`,
    {
      method: 'GET',
      cache: 'no-store',
      headers: {
        'Content-Type': 'application/json',
        'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
        Authorization: `Bearer ${token}`,
      },
    },
  )
    .then(async (response) => {
      const result = await response.json()
      if (!response.ok || result?.message?.status !== 'success') {
        throw new Error(result?.message?.message || 'Unable to load sections')
      }
      cachedBlocks = Array.isArray(result.message.data)
        ? result.message.data
        : []
      return cachedBlocks
    })
    .finally(() => {
      pendingRequest = null
    })

  return pendingRequest
}
