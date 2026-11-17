<template>
  <div class="flex min-h-screen flex-col overflow-y-auto bg-[#f8f8f3]">
    <div
      v-if="loading"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-slate-950/35 px-4 backdrop-blur-[2px]"
    >
      <div
        class="w-full max-w-[320px] rounded-3xl bg-white px-6 py-7 text-center shadow-[0_24px_80px_rgba(15,23,42,0.2)]"
      >
        <div
          class="mx-auto mb-4 h-11 w-11 animate-spin rounded-full border-4 border-emerald-100 border-t-emerald-600"
        ></div>
        <h3 class="text-lg font-semibold text-slate-900">Registering...</h3>
        <p class="mt-2 text-sm text-slate-500">
          Please wait while we create your business account.
        </p>
      </div>
    </div>

    <div
      class="mx-auto flex w-full max-w-[1600px] items-center justify-between px-4 pb-0 pt-2 sm:px-6 xl:px-10 xl:pt-2 2xl:px-12"
    >
      <RouterLink
        to="/"
        class="block h-12 w-[220px] overflow-hidden sm:h-14 sm:w-[260px] xl:h-16 xl:w-[300px]"
      >
        <img
          src="@/assets/pnd-logo-black.png"
          alt="PickNDrop"
          class="h-full w-full origin-left scale-[1.8] object-contain object-left xl:scale-[2]"
        />
      </RouterLink>
      <div class="flex gap-2">
        <a
          href="https://pickndropnepal.com/home"
          class="hidden items-center justify-center rounded-full px-7 py-3 text-base font-semibold shadow-sm transition xl:inline-flex"
          style="background: #059669; color: #ffffff"
        >
          Visit Website
        </a>
        <a
          href="/login"
          class="hidden items-center justify-center rounded-full px-7 py-3 text-base font-semibold shadow-sm transition xl:inline-flex"
          style="background: #059669; color: #ffffff"
        >
          Login
        </a>
      </div>
    </div>

    <!-- MAIN CONTAINER -->
    <div
      class="signup-shell mx-auto grid w-full max-w-[1600px] flex-1 items-start gap-1 px-4 pb-10 pt-2 sm:px-6 sm:pt-3 xl:grid-cols-[1.08fr_0.92fr] xl:px-10 xl:pb-28 xl:pt-0 2xl:px-12"
    >
      <!-- LEFT SECTION -->
      <section class="hidden xl:flex xl:items-start">
        <div class="max-w-[640px] mt-24">
          <div
            class="inline-flex items-center gap-2 rounded-full border border-emerald-100 bg-emerald-50/80 px-5 py-2 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-700 shadow-sm"
          >
            <span
              style="
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 9999px;
                background: #059669;
                flex-shrink: 0;
              "
            ></span>
            Grow your business nationwide
          </div>

          <div class="mt-4">
            <h1
              class="text-[88px] font-black leading-[0.9] tracking-[-0.04em] text-[#0f172a]"
            >
              Reliable Logistics
              <span class="block text-[#0e9f6e]">Simplified.</span>
            </h1>
          </div>

          <div
            class="signup-metrics mt-8 grid max-w-[560px] grid-cols-2 gap-x-12 gap-y-9"
          >
            <div
              v-for="item in heroHighlights"
              :key="item.title"
              class="flex gap-4"
            >
              <div class="mt-1 h-12 w-[3px] rounded-full bg-[#0e9f6e]"></div>
              <div>
                <p
                  class="text-[30px] font-bold leading-none tracking-tight text-[#111827]"
                >
                  {{ item.title }}
                </p>
                <p
                  class="mt-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-[#9ca3af]"
                >
                  {{ item.subtitle }}
                </p>
              </div>
            </div>
          </div>

          <p class="mt-6 text-base italic text-[#4b5563]">
            *Pay for successful deliveries only.
          </p>
        </div>
      </section>

      <!-- RIGHT FORM -->
      <section
        class="flex w-full justify-center pt-1 sm:pt-0 xl:-mt-16 2xl:-mt-20"
      >
        <div
          class="w-full max-w-[720px] rounded-[28px] border border-white/80 bg-white p-4 shadow-[0_25px_80px_rgba(15,23,42,0.12)] sm:p-6"
        >
          <div class="mb-5 flex items-center gap-3 sm:mb-6 sm:gap-4">
            <p class="text-2xl font-bold text-slate-700 sm:text-2xl">
              Start Delivering Today
            </p>
            <div
              class="mt-1 h-1 w-16 shrink-0 rounded-full bg-emerald-600 sm:w-24"
            ></div>
          </div>

          <div class="grid gap-3 sm:grid-cols-2 sm:gap-4">
            <div>
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                Full Name
              </label>
              <input
                v-model="userDetails.contactPerson"
                type="text"
                placeholder="Your Name"
                class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-1 text-lg text-gray-700 outline-none transition placeholder:text-gray-400 focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100 sm:rounded-2xl sm:px-4 sm:py-3"
              />
            </div>

            <div>
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                Business Name
              </label>
              <input
                v-model="userDetails.storeName"
                type="text"
                placeholder="Store Name"
                class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-lg text-gray-700 outline-none transition placeholder:text-gray-400 focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100 sm:rounded-2xl sm:px-4 sm:py-3"
              />
            </div>

            <div>
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                Phone Number
              </label>
              <input
                v-model="userDetails.mobileNumber"
                type="tel"
                maxlength="10"
                placeholder="98XXXXXXXX"
                class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-lg text-gray-700 outline-none transition placeholder:text-gray-400 focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100 sm:rounded-2xl sm:px-4 sm:py-3"
              />
            </div>

            <div>
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                Email Address
              </label>
              <input
                v-model="userDetails.email"
                type="email"
                placeholder="email@example.com"
                class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-lg text-gray-700 outline-none transition placeholder:text-gray-400 focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100 sm:rounded-2xl sm:px-4 sm:py-3"
              />
            </div>

            <div>
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                City
              </label>
              <input
                v-model="userDetails.city"
                type="text"
                placeholder="City"
                class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-lg text-gray-700 outline-none transition placeholder:text-gray-400 focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100 sm:rounded-2xl sm:px-4 sm:py-3"
              />
            </div>

            <div>
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                Street
              </label>
              <input
                v-model="userDetails.street"
                type="text"
                placeholder="Street or landmark"
                class="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-lg text-gray-700 outline-none transition placeholder:text-gray-400 focus:border-emerald-400 focus:bg-white focus:ring-4 focus:ring-emerald-100 sm:rounded-2xl sm:px-4 sm:py-3"
              />
            </div>

            <div class="sm:col-span-2">
              <label
                class="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.14em] text-gray-800 sm:mb-2 sm:text-xs sm:tracking-[0.18em]"
              >
                Citizenship / Document Upload
                <span class="text-red-500">*</span>
              </label>
              <label
                for="citizenship-upload"
                class="relative mt-1 flex min-h-[98px] cursor-pointer flex-col items-center justify-center rounded-[20px] border border-dashed border-gray-200 bg-gray-50 px-4 py-2 text-center transition hover:border-emerald-300 hover:bg-emerald-50/40 sm:min-h-[106px] sm:rounded-[24px] sm:px-6 sm:py-2"
              >
                <img
                  v-if="userDetails.citizenship"
                  :src="userDetails.citizenship"
                  alt="Document preview"
                  class="absolute right-4 top-1/2 h-14 w-20 -translate-y-1/2 rounded-lg object-cover ring-1 ring-emerald-100 sm:h-16 sm:w-24"
                />
                <div
                  class="mb-1.5 flex h-8 w-8 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 sm:mb-2 sm:h-9 sm:w-9"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                    class="h-6 w-6"
                  >
                    <path d="M12 16V6" />
                    <path d="m8 10 4-4 4 4" />
                    <path
                      d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"
                    />
                    <path d="M8 16h8" />
                  </svg>
                </div>
                <p class="text-lg font-semibold text-slate-700 sm:text-[15px]">
                  {{
                    selectedFile
                      ? `Selected: ${selectedFile.name}`
                      : 'Upload your documents here'
                  }}
                </p>
                <p class="mt-0.5 text-[13px] text-slate-400 sm:text-[15px]">
                  Image files only. Click to browse and upload.
                </p>
              </label>
              <input
                id="citizenship-upload"
                type="file"
                accept="image/*"
                @change="onFileSelected"
                class="hidden"
              />
            </div>
            <div class="sm:col-span-2">
              <div class="flex flex-col items-center">
                <div ref="turnstileContainer" class="min-h-[65px]"></div>
                <p v-if="captchaLoading" class="mt-2 text-xs text-gray-500">
                  Loading security check...
                </p>
                <p
                  v-else-if="!captchaSiteKey"
                  class="mt-2 text-xs text-red-500"
                >
                  Signup protection is unavailable right now. Please contact
                  support.
                </p>
              </div>
            </div>
          </div>

          <ErrorMessage :message="errorMessage" class="mt-4" />

          <div class="mt-4">
            <Button
              variant="solid"
              size="lg"
              :label="loading ? 'Registering...' : 'Registration'"
              :disabled="loading || captchaLoading || !captchaSiteKey"
              class="w-full rounded-xl border-0 bg-emerald-700 py-2.5 text-sm font-semibold text-white shadow-none hover:bg-emerald-800 disabled:bg-gray-300 sm:rounded-2xl sm:py-3 sm:text-base"
              @click="createUser"
            />
          </div>

          <p class="mt-3 text-center text-xs text-slate-400">
            By registering, you agree to our
            <a
              href="https://pickndropnepal.com/terms"
              class="font-medium text-emerald-700 hover:text-emerald-800"
            >
              Terms of Service
            </a>
            .
          </p>

          <div class="mt-2 text-center">
            <a
              href="/login"
              class="text-lg font-medium text-green-700 hover:text-emerald-800"
            >
              Already have an account? Login
            </a>
          </div>
        </div>
      </section>
    </div>

    <!-- FOOTER -->
    <footer
      class="left-0 right-0 z-20 bg-[#0e9f6e] px-6 py-3 text-center text-sm text-white xl:fixed xl:bottom-0"
    >
      &copy; {{ currentYear }} Pick & Drop Ecommerce V1.2.0. All rights reserved
    </footer>
  </div>
</template>

<script setup>
import { Button, ErrorMessage } from 'frappe-ui'
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const currentYear = new Date().getFullYear()
const signupPageTitle = 'Register Your Business | PickNDrop'
const signupMetaDescription =
  'Register your business with PickNDrop and access fast, reliable delivery, COD settlement, nationwide coverage, and business-friendly logistics solutions in Nepal.'
const previousPageTitle = typeof document !== 'undefined' ? document.title : ''
const previousMetaValues = {
  description: '',
  ogTitle: '',
  ogDescription: '',
  twitterTitle: '',
  twitterDescription: '',
}

const userDetails = ref({
  storeName: '',
  contactPerson: '',
  email: '',
  mobileNumber: '',
  city: '',
  street: '',
  citizenship: '',
})

let errorMessage = ref('')
let loading = ref(false)

const selectedFile = ref(null)
const turnstileContainer = ref(null)
const captchaToken = ref('')
const captchaSiteKey = ref('')
const captchaLoading = ref(true)
const captchaWidgetId = ref(null)
const heroHighlights = [
  { title: '77 Districts', subtitle: 'Full Coverage' },
  { title: '500+ Locations', subtitle: 'Wider Reach' },
  { title: 'Next Day', subtitle: 'COD Settlement' },
  { title: 'Zero Charge', subtitle: 'On Returns*' },
]

// -----------------------------
// URL REF CODE
// -----------------------------
const urlReferralCode = computed(() => {
  return route.query.utm_source ? String(route.query.utm_source) : ''
})

// -----------------------------
// FINAL CODE (USE THIS IN API)
// -----------------------------
const referralCode = computed(() => urlReferralCode.value)
const loadTurnstileScript = () =>
  new Promise((resolve, reject) => {
    if (window.turnstile) {
      resolve(window.turnstile)
      return
    }

    const existingScript = document.querySelector(
      'script[data-turnstile-script="true"]',
    )

    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(window.turnstile), {
        once: true,
      })
      existingScript.addEventListener(
        'error',
        () => reject(new Error('Failed to load Turnstile.')),
        { once: true },
      )
      return
    }

    const script = document.createElement('script')
    script.src =
      'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit'
    script.async = true
    script.defer = true
    script.dataset.turnstileScript = 'true'
    script.onload = () => resolve(window.turnstile)
    script.onerror = () => reject(new Error('Failed to load Turnstile.'))
    document.head.appendChild(script)
  })

const resetCaptcha = () => {
  captchaToken.value = ''

  if (window.turnstile && captchaWidgetId.value !== null) {
    window.turnstile.reset(captchaWidgetId.value)
  }
}

const renderCaptcha = async () => {
  if (!turnstileContainer.value || !captchaSiteKey.value) {
    return
  }

  const turnstile = await loadTurnstileScript()

  captchaWidgetId.value = turnstile.render(turnstileContainer.value, {
    sitekey: captchaSiteKey.value,
    theme: 'light',
    callback: (token) => {
      captchaToken.value = token
      errorMessage.value = ''
    },
    'expired-callback': () => {
      captchaToken.value = ''
    },
    'error-callback': () => {
      captchaToken.value = ''
      errorMessage.value =
        'Security check failed to load. Please refresh and try again.'
    },
  })
}

const fetchCaptchaConfig = async () => {
  captchaLoading.value = true

  try {
    const response = await fetch(
      '/api/method/ecommerce.api.get_signup_captcha_config',
    )
    const data = await response.json()

    if (
      response.ok &&
      data.message?.status === 'success' &&
      data.message.siteKey
    ) {
      captchaSiteKey.value = data.message.siteKey
      await renderCaptcha()
      return
    }

    errorMessage.value =
      data.message?.message || 'Signup protection is unavailable right now.'
  } catch (error) {
    errorMessage.value =
      'Unable to load signup protection right now. Please try again later.'
  } finally {
    captchaLoading.value = false
  }
}

const ensureMetaTag = (selector, attributes) => {
  let metaTag = document.querySelector(selector)

  if (!metaTag) {
    metaTag = document.createElement('meta')
    Object.entries(attributes).forEach(([key, value]) => {
      metaTag.setAttribute(key, value)
    })
    document.head.appendChild(metaTag)
  }

  return metaTag
}

const applyPageMeta = () => {
  document.title = signupPageTitle
  const descriptionTag = ensureMetaTag('meta[name="description"]', {
    name: 'description',
  })
  const ogTitleTag = ensureMetaTag('meta[property="og:title"]', {
    property: 'og:title',
  })
  const ogDescriptionTag = ensureMetaTag('meta[property="og:description"]', {
    property: 'og:description',
  })
  const twitterTitleTag = ensureMetaTag('meta[name="twitter:title"]', {
    name: 'twitter:title',
  })
  const twitterDescriptionTag = ensureMetaTag(
    'meta[name="twitter:description"]',
    {
      name: 'twitter:description',
    },
  )

  previousMetaValues.description = descriptionTag.getAttribute('content') || ''
  previousMetaValues.ogTitle = ogTitleTag.getAttribute('content') || ''
  previousMetaValues.ogDescription =
    ogDescriptionTag.getAttribute('content') || ''
  previousMetaValues.twitterTitle =
    twitterTitleTag.getAttribute('content') || ''
  previousMetaValues.twitterDescription =
    twitterDescriptionTag.getAttribute('content') || ''

  descriptionTag.setAttribute('content', signupMetaDescription)
  ogTitleTag.setAttribute('content', signupPageTitle)
  ogDescriptionTag.setAttribute('content', signupMetaDescription)
  twitterTitleTag.setAttribute('content', signupPageTitle)
  twitterDescriptionTag.setAttribute('content', signupMetaDescription)
}

const restorePageMeta = () => {
  document.title = previousPageTitle
  const descriptionTag = document.querySelector('meta[name="description"]')
  const ogTitleTag = document.querySelector('meta[property="og:title"]')
  const ogDescriptionTag = document.querySelector(
    'meta[property="og:description"]',
  )
  const twitterTitleTag = document.querySelector('meta[name="twitter:title"]')
  const twitterDescriptionTag = document.querySelector(
    'meta[name="twitter:description"]',
  )

  if (descriptionTag)
    descriptionTag.setAttribute('content', previousMetaValues.description)
  if (ogTitleTag) ogTitleTag.setAttribute('content', previousMetaValues.ogTitle)
  if (ogDescriptionTag) {
    ogDescriptionTag.setAttribute('content', previousMetaValues.ogDescription)
  }
  if (twitterTitleTag) {
    twitterTitleTag.setAttribute('content', previousMetaValues.twitterTitle)
  }
  if (twitterDescriptionTag) {
    twitterDescriptionTag.setAttribute(
      'content',
      previousMetaValues.twitterDescription,
    )
  }
}

const onFileSelected = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    const reader = new FileReader()
    reader.onload = () => {
      userDetails.value.citizenship = reader.result
    }
    reader.readAsDataURL(file)
  } else {
    selectedFile.value = null
    userDetails.value.citizenship = ''
  }
}

const validateForm = () => {
  const {
    storeName,
    contactPerson,
    email,
    mobileNumber,
    city,
    street,
    citizenship,
  } = userDetails.value
  // console.log('Validating form with details:', userDetails.value)

  if (
    !storeName ||
    !contactPerson ||
    !email ||
    !mobileNumber ||
    !city ||
    !street
  ) {
    errorMessage.value = 'Please fill all the fields'
    return false
  }

  if (!citizenship || !selectedFile.value) {
    errorMessage.value = 'Please upload citizenship'
    return false
  }

  const namePattern = /^[a-zA-Z\s]*$/
  const cityStreetPattern = /^[a-zA-Z0-9\s,]*$/

  if (!namePattern.test(storeName)) {
    errorMessage.value = 'Store Name should not contain special characters.'
    return false
  }
  if (!namePattern.test(contactPerson)) {
    errorMessage.value = 'Contact Person should not contain special characters.'
    return false
  }
  if (!cityStreetPattern.test(city)) {
    errorMessage.value =
      'City should only contain letters, numbers, spaces, and commas.'
    return false
  }
  if (!cityStreetPattern.test(street)) {
    errorMessage.value =
      'Street should only contain letters, numbers, spaces, and commas.'
    return false
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailPattern.test(email)) {
    errorMessage.value = 'Please enter a valid email address'
    return false
  }

  if (mobileNumber.length !== 10) {
    errorMessage.value = 'Mobile number must be 10 digits'
    return false
  }

  if (!captchaToken.value) {
    errorMessage.value = 'Please complete the security check'
    return false
  }

  errorMessage.value = ''
  return true
}

const createUser = async () => {
  if (!validateForm()) {
    toast.error(errorMessage.value)
    return
  }

  loading.value = true
  const apiUrl = '/api/method/ecommerce.api.signup'
  // const payload = {
  //   ...userDetails.value,
  //   referralCode: referralCode.value,
  //   captchaToken: captchaToken.value,
  // }

 //  // console.log('🚀 Signup Payload:', payload)
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...userDetails.value,
        referralCode: referralCode.value,
        captchaToken: captchaToken.value,
      }),
    })

    const data = await response.json()

    if (response.ok && data.message.status === 'success') {
      toast.success(
        'Business created successfully. Please set your password using the link in the email.',
        { timeout: 5000 },
      )

      userDetails.value = {
        storeName: '',
        contactPerson: '',
        email: '',
        mobileNumber: '',
        city: '',
        street: '',
        citizenship: '',
      }
      selectedFile.value = null
      await router.push({
        path: '/register/thank-you',
        query: route.query,
      })
    } else {
      errorMessage.value =
        data.message?.message || 'Signup failed. Please try again.'
      toast.error(errorMessage.value)
    }
  } catch (error) {
    errorMessage.value = 'An error occurred. Please try again.'
    toast.error(errorMessage.value)
  } finally {
    resetCaptcha()
    loading.value = false
  }
}

onMounted(() => {
  applyPageMeta()
  fetchCaptchaConfig()
})

onBeforeUnmount(() => {
  restorePageMeta()
})
</script>

<style scoped>
@media (min-width: 1024px) and (max-height: 940px) {
  .signup-shell {
    transform: scale(0.9);
    transform-origin: center center;
  }

  .signup-metrics {
    margin-top: 1.5rem;
    gap: 1.5rem 2rem;
  }
}

@media (min-width: 1024px) and (max-height: 860px) {
  .signup-shell {
    transform: scale(0.84);
  }

  .signup-metrics {
    margin-top: 1.25rem;
    gap: 1.25rem 1.75rem;
  }
}
</style>
