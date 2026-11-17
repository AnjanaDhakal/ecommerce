<template>
  <div class="min-h-full bg-[#f5f7f8] p-3 md:p-6">
    <div class="mx-auto flex h-[calc(100vh-2rem)] max-w-[1500px] flex-col overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm md:h-[calc(100vh-3rem)]">
      <header class="flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 px-4 py-3 md:px-6">
        <div>
          <h1 class="text-xl font-semibold text-gray-950">Omnichannel Inbox</h1>
          <p class="mt-0.5 text-sm text-gray-500">Messenger, Instagram, and WhatsApp in one place</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <span
            v-for="item in channelSummary"
            :key="item.channel"
            class="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium"
            :class="item.connected ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-gray-200 bg-gray-50 text-gray-500'"
          >
            <span class="h-1.5 w-1.5 rounded-full" :class="item.connected ? 'bg-emerald-500' : 'bg-gray-300'" />
            {{ item.channel }}
          </span>
          <button
            type="button"
            class="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            @click="showWhatsAppSetup = !showWhatsAppSetup"
          >
            Connect WhatsApp
          </button>
        </div>
      </header>

      <div v-if="showWhatsAppSetup" class="border-b border-emerald-100 bg-emerald-50/60 p-4">
        <form class="grid gap-3 md:grid-cols-5" @submit.prevent="connectWhatsApp">
          <input v-model.trim="whatsAppForm.business_account_id" required class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="WhatsApp Business Account ID" />
          <input v-model.trim="whatsAppForm.phone_number_id" required class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Phone Number ID" />
          <input v-model.trim="whatsAppForm.display_name" class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="Display name (optional)" />
          <input v-model.trim="whatsAppForm.access_token" required type="password" autocomplete="off" class="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm" placeholder="System User access token" />
          <button type="submit" :disabled="connectingWhatsApp" class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60">
            {{ connectingWhatsApp ? 'Connecting…' : 'Connect account' }}
          </button>
        </form>
        <p class="mt-2 text-xs text-gray-600">Use a System User token with WhatsApp messaging and management permissions. The token is sent only to Ecommerce.</p>
        <p v-if="setupError" class="mt-2 text-sm font-medium text-red-600">{{ setupError }}</p>
      </div>

      <div class="grid min-h-0 flex-1 md:grid-cols-[360px_minmax(0,1fr)]">
        <aside class="flex min-h-0 flex-col border-r border-gray-200" :class="selectedConversation ? 'hidden md:flex' : 'flex'">
          <div class="space-y-3 border-b border-gray-200 p-3">
            <input v-model="search" class="w-full rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100" placeholder="Search conversations" @input="scheduleConversationRefresh" />
            <div class="flex gap-1 overflow-x-auto pb-1">
              <button
                v-for="filter in channelFilters"
                :key="filter.value"
                type="button"
                class="whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-semibold"
                :class="activeChannel === filter.value ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
                @click="setChannel(filter.value)"
              >
                {{ filter.label }}
              </button>
            </div>
          </div>

          <div class="min-h-0 flex-1 overflow-y-auto">
            <div v-if="loadingConversations" class="p-6 text-center text-sm text-gray-500">Loading conversations…</div>
            <template v-else>
              <button
                v-for="conversation in conversations"
                :key="conversation.name"
                type="button"
                class="flex w-full gap-3 border-b border-gray-100 p-4 text-left hover:bg-gray-50"
                :class="selectedConversation?.name === conversation.name ? 'bg-emerald-50/70' : ''"
                @click="openConversation(conversation)"
              >
                <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white" :class="channelColor(conversation.channel)">
                  {{ initials(conversation.customer_name || conversation.customer_id) }}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="flex items-center justify-between gap-2">
                    <p class="truncate text-sm font-semibold text-gray-900">{{ conversation.customer_name || conversation.customer_id }}</p>
                    <span class="shrink-0 text-[11px] text-gray-400">{{ shortTime(conversation.last_message_at) }}</span>
                  </div>
                  <div class="mt-1 flex items-center gap-2">
                    <span class="rounded px-1.5 py-0.5 text-[10px] font-semibold" :class="channelBadge(conversation.channel)">{{ conversation.channel }}</span>
                    <p class="min-w-0 flex-1 truncate text-xs text-gray-500">{{ conversation.last_message }}</p>
                    <span v-if="conversation.unread_count" class="flex h-5 min-w-5 items-center justify-center rounded-full bg-emerald-600 px-1 text-[10px] font-bold text-white">{{ conversation.unread_count }}</span>
                  </div>
                </div>
              </button>
            </template>
            <div v-if="!loadingConversations && conversations.length === 0" class="p-8 text-center text-sm text-gray-500">
              No messages yet. Connect a channel and send it a test message.
            </div>
          </div>
        </aside>

        <main class="min-h-0" :class="selectedConversation ? 'flex flex-col' : 'hidden md:flex md:items-center md:justify-center'">
          <template v-if="selectedConversation">
            <div class="flex items-center gap-3 border-b border-gray-200 px-4 py-3">
              <button type="button" class="rounded-lg p-1 text-gray-500 hover:bg-gray-100 md:hidden" @click="selectedConversation = null">←</button>
              <div class="flex h-9 w-9 items-center justify-center rounded-full text-xs font-bold text-white" :class="channelColor(selectedConversation.channel)">{{ initials(selectedConversation.customer_name || selectedConversation.customer_id) }}</div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold text-gray-900">{{ selectedConversation.customer_name || selectedConversation.customer_id }}</p>
                <p class="text-xs text-gray-500">{{ selectedConversation.channel }} · {{ selectedConversation.customer_id }}</p>
              </div>
            </div>

            <div ref="messageScroller" class="min-h-0 flex-1 space-y-3 overflow-y-auto bg-[#f7f8f9] p-4 md:p-6">
              <div v-if="loadingMessages" class="text-center text-sm text-gray-500">Loading messages…</div>
              <div v-for="message in messages" :key="message.name" class="flex" :class="message.direction === 'Outbound' ? 'justify-end' : 'justify-start'">
                <div class="max-w-[82%] rounded-2xl px-4 py-2.5 shadow-sm" :class="message.direction === 'Outbound' ? 'rounded-br-md bg-emerald-600 text-white' : 'rounded-bl-md border border-gray-200 bg-white text-gray-900'">
                  <p class="whitespace-pre-wrap break-words text-sm leading-5">{{ message.text }}</p>
                  <p class="mt-1 text-right text-[10px]" :class="message.direction === 'Outbound' ? 'text-emerald-100' : 'text-gray-400'">
                    {{ shortTime(message.sent_at) }}<span v-if="message.direction === 'Outbound'"> · {{ message.delivery_status }}</span>
                  </p>
                </div>
              </div>
            </div>

            <form class="flex gap-2 border-t border-gray-200 bg-white p-3 md:p-4" @submit.prevent="sendMessage">
              <textarea v-model="draft" rows="1" maxlength="2000" class="max-h-32 min-h-10 flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2 text-sm outline-none focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100" placeholder="Write a reply…" @keydown.enter.exact.prevent="sendMessage" />
              <button type="submit" :disabled="sending || !draft.trim()" class="rounded-xl bg-emerald-600 px-5 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50">{{ sending ? 'Sending…' : 'Send' }}</button>
            </form>
            <p v-if="sendError" class="border-t border-red-100 bg-red-50 px-4 py-2 text-xs text-red-700">{{ sendError }}</p>
          </template>
          <div v-else class="text-center text-gray-500">
            <div class="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-100 text-2xl">💬</div>
            <p class="font-medium text-gray-700">Select a conversation</p>
            <p class="mt-1 text-sm">Messages from all connected channels appear here.</p>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

const API_BASE = '/api/method/ecommerce.omnichannel'
const conversations = ref([])
const messages = ref([])
const channels = ref([])
const selectedConversation = ref(null)
const activeChannel = ref('')
const search = ref('')
const draft = ref('')
const loadingConversations = ref(false)
const loadingMessages = ref(false)
const sending = ref(false)
const sendError = ref('')
const showWhatsAppSetup = ref(false)
const connectingWhatsApp = ref(false)
const setupError = ref('')
const messageScroller = ref(null)
const whatsAppForm = reactive({ business_account_id: '', phone_number_id: '', display_name: '', access_token: '' })
let pollTimer = null
let searchTimer = null

const channelFilters = [
  { label: 'All', value: '' },
  { label: 'Messenger', value: 'Messenger' },
  { label: 'Instagram', value: 'Instagram' },
  { label: 'WhatsApp', value: 'WhatsApp' },
]

const channelSummary = computed(() =>
  ['Messenger', 'Instagram', 'WhatsApp'].map((channel) => ({
    channel,
    connected: channels.value.some((item) => (item.social_media === 'Facebook' ? 'Messenger' : item.social_media) === channel),
  })),
)

async function api(method, { httpMethod = 'GET', params = {} } = {}) {
  const options = { method: httpMethod, headers: {} }
  let url = `${API_BASE}.${method}`
  if (httpMethod === 'GET') {
    const query = new URLSearchParams(Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ''))
    if (query.size) url += `?${query}`
  } else {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(params)
  }
  const response = await fetch(url, options)
  const payload = await response.json()
  const result = payload.message ?? payload.data ?? payload
  if (!response.ok || result.status === 'error') throw new Error(result.message || 'Request failed')
  return result
}

async function loadChannels() {
  const result = await api('get_omnichannel_channels')
  channels.value = result.data || []
}

async function loadConversations({ quiet = false } = {}) {
  if (!quiet) loadingConversations.value = true
  try {
    const result = await api('get_omnichannel_conversations', { params: { channel: activeChannel.value, search: search.value, status: 'Open' } })
    conversations.value = result.data || []
    if (selectedConversation.value) {
      selectedConversation.value = conversations.value.find((item) => item.name === selectedConversation.value.name) || selectedConversation.value
    }
  } finally {
    loadingConversations.value = false
  }
}

async function openConversation(conversation, { quiet = false } = {}) {
  selectedConversation.value = conversation
  if (!quiet) loadingMessages.value = true
  try {
    const result = await api('get_omnichannel_messages', { params: { conversation_id: conversation.name } })
    messages.value = result.data || []
    await api('mark_omnichannel_conversation_read', { httpMethod: 'POST', params: { conversation_id: conversation.name } })
    conversation.unread_count = 0
    await scrollToBottom()
  } finally {
    loadingMessages.value = false
  }
}

async function sendMessage() {
  const text = draft.value.trim()
  if (!text || !selectedConversation.value || sending.value) return
  sending.value = true
  sendError.value = ''
  try {
    await api('send_omnichannel_message', { httpMethod: 'POST', params: { conversation_id: selectedConversation.value.name, text } })
    draft.value = ''
    await openConversation(selectedConversation.value, { quiet: true })
    await loadConversations({ quiet: true })
  } catch (error) {
    sendError.value = error.message || 'Message could not be sent.'
  } finally {
    sending.value = false
  }
}

async function connectWhatsApp() {
  connectingWhatsApp.value = true
  setupError.value = ''
  try {
    await api('connect_whatsapp_channel', { httpMethod: 'POST', params: { ...whatsAppForm } })
    whatsAppForm.access_token = ''
    showWhatsAppSetup.value = false
    await loadChannels()
  } catch (error) {
    setupError.value = error.message || 'WhatsApp could not be connected.'
  } finally {
    connectingWhatsApp.value = false
  }
}

function setChannel(channel) {
  activeChannel.value = channel
  selectedConversation.value = null
  messages.value = []
  loadConversations()
}

function scheduleConversationRefresh() {
  window.clearTimeout(searchTimer)
  searchTimer = window.setTimeout(() => loadConversations(), 250)
}

async function scrollToBottom() {
  await nextTick()
  if (messageScroller.value) messageScroller.value.scrollTop = messageScroller.value.scrollHeight
}

function initials(value = '') { return value.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]?.toUpperCase()).join('') || '?' }
function shortTime(value) { if (!value) return ''; const date = new Date(value); return Number.isNaN(date.getTime()) ? '' : date.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }
function channelColor(channel) { return { Messenger: 'bg-[#168aff]', Instagram: 'bg-gradient-to-br from-[#833ab4] via-[#e1306c] to-[#f77737]', WhatsApp: 'bg-[#25d366]' }[channel] || 'bg-gray-500' }
function channelBadge(channel) { return { Messenger: 'bg-blue-50 text-blue-700', Instagram: 'bg-pink-50 text-pink-700', WhatsApp: 'bg-emerald-50 text-emerald-700' }[channel] || 'bg-gray-100 text-gray-600' }

onMounted(async () => {
  await Promise.all([loadChannels(), loadConversations()])
  pollTimer = window.setInterval(async () => {
    await loadConversations({ quiet: true })
    if (selectedConversation.value) await openConversation(selectedConversation.value, { quiet: true })
  }, 5000)
})

onBeforeUnmount(() => {
  window.clearInterval(pollTimer)
  window.clearTimeout(searchTimer)
})
</script>
