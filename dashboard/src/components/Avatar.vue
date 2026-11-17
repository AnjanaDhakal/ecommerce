<template>
  <div class="">
    <Dropdown :options="showOptions">
      <Avatar
        v-if="userInfo && userInfo.data"
        :shape="'circle'"
        :image="userImage"
        :label="userImage ? '' : initials"
        size="lg"
        class="cursor-pointer h-8 w-8"
      />
    </Dropdown>
  </div>
</template>

<script setup>
import { Avatar, FeatherIcon } from 'frappe-ui'
import { Dropdown } from 'frappe-ui'
import { ref, computed } from 'vue'
import { session } from '../data/session'
import userInfo from '../data/userInfo'
import { h } from 'vue'
import { useRouter } from 'vue-router'

// Correct import for Feather Icons

const initials = computed(() => {
  const words = userName.value.trim().split(/\s+/).filter(Boolean)
  if (!words.length) return 'G'
  return words
    .slice(0, 2)
    .map((word) => word.charAt(0).toUpperCase())
    .join('')
})

const userPayload = computed(() => {
  return userInfo?.data?.message || userInfo?.data || {}
})

const userName = computed(() => {
  return (
    userPayload.value.full_name ||
    userPayload.value.fullName ||
    userPayload.value.name ||
    'Guest'
  )
})

const userImage = computed(() => {
  return userPayload.value.user_image || userPayload.value.image || ''
})

const router = useRouter()

const imageUrl = ref('https://i.pravatar.cc/100')

const showOptions = [
  {
    label: 'Edit Profile',
    onClick: () => {
      router.push('/editprofile')
    },
    icon: () => h(FeatherIcon, { name: 'edit' }), // Correct usage of FeatherIcon
  },
  {
    label: 'Reset Password',
    onClick: () => {
      router.push('/passwordreset')
    },
    icon: () => h(FeatherIcon, { name: 'edit-2' }), // Correct usage of FeatherIcon
  },
  {
    label: 'Logout',
    onClick: () => {
      session.logout.submit()
    },
    icon: () => h(FeatherIcon, { name: 'log-out' }), // Correct usage of FeatherIcon
  },
]
</script>
<style scoped>
.glowing-text {
  font-weight: bold;
  color: #edeff4;
  text-shadow:
    0 0 5px #1e3a8a,
    0 0 10px #1e3a8a,
    0 0 15px #1e3a8a,
    0 0 20px #1e3a8a,
    0 0 25px #1e3a8a,
    0 0 30px #1e3a8a,
    0 0 35px #1e3a8a;
}
</style>
