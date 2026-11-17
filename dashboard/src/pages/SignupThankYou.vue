<template>
  <div class="flex min-h-screen flex-col bg-[#f8f8f3]">
    <div
      class="mx-auto flex w-full max-w-[1600px] items-center justify-between px-6 pb-0 pt-2 lg:px-10 lg:pt-2 xl:px-12"
    >
      <RouterLink to="/" class="block h-14 w-[260px] overflow-hidden lg:h-16 lg:w-[300px]">
        <img
          src="@/assets/pnd-logo-black.png"
          alt="PickNDrop"
          class="h-full w-full origin-left scale-[1.8] object-contain object-left lg:scale-[2]"
        />
      </RouterLink>

      <a
        href="https://pickndropnepal.com/home"
        class="inline-flex items-center justify-center rounded-full px-7 py-3 text-base font-semibold shadow-sm transition"
        style="background:#059669;color:#ffffff;"
      >
        Home
      </a>
    </div>

    <main class="flex flex-1 items-center justify-center px-6 py-12 lg:px-10 xl:px-12">
      <section
        class="w-full max-w-3xl rounded-[32px] border border-white/80 bg-white p-8 text-center shadow-[0_25px_80px_rgba(15,23,42,0.12)] sm:p-12"
      >
        <div
          class="mx-auto flex h-16 w-16 items-center bg-green-700 justify-center rounded-full bg-emerald-100 text-emerald-700"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            class="h-8 w-8 text-white"
          >
            <path d="M20 6 9 17l-5-5" />
          </svg>
        </div>

        <p class="mt-6 text-sm font-semibold uppercase tracking-[0.24em] text-emerald-700 ">
          Registration received
        </p>
        <h1 class="mt-3 text-4xl font-black tracking-tight text-slate-900 sm:text-5xl">
          Thank you for registering with us!
        </h1>
        <p class="mx-auto mt-6 max-w-2xl text-base leading-8 text-slate-600 sm:text-lg">
          We have sent a message to set a password to your email. Please check your
          inbox. If you have any questions, feel free to call us at
          <a href="tel:9801235811" class="font-semibold text-emerald-700 underline">
            9801235811
          </a>.
          We look forward to working with you!
        </p>

        <div class="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <button
            class="inline-flex w-full items-center justify-center rounded-2xl bg-green-700 px-8 py-3 text-base font-semibold text-white transition hover:bg-emerald-800 sm:w-auto"
            @click="goToLogin"
          >
            Go to login
          </button>
          <button
            class="inline-flex w-full items-center justify-center rounded-2xl border border-slate-200 px-8 py-3 text-base font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 sm:w-auto"
            @click="goToSignup"
          >
            Back to registration
          </button>
        </div>
      </section>
    </main>

    <footer
      class="bg-[#0e9f6e] px-6 py-3 text-center text-sm text-white"
    >
      &copy; {{ currentYear }} PickNDrop Ecommerce V1.2.0. All rights reserved
    </footer>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const currentYear = new Date().getFullYear()

const goToLogin = () => {
  window.location.href = '/login?redirect-to=/dashboard'
}

const goToSignup = () => {
  router.push({
    path: '/register',
    query: route.query,
  })
}
</script>
