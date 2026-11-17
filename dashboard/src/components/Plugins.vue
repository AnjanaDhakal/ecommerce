<template>
  <div class="min-h-full bg-white p-1">
    <template v-if="!activePlugin">
      <div class="mb-6">
        <strong v-if="!embedded" class="text-xl text-gray-800">Extensions</strong>
        <p class="mt-1 max-w-2xl text-sm leading-6 text-gray-500">
          Add optional tools to improve customer support and your storefront experience.
          Each extension is configured separately for the website you choose.
        </p>
      </div>

      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <article
          class="group flex min-h-[280px] flex-col rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-200 hover:shadow-md"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <MessageCircleMore class="h-6 w-6" aria-hidden="true" />
            </div>
            <span
              class="rounded-full px-2.5 py-1 text-[11px] font-semibold"
              :class="connectedWebsiteCount ? 'bg-emerald-50 text-emerald-700' : 'bg-gray-100 text-gray-600'"
            >
              {{ connectedWebsiteCount ? 'Connected' : 'Available' }}
            </span>
          </div>

          <div class="mt-5">
            <h3 class="text-lg font-semibold text-gray-900">Tawk.to Live Chat</h3>
            <p class="mt-2 text-sm leading-6 text-gray-500">
              Talk with storefront visitors in real time, answer product questions,
              and help customers complete their orders.
            </p>
          </div>

          <ul class="mt-4 space-y-2 text-sm text-gray-600">
            <li class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base text-emerald-600">check_circle</span>
              Live customer conversations
            </li>
            <li class="flex items-center gap-2">
              <span class="material-symbols-outlined text-base text-emerald-600">check_circle</span>
              Configure each storefront separately
            </li>
          </ul>

          <div class="mt-auto flex items-center justify-between gap-3 border-t border-gray-100 pt-5">
            <p class="text-xs text-gray-500">
              <template v-if="connectedWebsiteCount">
                Active on {{ connectedWebsiteCount }} {{ connectedWebsiteCount === 1 ? 'website' : 'websites' }}
              </template>
              <template v-else>Free Tawk.to account required</template>
            </p>
            <Button theme="green" variant="solid" @click="openPlugin('tawk')">
              {{ connectedWebsiteCount ? 'Manage' : 'Connect' }}
              <span class="material-symbols-outlined ml-1 text-base">arrow_forward</span>
            </Button>
          </div>
        </article>
      </div>
    </template>

    <template v-else>
      <div class="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 pb-4">
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="inline-grid h-9 w-9 place-items-center rounded-lg border border-gray-200 text-gray-600 transition hover:bg-gray-50 hover:text-gray-900"
            aria-label="Back to extensions"
            title="Back to extensions"
            @click="closePlugin"
          >
            <span class="material-symbols-outlined">arrow_back</span>
          </button>
          <div>
            <h3 class="text-lg font-semibold text-gray-900">Connect Tawk.to Live Chat</h3>
            <p class="text-sm text-gray-500">Choose a storefront and add its Tawk.to widget.</p>
          </div>
        </div>
        <a
          href="https://dashboard.tawk.to/"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex h-9 items-center gap-1.5 rounded-lg border border-gray-200 px-3 text-sm font-medium text-gray-700 transition hover:bg-gray-50 hover:text-gray-900"
        >
          Open Tawk.to
          <span class="material-symbols-outlined text-base">open_in_new</span>
        </a>
      </div>

      <div class="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
        <section class="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm sm:p-6">
          <div class="mb-6 flex items-start gap-3">
            <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700">
              <MessageCircleMore class="h-5 w-5" aria-hidden="true" />
            </div>
            <div>
              <h4 class="font-semibold text-gray-900">Storefront connection</h4>
              <p class="mt-1 text-sm leading-5 text-gray-500">
                The widget appears only on the selected published ecommerce website.
              </p>
            </div>
          </div>

          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">Website</label>
          <select
            v-model="selectedWebsite"
            class="mb-5 h-11 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
            :disabled="loading || !websites.length"
            @change="loadSettings(selectedWebsite)"
          >
            <option v-if="!websites.length" value="">No ecommerce website available</option>
            <option v-for="website in websites" :key="website.name" :value="String(website.name)">
              {{ website.website_link || `Website ${website.name}` }} · {{ website.status }}
            </option>
          </select>

          <label class="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-gray-500">Widget code or direct chat link</label>
          <textarea
            v-model="tawkId"
            rows="4"
            placeholder="Paste the Widget Code, Direct Chat Link, or property-id/widget-id"
            class="w-full resize-y rounded-lg border border-gray-300 px-3 py-2.5 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100"
            :disabled="loading || saving || !selectedWebsite"
          ></textarea>

          <div class="mt-4 flex flex-wrap items-center gap-2">
            <Button
              theme="green"
              variant="solid"
              :disabled="loading || saving || !selectedWebsite || !tawkId.trim()"
              @click="addWidget"
            >
              {{ saving ? 'Saving…' : installedWidgetId ? 'Update connection' : 'Connect Tawk.to' }}
            </Button>
            <Button
              v-if="installedWidgetId"
              theme="red"
              variant="subtle"
              :disabled="loading || saving || !selectedWebsite"
              @click="removeWidget"
            >
              Remove connection
            </Button>
          </div>

          <p
            v-if="message"
            class="mt-4 rounded-lg px-3 py-2 text-sm font-medium"
            :class="messageType === 'error' ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-700'"
          >
            {{ message }}
          </p>
          <p v-else-if="installedWidgetId" class="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
            Tawk.to is active on this storefront.
          </p>
        </section>

        <aside class="rounded-2xl border border-gray-200 bg-gray-50 p-5 sm:p-6">
          <h4 class="font-semibold text-gray-900">How to connect</h4>
          <ol class="mt-5 space-y-5">
            <li v-for="(step, index) in connectionSteps" :key="step.title" class="flex gap-3">
              <span class="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-bold text-white">
                {{ index + 1 }}
              </span>
              <div>
                <p class="text-sm font-semibold text-gray-800">{{ step.title }}</p>
                <p class="mt-1 text-xs leading-5 text-gray-500">{{ step.description }}</p>
              </div>
            </li>
          </ol>
          <div class="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs leading-5 text-amber-800">
            Publishing the website is required before customers can see the chat widget.
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Button } from 'frappe-ui'
import { MessageCircleMore } from 'lucide-vue-next'

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const tawkId = ref('')
const installedWidgetId = ref('')
const selectedWebsite = ref('')
const websites = ref([])
const loading = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')
const activePlugin = ref('')
const connectedWebsiteCount = computed(
  () => websites.value.filter((website) => website.tawk_widget_id).length,
)
const connectionSteps = [
  {
    title: 'Open your Tawk.to dashboard',
    description: 'Create or select the property that belongs to your ecommerce website.',
  },
  {
    title: 'Copy the widget details',
    description: 'Go to Administration → Channels → Chat Widget and copy the Widget Code or Direct Chat Link.',
  },
  {
    title: 'Paste and connect',
    description: 'Select the website here, paste the copied value, and save the connection.',
  },
]

function openPlugin(plugin) {
  activePlugin.value = plugin
  message.value = ''
}

function closePlugin() {
  activePlugin.value = ''
  message.value = ''
}

function headers() {
  const token = localStorage.getItem('access_token') || ''
  const csrfToken = window.csrf_token || window.frappe?.csrf_token || ''
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(csrfToken ? { 'X-Frappe-CSRF-Token': csrfToken } : {}),
  }
}

function unwrap(body) {
  return body?.message ?? body
}

async function loadSettings(websiteId = '') {
  loading.value = true
  message.value = ''
  try {
    const query = websiteId ? `?website_id=${encodeURIComponent(websiteId)}` : ''
    const response = await fetch(`/api/method/ecommerce.api.get_ecommerce_plugin_settings${query}`, { headers: headers() })
    const result = unwrap(await response.json().catch(() => ({})))
    if (!response.ok || result?.status !== 'success') throw new Error(result?.message || 'Unable to load plugin settings.')
    websites.value = Array.isArray(result.data?.websites) ? result.data.websites : []
    selectedWebsite.value = String(result.data?.selected_website || '')
    installedWidgetId.value = result.data?.tawk_widget_id || ''
    tawkId.value = installedWidgetId.value
  } catch (error) {
    messageType.value = 'error'
    message.value = error?.message || 'Unable to load plugin settings.'
  } finally {
    loading.value = false
  }
}

async function saveWidget(widgetId) {
  if (!selectedWebsite.value) return
  saving.value = true
  message.value = ''
  try {
    const response = await fetch('/api/method/ecommerce.api.set_ecommerce_tawk_widget', {
      method: 'POST',
      headers: headers(),
      body: JSON.stringify({ website_id: selectedWebsite.value, widget_id: widgetId }),
    })
    const result = unwrap(await response.json().catch(() => ({})))
    if (!response.ok || result?.status !== 'success') throw new Error(result?.message || 'Unable to update Tawk.to.')
    installedWidgetId.value = result.data?.tawk_widget_id || ''
    tawkId.value = installedWidgetId.value
    messageType.value = 'success'
    message.value = result.message
    const website = websites.value.find(item => String(item.name) === selectedWebsite.value)
    if (website) website.tawk_widget_id = installedWidgetId.value
  } catch (error) {
    messageType.value = 'error'
    message.value = error?.message || 'Unable to update Tawk.to.'
  } finally {
    saving.value = false
  }
}

function addWidget() {
  if (tawkId.value.trim()) saveWidget(tawkId.value.trim())
}

function removeWidget() {
  saveWidget('')
}

onMounted(() => {
  let websiteId = ''
  try {
    const selected = JSON.parse(localStorage.getItem('selectedWebsite') || '{}')
    if (selected?.type === 'Ecommerce') websiteId = String(selected.name || '')
  } catch (_error) {
    websiteId = ''
  }
  loadSettings(websiteId)
})
</script>
