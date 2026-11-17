<template>
  <div class="p-6 text-center">
    <h2 class="text-xl font-bold mb-2">Logging you in...</h2>
    <p class="text-gray-600">
      Please wait while we complete the authentication.
    </p>
  </div>
</template>

<script>
import { onMounted } from 'vue'
import { auth } from '@/composables/useAuth'
import { session } from '@/data/session'

export default {
  setup() {
    onMounted(async () => {
      const params = new URLSearchParams(window.location.search)
      const code = params.get('code')

      if (!code) {
        console.warn('⚠️ No OAuth code found in URL')
        return
      }

      // Exchange code for access token
      await auth.handleOAuthCallback()

      const token = localStorage.getItem('access_token')
      // console.log('🛡️ Access Token:', token)

      if (token) {
        // ✅ Set session user to mark logged-in state
        session.user = 'OAuthUser'

        try {
          const { rolesResource } = await import('@/data/roles')
          await rolesResource.fetch()
          // console.log('✅ Roles fetched:', rolesResource.data)
        } catch (err) {
          console.warn('⚠️ Role fetch failed:', err)
        }

        window.location.replace('/dashboard/main')
      } else {
        window.location.replace('/login')
      }
    })
  },
}
</script>
