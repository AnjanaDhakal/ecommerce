<template>
  <main class="flex min-h-screen items-center justify-center bg-gray-50 px-6">
    <section class="w-full max-w-md rounded-lg border border-gray-200 bg-white p-8 text-center shadow-sm">
      <h1 class="text-2xl font-semibold text-gray-900">Vendor access required</h1>
      <p class="mt-3 text-sm leading-6 text-gray-600">
        This account does not have access to the vendor portal. Ask an administrator to assign the Ecommerce Vendor role.
      </p>
      <button
        type="button"
        class="mt-6 inline-flex rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-60"
        :disabled="session.logout.loading"
        @click="signOut"
      >
        {{ session.logout.loading ? 'Signing out…' : 'Sign out and use another account' }}
      </button>
      <p v-if="logoutError" class="mt-3 text-sm text-red-600" role="alert">
        {{ logoutError }}
      </p>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'

import { session } from '@/data/session'

const logoutError = ref('')

async function signOut() {
  logoutError.value = ''

  try {
    await session.logout.submit()
  } catch (error) {
    console.warn('Could not sign out from the access-denied page:', error)
    logoutError.value = 'Could not sign out. Please try again.'
  }
}
</script>
