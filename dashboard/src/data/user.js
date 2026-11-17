import router from '@/router'
import { createResource } from 'frappe-ui'
import { ref, watchEffect } from 'vue'

// Define the user resource to get the logged-in user
export const userResource = createResource({
  url: 'frappe.auth.get_logged_user',
  cache:"User",
  onError(error) {
    if (error && error.exc_type === 'AuthenticationError') {
      router.push({ name: 'Login' })
    }
  },
})
