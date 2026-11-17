<template>
  <div class="min-h-full bg-white p-4">
    <!-- Header -->
    <div class="mb-4 flex justify-between items-center">
      <strong class="text-gray-800 text-xl">Website</strong>
      <Button
        v-if="websites.length"
        theme="green"
        variant="solid"
        @click="openCreate"
      >
        Add New Website
      </Button>
    </div>

    <!-- Website Table -->
    <div
      v-if="isLoading"
      class="flex min-h-[calc(100vh-10rem)] items-center justify-center"
    >
      <p class="text-sm text-gray-500">Loading websites...</p>
    </div>

    <div v-else-if="websites.length" class="overflow-x-auto mt-6">
      <table class="min-w-full">
        <thead class="bg-gray-100">
          <tr>
            <th
              class="w-[34%] px-4 py-2 text-left text-sm font-semibold text-gray-700"
            >
              Website Link
            </th>
            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700">
              Created
            </th>
            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700">
              Type
            </th>
            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700">
              Status
            </th>
            <th class="px-4 py-2 text-left text-sm font-semibold text-gray-700">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="website in websites"
            :key="website.name"
            class="cursor-pointer hover:bg-gray-50 transition"
            tabindex="0"
            role="link"
            title="Open website editor in a new tab"
            @click="openWebsiteEditorFromRow(website, $event)"
            @keydown.enter.self="openWebsiteEditorInNewTab(website)"
          >
            <td class="px-4 py-2 text-sm text-gray-800">
              <a
                v-if="website.canonical_url && website.status === 'Published'"
                :href="website.canonical_url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-green-700 hover:underline"
              >
                {{ website.canonical_url }}
              </a>
              <span v-else-if="website.canonical_url" class="text-gray-500">
                {{ website.canonical_url }}
                <span class="ml-1 text-xs">— publish to make live</span>
              </span>
              <span v-else>{{ website.website_link }}</span>
              <div
                v-if="website.custom_domain"
                class="mt-1 text-xs text-gray-500"
              >
                Custom domain: {{ website.custom_domain }}
              </div>
            </td>
            <td class="px-4 py-2 text-sm text-gray-600">
              {{ formatWebsiteDate(website.creation) }}
            </td>
            <td class="px-4 py-2 text-sm text-gray-600">
              {{ website.type || '-' }}
            </td>
            <td class="px-4 py-2">
              <div
                class="inline-flex rounded-lg border border-gray-200 bg-gray-100 p-0.5 shadow-sm"
                role="group"
                :aria-label="`Status for ${website.website_link}`"
              >
                <button
                  v-for="status in websiteStatuses"
                  :key="status"
                  type="button"
                  :disabled="isStatusUpdating(website.name)"
                  :aria-pressed="website.status === status"
                  class="rounded-md px-2 py-1 text-[11px] font-semibold transition focus:outline-none focus:ring-2 focus:ring-green-500 disabled:cursor-wait disabled:opacity-60"
                  :class="statusButtonClass(website.status, status)"
                  @click="setWebsiteStatus(website, status)"
                >
                  {{ websiteStatusLabel(status) }}
                </button>
              </div>
            </td>
            <td class="px-4 py-2">
              <div class="flex items-center gap-1">
                <button
                  type="button"
                  class="inline-grid h-9 w-9 place-items-center rounded-lg text-green-600 transition hover:bg-green-50 hover:text-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1"
                  :aria-label="`Edit ${website.website_link}`"
                  title="Edit website"
                  @click="openEdit(website)"
                >
                  <span
                    class="material-symbols-outlined text-xl"
                    aria-hidden="true"
                  >
                    edit_square
                  </span>
                </button>
                <a
                  v-if="website.canonical_url && website.status === 'Published'"
                  :href="website.canonical_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-grid h-9 w-9 place-items-center rounded-full text-green-700 transition hover:bg-green-50 hover:text-green-800 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1"
                  :aria-label="`View live website ${website.website_link}`"
                  title="View live website"
                >
                  <span
                    class="material-symbols-outlined text-xl"
                    aria-hidden="true"
                  >
                    language
                  </span>
                </a>
                <button
                  v-else
                  type="button"
                  disabled
                  class="inline-grid h-9 w-9 cursor-not-allowed place-items-center rounded-full text-gray-300"
                  :aria-label="`${website.website_link} is not published`"
                  title="Publish this website to view it live"
                >
                  <span
                    class="material-symbols-outlined text-xl"
                    aria-hidden="true"
                  >
                    language
                  </span>
                </button>
                <button
                  type="button"
                  class="inline-grid h-9 w-9 place-items-center rounded-full text-gray-500 transition hover:bg-green-50 hover:text-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1"
                  :aria-label="`Open website editor for ${website.website_link}`"
                  title="Open website editor"
                  @click="openWebsiteEditorInNewTab(website)"
                >
                  <span
                    class="material-symbols-outlined text-xl"
                    aria-hidden="true"
                  >
                    palette
                  </span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div
      v-else
      class="flex min-h-[calc(100vh-10rem)] flex-col items-center justify-center px-6 pb-16 text-center"
    >
      <div class="relative mb-7 h-40 w-44">
        <div
          class="absolute inset-x-3 bottom-0 h-32 rounded-full bg-gray-100"
        ></div>
        <div
          class="absolute bottom-0 left-1/2 h-28 w-28 -translate-x-1/2 rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
        >
          <div class="space-y-3 pt-2">
            <div class="h-2 w-12 rounded-full bg-gray-300"></div>
            <div class="h-2 w-16 rounded-full bg-gray-200"></div>
            <div class="h-2 w-10 rounded-full bg-gray-300"></div>
            <div class="h-2 w-14 rounded-full bg-gray-200"></div>
          </div>
        </div>
        <div
          class="absolute left-1/2 top-0 flex h-14 w-28 -translate-x-1/2 items-center rounded-xl bg-gray-400 px-4 shadow"
        >
          <span class="material-symbols-outlined text-2xl text-white">
            language
          </span>
        </div>
      </div>

      <h2 class="text-2xl font-semibold text-gray-900">
        Create Your First Website
      </h2>
      <p class="mt-2 max-w-md text-sm leading-6 text-gray-500">
        Add a new website and start building pages, customizing your storefront,
        and exploring the website builder.
      </p>
      <Button class="mt-6" theme="green" variant="solid" @click="openCreate">
        + Add New Website
      </Button>
    </div>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="translate-y-3 opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-3 opacity-0"
    >
      <aside
        v-if="showJourneyTour"
        class="fixed bottom-4 right-4 z-40 w-[calc(100vw-2rem)] max-w-sm overflow-hidden rounded-2xl border border-emerald-200 bg-white shadow-2xl sm:bottom-6 sm:right-6"
        aria-label="Website journey"
      >
        <div class="h-1 bg-gradient-to-r from-emerald-500 via-green-500 to-lime-400"></div>
        <div class="p-5">
          <div class="flex items-start justify-between gap-4">
            <div class="flex min-w-0 items-center gap-3">
              <span class="material-symbols-outlined grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-xl text-emerald-700" aria-hidden="true">rocket_launch</span>
              <div class="min-w-0">
                <p class="text-[11px] font-bold uppercase tracking-[0.14em] text-emerald-700">Website journey</p>
                <p class="truncate text-xs text-gray-500">{{ journeyWebsite.website_link }}</p>
              </div>
            </div>
            <button
              type="button"
              class="inline-grid h-8 w-8 shrink-0 place-items-center rounded-lg text-gray-400 transition hover:bg-gray-100 hover:text-gray-700"
              aria-label="Dismiss website journey"
              title="Dismiss"
              @click="dismissJourneyTour"
            >
              <span class="material-symbols-outlined text-lg" aria-hidden="true">close</span>
            </button>
          </div>

          <h3 class="mt-4 text-lg font-semibold text-gray-900">Continue in the website builder</h3>
          <p class="mt-1.5 text-sm leading-6 text-gray-600">
            Open the website workspace to manage pages, customize the storefront, and access its preview.
          </p>

          <div class="mt-4 flex items-center gap-2 text-[11px] font-semibold text-gray-500">
            <span class="rounded-full bg-emerald-100 px-2.5 py-1 text-emerald-700">1. Create</span>
            <span class="material-symbols-outlined text-sm text-gray-300" aria-hidden="true">arrow_forward</span>
            <span class="rounded-full bg-emerald-100 px-2.5 py-1 text-emerald-700">2. Design</span>
            <span class="material-symbols-outlined text-sm text-gray-300" aria-hidden="true">arrow_forward</span>
            <span class="rounded-full bg-gray-100 px-2.5 py-1 text-gray-700">3. Preview</span>
          </div>

          <button
            type="button"
            class="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gray-900 px-4 py-3 text-sm font-semibold text-white transition hover:bg-black focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
            @click="openJourneyWebsite"
          >
            Go to website builder
            <span class="material-symbols-outlined text-lg" aria-hidden="true">arrow_forward</span>
          </button>
        </div>
      </aside>
    </Transition>

    <Dialog :options="dialogOptions" v-model="showModal">
      <template #body-content>
        <div
          class="max-h-[calc(100dvh-16rem)] overflow-y-auto overscroll-contain px-1 pr-3"
          style="-webkit-overflow-scrolling: touch; scrollbar-gutter: stable"
        >
          <div class="grid grid-cols-1 gap-4 xl:grid-cols-12">
            <section class="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm xl:col-span-8">
              <div class="mb-4 flex items-center gap-3 border-b border-gray-100 pb-3">
                <span class="material-symbols-outlined grid h-9 w-9 place-items-center rounded-lg bg-green-50 text-xl text-green-700" aria-hidden="true">language</span>
                <div>
                  <h3 class="text-sm font-semibold text-gray-900">Website details</h3>
                  <p class="mt-0.5 text-xs text-gray-500">Set the website identity, content, and publishing options.</p>
                </div>
              </div>

              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div class="md:col-span-2">
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Website name <span class="text-red-500">*</span></label>
                  <input v-model="form.name" type="text" required placeholder="Enter website name" class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100" />
                  <p v-if="domainPreview" class="mt-1.5 break-all text-xs text-gray-500">
                    Publishes at <span class="font-semibold text-green-700">{{ domainPreview }}</span>
                  </p>
                </div>

                <div class="md:col-span-2">
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Custom domain <span class="font-normal text-gray-400">(optional)</span></label>
                  <input v-model="form.custom_domain" type="text" inputmode="url" autocomplete="url" placeholder="example.com" class="h-11 w-full rounded-lg border border-gray-300 px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100" />
                  <p class="mt-1.5 text-xs leading-5 text-gray-500">
                    It serves the same published website as
                    <span class="font-semibold text-green-700">{{ domainPreview || 'your storefront address' }}</span>
                    while keeping the custom address in the browser.
                  </p>
                  <div
                    v-if="customDomainPreview"
                    class="mt-2 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-xs leading-5 text-green-900"
                  >
                    In the DNS account that owns
                    <strong>{{ customDomainPreview }}</strong>, create a proxied
                    <strong>CNAME</strong> pointing to
                    <strong>{{ customDomainTarget }}</strong>.
                    The target stays the same for every website.
                  </div>
                </div>

                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Type <span class="text-red-500">*</span></label>
                  <select v-model="form.type" required class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100">
                    <option value="Ecommerce">Ecommerce</option>
                    <option value="Blog">Blog</option>
                  </select>
                </div>

                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Status <span class="text-red-500">*</span></label>
                  <select v-model="form.status" required class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100">
                    <option value="Published">Published</option>
                    <option value="Draft">Draft</option>
                    <option value="Discarded">Archived</option>
                  </select>
                </div>

                <div :class="form.type !== 'Ecommerce' || !catalogueSourceOptions.length ? 'md:col-span-2' : ''">
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Page template</label>
                  <select v-model="form.template" class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100">
                    <option v-for="page in pages" :key="page.name" :value="page.name">{{ page.page_name }}</option>
                  </select>
                </div>

                <div v-if="form.type === 'Ecommerce' && catalogueSourceOptions.length">
                  <div class="mb-1.5 flex items-center gap-1.5">
                    <label class="block text-sm font-semibold text-gray-700">{{ isEditing ? 'Import existing catalogue' : 'Catalogue' }}</label>
                    <span class="group/catalogue-help relative inline-flex" tabindex="0" aria-label="Catalogue import information">
                      <span class="material-symbols-outlined cursor-help text-base text-gray-400 transition group-hover/catalogue-help:text-gray-700 group-focus/catalogue-help:text-gray-700" aria-hidden="true">info</span>
                      <span role="tooltip" class="pointer-events-none absolute bottom-full left-1/2 z-30 mb-2 hidden w-72 -translate-x-1/2 rounded-lg bg-gray-900 px-3 py-2 text-xs font-normal leading-5 text-white shadow-lg group-hover/catalogue-help:block group-focus/catalogue-help:block">Copies brands, categories, products, media, variants, stock and publication settings. Existing matching items are skipped.</span>
                    </span>
                  </div>
                  <select v-model="form.catalogue_source" class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100">
                    <option value="">Start with an empty catalogue</option>
                    <option v-for="website in catalogueSourceOptions" :key="website.name" :value="website.name">
                      Copy from {{ website.website_link }}{{ website.status === 'Discarded' ? ' (archived website)' : '' }}{{ website.product_count ? ` — ${website.product_count} products` : '' }}
                    </option>
                  </select>
                </div>

                <div class="md:col-span-2">
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Website icon</label>
                  <div class="flex items-center gap-3 rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                    <div class="grid h-14 w-14 shrink-0 place-items-center overflow-hidden rounded-xl border border-gray-200 bg-white">
                      <img
                        v-if="form.favicon"
                        :src="form.favicon"
                        alt="Website icon preview"
                        class="h-full w-full object-cover"
                      />
                      <span v-else class="material-symbols-outlined text-2xl text-gray-400" aria-hidden="true">public</span>
                    </div>
                    <div class="min-w-0 flex-1">
                      <input
                        ref="faviconInput"
                        type="file"
                        accept="image/png,image/jpeg,image/gif,image/webp"
                        class="block w-full text-xs text-gray-600 file:mr-3 file:rounded-lg file:border-0 file:bg-green-50 file:px-3 file:py-2 file:text-xs file:font-semibold file:text-green-700 hover:file:bg-green-100"
                        @change="handleFaviconChange"
                      />
                      <p class="mt-1 text-xs leading-5 text-gray-500">Displayed in the browser tab. Use a square PNG or WebP image, up to 1 MB.</p>
                    </div>
                    <button
                      v-if="form.favicon"
                      type="button"
                      class="shrink-0 rounded-lg px-2 py-1 text-xs font-semibold text-red-600 hover:bg-red-50"
                      @click="removeFavicon"
                    >
                      Remove
                    </button>
                  </div>
                </div>

                <div class="md:col-span-2">
                  <label class="mb-1.5 block text-sm font-semibold text-gray-700">Description</label>
                  <textarea v-model="form.description" rows="4" placeholder="Describe this website" class="w-full resize-none rounded-lg border border-gray-300 px-3.5 py-2.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100"></textarea>
                </div>
              </div>
            </section>

            <aside class="rounded-2xl border border-gray-200 bg-gray-50/70 p-4 xl:col-span-4">
              <div class="mb-4 flex items-center gap-3 border-b border-gray-200 pb-3">
                <span class="material-symbols-outlined grid h-9 w-9 place-items-center rounded-lg bg-white text-xl text-green-700 shadow-sm" aria-hidden="true">palette</span>
                <div>
                  <h3 class="text-sm font-semibold text-gray-900">Brand styling</h3>
                  <p class="mt-0.5 text-xs text-gray-500">Choose the typography and colors.</p>
                </div>
              </div>

              <div class="space-y-4">
                <div>
                  <div class="mb-1.5 flex items-center gap-1.5">
                    <label class="block text-sm font-semibold text-gray-700">Google font</label>
                    <span class="group/font-help relative inline-flex" tabindex="0" aria-label="Google Font information">
                      <span class="material-symbols-outlined cursor-help text-base text-gray-400 transition group-hover/font-help:text-gray-700 group-focus/font-help:text-gray-700" aria-hidden="true">info</span>
                      <span role="tooltip" class="pointer-events-none absolute bottom-full right-0 z-30 mb-2 hidden w-72 rounded-lg bg-gray-900 px-3 py-2 text-xs font-normal leading-5 text-white shadow-lg group-hover/font-help:block group-focus/font-help:block">{{ googleFontsLoading ? 'Loading the Google Fonts catalog…' : googleFontsApiKey ? `${googleFonts.length} Google Font families available.` : 'Type any exact Google Fonts family name. Add VITE_GOOGLE_FONTS_API_KEY to load the complete catalog.' }}</span>
                    </span>
                  </div>
                  <input v-model="form.font" type="text" autocomplete="off" placeholder="Enter a Google Font family" class="h-11 w-full rounded-lg border border-gray-300 bg-white px-3.5 text-sm outline-none transition focus:border-green-500 focus:ring-2 focus:ring-green-100" />
                </div>

                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-1">
                  <ColorPickerBlock label="Primary color" v-model="color" />
                  <ColorPickerBlock label="Secondary color" v-model="secondaryColor" />
                  <ColorPickerBlock label="Additional color 1" v-model="additionalColor1" clearable />
                  <ColorPickerBlock label="Additional color 2" v-model="additionalColor2" clearable />
                </div>
              </div>
            </aside>
          </div>

          <div v-if="error" class="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {{ error }}
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button, Dialog } from 'frappe-ui'
import { useToast } from 'vue-toastification'
import ColorPickerBlock from '../webcomponents/ColorPickerBlock.vue'

// Color picker
const color = ref('#ff0000')
const showPicker = ref(false)
const pickerRef = ref(null)
const previewRef = ref(null)
const faviconInput = ref(null)

const secondaryColor = ref('#0000ff') // 👈 default secondary color

const additionalColor1 = ref('') // Optional action color; falls back to dark
const additionalColor2 = ref('') // Optional supporting accent; falls back to primary
const popularGoogleFonts = [
  'Inter',
  'Roboto',
  'Open Sans',
  'Lato',
  'Montserrat',
  'Poppins',
  'Outfit',
  'Nunito',
  'Raleway',
  'Ubuntu',
  'Merriweather',
  'Playfair Display',
  'Oswald',
  'Source Sans 3',
  'Noto Sans',
  'Noto Serif',
  'PT Sans',
  'Rubik',
  'Work Sans',
  'DM Sans',
  'Manrope',
  'Mulish',
  'Fira Sans',
  'Barlow',
  'Quicksand',
]
const googleFonts = ref([...popularGoogleFonts])
const googleFontsLoading = ref(false)
const googleFontsApiKey = import.meta.env.VITE_GOOGLE_FONTS_API_KEY || ''
let fontPreviewTimer = null

function validGoogleFontName(value) {
  return /^[A-Za-z0-9][A-Za-z0-9 .&+'-]{0,79}$/.test(String(value || '').trim())
}

function loadFontPreview(family) {
  document.getElementById('ecommerce-font-picker-preview')?.remove()
  if (!validGoogleFontName(family)) return
  const link = document.createElement('link')
  link.id = 'ecommerce-font-picker-preview'
  link.rel = 'stylesheet'
  link.href = `https://fonts.googleapis.com/css2?family=${encodeURIComponent(family.trim()).replaceAll('%20', '+')}&display=swap`
  document.head.appendChild(link)
}

async function loadGoogleFontsCatalog() {
  if (!googleFontsApiKey) return
  googleFontsLoading.value = true
  try {
    const response = await fetch(
      `https://www.googleapis.com/webfonts/v1/webfonts?sort=popularity&key=${encodeURIComponent(googleFontsApiKey)}`,
    )
    const result = await response.json()
    if (response.ok && Array.isArray(result?.items)) {
      googleFonts.value = result.items
        .map((item) => item.family)
        .filter(Boolean)
    }
  } catch (_error) {
    googleFonts.value = [...popularGoogleFonts]
  } finally {
    googleFontsLoading.value = false
  }
}

// Websites & form
const websites = ref([])
const catalogueSources = ref([])
const customDomainTarget = ref(window.location.hostname)
const storefrontBaseDomain = ref(window.location.hostname)
const pages = ref([])
const showModal = ref(false)
const isLoading = ref(true)
const route = useRoute()
const router = useRouter()
const isEditing = ref(false)
const editingId = ref(null)
const error = ref('')
const isSubmitting = ref(false)
const updatingStatusIds = ref([])
const toast = useToast()
const journeyTourDismissed = ref(false)

const form = reactive({
  name: '',
  custom_domain: '',
  status: 'Published',
  type: 'Ecommerce',
  template: '',
  description: '',
  favicon: '',
  font: 'Inter',
  primary_color: '#ff0000',
  secondary_color: '#00ff00',
  additional_color: '#0000ff',
  catalogue_source: '',
})

const catalogueSourceOptions = computed(() =>
  catalogueSources.value.filter(
    (website) => String(website.name) !== String(editingId.value || ''),
  ),
)

const journeyWebsite = computed(
  () =>
    websites.value.find((website) => website.status === 'Draft') ||
    websites.value[0] ||
    null,
)
const showJourneyTour = computed(
  () =>
    !isLoading.value &&
    !showModal.value &&
    journeyWebsite.value &&
    !journeyTourDismissed.value,
)

function storefrontNameSlug(value) {
  const input = String(value || '').trim()
  let source = input
  if (input && !/\s/.test(input)) {
    try {
      const parsed = new URL(
        input.includes('://') ? input : `https://${input}`,
      )
      const host = parsed.hostname.toLowerCase().replace(/^www\./, '')
      if (host.includes('.') && !host.endsWith(`.${storefrontBaseDomain.value}`) && host !== storefrontBaseDomain.value) {
        source = host.replace(/\.[^.]+$/, '')
      }
    } catch (_error) {
      source = input
    }
  }

  return source
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 63)
    .replace(/-+$/g, '')
}

const domainPreview = computed(() => {
  const slug = storefrontNameSlug(form.name)
  return slug ? `https://${slug}.${storefrontBaseDomain.value}` : ''
})

const customDomainPreview = computed(() => {
  const input = String(form.custom_domain || '').trim()
  if (!input || /\s/.test(input)) return ''
  try {
    return new URL(
      input.includes('://') ? input : `https://${input}`,
    ).hostname.toLowerCase().replace(/\.$/, '')
  } catch (_error) {
    return ''
  }
})

watch(
  () => form.font,
  (family) => {
    window.clearTimeout(fontPreviewTimer)
    fontPreviewTimer = window.setTimeout(() => loadFontPreview(family), 350)
  },
  { immediate: true },
)

watch(
  pages,
  (newPages) => {
    if (newPages.length > 0 && !form.template) {
      form.template = newPages[0].name
    }
  },
  { immediate: true },
)

function handleFaviconChange(event) {
  const file = event.target?.files?.[0]
  if (!file) return

  const supportedTypes = new Set([
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/webp',
  ])
  if (!supportedTypes.has(file.type)) {
    error.value = 'Please choose a PNG, JPEG, GIF, or WebP image.'
    toast.error(error.value)
    event.target.value = ''
    return
  }
  if (file.size > 1024 * 1024) {
    error.value = 'Website icon must be 1 MB or smaller.'
    toast.error(error.value)
    event.target.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    form.favicon = String(reader.result || '')
    error.value = ''
  }
  reader.onerror = () => {
    error.value = 'Unable to read the selected website icon.'
    toast.error(error.value)
    event.target.value = ''
  }
  reader.readAsDataURL(file)
}

function removeFavicon() {
  form.favicon = ''
  if (faviconInput.value) faviconInput.value.value = ''
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  form.name = ''
  form.custom_domain = ''
  form.status = 'Published'
  form.type = 'Ecommerce'
  form.template = pages.value[0]?.name || ''
  form.description = ''
  form.favicon = ''
  if (faviconInput.value) faviconInput.value.value = ''
  form.font = 'Inter'
  form.catalogue_source =
    catalogueSources.value.find((website) => website.product_count)?.name || ''
  color.value = '#ff0000'
  secondaryColor.value = '#0000ff'
  additionalColor1.value = ''
  additionalColor2.value = ''
  error.value = ''
  showModal.value = true
}

watch(
  () => route.query.create,
  (shouldCreate) => {
    if (shouldCreate !== '1') return

    openCreate()

    const { create, ...remainingQuery } = route.query
    router.replace({ query: remainingQuery })
  },
  { immediate: true },
)

function openEdit(website) {
  // console.log('Opening edit for:', website.name)
  isEditing.value = true
  editingId.value = website.name
  // console.log('isEditing:', isEditing.value, 'editingId:', editingId.value)

  form.name = website.website_link
  form.custom_domain = website.custom_domain || ''
  form.status = website.status
  form.type = website.type
  form.template = website.template
  form.description = website.description || ''
  form.favicon = website.favicon || ''
  if (faviconInput.value) faviconInput.value.value = ''
  form.font = website.font || 'Inter'
  form.catalogue_source = ''

  color.value = website.primary_color || '#ff0000'
  secondaryColor.value = website.secondary_color || '#0000ff'
  additionalColor1.value = website.additional_color1 || ''
  additionalColor2.value = website.additional_color2 || ''

  showModal.value = true
}

function getWebsiteEditorLocation(website) {
  const activePages = Array.isArray(website.pages)
    ? website.pages.filter((page) => page.page_status !== 'Archived')
    : []
  const homePage =
    activePages.find((page) => !page.parent1) || activePages[0] || null

  if (!homePage) {
    toast.error('This website does not have an editable page yet.')
    return null
  }

  localStorage.setItem('selectedWebsite', JSON.stringify(website))
  localStorage.setItem(
    'mainpage',
    JSON.stringify({
      ...homePage,
      main_page_name: homePage.name,
      website_name: website.website_link || homePage.website_name || '',
    }),
  )

  return router.resolve({
    name: 'WebsitePageEdit',
    params: { page_name: homePage.name },
  }).href
}

function openWebsiteEditorInNewTab(website) {
  const editorLocation = getWebsiteEditorLocation(website)
  if (!editorLocation) return
  window.open(editorLocation, '_blank', 'noopener,noreferrer')
}

function dismissJourneyTour() {
  journeyTourDismissed.value = true
}

function openJourneyWebsite() {
  const website = journeyWebsite.value
  if (!website) return
  localStorage.setItem('selectedWebsite', JSON.stringify(website))
  dismissJourneyTour()
  router.push({ name: 'WebsiteHome' })
}

function openWebsiteEditorFromRow(website, event) {
  if (
    event.target.closest(
      'a, button, select, input, textarea, [role="button"]',
    )
  ) {
    return
  }
  openWebsiteEditorInNewTab(website)
}

function isStatusUpdating(websiteId) {
  return updatingStatusIds.value.includes(String(websiteId))
}

function formatWebsiteDate(value) {
  return String(value || '').match(/^\d{4}-\d{2}-\d{2}/)?.[0] || '-'
}

const websiteStatuses = ['Draft', 'Published', 'Discarded']

function websiteStatusLabel(status) {
  return status === 'Discarded' ? 'Archived' : status
}

function statusButtonClass(currentStatus, status) {
  if (currentStatus !== status) {
    return 'text-gray-500 hover:bg-white hover:text-gray-800'
  }
  if (status === 'Published') {
    return 'bg-green-600 text-white shadow-sm'
  }
  if (status === 'Discarded') {
    return 'bg-gray-700 text-white shadow-sm'
  }
  return 'bg-amber-500 text-white shadow-sm'
}

async function setWebsiteStatus(website, nextStatus) {
  const previousStatus = website.status
  if (nextStatus === previousStatus || isStatusUpdating(website.name)) return

  const websiteId = String(website.name)
  updatingStatusIds.value = [...updatingStatusIds.value, websiteId]

  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.update_website`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          name: website.name,
          status: nextStatus,
        }),
      },
    )
    const data = await response.json()

    if (!response.ok || data?.message?.status !== 'success') {
      throw new Error(
        data?.message?.message ||
          data?.message ||
          'Unable to update website status.',
      )
    }

    website.status = nextStatus
    toast.success(`Website status changed to ${nextStatus}.`)
    window.dispatchEvent(new CustomEvent('ecommerce:website-updated'))
    await fetchWebsites()
  } catch (statusError) {
    toast.error(statusError?.message || 'Unable to update website status.')
  } finally {
    updatingStatusIds.value = updatingStatusIds.value.filter(
      (id) => id !== websiteId,
    )
  }
}

// Update submitForm
const submitForm = async () => {
  if (isSubmitting.value) return
  if (!form.name || !form.status || !form.type) {
    error.value = 'Please fill in all required fields.'
    toast.error(error.value)
    return
  }
  error.value = ''
  isSubmitting.value = true

  try {
    const editing = isEditing.value
    const url = `${Frappe_URL}/api/method/ecommerce.api.${editing ? 'update_website' : 'create_website'}`
    const payload = {
      name: editing ? editingId.value : form.name,
      ...(editing ? { website_link: form.name } : {}),
      custom_domain: form.custom_domain.trim() || null,
      status: form.status,
      type: form.type,
      description: form.description,
      favicon: form.favicon || null,
      template: form.template,
      font: form.font,
      ...(editing
        ? { primary_color: color.value }
        : { color: color.value }),
      secondary_color: secondaryColor.value,
      additional_color_1: additionalColor1.value,
      additional_color_2: additionalColor2.value,
      catalogue_source:
        form.type === 'Ecommerce' ? form.catalogue_source || null : null,
    }

    const response = await fetch(url, {
      method: editing ? 'PUT' : 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(payload),
    })
    const data = await response.json()
    const responseMessage =
      data?.message?.message ||
      (typeof data?.message === 'string' ? data.message : '')

    if (!response.ok || data?.message?.status !== 'success') {
      throw new Error(
        responseMessage ||
          (editing
            ? 'Unable to update website.'
            : 'Unable to create website.'),
      )
    }

    toast.success(
      responseMessage ||
        (editing
          ? 'Website updated successfully.'
          : 'Website created successfully.'),
    )
    showModal.value = false
    isEditing.value = false
    editingId.value = null
    await fetchWebsites()
    window.dispatchEvent(new CustomEvent('ecommerce:website-updated'))
  } catch (err) {
    console.error('Website save error:', err)
    error.value = err?.message || 'Unable to save website. Please try again.'
    toast.error(error.value)
  } finally {
    isSubmitting.value = false
  }
}

const dialogOptions = computed(() => ({
  title: isEditing.value ? 'Edit Website' : 'Add Website',
  description: isEditing.value
    ? 'Update website details, catalogue, design, and publishing settings.'
    : 'Create a website and configure its catalogue, template, and design.',
  size: '3xl',
  actions: [
    {
      label: isEditing.value ? 'Update Website' : 'Create Website',
      variant: 'solid',
      onClick: submitForm,
    },
  ],
}))

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')
// Fetch pages
const fetchPages = async () => {
  try {
    const url = `${Frappe_URL}/api/method/ecommerce.api.get_pages`
    console.log('🌐 GET page templates:', url)

    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // ✅ Use "Bearer" if you're using OAuth (JWT)
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
    console.log('📡 GET page templates status:', res.status, res.statusText)

    const result = await res.json()
    console.log('📦 GET page templates response:', result)

    const payload = result?.message

    if (!res.ok || payload?.status !== 'success') {
      pages.value = []
      error.value =
        payload?.message ||
        `Unable to load page templates (HTTP ${res.status}).`
      return
    }

    pages.value = payload.data || []
  } catch (err) {
    console.error('Error fetching pages:', err)
    pages.value = []
    error.value = 'Unable to load page templates. Please try again.'
  }
}

// Fetch websites
const fetchWebsites = async () => {
  isLoading.value = true
  try {
    const url = `${Frappe_URL}/api/method/ecommerce.api.get_vendor_websites`
    //  //console.log('🌐 Fetching from:', url)

    const res = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // ✅ Use "Bearer" if you're using OAuth (JWT)
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    })
    // const res = await fetch(
    //   '/api/method/ecommerce.api.get_vendor_websites',
    // )
    const result = await res.json()
    const data = result?.message
    if (data?.status === 'success') {
      customDomainTarget.value =
        data.custom_domain_target || window.location.hostname
      storefrontBaseDomain.value =
        data.storefront_base_domain || window.location.hostname
      websites.value = Array.isArray(data.data) ? data.data : []
      catalogueSources.value = Array.isArray(data.catalogue_sources)
        ? data.catalogue_sources
        : websites.value.filter((website) => website.type === 'Ecommerce')
    }
  } catch (err) {
    console.error('Network Error:', err)
    websites.value = []
    catalogueSources.value = []
  } finally {
    isLoading.value = false
  }
}

// Submit
// const submitForm = async () => {
//   if (!form.name || !form.status || !form.type || !form.template) {
//     error.value = 'Please fill in all required fields.'
//     return
//   }
//   error.value = ''

//   try {
//     const response = await fetch(
//       '/api/method/ecommerce.api.create_website',
//       {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           name: form.name,
//           status: form.status,
//           type: form.type,
//           description: form.description,
//           template: form.template,
//           color: color.value,
//           font: form.font,
//           secondary_color: secondaryColor.value,
//           additional_color_1: additionalColor1.value,
//           additional_color_2: additionalColor2.value,
//         }),
//       },
//     )
//     const data = await response.json()
//     if (data?.message?.status === 'success') {
//       error.value = '✅ Website created successfully!'
//       showSidebar.value = false
//       window.location.reload()
//     } else error.value = data?.message || '❌ Something went wrong.'
//   } catch (err) {
//     console.error('Fetch Error:', err)
//     error.value = '❌ Network error. Please try again.'
//   }
// }

// Close color picker when clicking outside
function handleClickOutside(e) {
  if (
    showPicker.value &&
    !pickerRef.value?.contains(e.target) &&
    !previewRef.value?.contains(e.target)
  ) {
    showPicker.value = false
  }
}

onMounted(() => {
  fetchWebsites()
  fetchPages()
  loadGoogleFontsCatalog()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  window.clearTimeout(fontPreviewTimer)
  document.getElementById('ecommerce-font-picker-preview')?.remove()
  document.removeEventListener('click', handleClickOutside)
})
</script>
