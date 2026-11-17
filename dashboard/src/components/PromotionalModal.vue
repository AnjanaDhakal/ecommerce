<template>
  <transition name="promo-fade">
    <div
      v-if="isVisible && slides.length"
      class="fixed inset-0 z-[120] flex items-center justify-center bg-slate-900/70 px-2 py-2"
    >
      <div
        v-if="showConfetti"
        class="pointer-events-none absolute inset-0 overflow-hidden"
      >
        <span
          v-for="piece in confettiPieces"
          :key="piece.key"
          class="promo-confetti"
          :style="piece.style"
        />
      </div>

      <div class="relative inline-flex w-auto max-w-none flex-col items-center">
        <button
          type="button"
          class="absolute top-1 right-1 rounded-full border-2 border-green-400 bg-white p-1 text-green-600 transition hover:bg-green-50"
          @click="handleClose"
        >
          <X class="h-4 w-4" />
        </button>

        <div class="overflow-hidden rounded-2xl bg-transparent leading-none">
          <button
            type="button"
            class="block rounded-2xl bg-transparent leading-none"
            @click="openTarget(slides[currentIndex]?.targetUrl)"
          >
            <img
              v-if="slides[currentIndex]?.imageUrl"
              :src="slides[currentIndex].imageUrl"
              :alt="slides[currentIndex]?.text || 'Promotion'"
              class="block h-auto w-auto max-h-[86vh] max-w-[96vw] rounded-2xl object-contain"
            />
            <div
              v-else
              class="flex h-[460px] w-full items-center justify-center rounded-2xl border border-slate-200 bg-white px-6 text-center"
            >
              <div>
                <p class="text-xl font-semibold text-slate-900">
                  {{ slides[currentIndex]?.text || 'Promotion' }}
                </p>
                <p
                  v-if="slides[currentIndex]?.targetUrl"
                  class="mt-2 text-sm text-slate-500"
                >
                  Click to learn more
                </p>
              </div>
            </div>
          </button>
        </div>

        <p class="-mt-3 text-center text-sm leading-tight text-slate-200">
          {{ slides[currentIndex]?.text || '' }}
        </p>

        <label class="-mt-0.5 flex items-center justify-center gap-2 text-sm text-slate-200">
          <input
            v-model="isChecked"
            type="checkbox"
            class="h-4 w-4 rounded border-slate-300 accent-slate-200"
          />
          <span>Do not show again</span>
        </label>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''

const isChecked = ref(false)
const isVisible = ref(false)
const currentIndex = ref(0)
const promoImageLinks = ref([])
const autoScrollRef = ref(null)
const timeoutRef = ref(null)

const slides = computed(() =>
  Array.isArray(promoImageLinks.value) ? promoImageLinks.value : [],
)

const showConfetti = computed(
  () => isVisible.value && Boolean(slides.value[currentIndex.value]?.displayConfetti),
)

const confettiColors = ['#22c55e', '#60a5fa', '#fbbf24', '#f97316', '#a78bfa']
const confettiPieces = Array.from({ length: 28 }).map((_, index) => ({
  key: `confetti-${index}`,
  style: {
    left: `${Math.random() * 100}%`,
    width: `${6 + Math.random() * 6}px`,
    height: `${10 + Math.random() * 10}px`,
    backgroundColor: confettiColors[index % confettiColors.length],
    animationDelay: `${Math.random() * 0.8}s`,
    animationDuration: `${2.2 + Math.random() * 1.6}s`,
    transform: `rotate(${Math.random() * 360}deg)`,
  },
}))

const buildImageUrl = (item) => {
  if (item?.banner_base64) {
    const base64 = item.banner_base64.trim()
    return base64.startsWith('data:image')
      ? base64
      : `data:image/png;base64,${base64}`
  }

  if (item?.banner) {
    return item.banner.startsWith('http')
      ? item.banner
      : `${Frappe_URL}${item.banner.startsWith('/') ? '' : '/'}${item.banner}`
  }

  if (item?.banner_url) {
    return item.banner_url
  }

  return ''
}

const resetAutoScroll = () => {
  clearInterval(autoScrollRef.value)
  clearTimeout(timeoutRef.value)
}

const startAutoScroll = () => {
  resetAutoScroll()
  if (slides.value.length <= 1) return

  autoScrollRef.value = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % slides.value.length
  }, 3000)
}

const goToSlide = (index) => {
  currentIndex.value = index
  resetAutoScroll()
  timeoutRef.value = setTimeout(() => {
    startAutoScroll()
  }, 3000)
}

const openTarget = (targetUrl) => {
  if (targetUrl) {
    window.open(targetUrl, '_blank', 'noopener,noreferrer')
  }
}

const handleClose = async () => {
  if (isChecked.value) {
    try {
      const currentAdId = slides.value[currentIndex.value]?.id
      const payload = currentAdId ? { seen_ads: [currentAdId] } : {}
      await fetch(
        `${Frappe_URL}/api/method/ecommerce.vendorapi.update_ads_seen_and_analytics`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        },
      )
    } catch (error) {
      console.error('Error updating ad analytics:', error)
    }
  }

  isVisible.value = false
  resetAutoScroll()
}

const initializePromo = async () => {
  try {
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.vendorapi.get_advertisement_banners`,
    )
    const promoData = await response.json()
    const responseData = promoData?.message?.data
    const items =
      (Array.isArray(responseData) ? responseData : responseData?.groups) || []

    const promoLinks = (Array.isArray(items) ? items : [])
      .map((item) => ({
        id: item?.id || item?.name || `${item?.message || item?.ad_title || ''}`,
        imageUrl: buildImageUrl(item),
        text: item?.message || item?.ad_title || '',
        targetUrl: item?.target_url || '',
        displayConfetti:
          item?.display_confetti === 1 ||
          item?.display_confetti === '1' ||
          item?.display_confetti === true,
      }))
      .filter((item) => item.text || item.imageUrl)

    promoImageLinks.value = promoLinks
    currentIndex.value = 0
    isVisible.value = promoLinks.length > 0
  } catch (error) {
    console.error('Error fetching promo data:', error)
    isVisible.value = false
  }
}

watch(
  () => slides.value.length,
  () => {
    if (isVisible.value) {
      startAutoScroll()
    }
  },
)

onMounted(() => {
  initializePromo()
})

onBeforeUnmount(() => {
  resetAutoScroll()
})
</script>

<style scoped>
.promo-fade-enter-active,
.promo-fade-leave-active {
  transition: opacity 0.2s ease;
}

.promo-fade-enter-from,
.promo-fade-leave-to {
  opacity: 0;
}

.promo-confetti {
  position: absolute;
  top: -24px;
  border-radius: 2px;
  opacity: 0.9;
  animation-name: promo-confetti-fall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}

@keyframes promo-confetti-fall {
  0% {
    transform: translate3d(0, 0, 0) rotate(0deg);
  }

  100% {
    transform: translate3d(24px, 110vh, 0) rotate(360deg);
  }
}
</style>
