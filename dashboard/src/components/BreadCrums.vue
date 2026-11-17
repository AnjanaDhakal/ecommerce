<template>
  <div>
    <Breadcrumbs :items="breadcrumbItems" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Breadcrumbs } from 'frappe-ui'

const route = useRoute()

const breadcrumbItems = computed(() => {
  let pathSegments = route.path.split('/').filter((segment) => segment)

  // Initialize breadcrumb array with Home
  let breadcrumbs = [
    {
      label: 'Home',
      route: {
        path: '/',
      },
    },
  ]

  // Add other segments to breadcrumbs
  pathSegments.forEach((segment, index) => {
    breadcrumbs.push({
      label: segment.charAt(0).toUpperCase() + segment.slice(1),
      route: {
        path: '/' + pathSegments.slice(0, index + 1).join('/'),
      },
    })
  })

  return breadcrumbs
})
</script>
