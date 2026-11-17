import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export function useRoutedCollectionSelection(items, selectedKey, toolKey) {
  const route = useRoute()
  const router = useRouter()

  function matchingItem(key) {
    if (key === undefined || key === null || key === '') return null
    return items.value.find(item => String(item.name) === String(key)) || null
  }

  function isCurrentToolRoute() {
    return route.name === 'apiintegration'
      && String(route.params.integrationTab || '') === 'ecommerce'
      && String(route.params.integrationTool || '') === toolKey
  }

  function updateRoute(key) {
    if (!isCurrentToolRoute() || key === undefined || key === null) return
    if (String(route.query.item || '') === String(key)) return
    router.replace({
      query: { ...route.query, item: String(key) },
    })
  }

  function selectItem(key, { syncRoute = true } = {}) {
    const item = matchingItem(key)
    if (!item) return false
    selectedKey.value = item.name
    if (syncRoute) updateRoute(item.name)
    return true
  }

  function restoreSelection() {
    if (!items.value.length) {
      selectedKey.value = ''
      return
    }
    const routeItem = isCurrentToolRoute() ? route.query.item : null
    if (selectItem(routeItem)) return
    if (selectItem(selectedKey.value)) return
    selectItem(items.value[0].name)
  }

  watch(
    () => route.query.item,
    item => {
      if (isCurrentToolRoute()) selectItem(item, { syncRoute: false })
    },
  )

  return { selectItem, restoreSelection }
}
