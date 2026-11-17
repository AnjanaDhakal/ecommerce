import { createRouter, createWebHistory } from 'vue-router'
import { confirmDiscardChanges } from './composables/useUnsavedChanges'

const routes = [
  { path: '/', redirect: '/website' },
  {
    path: '/website',
    component: () => import('@/views/WebsiteLayout.vue'),
    meta: { requiresLogin: true },
    children: [
      { path: '', name: 'WebsiteHome', component: () => import('@/pages/Website.vue') },
      { path: 'pages', name: 'WebsitePageCreate', component: () => import('@/views/WebsitePages.vue') },
      { path: 'pages/:page_name', name: 'WebsitePageEdit', component: () => import('@/views/WebsitePages.vue') },
    ],
  },
  {
    path: '/store/:websiteId',
    component: () => import('@/views/StorefrontLayout.vue'),
    meta: { requiresLogin: false },
    children: [
      { path: 'product/:slug', name: 'StorefrontProduct', component: () => import('@/views/StorefrontProduct.vue') },
      { path: 'category/:slug', name: 'StorefrontCategory', component: () => import('@/views/StorefrontCategory.vue') },
      { path: 'brand/:slug', name: 'StorefrontBrand', component: () => import('@/views/StorefrontCategory.vue'), meta: { storefrontEntity: 'brand' } },
      { path: 'cart', name: 'StorefrontCart', component: () => import('@/views/StorefrontCart.vue') },
      { path: 'checkout', name: 'StorefrontCheckout', component: () => import('@/views/StorefrontCheckout.vue') },
    ],
  },
  {
    path: '/store/:websiteId/page/:pageId',
    name: 'StorefrontPagePreview',
    component: () => import('@/views/StorefrontPagePreview.vue'),
    meta: { requiresLogin: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/website' },
]

const router = createRouter({
  history: createWebHistory('/ecommerce'),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to, from) => {
  if (to.meta.requiresLogin === false) return true
  if (from.name && !(await confirmDiscardChanges())) return false
  return true
})

export default router
