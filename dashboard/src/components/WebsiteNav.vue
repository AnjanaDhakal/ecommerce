<template>
  <nav class="fixed top-0 z-50 w-full bg-[#27b67c] border-b border-gray-200">
    <div class="px-3 py-3 lg:px-5 lg:pl-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center justify-start rtl:justify-end">
          <button
            @click="toggleSideBar"
            data-drawer-target="logo-sidebar"
            data-drawer-toggle="logo-sidebar"
            aria-controls="logo-sidebar"
            type="button"
            class="inline-flex text-white items-center p-2 text-sm rounded-lg lg:hidden focus:outline-none"
          >
            <span class="sr-only">Open sidebar</span>
            <svg
              class="w-6 h-6 fill-white"
              aria-hidden="true"
              viewBox="0 0 20 20"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                clip-rule="evenodd"
                fill-rule="evenodd"
                d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"
              ></path>
            </svg>
          </button>
          <router-link to="/main">
            <img
              src="@/assets/logo-white-pnd.png"
              class="h-8"
              alt="pickndrop Logo"
            />
          </router-link>
        </div>

        <div class="flex items-center justify-start gap-3">
          <div
            class="text-gray-200 text-sm justify-end items-end flex-col hover:underline hidden sm:block"
          >
            <h3>Welcome,</h3>
            <h3>{{ userName }}</h3>
          </div>

          <Avatar />
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, inject } from 'vue'
import Avatar from '../components/Avatar.vue'
import userInfo from '../data/userInfo'

const userName = computed(() => {
  const payload = userInfo?.data?.message || userInfo?.data || {}
  return payload.full_name || payload.fullName || payload.name || 'Guest'
})

const toggleSideBar = inject('toggleSideBar')
</script>
