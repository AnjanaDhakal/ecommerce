<template>
  <div :class="embedded ? '' : 'p-4 lg:bg-gray-200 min-h-screen'">
    <div
      :class="
        embedded
          ? 'bg-white rounded-lg border border-gray-200 p-4 sm:p-5'
          : 'p-3 lg:p-4 rounded-lg bg-white min-h-screen'
      "
    >
      <div class="flex justify-between items-center mb-4">
        <div class="text-lg font-pregular font-bold">Reset Password</div>
        <Button
          variant="solid"
          theme="gray"
          size="sm"
          type="submit"
          form="reset-password-form"
        >
          Submit
        </Button>
      </div>

      <div class="my-3">
        <form
          id="reset-password-form"
          @submit.prevent="handlePasswordReset"
          class="grid grid-cols-1 md:grid-cols-3 gap-4"
        >
          <FormControl
            v-model="oldPassword"
            type="password"
            size="sm"
            variant="subtle"
            label="Old Password"
            placeholder="Enter your old password"
            required
          />

          <FormControl
            v-model="newPassword"
            type="password"
            size="sm"
            variant="subtle"
            label="New Password"
            placeholder="Enter your new password"
            required
          />

          <FormControl
            v-model="confirmPassword"
            type="password"
            size="sm"
            variant="subtle"
            label="Confirm Password"
            placeholder="Confirm your new password"
            required
          />
        </form>

        <div
          v-if="errorMessage"
          class="mt-6 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600"
        >
          {{ errorMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { FormControl, Button } from 'frappe-ui' // Import Frappe UI components
import userInfo from '../data/userInfo'
import { session } from '../data/session'
import { useToast } from 'vue-toastification'

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const toast = useToast()
const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const useremail = computed(
  () => userInfo?.data?.email || userInfo?.data?.message?.email || '',
)

//console.log('User email:', useremail.value) // Debugging line to check the email value
const passwordsMatch = computed(() => {
  return newPassword.value === confirmPassword.value
})

const handlePasswordReset = async () => {
  errorMessage.value = ''

  if (!passwordsMatch.value) {
    toast.error('New password and confirm password do not match.')
    return
  }

  if (!useremail.value) {
    errorMessage.value = 'User email could not be loaded. Please refresh and try again.'
    return
  }

  try {
    const response = await fetch('/api/method/login', {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },

      body: JSON.stringify({
        usr: useremail.value,
        pwd: oldPassword.value,
      }),
    })
    const data = await response.json()

    if (data.full_name) {
      // Now, update the user's password
      const updateResponse = await fetch(
        `/api/resource/User/${useremail.value}`,
        {
          method: 'PUT',
          headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            new_password: newPassword.value,
          }),
        },
      )

      const updateData = await updateResponse.json()

      if (updateData.data) {
        toast.success('Password updated successfully')
        try {
          await session.logout.submit()
        } finally {
          localStorage.clear()
          sessionStorage.clear()
          window.location.replace(
            `${window.location.origin}/login?redirect-to=/dashboard`,
          )
        }
      } else {
        toast.error('Failed to update password.')
      }
    } else {
      toast.error('Old password does not match.')
    }
  } catch (error) {
    // console.error('Error:', error)
    toast.error(`Error: ${error.message}`)
  }
}
</script>
