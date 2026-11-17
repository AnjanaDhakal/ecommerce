// useAuth.js
import { ref } from 'vue'
import axios from 'axios'

const user = ref(null)
const loading = ref(false)
const isAuthenticated = ref(false)

const FRAPPE_URL = import.meta.env.VITE_FRAPPE_URL
const CLIENT_ID = import.meta.env.VITE_FRAPPE_CLIENT_ID
const REDIRECT_URI = import.meta.env.VITE_REDIRECT_URI

export const auth = {
  user,
  loading,
  isAuthenticated,

  // 🔹 Redirect to Frappe OAuth login
  login: () => {
    const authUrl =
      `${FRAPPE_URL}/api/method/frappe.integrations.oauth2.authorize` +
      `?response_type=code&client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}` // exact match
    // console.log('Redirecting to Frappe login...')
    window.location.href = authUrl
  },

  // 🔹 Handle redirect callback after login
  // ✅ Handle redirect callback after Frappe login
  handleOAuthCallback: async () => {
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')

    if (!code) {
      console.warn('No code found in URL')
      return false
    }

    // console.log('🔑 Authorization code received:', code)
    loading.value = true

    try {
      // ⚠️ Do NOT encode redirect_uri here
      const params = new URLSearchParams()
      params.append('grant_type', 'authorization_code')
      params.append('client_id', CLIENT_ID)
      params.append('redirect_uri', REDIRECT_URI) // exact match, no encodeURIComponent
      params.append('code', code)

      const response = await axios.post(
        `${FRAPPE_URL}/api/method/frappe.integrations.oauth2.get_token`,
        params.toString(), // send as application/x-www-form-urlencoded
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
      )

      const data = response.data.message || response.data
      // console.log('✅ Token exchange success:', data)

      localStorage.setItem('access_token', data.access_token)
     //  //  console.log('🔑 Access Token stored', data)
      localStorage.setItem('refresh_token', data.refresh_token)
      axios.defaults.headers.common['Authorization'] =
        `Bearer ${data.access_token}`

      await auth.fetchUser()
      return true
    } catch (error) {
      console.error('❌ OAuth callback error:', error.response?.data || error)
      return false
    } finally {
      loading.value = false
    }
  },

  // 🔹 Fetch user info using access token
  fetchUser: async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      console.warn('⚠️ No access token found in fetchUser()')
      return null
    }

    try {
      const response = await axios.get(
        `${FRAPPE_URL}/api/method/frappe.integrations.oauth2.openid_profile`,
        { headers: { Authorization: `Bearer ${token}` } },
      )

      const data = response.data.message || response.data
      user.value = data
      isAuthenticated.value = true
      // console.log('👤 Logged User:', data)
      return data
    } catch (err) {
      console.error('❌ Failed to fetch user info:', err.response?.data || err)
      user.value = null
      isAuthenticated.value = false
      return null
    }
  },

  // 🔹 Check if already authenticated
  checkAuth: async () => {
    loading.value = true
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        isAuthenticated.value = false
        return
      }

      const response = await axios.get(
        `${FRAPPE_URL}/api/method/frappe.integrations.oauth2.openid_profile`,
        { headers: { Authorization: `Bearer ${token}` } },
      )

      user.value = response.data.message || response.data || null
      isAuthenticated.value = !!user.value
      // console.log('✅ Authenticated User:', user.value)
    } catch (err) {
      console.error('Check Auth error:', err.response?.data || err)
      user.value = null
      isAuthenticated.value = false
    } finally {
      loading.value = false
    }
  },

  // 🔹 Logout (clear local + revoke token)
  logout: async () => {
    const token = localStorage.getItem('access_token')

    try {
      if (token) {
        await axios.post(
          `${FRAPPE_URL}/api/method/frappe.integrations.oauth2.revoke_token`,
          new URLSearchParams({ token, token_type_hint: 'access_token' }),
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
        )
        // console.log('✅ Token revoked')
      }
    } catch (err) {
      console.warn('⚠️ Token revoke failed:', err.response?.data || err)
    }

    try {
      const loginRedirect = `${window.location.origin}`
      await fetch(
        `${FRAPPE_URL}/api/method/logout?redirect-to=${encodeURIComponent(loginRedirect)}`,
        {
          method: 'GET',
          credentials: 'include',
          mode: 'no-cors',
        },
      )
      // console.log('✅ Silent Frappe logout (background)')
    } catch (err) {
      console.warn('⚠️ Background logout failed:', err)
    }

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isAuthenticated.value = false
    // console.log('🚪 Local + Frappe logout complete')

    window.location.replace(`${window.location.origin}/login`)
  },
}
