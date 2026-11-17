<template>
  <div
    class="p-2 lg:bg-gray-200 h-svh overflow-hidden"
  >
    <div
      class="border-gray-200 rounded-lg bg-white h-full overflow-hidden grid grid-cols-1"
      :style="desktopCommentGridStyle"
    >
      <!-- order list -->
      <div
        class="bg-white text-gray-900 flex flex-col border-r border-gray-200 min-h-0 rounded-l-lg shadow-sm"
        :class="isMobile && !showListMobile ? 'hidden' : 'flex'"
      >
        <div
          class="h-[72px] p-4 border-b border-gray-200 flex items-start justify-between"
        >
          <div v-if="!isDesktopCollapsed" class="flex items-start gap-3">
            <button
              v-if="isMobile"
              type="button"
              class="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-gray-200 bg-white text-gray-700 transition-colors hover:bg-gray-50"
              aria-label="Open sidebar"
              @click="toggleSidebar"
            >
              <span class="material-symbols-outlined text-2xl">menu</span>
            </button>
            <div>
              <p class="text-[11px] uppercase tracking-wide text-gray-800">
                Orders
              </p>
              <p class="font-semibold text-sm">{{ orders.length }} total</p>
            </div>
          </div>
        </div>
        <div v-if="!isDesktopCollapsed" class="p-3">
          <div class="relative">
            <span class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-lg">
              search
            </span>
            <input
              v-model="searchTerm"
              type="text"
              placeholder="Search by customer, phone or order id..."
              class="w-full h-10 px-3 pl-10 text-sm text-gray-800 bg-gray-50 border border-gray-200 focus:outline-none focus:border-[#00a884] rounded-md"
            />
          </div>
        </div>
        <div
          class="flex-1 overflow-y-auto p-3 pt-0 space-y-1"
          :class="isDesktopCollapsed ? 'flex flex-col items-center pt-3' : ''"
        >
          <button
            v-for="order in filteredOrders"
            :key="order.name"
            class="w-full text-left px-4 py-2 hover:bg-[#f7f7fb] transition-colors border border-transparent rounded-xl"
            :class="{
              'bg-[#eaf5ef] text-[#2f9e62]': order.name === selectedOrderId,
              'justify-center !px-0': isDesktopCollapsed,
            }"
            @click="selectOrder(order.name)"
            :title="`${order.name} ${order.customer_name || ''} ${order.customer_phone || ''}`"
          >
            <div
              v-if="!isDesktopCollapsed"
              class="min-w-0 space-y-1"
            >
              <div class="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
                <div
                  class="min-w-0 text-sm font-semibold"
                  :class="order.name === selectedOrderId ? 'text-[#2f9e62]' : 'text-gray-800'"
                >
                  {{ order.name }}
                </div>
                <span
                  class="text-[11px] leading-4 break-words text-right"
                  :class="order.name === selectedOrderId ? 'text-[#4aa574]' : 'text-gray-500'"
                  v-if="order.latestTimestamp"
                >
                  {{ order.latestTimestamp }}
                </span>
              </div>

              <div class="grid grid-cols-[minmax(0,1fr)_auto] items-start gap-3">
                <div
                  class="min-w-0 text-sm"
                  :class="order.name === selectedOrderId ? 'text-[#4aa574]' : 'text-gray-800'"
                >
                  <div class="flex min-w-0 items-center gap-1">
                    <span class="min-w-0 flex-1 truncate">
                      {{ order.customer_name }}
                    </span>
                    <span class="shrink-0">
                      {{ order.customer_phone }}
                    </span>
                  </div>
                </div>
                <div class="flex items-center gap-1 justify-end">
                  <span
                    v-if="order.unseen_comment_count > 0"
                    class="min-w-5 h-5 px-1.5 rounded-full text-[10px] font-semibold inline-flex items-center justify-center"
                    :class="
                      order.name === selectedOrderId
                        ? 'bg-white text-[#2f9e62]'
                        : 'bg-[#00a884] text-white'
                    "
                  >
                    {{ order.unseen_comment_count }}
                  </span>
                  <span class="material-symbols-outlined text-gray-400 text-base">
                    chevron_right
                  </span>
                </div>
              </div>

              <div
                class="text-sm truncate"
                :class="order.name === selectedOrderId ? 'text-[#4aa574]' : 'text-gray-500'"
                v-if="order.latestPreview"
              >
                {{ order.latestPreview }}
              </div>
            </div>
            <div v-else class="relative flex items-center justify-center">
              <span
                class="max-w-[52px] truncate text-[10px] font-semibold"
                :class="order.name === selectedOrderId ? 'text-[#2f9e62]' : 'text-gray-600'"
              >
                {{ order.name }}
              </span>
              <span
                v-if="order.unseen_comment_count > 0"
                class="absolute -top-2 -right-2 min-w-5 h-5 px-1 rounded-full text-[10px] font-semibold inline-flex items-center justify-center bg-[#00a884] text-white"
              >
                {{ order.unseen_comment_count }}
              </span>
            </div>
          </button>
          <div v-if="isLoading" class="p-4 text-sm text-gray-500 text-center">
            <span class="inline-flex items-center gap-2">
              <span class="material-symbols-outlined animate-spin text-base">
                progress_activity
              </span>
              Loading...
            </span>
          </div>
          <div
            v-else-if="!orders.length"
            class="p-4 text-sm text-gray-500 text-center"
          >
            No orders available
          </div>
        </div>
        <div
          v-if="!isDesktopCollapsed"
          class="h-1.5 bg-gray-100 cursor-col-resize hidden md:block"
          @mousedown.prevent="startResizing"
        ></div>
      </div>

      <!-- chat pane -->
      <div
        class="bg-white flex flex-col overflow-hidden min-h-0 h-full shadow-sm border border-gray-200 border-l-0"
        :class="[
          isMobile && showListMobile ? 'hidden' : 'flex',
          !showDetailPanel ? 'rounded-r-lg' : '',
        ]"
      >
        <div
          class="h-14 px-4 flex items-center justify-between border-b border-gray-200 bg-gray-50"
        >
          <div class="flex items-center gap-2">
            <button
              v-if="isMobile"
              type="button"
              class="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-gray-200 bg-white text-gray-700 transition-colors hover:bg-gray-100"
              aria-label="Open sidebar"
              @click="toggleSidebar"
            >
              <span class="material-symbols-outlined text-xl">menu</span>
            </button>
            <button
              v-if="isMobile"
              type="button"
              class="inline-flex h-9 w-9 shrink-0 items-center justify-center text-gray-600 hover:text-gray-800"
              aria-label="Back to orders"
              @click="showListMobile = true"
            >
              <span class="material-symbols-outlined text-lg">arrow_back</span>
            </button>
            <div class="space-y-0.5">
              <div class="text-sm text-gray-800 flex items-center gap-2">
                <span>{{ selectedOrder?.name  }}</span>
                <span
                  v-if="selectedOrder?.status"
                  class="text-[11px] px-2 py-0.5 rounded-full border text-[#00a884] "
                >
                  {{ selectedOrder.status }}
                </span>
              </div>
              <div class="text-sm text-gray-800">
                {{ selectedOrder?.customer_name }} {{ selectedOrder?.customer_phone }}
              </div>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-if="getDisplayOrderType(orderDetail)"
              class="inline-flex items-center rounded-full bg-[#e8f1ff] px-3 py-1 text-xs font-bold text-[#1976d2]"
            >
              {{ getDisplayOrderType(orderDetail) }}
            </span>
            <div class="md:hidden">
            <router-link
              v-if="selectedOrder?.name"
              :to="`/main/${selectedOrder.name}`"
              target="_blank"
              class="text-xs text-[#00a884] hover:underline"
            >
              Order Details
            </router-link>
            </div>
          </div>
        </div>

        <div
          ref="chatBody"
          :key="selectedOrderId"
          class="flex-1 min-h-0 px-6 py-4 space-y-4 overflow-y-auto bg-gray-50"
        >
          <div v-if="isLoading" class="text-center text-sm text-gray-500 mt-8">
            <span class="inline-flex items-center gap-2">
              <span class="material-symbols-outlined animate-spin text-base">
                progress_activity
              </span>
              Loading comments...
            </span>
          </div>

          <div
            v-else-if="!selectedOrder"
            class="h-full flex items-center justify-center"
          >
         <main class="relative w-full overflow-hidden text-[#151515]">
  <!-- Background shapes -->
  <div class="absolute -bottom-20 -right-20 h-20 w-[260px] rounded-tl-[120px] bg-yellow-300 sm:-bottom-10 sm:w-[360px] lg:-bottom-6 lg:h-32 lg:w-[420px]"></div>

  <section class="relative z-10 mx-auto flex w-full max-w-5xl items-center justify-center px-4 py-6 sm:px-6 lg:px-8">
    <div class="grid w-full grid-cols-1 items-center gap-6 md:grid-cols-[0.85fr_1fr] md:gap-8 lg:gap-10">

      <!-- Phone mockup -->
      <div class="flex justify-center md:justify-end">
        <div class="relative h-[330px] w-[172px] overflow-hidden rounded-[32px] border-[6px] border-black bg-black shadow-2xl xs:h-[360px] xs:w-[188px] sm:h-[430px] sm:w-[224px] sm:rounded-[42px] sm:border-[8px] lg:h-[480px] lg:w-[250px]">
          <div class="absolute left-1/2 top-0 z-20 h-5 w-20 -translate-x-1/2 rounded-b-2xl bg-black sm:h-6 sm:w-28"></div>

          <img
            src="https://pickndropnepal.com/files/460x996bb.webp"
            alt="Pick & Drop Nepal app preview"
            class="h-full w-full object-cover"
          />
        </div>
      </div>

      <!-- Content -->
      <div class="text-center md:text-left">
        <h1 class="text-3xl font-black tracking-[0.12em] sm:text-4xl lg:text-5xl">
          DOWNLOAD
        </h1>

        <h2 class="mt-1 text-xl font-bold tracking-[0.18em] sm:text-2xl lg:text-3xl">
          OUR APP
        </h2>

        <p class="mx-auto mt-3 max-w-sm text-xs leading-5 text-gray-700 sm:text-sm sm:leading-6 md:mx-0">
          Get the Pick & Drop Nepal app to book pickups faster, track every
          delivery live, and manage your orders with ease — anytime, anywhere.
        </p>

        <div class="mt-6 flex flex-col items-center justify-center gap-4 sm:flex-row md:justify-start">
          <!-- Store buttons -->
          <div class="flex flex-row gap-3 sm:flex-col sm:gap-2">
            <a
              href="https://pickndropnepal.com/download"
              target="_blank"
              class="block w-[135px] transition hover:-translate-y-1 sm:w-[160px] lg:w-[165px]"
            >
              <img
                src="https://pickndropnepal.com/files/google-play.svg"
                alt="Get it on Google Play"
                class="block w-full"
              />
            </a>

            <a
              href="https://pickndropnepal.com/download"
              target="_blank"
              class="block w-[135px] transition hover:-translate-y-1 sm:w-[160px] lg:w-[165px]"
            >
              <img
                src="https://pickndropnepal.com/files/app-store.svg"
                alt="Download on the App Store"
                class="block w-full"
              />
            </a>
          </div>

          <!-- QR style box -->
          <a
            href="https://pickndropnepal.com/download"
            target="_blank"
            class="grid h-24 w-24 shrink-0 grid-cols-5 gap-1 bg-white p-2 shadow-xl transition hover:-translate-y-1 sm:h-28 sm:w-28"
            aria-label="Download Pick and Drop Nepal"
          >
            <div class="bg-black"></div>
            <div class="bg-black"></div>
            <div class="bg-black"></div>
            <div class="bg-white"></div>
            <div class="bg-black"></div>

            <div class="bg-black"></div>
            <div class="bg-white"></div>
            <div class="bg-black"></div>
            <div class="bg-white"></div>
            <div class="bg-white"></div>

            <div class="bg-black"></div>
            <div class="bg-black"></div>
            <div class="bg-white"></div>
            <div class="bg-black"></div>
            <div class="bg-black"></div>

            <div class="bg-white"></div>
            <div class="bg-black"></div>
            <div class="bg-white"></div>
            <div class="bg-black"></div>
            <div class="bg-white"></div>

            <div class="bg-black"></div>
            <div class="bg-white"></div>
            <div class="bg-black"></div>
            <div class="bg-black"></div>
            <div class="bg-black"></div>
          </a>
        </div>
      </div>
    </div>
  </section>
</main>
          </div>

          <div
            v-else-if="!selectedOrder.comments.length"
            class="text-center text-sm text-gray-500 mt-8"
          >
            No comments available.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="(msg, idx) in selectedOrder.comments"
              :key="idx"
              class="flex"
              :class="isStaff(msg) ? 'justify-start' : 'justify-end'"
            >
              <div class="max-w-[72%]">
                <div
                  class="rounded-lg shadow-sm text-sm leading-relaxed"
                  :class="
                    isStaff(msg)
                      ? isImageMessage(msg)
                        ? 'bg-gray-100 text-gray-800 border border-gray-200 px-2 py-1'
                        : 'bg-gray-100 text-gray-800 border border-gray-200 px-3 py-2'
                      : isImageMessage(msg)
                        ? 'bg-[#005c4b] text-[#e9edef] px-2 py-1'
                        : 'bg-[#005c4b] text-[#e9edef] px-3 py-2'
                  "
                >
                  <div
                    class="comment-html whitespace-pre-line break-words"
                    v-html="msg.content"
                  />
                </div>
                <div
                  class="mt-1 text-[11px]"
                  :class="
                    isStaff(msg)
                      ? 'text-left text-[#a7c8bd]'
                      : 'text-right text-gray-500'
                  "
                >
                  <span
                    v-if="isStaff(msg)"
                    class="inline-flex items-center gap-1"
                  >
                    <span
                      class="material-symbols-outlined text-base align-middle"
                      :class="msg.read ? 'text-[#53bdeb]' : 'text-[#8696a0]'"
                    >
                      done_all
                    </span>
                    <span>{{ msg.creation }}</span>
                  </span>
                  <span v-else>
                    {{ msg.comment_by }} • {{ msg.creation }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="selectedOrder"
          class="px-4 py-3 flex items-end gap-3 border-t border-gray-200 bg-gray-50 flex-shrink-0"
        >
          <textarea
            ref="composeTextarea"
            v-model="composeMessage"
            placeholder="Reply to comment..."
            rows="2"
            class="flex-1 min-h-[44px] overflow-hidden rounded-lg bg-white text-sm text-gray-800 px-3 py-2 resize-none focus:outline-none border border-gray-200 focus:border-[#00a884]"
            @keydown.enter.exact.prevent="sendMessage"
            @input="autoResizeCompose"
          />
          <button
            class="h-11 px-4 rounded-lg bg-[#00a884] text-white text-sm font-semibold disabled:opacity-50 inline-flex items-center gap-1"
            :disabled="!composeMessage.trim() || !selectedOrder"
            @click="sendMessage"
          >
            <span class="material-symbols-outlined text-base">send</span>
            Send
          </button>
        </div>
      </div>

      <div
        v-if="showDetailPanel"
        class="bg-white flex-col overflow-hidden min-h-0 h-full rounded-r-lg shadow-sm border border-gray-200 border-l-0 hidden md:flex"
      >
        <div class="flex flex-1 min-h-0 flex-col bg-gray-100">
          <div
            v-if="isOrderDetailLoading"
            class="flex h-full items-center justify-center text-sm text-gray-500"
          >
            <span class="inline-flex items-center gap-2">
              <span class="material-symbols-outlined animate-spin text-base">
                progress_activity
              </span>
              Loading order details...
            </span>
          </div>

          <div
            v-else-if="!selectedOrder"
            class="flex h-full items-center justify-center text-sm text-gray-500"
          >
            Select an order to view details.
          </div>

          <div
            v-else-if="!orderDetail"
            class="flex h-full items-center justify-center text-sm text-gray-500"
          >
            Order details unavailable.
          </div>

          <div v-else class="flex min-h-0 flex-1 flex-col">
            <div class="flex-shrink-0">
              <div class="h-[72px] border-b border-gray-200 bg-white p-4">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2">
                      <h3 class="truncate text-[16px] font-bold text-[#1d2b24]">
                        Order Details
                      </h3>
                      <span
                        v-if="orderDetail.express_delivery"
                        class="inline-flex items-center rounded-full bg-[#eaf5ef] px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wide text-[#23814f]"
                      >
                        Express
                      </span>
                    </div>
                    <p
                      v-if="orderDetail.reference_id"
                      class="mt-0.5 text-xs font-medium text-gray-500"
                    >
                      Ref No : {{ orderDetail.reference_id }}
                    </p>
                  </div>
                  <div class="flex shrink-0 items-center gap-2">

                    <router-link
                      v-if="selectedOrder?.name"
                      :to="`/main/${selectedOrder.name}`"
                      target="_blank"
                      class="inline-flex items-center gap-2 rounded-full border border-[#b8dcc7] bg-white px-3 py-1.5 text-xs font-semibold text-[#23814f]"
                    >
                      Open
                    </router-link>
                    <span
                      v-else
                      class="inline-flex items-center gap-2 rounded-full border border-[#b8dcc7] bg-white px-3 py-1.5 text-xs font-semibold text-[#23814f]"
                    >
                      <span class="h-2.5 w-2.5 rounded-full bg-[#23814f]"></span>
                      {{ orderDetail.status || 'Open' }}
                    </span>
                  </div>
                </div>
              </div>

              <div class="m-4 mb-3 overflow-hidden rounded-md border border-gray-200 bg-white">
                <div class="flex items-center justify-between bg-[#23814f] px-4 py-2 text-white">
                  <span class="text-[11px] font-extrabold uppercase tracking-[0.14em]">
                    Shipment Ticket
                  </span>
                  <span class="text-[11px] font-bold uppercase tracking-wide">
                  {{ orderDetail.order_name || '-' }}
                  </span>
                </div>

                <div class="relative px-4 py-4">
                  <div class="grid grid-cols-[minmax(0,1fr)_44px_minmax(0,1fr)] items-start gap-2">
                    <div class="min-w-0">
                      <p class="text-[10px] font-extrabold uppercase tracking-[0.14em] text-gray-400">
                        From
                      </p>
                      <p class="mt-1.5 break-words text-[13px] font-bold leading-4 text-[#1d2b24]">
                        {{ orderDetail.pickup_branch || '-' }}

                      </p>

                    </div>

                    <div class="flex flex-col items-center pt-3">
                      <div class="flex items-center gap-0.5 text-[#23814f]">
                        <span class="comment-pulse h-2.5 w-2.5 rounded-full border-[3px] border-[#23814f] bg-white"></span>
                        <span class="comment-dash-flow h-[2px] w-3"></span>
                        <span class="comment-arrow-drift material-symbols-outlined text-[15px]">trending_flat</span>
                        <span class="comment-dash-flow comment-dash-delay h-[2px] w-3"></span>
                        <span class="comment-pulse comment-pulse-delay h-3 w-3 rounded-full bg-[#23814f]"></span>
                      </div>

                    </div>

                    <div class="min-w-0 text-right">
                      <p class="text-[10px] font-extrabold uppercase tracking-[0.14em] text-gray-400">
                        To
                      </p>
                      <p class="mt-1.5 break-words text-[13px] font-bold leading-4 text-[#1d2b24]">
                        {{ orderDetail.destination_branch || '-' }}

                      </p>

                    </div>
                  </div>

                  <div class="relative my-3">
                    <span class="absolute -left-8 top-1/2 h-8 w-8 -translate-y-1/2 rounded-full bg-gray-50"></span>
                    <span class="absolute -right-8 top-1/2 h-8 w-8 -translate-y-1/2 rounded-full bg-gray-50"></span>
                    <div class="border-t-2 border-dashed border-[#dbe3de]"></div>
                  </div>

                  <div class="grid grid-cols-[1fr_auto] items-end gap-4">
                    <div>
                      <p class="text-[10px] font-extrabold uppercase tracking-[0.14em] text-gray-400">
                        Deliver To
                      </p>
                      <p class="mt-1.5 text-[12px] font-semibold leading-5 text-[#1d2b24]">
                        {{ orderDetail.location || '-' }}, {{ orderDetail.name_of_city_area || '-' }}
                      </p>
                    </div>

                  </div>
                </div>
              </div>

              <div class="mx-4 mt-0 mb-3 grid grid-cols-2 gap-3">
                <div class="rounded-md border border-gray-200 bg-white px-4 py-2.5">
                  <p class="text-[11px] font-bold tracking-[0.14em] text-gray-700">
                    COD
                  </p>
                  <p class="mt-1 text-[15px] font-bold leading-none text-[#1d2b24]">
                    {{ formatCurrency(orderDetail.cod_amount) }}
                  </p>
                </div>

                <div class="rounded-md border border-gray-200 bg-white px-4 py-2.5">
                  <p class="text-[11px] font-bold tracking-[0.14em] text-gray-700">
                    Delivery Charge
                  </p>
                  <p class="mt-1 text-[15px] font-bold leading-none text-[#1d2b24]">
                    {{ formatCurrency(orderDetail.delivery_amount) }}
                  </p>
                </div>
              </div>
            </div>

            <div
              v-if="orderStatusLogs.length"
              class="min-h-0 flex-1 overflow-hidden rounded-md border border-gray-200 bg-white mx-4 mb-3"
            >
              <div class="flex items-center justify-between px-4 py-3">
                <h4 class="text-[16px] font-bold text-[#1d2b24]">Status Logs</h4>
                <span class="text-xs font-semibold text-gray-400">
                  {{ orderStatusLogs.length }} updates
                </span>
              </div>

              <div class="h-full overflow-y-auto px-4 pb-4">
                <div
                  v-for="(log, index) in orderStatusLogs"
                  :key="`${log.timestamp}-${log.status}-${index}`"
                  class="relative pl-8 pb-6 last:pb-0"
                >
                  <div
                    class="absolute left-[8px] top-5 h-full w-[3px] rounded-full bg-[#e3e8e4] last:hidden"
                    :class="index === orderStatusLogs.length - 1 ? 'hidden' : ''"
                  ></div>
                  <div
                    class="absolute left-0 top-1 flex h-4 w-4 items-center justify-center rounded-full"
                    :class="getStatusLogDotClass(log.status)"
                  >
                    <div class="h-2 w-2 rounded-full bg-current"></div>
                  </div>

                  <div class="flex items-center gap-3">
                    <span
                      class="text-[13px] font-bold"
                      :class="getStatusLogTextClass(log.status)"
                    >
                      {{ log.status }}
                    </span>
                    <p class="text-xs font-semibold text-gray-400">
                      {{ formatStatusLogTimestamp(log.timestamp) }}
                    </p>
                  </div>
                  <p class="mt-1.5 text-[13px] leading-6 text-[#39453f] break-words">
                    {{ log.log }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch, nextTick } from 'vue'
import comments from '../data/comments'
import { useSidebar } from '@/components/ui/sidebar'
import {
  SIDEBAR_WIDTH,
  SIDEBAR_WIDTH_ICON,
} from '@/components/ui/sidebar/utils'

const COMMENT_SELECTION_KEY = 'ecommerce-comment-selected-order'
let hasHandledPageReload = false

const clearSelectionOnHardReload = () => {
  const entry = performance.getEntriesByType('navigation')[0]
  const isReload = entry?.type === 'reload'
  if (isReload && !hasHandledPageReload) {
    sessionStorage.removeItem(COMMENT_SELECTION_KEY)
    hasHandledPageReload = true
    return ''
  }
  hasHandledPageReload = true
  return sessionStorage.getItem(COMMENT_SELECTION_KEY) || ''
}

const orders = ref([])
const selectedOrderId = ref(clearSelectionOnHardReload())
const sidebarWidth = ref(320)
const isResizing = ref(false)
const isMobile = ref(false)
const showListMobile = ref(true)
const isCommentSidebarOpen = ref(true)
const isLoading = ref(false)
const isOrderDetailLoading = ref(false)
const composeMessage = ref('')
const composeTextarea = ref(null)
const searchTerm = ref('')
const chatBody = ref(null)
const orderDetail = ref(null)
const { setOpen, toggleSidebar } = useSidebar()

const isDesktopCollapsed = computed(
  () => !isMobile.value && !isCommentSidebarOpen.value,
)

const persistSelectedOrder = (id) => {
  if (id) {
    sessionStorage.setItem(COMMENT_SELECTION_KEY, id)
    return
  }
  sessionStorage.removeItem(COMMENT_SELECTION_KEY)
}

const parsePreviewText = (html) => {
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html || '', 'text/html')
    return (doc.body.textContent || '').trim()
  } catch {
    return html || ''
  }
}

const parseContent = (html) => {
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html || '', 'text/html')

    if (doc.body.querySelector('img, .failed-img, a')) {
      return doc.body.innerHTML || html || ''
    }

    return (doc.body.textContent || '').trim()
  } catch {
    return html || ''
  }
}

const formatTime = (date) =>
  date instanceof Date
    ? new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(date)
    : ''

const isStaff = (msg) =>
  msg?.comment_by?.toLowerCase().includes('staff') ||
  msg?.email === 'Administrator'

const isImageMessage = (msg) =>
  /<img|class=["']failed-img["']|<a/i.test(msg?.content || '')


const scrollToBottom = async () => {
  await nextTick()
  if (!selectedOrder.value?.name) return
  const el = chatBody.value
  if (el) {
    // Wait for next animation frame for smoother scroll
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight
    })
  }
}

const fetchComments = async () => {
  isLoading.value = true
  try {
    const resp = await comments.fetch()
    const data = resp.data
    // console.log('Fetched comments API response:', data)
    if (data && Array.isArray(data.comments)) {
      const mapped = data.comments.flatMap(
        (c) =>
          c.details?.map((d) => {
            const parsed =
              d.comments?.map((m) => {
                const dt = new Date(m.creation)
                return {
                  content: parseContent(m.content),
                  previewText: parsePreviewText(m.content),
                  creation: formatTime(dt),
                  createdAt: dt,
                  email: m.email,
                  comment_by: m.comment_by,
                  read: true,
                }
              }) || []

            parsed.sort((a, b) => a.createdAt - b.createdAt)
            const last = parsed[parsed.length - 1]
            return {
              name: d.name,
              customer_name: d.customer_name,
              customer_phone: d.customer_phone,
              vendorId: d.vendor_id,
              status: d.status,
              unseen_comment_count: d.unseen_comment_count || 0,
              comments: parsed,
              latestCreatedAt: last?.createdAt || null,
              latestTimestamp: last ? formatTime(last.createdAt) : '',
              latestPreview: last ? last.previewText.slice(0, 70) : '',
            }
          }) || [],
      )

      orders.value = mapped.sort((a, b) => {
        const ta = a.latestCreatedAt ? a.latestCreatedAt.getTime() : 0
        const tb = b.latestCreatedAt ? b.latestCreatedAt.getTime() : 0
        return tb - ta
      })
      // console.log('Mapped comment orders:', orders.value)

      const hasCurrentSelection = orders.value.some(
        (order) => order.name === selectedOrderId.value,
      )
      if (!hasCurrentSelection) {
        persistSelectedOrder('')
      }

      if (selectedOrderId.value) {
        await scrollToBottom()
      }
    }
  } catch (err) {
    console.error('Error fetching comments', err)
  } finally {
    isLoading.value = false
  }
}

const selectedOrder = computed(
  () => orders.value.find((o) => o.name === selectedOrderId.value) || null,
)

const showDetailPanel = computed(() => !isMobile.value && !!selectedOrder.value)

const desktopCommentGridStyle = computed(() => {
  if (isMobile.value) {
    return {}
  }

  if (!showDetailPanel.value) {
    return {
      gridTemplateColumns: isDesktopCollapsed.value
        ? `${SIDEBAR_WIDTH_ICON} minmax(0, 1fr)`
        : `${sidebarWidth.value}px minmax(0, 1fr)`,
    }
  }

  return {
    gridTemplateColumns: isDesktopCollapsed.value
      ? `${SIDEBAR_WIDTH_ICON} minmax(0, 1fr) 360px`
      : `${sidebarWidth.value}px minmax(0, 1fr) 360px`,
  }
})

const formatCurrency = (amount) => {
  const numeric = Number(amount)
  if (Number.isNaN(numeric)) return amount || '-'
  return `Rs ${numeric}`
}

const orderStatusLogs = computed(() => orderDetail.value?.status_logs || [])

const formatStatusLogTimestamp = (timestamp) => {
  if (!timestamp) return '-'

  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'numeric',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

const getStatusLogBadgeClass = (status) => {
  const normalizedStatus = String(status || '').toLowerCase()

  if (normalizedStatus.includes('received')) {
    return 'bg-[#19c6d4]'
  }

  if (
    normalizedStatus.includes('pickup') ||
    normalizedStatus.includes('process')
  ) {
    return 'bg-[#b7b4ff]'
  }

  if (normalizedStatus.includes('created')) {
    return 'bg-[#8f8f8f]'
  }

  return 'bg-[#2f9e62]'
}

const getStatusLogDotClass = (status) => {
  const normalizedStatus = String(status || '').toLowerCase()

  if (normalizedStatus.includes('received')) {
    return 'bg-[#dff7fa] text-[#19c6d4]'
  }

  if (
    normalizedStatus.includes('pickup') ||
    normalizedStatus.includes('process') ||
    normalizedStatus.includes('initiated')
  ) {
    return 'bg-[#e3f5ea] text-[#2f9e62]'
  }

  return 'bg-[#eef2ee] text-[#a7b0aa]'
}

const getStatusLogTextClass = (status) => {
  const normalizedStatus = String(status || '').toLowerCase()

  if (normalizedStatus.includes('received')) {
    return 'text-[#19aeca]'
  }

  if (
    normalizedStatus.includes('pickup') ||
    normalizedStatus.includes('process') ||
    normalizedStatus.includes('initiated')
  ) {
    return 'text-[#2f9e62]'
  }

  return 'text-[#7e8882]'
}

const filteredOrders = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  if (!term) return orders.value
  return orders.value.filter((order) =>
    [order.name, order.vendorId, order.customer_name, order.customer_phone, order.latestPreview]
      .filter(Boolean)
      .some((field) => field.toString().toLowerCase().includes(term)),
  )
})

const startResizing = () => (isResizing.value = true)
const stopResizing = () => (isResizing.value = false)
const handleMouseMove = (e) => {
  if (!isResizing.value) return
  const min = 240
  const max = 480
  const w = Math.min(Math.max(e.clientX, min), max)
  sidebarWidth.value = w
}

const autoResizeCompose = () => {
  const el = composeTextarea.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${el.scrollHeight}px`
}

const getDisplayOrderType = (order) => {
  if (!order) return ''

  const hasExchangeRef =
    String(order.return_with_exchange_order || '').trim() !== ''
  const isExchangeFlag =
    String(order.return_with_exchange_order || '').trim() === '1'

  if (order.order_type === 'Return' && (hasExchangeRef || isExchangeFlag)) {
    return 'Exchange Return'
  }

  return order.order_type || ''
}

watch(composeMessage, () => {
  nextTick(() => {
    autoResizeCompose()
  })
})

watch(selectedOrderId, () => {
  composeMessage.value = ''
  nextTick(() => {
    autoResizeCompose()
  })
})

const selectOrder = async (id) => {
  selectedOrderId.value = id
  persistSelectedOrder(id)
  if (isMobile.value) {
    showListMobile.value = false
  }
  await markCommentSeen(id)
  await scrollToBottom()
}

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')

const fetchOrderDetail = async (orderId) => {
  if (!orderId) {
    orderDetail.value = null
    return
  }

  isOrderDetailLoading.value = true
  orderDetail.value = null

  try {
    const resp = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_order_details?order_id=${encodeURIComponent(orderId)}`,
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
      },
    )

    const result = await resp.json()
    const payload = result?.message || result
    orderDetail.value = payload?.data?.[0] || null
  } catch (err) {
    console.error('Error fetching order detail:', err)
    orderDetail.value = null
  } finally {
    isOrderDetailLoading.value = false
  }
}

const markCommentSeen = async (orderId) => {
  if (!orderId) return

  try {
    const resp = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.update_comment_seen`,
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ order_id: orderId }),
      },
    )

    if (!resp.ok) {
      console.error('Failed to mark comments as seen:', await resp.text())
      return
    }

    orders.value = orders.value.map((order) =>
      order.name === orderId
        ? {
            ...order,
            unseen_comment_count: 0,
            comments: order.comments.map((comment) => ({
              ...comment,
              custom_vendor_seen: 1,
            })),
          }
        : order,
    )
  } catch (err) {
    console.error('Error marking comments as seen:', err)
  }
}

const sendMessage = async () => {
  const text = composeMessage.value.trim()
  if (!text || !selectedOrderId.value) return
  const order = selectedOrder.value
  if (!order) return

  const payload = {
    content: text,
    reference_name: selectedOrderId.value,
    custom_vendor_seen: 1,
  }

  try {
    const resp = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.create_comments`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      },
    )

    const now = new Date()
    const msg = {
      content: text,
      creation: formatTime(now),
      createdAt: now,
      email: 'you@local',
      comment_by: 'you',
      read: true,
    }

    // Add to message list
    order.comments.push(msg)

    // Update sidebar fields
    order.latestCreatedAt = now
    order.latestTimestamp = formatTime(now)
    order.latestPreview = text.slice(0, 70)

    // 🔥 Force sidebar refresh WITHOUT reloading whole page
    orders.value = [...orders.value].sort((a, b) => {
      const ta = a.latestCreatedAt ? a.latestCreatedAt.getTime() : 0
      const tb = b.latestCreatedAt ? b.latestCreatedAt.getTime() : 0
      return tb - ta
    })

    composeMessage.value = ''
    autoResizeCompose()

    await scrollToBottom()

    if (!resp.ok) {
      console.error('Failed to post:', await resp.text())
    }
  } catch (err) {
    console.error('Error posting comment:', err)
  }
}

onMounted(() => {
  const checkMobile = () => {
    isMobile.value = window.innerWidth < 768
    if (!isMobile.value) {
      showListMobile.value = true
    }
  }
  checkMobile()
  window.addEventListener('resize', checkMobile)
  nextTick(() => {
    autoResizeCompose()
  })

  fetchComments()
  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseup', stopResizing)

  onBeforeUnmount(() => {
    window.removeEventListener('resize', checkMobile)
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseup', stopResizing)
  setOpen(true)
})

watch(
  [isMobile, isCommentSidebarOpen],
  ([mobile, isOpen]) => {
    if (!mobile) {
      setOpen(!isOpen)
    }
  },
  { immediate: true },
)

// Watch for new comments or order switch
watch(
  () => selectedOrderId.value,
  async (id) => {
    persistSelectedOrder(id)
    await scrollToBottom()
    setTimeout(() => {
      fetchOrderDetail(id)
    }, 0)
  },
  { immediate: true },
)

watch(
  () => selectedOrder.value?.comments.length,
  async () => {
    await scrollToBottom()
  },
)
</script>

<style scoped>
@keyframes commentArrowDrift {
  0%,
  100% {
    transform: translateX(0);
  }
  50% {
    transform: translateX(3px);
  }
}

@keyframes commentPulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.08);
    opacity: 0.85;
  }
}

@keyframes commentDashFlow {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 16px 0;
  }
}

.comment-arrow-drift {
  animation: commentArrowDrift 1.4s ease-in-out infinite;
}

.comment-pulse {
  animation: commentPulse 1.8s ease-in-out infinite;
}

.comment-pulse-delay {
  animation-delay: 0.2s;
}

.comment-dash-flow {
  display: inline-block;
  background-image: repeating-linear-gradient(
    to right,
    #cfd8d2 0 6px,
    transparent 6px 10px
  );
  background-repeat: repeat-x;
  background-size: 16px 2px;
  animation: commentDashFlow 0.9s linear infinite;
}

.comment-dash-delay {
  animation-delay: 0.12s;
}
</style>

<style scoped>
.comment-html :deep(img) {
  display: block;
  max-width: 180px;
  max-height: 220px;
  width: auto;
  height: auto;
  margin-top: 2px;
  margin-bottom: 2px;
  border-radius: 12px;
  object-fit: cover;
}

.comment-html :deep(.failed-img) {
  display: inline-block;
  max-width: 180px;
  margin-top: 2px;
  margin-bottom: 2px;
}

.comment-html :deep(.failed-img a) {
  display: inline-block;
  max-width: 180px !important;
  text-decoration: none;
}

.comment-html :deep(.failed-img img) {
  max-width: 180px !important;
  max-height: 220px !important;
  width: 100% !important;
  height: auto !important;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  border-radius: 12px;
  object-fit: cover;
}
</style>
