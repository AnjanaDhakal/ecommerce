<template>
  <div class="branch-container flex">
    <SidebarProvider>
      <Nav v-if="!hideChrome" />
      <AppSidebar />
      <main
        class="flex-1 overflow-hidden bg-gray-200"
        :class="hideChrome ? '' : 'pt-20 lg:pt-[4.5rem]'"
      >
        <slot />
        <router-view />
      </main>
    </SidebarProvider>
  </div>

  <DialogOnload v-model="display.isDisplay" />
  <PromotionalModal />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import Nav from '../components/Nav.vue'
import { display } from '../composables/display'
import DialogOnload from '../components/DialogOnload.vue'
import PromotionalModal from '../components/PromotionalModal.vue'
import { SidebarProvider } from '@/components/ui/sidebar'
import AppSidebar from '@/components/AppSidebar.vue'

const route = useRoute()
const hideChrome = computed(() => route.name === 'comment')
const isEcommerceRoute = computed(() => route.path.startsWith('/ecommerce'))

watch(
  isEcommerceRoute,
  (isEcommerce) => {
    document.body.classList.toggle('ecommerce-theme', isEcommerce)
  },
  { immediate: true },
)

onMounted(() => {
  display.isDisplay = true
})

onBeforeUnmount(() => {
  document.body.classList.remove('ecommerce-theme')
})
</script>

<style scoped>
/* Hide scrollbar for Chrome, Safari and Opera */
.branch-container::-webkit-scrollbar {
  background-color: transparent;
  width: 7px;
  height: 7px;
}

/* Hide scrollbar for IE, Edge and Firefox */
.branch-container {
  -ms-overflow-style: none;
  /* IE and Edge */
  scrollbar-width: none;
  /* Firefox */
}
</style>
