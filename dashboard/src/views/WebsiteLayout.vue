<template>
  <div class="flex h-svh overflow-hidden bg-gray-100">
    <SidebarProvider>
      <div class="flex min-w-0 flex-1 flex-col">
        <div class="flex min-h-0 min-w-0 flex-1 flex-col gap-2 overflow-hidden p-2 md:flex-row">
          <EcommerceToolNavigation
            :model-value="activeWorkspaceTool"
            show-all-apps
            show-account-chrome
            class="w-full md:h-full md:w-52"
            @update:model-value="navigateEcommerceTool"
            @all-apps="navigateAllIntegrations"
          />

          <WebsiteSidebar
            v-if="isWebsiteWorkspace && isPageEditor"
            class="hidden h-full !w-52 flex-none lg:block"
          />

          <main
            class="min-w-0 flex-1 rounded-lg border border-gray-200 bg-white shadow-sm"
            :class="
              !isWebsiteWorkspace || isPageEditor
                ? 'overflow-hidden'
                : 'overflow-y-auto'
            "
          >
            <router-view v-if="isWebsiteWorkspace" v-slot="{ Component }">
              <transition name="workspace-page" mode="out-in">
                <component :is="Component" :key="route.fullPath" />
              </transition>
            </router-view>

            <div
              v-else
              class="flex h-full min-h-0 flex-col overflow-hidden p-4"
            >
              <div
                class="mb-4 flex shrink-0 items-center justify-between gap-3 border-b border-gray-200 pb-3"
              >
                <h2 class="text-lg font-semibold text-gray-900">
                  {{ activeWorkspaceMeta.label }}
                </h2>
              </div>

              <component
                :is="activeWorkspaceMeta.component"
                :key="activeWorkspaceTool"
                embedded
                class="min-h-0 flex-1"
                :class="
                  activeWorkspaceTool === 'analytics'
                    ? 'overflow-y-auto overscroll-contain px-1 pb-4'
                    : ''
                "
              />
            </div>
          </main>
        </div>
      </div>
    </SidebarProvider>
    <BuilderCommerceDialogHost v-if="isWebsiteWorkspace" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { SidebarProvider } from '@/components/ui/sidebar'
import WebsiteSidebar from '@/components/WebsiteSidebar.vue'
import EcommerceToolNavigation from '@/components/EcommerceToolNavigation.vue'
import EcommerceOrders from '@/components/EcommerceOrders.vue'
import EcommerceAddProduct from '@/components/AddProduct.vue'
import EcommerceCategories from '@/components/Catagories.vue'
import EcommerceBrands from '@/components/Brands.vue'
import EcommerceAnalytics from '@/components/EcommerceAnalytics.vue'
import EcommercePlugins from '@/components/Plugins.vue'
import EcommerceArchive from '@/components/EcommerceArchive.vue'
import BuilderCommerceDialogHost from '@/components/BuilderCommerceDialogHost.vue'
import { confirmDiscardChanges } from '@/composables/useUnsavedChanges'

const router = useRouter()
const route = useRoute()
const activeWorkspaceTool = ref('overview')
const workspaceTools = {
  orders: { label: 'Orders', component: EcommerceOrders },
  'add-product': { label: 'Products', component: EcommerceAddProduct },
  categories: { label: 'Categories', component: EcommerceCategories },
  brands: { label: 'Brands', component: EcommerceBrands },
  analytics: { label: 'Analytics', component: EcommerceAnalytics },
  plugins: { label: 'Extensions', component: EcommercePlugins },
  archive: { label: 'Archive', component: EcommerceArchive },
}
const isWebsiteWorkspace = computed(
  () => activeWorkspaceTool.value === 'overview',
)
const activeWorkspaceMeta = computed(
  () => workspaceTools[activeWorkspaceTool.value] || workspaceTools.orders,
)
const isPageEditor = computed(() =>
  ['WebsitePageCreate', 'WebsitePageEdit'].includes(String(route.name || '')),
)

async function navigateEcommerceTool(tool) {
  const nextTool = tool === 'website-builder' ? 'overview' : tool
  if (
    nextTool === activeWorkspaceTool.value ||
    (!workspaceTools[nextTool] && nextTool !== 'overview')
  ) {
    return
  }
  if (isWebsiteWorkspace.value && !(await confirmDiscardChanges())) return
  activeWorkspaceTool.value = nextTool
}

function navigateAllIntegrations() {
  router.push({
    name: 'apiintegration',
    params: { integrationTab: 'api' },
  })
}
</script>

<style scoped>
.workspace-page-enter-active,
.workspace-page-leave-active {
  transition: opacity 140ms ease, transform 140ms ease;
}

.workspace-page-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.workspace-page-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .workspace-page-enter-active,
  .workspace-page-leave-active {
    transition: none;
  }
}
</style>
