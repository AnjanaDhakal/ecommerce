<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 p-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-lg">
      <div class="mb-6 text-center">
        <h1 class="text-2xl font-bold text-gray-900">Vendor Portal</h1>
        <p class="mt-1 text-gray-500">Sign in to continue to your dashboard.</p>
      </div>

      <form class="space-y-4" @submit.prevent="submit">
        <Input
          required
          name="email"
          type="text"
          label="Email or mobile number"
          placeholder="Enter your email or mobile number"
        />
        <Input
          required
          name="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
        />
        <Button class="w-full" :loading="session.login.loading" variant="solid">
          Sign in
        </Button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { session } from '../data/session'

function submit(event) {
  const formData = new FormData(event.target)
  session.login.submit({
    email: formData.get('email'),
    password: formData.get('password'),
  })
}
</script>
