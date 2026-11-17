import router from '@/router'
import { createResource } from 'frappe-ui'

export const rolesResource = createResource({
  url: '/api/method/ecommerce.get_role_profile_of_logged_user.get_role_profile_of_logged_user',
  method: 'GET',
  onError(error) {
    if (error && error.exc_type === 'AuthenticationError') {
      router.push({ name: 'Login' })
    }
  },
})
