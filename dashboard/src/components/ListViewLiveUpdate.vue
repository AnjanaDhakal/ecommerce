<template>
  <div>
    <PageLoader v-if="isLoading" />
    <div class="w-full overflow-x-auto pnd-scrollbar">
      <div class="w-max px-1 h-44">
        <div class="flex flex-row items-start gap-4">
          <div class="w-[360px] sm:block hidden">
            <div class="h-40 justify-center rounded-md shadow-sm">
              <div class="w-full rounded">
                <div class="rounded-t-md bg-[#ff9248]">
                  <p class="p-3 text-lg text-white font-semibold">Today's Delivery Update</p>
                </div>
                <div
                  class="flex sm:flex-row w-full items-center justify-around p-1 md:p-2"
                >
                  <div class="flex-col mb-4 sm:mb-0 space-y-3">
                    <p class="text-sm text-gray-800 font-pmedium">
                      Total Package
                    </p>
                    <p
                      class="text-base pl-5 text-gray-800 font-pmedium text-center"
                    >
                      {{ todayStatus.order_count }} Pkg
                    </p>
                  </div>
                  <div class="flex-col mb-4 sm:mb-0 space-y-3">
                    <p class="text-sm text-gray-800 font-pmedium text-center">
                      Total COD
                    </p>
                    <p
                      class="text-base pl-5 text-gray-800 font-pmedium text-center"
                    >
                      Rs {{ todayStatus.total_cod_amount }}
                    </p>
                  </div>
                  <div class="flex-col mb-4 sm:mb-0 space-y-3">
                    <p class="text-sm text-gray-800 font-pmedium">
                      Total Delivery Charge
                    </p>
                    <p
                      class="text-base pl-5 text-gray-800 font-pmedium text-center"
                    >
                      Rs {{ todayStatus.total_delivery_amount }}
                    </p>
                  </div>
                </div>
                <div class="flex justify-end p-1 rounded mr-2">
                  <router-link to="/account/orderpayment">
                    <Button class="text-xs font-semibold">View Details</Button>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
          <div class="w-[360px] sm:block hidden">
            <div class="h-40 justify-center rounded-md shadow-sm">
              <div class="w-full rounded">
                <!-- Header -->
                <div class="rounded-t-md bg-[#66bf17]">
                  <p class="p-3 text-lg text-white font-semibold">
                    Green Delivery CO<sub>2</sub> Offset
                  </p>
                </div>

                <!-- Content Section -->
                <div class="my-2">
                  <!-- Headers Row -->
                  <div class="flex justify-between mb-1">
                    <div class="flex space-x-20">
                      <p class="text-sm font-semibold pr-16"></p>
                      <p class="text-[10px] text-center font-semibold">
                        Monthly
                      </p>
                      <p class="text-[10px] text-center font-semibold">
                        Lifetime
                      </p>
                    </div>
                  </div>

                  <!-- Row 1 -->
                  <div class="flex items-center bg-gray-100 mb-1 p-1">
                    <p class="w-1/3 text-xs">Your Contribution</p>
                    <div class="flex gap-2">
                      <!-- Weekly -->
                      <div class="flex items-center gap-2">
                        <div
                          :class="[
                            'w-6 h-6 rounded-full flex items-center justify-center',
                            greenVendor.isWeeklyGreaterV
                              ? 'bg-green-500'
                              : 'bg-red-500',
                          ]"
                        >
                          <span
                            class="material-symbols-outlined text-white text-base"
                          >
                            monitoring
                          </span>
                        </div>
                        <div>
                          <p class="text-sm font-semibold">
                            {{ greenVendor.monthlyoffset }}Kg
                          </p>
                          <p class="text-[8px] text-gray-500">
                            {{ greenVendor.lastweek }}% since last week
                          </p>
                        </div>
                      </div>
                      <!-- Monthly -->
                      <div class="flex items-center gap-2">
                        <div
                          :class="[
                            'w-6 h-6 rounded-full flex items-center justify-center',
                            greenVendor.isMonthlyGreaterV
                              ? 'bg-green-500'
                              : 'bg-red-500',
                          ]"
                        >
                          <span
                            class="material-symbols-outlined text-white text-base"
                          >
                            monitoring
                          </span>
                        </div>
                        <div>
                          <p class="text-sm font-semibold">
                            {{ greenVendor.lifetimeoffset }}Kg
                          </p>
                          <p class="text-[8px] text-gray-500">
                            {{ greenVendor.lastmonth }}% since last week
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Row 2 -->
                  <div class="flex items-center bg-gray-100 p-1">
                    <p class="w-1/3 text-xs ">P&D Contribution</p>
                    <div class="flex gap-2">
                      <!-- Weekly -->
                      <div class="flex items-center gap-2">
                        <div
                          :class="[
                            'w-6 h-6 rounded-full flex items-center justify-center',
                            greenPnd.isWeeklyGreater
                              ? 'bg-green-500'
                              : 'bg-red-500',
                          ]"
                        >
                          <span
                            class="material-symbols-outlined text-white text-base"
                          >
                            monitoring
                          </span>
                        </div>
                        <div>
                          <p class="text-sm font-semibold">
                            {{ greenPnd.monthlyoffset }}Kg
                          </p>
                          <p class="text-[8px] text-gray-500">
                            {{ greenPnd.lastweek }}% since last week
                          </p>
                        </div>
                      </div>
                      <!-- Monthly -->
                      <div class="flex items-center gap-2">
                        <div
                          :class="[
                            'w-6 h-6 rounded-full flex items-center justify-center',
                            greenPnd.isMonthlyGreater
                              ? 'bg-green-500'
                              : 'bg-red-500',
                          ]"
                        >
                          <span
                            class="material-symbols-outlined text-white text-base"
                          >
                            monitoring
                          </span>
                        </div>
                        <div>
                          <p class="text-sm font-semibold">
                            {{ greenPnd.lifetimeoffset }}Kg
                          </p>
                          <p class="text-[8px] text-gray-500">
                            {{ greenPnd.lastmonth }}% since last week
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="w-[360px]">
            <div class="flex h-40 justify-center rounded-md shadow-sm">
              <div class="w-full rounded">
                <div class="rounded-t-md bg-[#5db9f1]">
                  <!-- <p class="p-3 text-lg text-white">
                    Total Balance
                    {{ totalAccount <= 0 ? 'Payable' : 'Receivable' }}
                  </p> -->
                  <p class="p-3 text-lg text-white font-semibold">
                    Total Balance
                    {{ balanceLabel }}
                  </p>
                </div>
                <div class="inline-flex w-full items-center justify-center p-2">
                  <div class="flex flex-col items-center justify-center">
                    <div class="flex flex-col items-center justify-center p-2">
                      <router-link to="/account/orderpayment">
                        <p
                          class="text-2xl text-center text-gray-800 font-pmedium"
                        >
                          Rs {{ totalAccount }}
                        </p>
                      </router-link>
                      <div class="flex justify-center space-x-4 p-2">
                        <!-- Add Balance Button -->
                        <!-- <button
                          class="flex items-center space-x-2 bg-purple-500 hover:bg-purple-600 text-white font-semibold px-2 rounded-full transition"
                        >
                          <span>Add Balance</span>
                          <span class="text-lg">+</span>
                        </button> -->

                        <!-- Cash Out Button -->
                        <button
                          class="flex text-sm items-center space-x-2 border border-purple-500 text-purple-500 hover:bg-purple-100 font-semibold p-2 rounded-full transition"
                          @click="handleCashOutClick"
                        >
                          <span>Cash Out</span>
                          <span class="text-md">→</span>
                        </button>
                        <DialogBank
                          :messageStatus="'success'"
                          :amount="totalAccount"
                          @close="handleDialogClose"
                        />
                      </div>
                      <div>
                        <p
                          class="text-xs text-gray-800"
                          v-html="lastSettlementText"
                        ></p>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="flex"></div>
              </div>
            </div>
          </div>




          <div class="w-[360px] sm:block hidden">
            <div class="h-40 justify-center rounded-md shadow-sm">
              <div class="w-full rounded">
                <div class="rounded-t-md bg-[#66bf17]">
                  <p class="p-3 text-lg text-white font-semibold">All Time Status</p>
                </div>
                <div
                  class="flex sm:flex-row w-full items-center justify-around p-1 md:p-2"
                >
                  <div class="flex-col mb-4 sm:mb-0 space-y-3">
                    <p class="text-sm text-gray-800 font-pmedium">
                      Total Package
                    </p>
                    <p
                      class="text-base pl-5 text-gray-800 font-pmedium text-center"
                    >
                      {{ totalStatus.order_count }} Pkg
                    </p>
                  </div>
                  <div class="flex-col mb-4 sm:mb-0 space-y-3">
                    <p class="text-sm text-gray-800 font-pmedium text-center">
                      Total COD
                    </p>
                    <p
                      class="text-base pl-5 text-gray-800 font-pmedium text-center"
                    >
                      Rs {{ totalStatus.total_cod_amount }}
                    </p>
                  </div>
                  <div class="flex-col mb-4 sm:mb-0 space-y-3">
                    <p class="text-sm text-gray-800 font-pmedium">
                      Total Delivery Charge
                    </p>
                    <p
                      class="text-base pl-5 text-gray-800 font-pmedium text-center"
                    >
                      Rs {{ totalStatus.total_delivery_amount }}
                    </p>
                  </div>
                </div>
                <div class="flex justify-end p-1 rounded mr-2">
                  <router-link to="/account/orderpayment">
                    <Button class="text-xs font-semibold">View Details</Button>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div
      class="pointer-events-none fixed bottom-4 right-4 z-30 flex flex-col items-end"
    >
      <transition name="timeline-slide">
        <div
          v-if="pickupNotifications.length"
          class="pointer-events-auto mb-2 flex flex-col items-end gap-2"
        >
          <div
            v-if="timelineOpen && selectedPickupNotification"
            class="relative w-[260px] max-w-[calc(100vw-1.5rem)] overflow-hidden rounded-2xl border border-green-100 bg-white/96 p-1 shadow-2xl backdrop-blur bg-gray-300 sm:w-[220px]"
          >
            <button
              type="button"
              class="absolute right-3 top-2 z-10 text-xl font-medium leading-none text-slate-600 transition hover:text-slate-900"
              aria-label="Close pickup timeline"
              @click="timelineOpen = false"
            >
              x
            </button>

            <div class="ml-3 mr-8 flex items-center justify-between gap-2">
              <div class="flex items-center gap-1">
                <h3 class="text-[11px] font-semibold text-slate-900">
                  Pickup Timeline
                </h3>
              </div>
              <div
                class="mb-1 rounded-full bg-green-50 px-2 py-1 text-[10px] font-semibold text-green-700 min-w-[34px] text-center"
              >
                {{ pickupNotifications.length }}
              </div>
            </div>

            <div
              class="rounded-2xl border border-green-100 bg-white/95 p-2 shadow-sm"
            >
              <div class="mb-1 flex items-center justify-between gap-2">
                <span class="text-[10px] font-semibold text-slate-900">
                  {{ selectedPickupNotification.stages.length }}/{{ allStages.length }}
                </span>
                <span
                  class="rounded-full bg-slate-100 px-2 py-0.5 text-[9px] font-semibold uppercase tracking-[0.12em] text-slate-600"
                >
                  {{ selectedPickupNotification.status }}
                </span>
              </div>

              <div
                v-if="selectedPickupNotification.completedStage"
                class="rounded-xl border border-green-200 bg-green-50 px-3 py-3 text-center"
              >
                  <div class="mx-auto mb-2 text-[24px] font-semibold leading-none text-green-600">
                    ✓
                  </div>
                  <h3 class="text-[13px] font-black leading-tight text-slate-900">
                    Pickup Completed!
                  </h3>
                  <div class="mt-2 inline-flex items-center rounded-xl border border-slate-200 bg-white px-2 py-1 text-slate-800">
                    <div class="flex items-center gap-1 text-[9px]">
                      <span class="material-symbols-outlined text-[12px]">calendar_month</span>
                      <span>{{ getCompletedDateDisplay(selectedPickupNotification.completedStage) }}</span>
                    </div>
                    <div class="mx-1.5 h-3 w-px bg-slate-300"></div>
                    <div class="flex items-center gap-1 text-[9px]">
                      <span class="material-symbols-outlined text-[12px]">schedule</span>
                      <span>{{ getCompletedTimeDisplay(selectedPickupNotification.completedStage) }}</span>
                    </div>
                  </div>
              </div>

              <div v-else class="space-y-1">
                <div
                  v-for="(item, index) in getDisplayedStages(selectedPickupNotification.stages)"
                  :key="`${selectedPickupNotification.name}-${index}`"
                  class="flex gap-1"
                >
                    <div class="flex flex-col items-center">
                      <div
                        class="flex h-5 w-5 items-center justify-center rounded-full border text-[11px] font-bold transition-colors"
                        :class="
                          item.completed
                            ? 'border-green-300 bg-green-100 text-green-700'
                            : 'border-slate-300 bg-slate-100 text-slate-400'
                        "
                      >
                        ✓
                      </div>
                    </div>

                    <div
                      class="mb-1 min-w-0 flex-1 rounded-xl border px-2 py-1.5 text-left transition-colors bg-white"
                      :class="
                        item.completed
                          ? 'border-green-200 bg-green-50'
                          : 'border-slate-200 bg-slate-50'
                      "
                    >
                      <div class="flex items-start justify-between gap-2">
                        <p
                          class="text-[10px] font-semibold leading-tight"
                          :class="item.completed ? 'text-green-700' : 'text-slate-500'"
                        >
                          {{ item.stage }}
                        </p>
                        <div
                          v-if="isLatestActiveStageFor(item, selectedPickupNotification.stages)"
                          class="flex shrink-0 items-center gap-1"
                        >
                          <span
                            class="timeline-active-pill rounded-full bg-green-600 px-2 py-0.5 text-[9px] font-bold uppercase tracking-[0.18em] text-white"
                          >
                            Active
                          </span>
                        </div>
                      </div>
                      <p
                        v-if="getTimelineItemDateTime(item)"
                        class="mt-0.5 break-words text-[8px] leading-tight text-slate-500"
                      >
                        {{ getTimelineItemDateTime(item) }}
                      </p>
                    </div>
                </div>
              </div>

            </div>
          </div>

          <div class="pointer-events-auto flex max-w-[760px] flex-wrap justify-end gap-2 self-end">
            <button
              v-for="notification in pickupNotifications"
              :key="notification.name"
              type="button"
              class="max-w-[min(16rem,calc(100vw-2rem))] truncate rounded-full border px-3 py-1.5 text-left text-[10px] font-semibold transition"
              :title="notification.pickup_address"
              :class="
                selectedPickupName === notification.name
                  ? 'border-green-500 bg-green-100 text-green-700'
                  : 'border-slate-200 bg-white text-slate-600 hover:border-green-300 hover:bg-green-50'
              "
              @click="togglePickupTab(notification.name)"
            >
              {{ notification.pickup_address }}
            </button>
          </div>
        </div>
      </transition>
    </div>

       <div v-if="sliderImage" class="hidden lg:block">
            <a
              v-if="sliderLink"
              :href="sliderLink"
              target="_blank"
              rel="noopener noreferrer"
              class="block"
            >
              <img
                :src="sliderImage"
                alt="App Banner"
                class="h-full w-full object-cover rounded-md"
              />
            </a>
            <img
              v-else
              :src="sliderImage"
              alt="App Banner"
              class="h-full w-full object-cover rounded-md"
            />
          </div>

    <div
      class="rounded bg-gray-50 p-1 mt-1 flex flex-col sm:flex-row justify-between items-start sm:items-center mb-3 px-2"
    >
      <h2>Live Status</h2>
      <div
        class="grid w-full grid-flow-col grid-rows-2 auto-cols-max gap-x-4 gap-y-2 overflow-x-auto pb-1 sm:inline-flex sm:flex-nowrap sm:space-x-2 sm:space-y-0 sm:overflow-x-auto sm:pb-0"
      >
        <!-- Sent for Delivery Status -->
        <div
          class="flex items-center space-x-2 cursor-pointer"
          @click="onStatusClick('Sent for Delivery')"
        >
          <div
            class="bg-[#65fffd] rounded-full p-3 w-4 h-4 text-xs flex items-center text-black justify-center"
          >
            {{ status_order_count['Sent for Delivery'] || 0 }}
          </div>
          <p class="text-xs font-semibold whitespace-nowrap">
            Sent for Delivery
          </p>
        </div>

        <!-- Cancelled Status -->
        <div
          class="flex items-center space-x-2 cursor-pointer"
          @click="onStatusClick('Cancelled in Branch')"
          :style="{ color: getBadgeStyle('Cancelled in Branch').color }"
        >
          <div
            class="rounded-full p-3 w-4 h-4 text-xs flex items-center justify-center"
            :style="getBadgeStyle('Cancelled in Branch')"
          >
            {{ status_order_count['Cancelled in Branch'] || 0 }}
          </div>
          <p class="text-xs text-black font-semibold whitespace-nowrap">
            Cancelled
          </p>
        </div>

        <!-- Received Status -->
        <div
          class="flex items-center space-x-2 cursor-pointer"
          @click="onStatusClick('Received')"
          :style="{ color: getBadgeStyle('Received').color }"
        >
          <div
            class="rounded-full p-3 w-4 h-4 text-xs flex items-center justify-center"
            :style="getBadgeStyle('Received')"
          >
            {{ status_order_count['Received'] || 0 }}
          </div>
          <p class="text-xs font-semibold whitespace-nowrap">Received</p>
        </div>

        <!-- Processing on Branch Status -->
        <div
          class="flex items-center space-x-1 cursor-pointer"
          @click="onStatusClick('Processing in Branch')"
          :style="{ color: getBadgeStyle('Processing in Branch').color }"
        >
          <div
            class="rounded-full p-3 w-4 h-4 text-xs flex items-center justify-center"
            :style="getBadgeStyle('Processing in Branch')"
          >
            {{ status_order_count['Processing in Branch'] || 0 }}
          </div>
          <p class="text-xs font-semibold whitespace-nowrap">
            Processing in Branch
          </p>
        </div>

        <!-- Failed Attempt Status -->
        <div
          class="flex items-center space-x-2 cursor-pointer"
          @click="onStatusClick('Failed Attempt')"
          :style="{ color: getBadgeStyle('Failed Attempt').color }"
        >
          <div
            class="rounded-full p-3 w-4 h-4 text-xs flex items-center justify-center"
            :style="getBadgeStyle('Failed Attempt')"
          >
            {{ status_order_count['Failed Attempt'] || 0 }}
          </div>
          <p class="text-xs font-semibold whitespace-nowrap">
            Failed Attempt By Rider
          </p>
        </div>

        <!-- Failed Attempt & Return to Branch Status -->
        <div
          class="flex items-center space-x-2 cursor-pointer"
          @click="onStatusClick('Failed Attempt & Return to Branch')"
        >
          <div
            class="bg-[#ff8533] rounded-full p-3 w-4 h-4 text-xs flex items-center text-black justify-center"
          >
            {{ status_order_count['Failed Attempt & Return to Branch'] || 0 }}
          </div>
          <p class="text-xs font-semibold whitespace-nowrap">
            Failed Attempt & Return to Branch
          </p>
        </div>
        <!-- Delivered Status -->
        <div
          class="flex items-center space-x-2 cursor-pointer"
          @click="onStatusClick('Delivered')"
          :style="{ color: getBadgeStyle('Delivered').color }"
        >
          <div
            class="rounded-full p-3 w-4 h-4 text-xs flex items-center justify-center"
            :style="getBadgeStyle('Delivered')"
          >
            {{ status_order_count['Delivered'] || 0 }}
          </div>
          <p class="text-xs text-black font-semibold whitespace-nowrap">
            Delivered
          </p>
        </div>
      </div>
    </div>

    <div class="mb-4">
      <div class="grid grid-cols-2 items-end gap-3 sm:flex sm:flex-wrap sm:gap-4">
        <!-- Date Pickers -->
        <div class="contents sm:flex sm:flex-wrap sm:items-end sm:gap-4">
          <div class="flex min-w-0 flex-col">
            <label class="text-sm pb-2"
              >Start date<span class="text-red-600">*</span></label
            >
            <DatePicker
              class="w-full sm:w-40"
              v-model="dateValue"
              variant="subtle"
              placeholder="YYYY-MM-DD"
            />
          </div>
          <div class="flex min-w-0 flex-col">
            <label class="text-sm pb-2"
              >End date<span class="text-red-600">*</span></label
            >
            <DatePicker
              class="w-full sm:w-40"
              variant="subtle"
              placeholder="YYYY-MM-DD"
              v-model="dateValue1"
            />
          </div>
        </div>

        <!-- Status Filter and Search -->
        <div class="contents sm:flex sm:flex-wrap sm:items-end sm:gap-4">
          <div class="flex min-w-0 flex-col">
            <label class="text-sm pb-2">Status Filter</label>
            <select
              v-model="inputValue1"
              class="form-select block w-full rounded-md border-gray-300 text-base shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50 sm:w-44 sm:text-sm"
            >
              <option value="">All</option>
              <option value="All Processing">All Processing</option>
              <option value="Received">Received</option>
              <option value="Processing in Branch">Processing in Branch</option>
              <option value="Sent for Delivery">Sent for Delivery</option>
              <option value="Cancelled in Branch">Cancelled</option>
              <option value="Delivered">Delivered</option>
              <option value="Failed Attempt & Return to Branch">
                Failed Attempt & Return to Branch
              </option>
              <option value="Failed Attempt">Failed Attempt By Ridert</option>
              <option value="Return to Vendor">Return to Vendor</option>
              <option value="Delivered to Vendor">Delivered to Vendor</option>
            </select>
          </div>
          <div class="flex min-w-0 flex-col">
            <label class="text-sm pb-2">Search</label>
            <FormControl
              class="w-full sm:w-64"
              type="search"
              size="sm"
              variant="subtle"
              placeholder="Name / Order ID / Mobile / Reference ID "
              v-model="search"
              @keydown.enter.prevent="onFilterClick"
            />
          </div>
        </div>

        <!-- Buttons -->
        <div class="col-span-2 flex flex-wrap items-end gap-3 sm:col-span-1">
          <Button
            variant="solid"
            size="sm"
            class="min-w-[100px]"
            @click="onFilterClick"
            >Filter</Button
          >
          <Button
            variant="solid"
            size="sm"
            class="min-w-[100px]"
            @click="clearAll"
            >Clear All</Button
          >
        </div>
      </div>
    </div>
    <div class="overflow-x-auto">
      <table class="min-w-full text-sm font-pregular">
        <thead>
          <tr>
            <!-- Serial Number Header -->
            <th
              class="px-6 py-3 h-10 font-pregular text-left text-xs text-gray-500 bg-gray-100 tracking-wider"
            >
              SN
            </th>
            <!-- Existing Column Headers -->
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-6 py-3 h-10 text-left text-xs font-pregular text-gray-500 bg-gray-100 tracking-wider"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in rows"
            :key="row.name"
            class="status-row"
            :style="
              getBadgeStyle(
                row.status ||
                  row.status_after_warehouse ||
                  row.status_before_warehouse,
              )
            "
          >
            <!-- Serial Number Column -->
            <td
              class="px-28 h-10 py-9 my-4 whitespace-nowrap font-pregular text-xs border border-white white-border-all-sides"
            >
              {{ (currentPage - 1) * pageSize + index + 1 }}
            </td>
            <!-- Existing Columns -->
            <td
              v-for="column in columns"
              :key="column.key"
              :style="{
                width: column.width,
                ...(column.key === 'status'
                  ? getBadgeStyle(
                      row.status ||
                        row.status_after_warehouse ||
                        row.status_before_warehouse,
                    )
                  : {}),
              }"
              class="px-28 h-10 py-9 my-4 whitespace-wrap font-pregular text-xs border border-white white-border-all-sides"
            >
              <router-link
                :to="`/main/${row.name.split(' / ')[0]}`"
                target="_blank"
              >
                <span
                  v-if="column.key === 'status'"
                  class="inline-flex items-center gap-1"
                >
                  <span v-html="row[column.key]"></span>
                  <template
                    v-if="row.order_type_icon && row.order_type_icon.length"
                  >
                    <span
                      v-for="(icon, idx) in row.order_type_icon"
                      :key="idx"
                      :class="[
                        'material-symbols-outlined text-[14px] align-middle',
                        icon.color,
                      ]"
                      :title="icon.title || ''"
                    >
                      {{ icon.name }}
                    </span>
                  </template>
                </span>
                <span v-else v-html="row[column.key]"></span>
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p class="text-center font-pmedium text-sm mt-8" v-if="rows.length === 0">
      {{ options.emptyState.title }}
    </p>

    <Pagination
      v-slot="{ page }"
      :items-per-page="pageSize"
      :total="totalOrders"
      :page="currentPage"
      class="mt-4"
      :class="pickupNotifications.length ? 'mb-24' : ''"
    >
      <PaginationContent v-slot="{ items }">
        <PaginationPrevious @click="changePage(page - 1)" />

        <template v-for="(item, index) in items" :key="index">
          <PaginationItem
            v-if="item.type === 'page'"
            :value="item.value"
            :is-active="item.value === page"
            @click="changePage(item.value)"
          >
            {{ item.value }}
          </PaginationItem>
        </template>

        <PaginationNext @click="changePage(page + 1)" />
      </PaginationContent>
    </Pagination>

    <div class="inline-block lg:hidden fixed bottom-24 right-4">
      <DialogPickup />
    </div>
  </div>
</template>
<script setup>
import { useToast } from 'vue-toastification'
import { displaybank } from '../composables/displaybank'
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { DatePicker, Button, FormControl } from 'frappe-ui'
import PageLoader from './PageLoader.vue'
import dayjs from 'dayjs'
import DialogBank from './DialogBank.vue'
import DialogPickup from './DialogPickup.vue'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination'

const toast = useToast()
// const handleCashOutClick = () => {
//  // console.log('Before setting isDisplay:', displaybank.isDisplay)
//   displaybank.isDisplay = true // Open the dialog
//  // console.log('After setting isDisplay:', displaybank.isDisplay)
// }

// Method to handle dialog close

const USE_STATIC_TIMELINE_PREVIEW = false
const staticTimelinePreview = [
  { stage: 'Pickup Requested', completed: true, time: '16 May 2026', order: 1 },
  { stage: 'Pickup Activated', completed: true, time: '16 May 2026', order: 2 },
  { stage: 'Rider Accepted', completed: true, time: '16 May 2026', order: 3 },
  { stage: 'Pickup Completed', completed: true, time: '16 May 2026 10:45 AM', rawTime: '2026-05-16 10:45:00', order: 4 },
]

const stages = ref(USE_STATIC_TIMELINE_PREVIEW ? staticTimelinePreview : [])
const pickupNotifications = ref(
  USE_STATIC_TIMELINE_PREVIEW
    ? [{ name: 'preview', pickup_address: 'Preview Address', status: 'Active', stages: staticTimelinePreview }]
    : [],
)
const selectedPickupName = ref(
  USE_STATIC_TIMELINE_PREVIEW ? 'preview' : '',
)
const timelineOpen = ref(true)

const allStages = [
  'Pickup Requested',
  'Pickup Activated',
  'Rider Accepted',
  'Pickup Completed',
]
const isPickupCompleted = computed(() => {
  if (stages.value.length < allStages.length) return false
  return allStages.every((stage) =>
    stages.value.some((item) => item.stage === stage && item.completed),
  )
})
const pickupCompletedStage = computed(() =>
  stages.value.find((item) => item.stage === 'Pickup Completed'),
)
const pickupCompletedMoment = computed(() => {
  const rawValue =
    pickupCompletedStage.value?.rawTime || pickupCompletedStage.value?.time

  if (!rawValue) return null

  const formats = [
    'DD MMM YYYY hh:mm A',
    'D MMM YYYY hh:mm A',
    'YYYY-MM-DD HH:mm:ss',
    'YYYY-MM-DD HH:mm',
    'YYYY-MM-DD',
  ]

  for (const format of formats) {
    const parsed = dayjs(rawValue, format, true)
    if (parsed.isValid()) return parsed
  }

  const fallback = dayjs(rawValue)
  return fallback.isValid() ? fallback : null
})
const pickupCompletedDateDisplay = computed(() => {
  if (pickupCompletedMoment.value) {
    return pickupCompletedMoment.value.format('DD MMM YYYY')
  }

  return pickupCompletedStage.value?.time || ''
})
const pickupCompletedTimeDisplay = computed(() => {
  if (pickupCompletedMoment.value) {
    return pickupCompletedMoment.value.format('hh:mm A')
  }

  return '--:--'
})
const parseTimelineMoment = (rawValue) => {
  if (!rawValue) return null

  const formats = [
    'DD MMM YYYY hh:mm A',
    'D MMM YYYY hh:mm A',
    'YYYY-MM-DD HH:mm:ss',
    'YYYY-MM-DD HH:mm',
    'YYYY-MM-DD',
  ]

  for (const format of formats) {
    const parsed = dayjs(rawValue, format, true)
    if (parsed.isValid()) return parsed
  }

  const fallback = dayjs(rawValue)
  return fallback.isValid() ? fallback : null
}
const getTimelineItemDateTime = (item) => {
  const parsed = parseTimelineMoment(item?.rawTime || item?.time)

  if (!parsed) return item?.time || ''

  return `${parsed.format('DD MMM YYYY')}, ${parsed.format('hh:mm A')}`
}
const getCompletedDateDisplay = (item) => {
  const parsed = parseTimelineMoment(item?.rawTime || item?.time)
  return parsed ? parsed.format('DD MMM YYYY') : item?.time || ''
}
const getCompletedTimeDisplay = (item) => {
  const parsed = parseTimelineMoment(item?.rawTime || item?.time)
  return parsed ? parsed.format('hh:mm A') : '--:--'
}
const displayedStages = computed(() => {
  if (stages.value.length === allStages.length) {
    return stages.value.slice(-1)
  }

  return [...stages.value].sort((a, b) => (b.order || 0) - (a.order || 0))
})
const getDisplayedStages = (stageList) => {
  if (stageList.length === allStages.length) {
    return stageList.slice(-1)
  }

  return [...stageList].sort((a, b) => (b.order || 0) - (a.order || 0))
}
const latestActiveStageIndex = computed(() => {
  if (isPickupCompleted.value || stages.value.length === 0) return -1
  return stages.value.length - 1
})

const isLatestActiveStage = (item) => {
  const latestStage = stages.value[latestActiveStageIndex.value]
  return !!latestStage && latestStage.stage === item.stage
}
const isLatestActiveStageFor = (item, stageList) => {
  if (!stageList.length || stageList.length === allStages.length) return false
  const latestStage = stageList[stageList.length - 1]
  return !!latestStage && latestStage.stage === item.stage
}
const selectedPickupNotification = computed(() => {
  if (!pickupNotifications.value.length) return null
  return (
    pickupNotifications.value.find(
      (notification) => notification.name === selectedPickupName.value,
    ) || pickupNotifications.value[0]
  )
})

const togglePickupTab = (name) => {
  if (selectedPickupName.value === name) {
    timelineOpen.value = !timelineOpen.value
    return
  }

  selectedPickupName.value = name
  timelineOpen.value = true
}

const fetchTimeline = async () => {
  if (USE_STATIC_TIMELINE_PREVIEW) return

  try {
    const res = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_pickuptimelines`,
    )

    const json = await res.json()

    const notifications = json?.message?.notifications || []

    pickupNotifications.value = notifications.map((notification) => {
      const notificationStages = [...(notification.data || [])]
        .sort((a, b) => (a.order || 0) - (b.order || 0))
        .map((item, index) => ({
          stage: item.stage,
          completed: true,
          time: item.display_time || null,
          rawTime: item.raw_time || null,
          order: item.order || index + 1,
        }))

      return {
        name: notification.name,
        pickup_address: notification.pickup_address,
        status: notification.status,
        stages: notificationStages,
        completedStage: notificationStages.find(
          (item) => item.stage === 'Pickup Completed',
        ) || null,
      }
    })

    selectedPickupName.value = pickupNotifications.value[0]?.name || ''
    stages.value = pickupNotifications.value[0]?.stages || []
  } catch (err) {
    console.error('Timeline error:', err)
  }
}

const option = { maximumFractionDigits: 2 }
const options = reactive({
  emptyState: {
    title: 'No orders found',
  },
})

const numericTotal = computed(() => Number(totalAccount.value))
const balanceLabel = computed(() =>
  numericTotal.value <= 0 ? 'Payable' : 'Receivable',
)

// Date range and search input
const dateValue = ref(dayjs().subtract(365, 'day').format('YYYY-MM-DD')) // Start date
const dateValue1 = ref(dayjs().format('YYYY-MM-DD')) // End date
const search = ref('')

// Pagination and table data
const currentPage = ref(1)
const pageSize = ref(60)
const rows = ref([])
const totalOrders = ref(0)
const totalPages = computed(() =>
  Math.max(
    1,
    Math.ceil((totalOrders.value || rows.value.length || 0) / pageSize.value),
  ),
)
const STATUS_FILTER_KEY = 'live_status_filter'
const savedStatusFilter = localStorage.getItem(STATUS_FILTER_KEY)
const initialStatus =
  savedStatusFilter === 'All' ? '' : savedStatusFilter || 'All Processing'
const inputValue1 = ref(initialStatus)
const isLoading = ref(false)

// Status tracking
const todayStatus = ref({
  order_count: 0,
  total_cod_amount: 0,
  total_delivery_amount: 0,
})
const greenVendor = ref({
  weekly: 0,
  monthly: 0,
  lastmonth: 0,
  lastweek: 0,
  isWeeklyGreaterV: ref(true),
  isMonthlyGreaterV: ref(true),
  monthlyoffset: 0,
  lifetimeoffset: 0,
  sevendaysoffset: 0,
})

const greenPnd = ref({
  weekly: 0,
  monthly: 0,
  lastmonth: 0,
  lastweek: 0,
  isWeeklyGreater: ref(true),
  isMonthlyGreater: ref(true),
  monthlyoffset: 0,
  lifetimeoffset: 0,
  sevendaysoffset: 0,
})

const totalStatus = ref({
  order_count: 0,
  total_cod_amount: 0,
  total_delivery_amount: 0,
})
const status_order_count = ref(0)
const totalAccount = ref(0)
const setteledAmount = ref(0)
const lastSettledAmount = ref('')
const lastPaymentDate = ref('')
const sliderImage = ref('')
const sliderLink = ref('')
const lastSettlementText = computed(() => {
  if (!lastSettledAmount.value && !lastPaymentDate.value) return ''
  const amt = lastSettledAmount.value || '0.00'
  const dt = lastPaymentDate.value || ''
  const datePart = dt ? ` on <strong>${dt}</strong>` : ''
  return `Last Settlement NPR <strong>${amt}</strong>${datePart}`
})
import { useLiveUpdateCount } from '@/composables/liveUpdateCount'
const { liveUpdateCount, setLiveUpdateCount, setLiveOpenInitCount } =
  useLiveUpdateCount()

const onStatusClick = (status) => {
  inputValue1.value = status // Set the selected status
  onFilterClick() // Trigger the filter
}

// Table columns
const columns = reactive([
  { label: 'Received Date', key: 'display_date' },
  //{ label: 'receiveDate', key: 'received_date' },
  { label: 'Order Code', key: 'name', width: '100px' },
  { label: 'Customer Name', key: 'customer_name', width: '100px' },
  { label: 'Phone', key: 'primary_mobile_no' },
  { label: 'Address', key: 'location', width: '120px' },
  { label: 'Destination Branch', key: 'destination_branch', width: '120px' },
  { label: 'COD Amount', key: 'cod_amount' },
  { label: 'Delivery Amount', key: 'delivery_amount', width: '80px' },
  { label: 'Status', key: 'status' },
  { label: 'Attempt', key: 'attempt', width: '5px' },
  { label: 'Action', key: 'action' },
])

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const fetchSliderImage = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_slider_data`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      },
    )

    if (!response.ok) return

    const data = await response.json()
    const slider = data?.message?.data?.[0]
    sliderImage.value = slider?.image || ''
    sliderLink.value = slider?.title || ''
  } catch (error) {
    console.error('Error fetching slider image:', error)
  }
}

const clearAll = () => {
  search.value = ''
  inputValue1.value = 'All Processing'
  dateValue.value = dayjs().subtract(365, 'day').format('YYYY-MM-DD')
  dateValue1.value = dayjs().format('YYYY-MM-DD')
  onFilterClick()
}
// Fetch filtered data from API
const fetchFilteredData = async () => {
  isLoading.value = true
  try {
    const params = new URLSearchParams({
      start_date: dateValue.value,
      end_date: dateValue1.value,
      search_input: search.value || '',
      limit_start: (currentPage.value - 1) * pageSize.value,
      limit_page_length: pageSize.value,
      status: inputValue1.value || '',
    })

   //  //console.log('status:', inputValue1.value || '')
    const url = `${Frappe_URL}/api/method/ecommerce.api.get_live_updatesfilter?${params.toString()}`

    const token = localStorage.getItem('access_token')

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      // console.error('API Error:', response.statusText)
      return
    }

    const data = await response.json()
   //  // console.log('response:', data)

    if (Array.isArray(data.message?.data?.orders)) {
      // Directly assign rows without further processing

      rows.value = data.message.data.orders.map((order) => {
        const creationDate = dayjs(order.creation).format('YYYY-MM-DD HH:mm')
        const receivedDate = order.received_date
          ? dayjs(order.received_date).format('YYYY-MM-DD HH:mm')
          : '0'
        const displayDate = receivedDate !== '0' ? receivedDate : creationDate

        const orderId = order.vendor_tracking_number
          ? `${order.name} / ${order.vendor_tracking_number}`
          : order.name
        const getDeliveryAmount = (item) => {
          if (
            order.status_after_warehouse === 'Return To Vendor' ||
            order.status_after_warehouse === 'Delivered To Vendor'
          ) {
            return 0
          }
          return item.delivery_amount
        }
        const greendelivery = order.green_delivery ? order.green_delivery : 0
        // const location = order.location + ' ,' + order.name_of_city_area;
        const location =
          order.location +
          (order.name_of_city_area ? ', ' + order.name_of_city_area : '')

        const hasExchangeRef =
          String(order.return_with_exchange_order || '').trim() !== ''
        const isExchangeFlag =
          String(order.return_with_exchange_order || '').trim() === '1'

        const orderTypeIcon = (() => {
          const icons = []
          if (Number(order.express_delivery) === 1) {
            icons.push({
              name: 'rocket_launch',
              color: 'text-rose-600',
              title: 'Express Delivery',
            })
          }
          if (
            order.order_type === 'Return' &&
            (hasExchangeRef || isExchangeFlag)
          ) {
            // Dual: combined icon
            icons.push({
              name: 'swap_calls',
              color: 'text-gray-800',
              title: 'Exchange Return',
            })
            return icons
          }
          if (order.order_type === 'Return') {
            icons.push({
              name: 'undo',
              color: 'text-gray-800',
              title: 'Return',
            })
            return icons
          }
          if (order.order_type === 'Exchange') {
            icons.push({
              name: 'swap_horiz',
              color: 'text-gray-800',
              title: 'Exchange',
            })
            return icons
          }
          return icons
        })()

        return {
          creation: creationDate,
          received_date: receivedDate,
          display_date: displayDate,
          name: orderId,
          customer_name: order.customer_name,
          primary_mobile_no: order.primary_mobile_no,
          pickup_branch: order.pickup_branch,
          location: location,
          destination_branch: order.destination_branch,
          cod_amount: order.cod_amount,
          delivery_amount: getDeliveryAmount(order),
          status: order.status_after_warehouse,
          status_after_warehouse: order.status_after_warehouse,
          status_before_warehouse: order.status,
          order_type: order.order_type,
          order_type_icon: orderTypeIcon,
          attempt: order.failed_attempt,
          action:
            greendelivery === 1
              ? 'View <span class="material-symbols-outlined text-green-800 text-center">eco</span> '
              : 'View',
        }
      })

      if (rows.value.length === 0) {
        options.emptyState.title = 'No orders found for the selected date range'
      }

      const orderStatus = data.message.data.order_status

      if (orderStatus) {
        todayStatus.value = {
          order_count: orderStatus.today.order_count || 0,
          total_cod_amount: orderStatus.today.total_cod_amount || 0,
          total_delivery_amount: orderStatus.today.total_delivery_amount || 0,
        }

        totalStatus.value = {
          order_count: orderStatus.total.order_count || 0,
          total_cod_amount: (
            orderStatus.total.total_cod_amount || 0
          ).toLocaleString('en-IN', option),
          total_delivery_amount: orderStatus.total.total_delivery_amount || 0,
        }

        greenPnd.value = {
          weekly: orderStatus.green_delivery.total_this_week || 0,
          monthly: orderStatus.green_delivery.total_this_month || 0,
          lastmonth: orderStatus.green_delivery.total_last_month || 0,
          lastweek: orderStatus.green_delivery.total_last_week || 0,
          isWeeklyGreater:
            (orderStatus.green_delivery.total_this_week || 0) >=
            (orderStatus.green_delivery.total_last_week || 0),
          isMonthlyGreater:
            (orderStatus.green_delivery.total_this_month || 0) >=
            (orderStatus.green_delivery.total_last_month || 0),
          monthlyoffset: orderStatus.carbon.current_month_pnd_offset || 0,
          lifetimeoffset: orderStatus.carbon.all_time_pnd_offset || 0,
          sevendaysoffset: orderStatus.carbon.last_7_days_pnd_offset || 0,
        }

        greenVendor.value = {
          weekly: orderStatus.green_delivery.vendor_this_week || 0,
          monthly: orderStatus.green_delivery.vendor_this_month || 0,
          lastmonth: orderStatus.green_delivery.vendor_last_month || 0,
          lastweek: orderStatus.green_delivery.vendor_last_week || 0,
          isWeeklyGreaterV:
            (orderStatus.green_delivery.vendor_this_week || 0) >=
            (orderStatus.green_delivery.vendor_last_week || 0),
          isMonthlyGreaterV:
            (orderStatus.green_delivery.vendor_this_month || 0) >=
            (orderStatus.green_delivery.vendor_last_month || 0),
          monthlyoffset: orderStatus.carbon.current_month_vendor_offset || 0,
          lifetimeoffset: orderStatus.carbon.all_time_vendor_offset || 0,
          sevendaysoffset: orderStatus.carbon.last_7_days_vendor_offset || 0,
        }

        setteledAmount.value =
          data.message.data.payable_balance?.[0]?.settled_account || 0

        totalAccount.value =
          data.message.data.payable_balance?.[0]?.total_balance || 0
        lastSettledAmount.value =
          data.message.data.payable_balance?.[0]?.last_settled_amount || ''
        lastPaymentDate.value =
          data.message.data.payable_balance?.[0]?.last_payment_date || ''
       //  // console.log('totalAccount:', totalAccount.value)

        let statusCountMap = {}
       //  //console.log("Order Status:", orderStatus.status_counts);

       //  //console.log("Order Status:", orderStatus.status_counts);

        orderStatus.status_counts.forEach((statusCount) => {
          // Use 'status_after_warehouse' instead of 'status'
          //  statusCountMap[statusCount.status_after_warehouse] = statusCount.status_order_count || 0;
          const count = statusCount.status_order_count || 0
          statusCountMap[statusCount.status_after_warehouse] =
            count > 99 ? '99+' : count
        })

       //  //console.log("Status Count Map:", statusCountMap);

        // If status_counts exists, iterate through and log each status without translation
        if (orderStatus.status_counts) {
          orderStatus.status_counts.forEach((status) => {
           //  // console.log(status.status_after_warehouse, status.status_order_count); // Log each status with its order count
          })
        } else {
         //  //console.log("status_counts is undefined or empty");
        }

        // Log the statusCountMap to verify it's being populated correctly
       //  //  console.log("Status Count Map:", statusCountMap);

        // Assign the map of status counts to `status_order_count`
        status_order_count.value = statusCountMap
      }

      // Handle pagination
      const pagination = data.message.data.pagination
      // Table pagination still uses the API's total, but the sidebar badge should reflect processing-only count.
      if (pagination) {
        const total = Number(
          pagination.total_count ??
            pagination.total_records ??
            pagination.total_orders ??
            rows.value.length ??
            0,
        )
        totalOrders.value = Number.isFinite(total) ? total : rows.value.length || 0
      } else {
        totalOrders.value = rows.value.length || 0
      }

      // Use the processing-specific count when available; fall back to the paginated total.
      const processingCount =
        data.message?.data?.all_processing_count ??
        data.data?.all_processing_count ??
        totalOrders.value
      setLiveUpdateCount(processingCount)

      const openInitCount =
        data.message?.data?.open_initiated_count ??
        data.data?.open_initiated_count ??
        totalOrders.value
      setLiveOpenInitCount(openInitCount)

      // ensure current page not beyond max
      if (currentPage.value > totalPages.value) {
        currentPage.value = totalPages.value
      }
    } else {
      rows.value = []
      // console.error('No data available or data is not an array')
    }
  } catch (error) {
    // console.error('Error fetching filtered data:', error)
  } finally {
    isLoading.value = false
  }
}

const handleCashOutClick = () => {
  const totalBalance = parseFloat(totalAccount.value) || 0 // Convert to decimal and handle invalid values

  //if(totalBalance){
  if (totalBalance > 0) {
    displaybank.isDisplay = true // Open the dialog
  } else {
    toast.error('Total account balance must be positive to cash out.')
  }
}

const totalDelivery = computed(() => {
  const total = rows.value.reduce(
    (acc, row) => acc + (row.delivery_amount || 0),
    0,
  )
 //  //  console.log("Total Delivery:", total);
  return total
})

const totalCOD = computed(() => {
  const total = rows.value.reduce((acc, row) => acc + (row.cod_amount || 0), 0)
 //  // console.log("Total COD:", total);
  return total
})

// Change page function
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchFilteredData()
}

// Validate date range
const validateDateRange = () => {
  const start = dayjs(dateValue.value)
  const end = dayjs(dateValue1.value)
  if (start.isAfter(end)) {
    toast.info('Start date must be on or before the end date.')
    return false
  }
  return true
}

// Filter and fetch data
const onFilterClick = async () => {
  if (!validateDateRange()) return
  currentPage.value = 1 // Reset to the first page when applying a filter
  await fetchFilteredData()
}

// On component mount, fetch data
onMounted(() => {
  if (window.innerWidth < 768) {
    timelineOpen.value = false
  }
  fetchFilteredData() // Initial fetch
  fetchTimeline() // Fetch timeline data
  fetchSliderImage()
})

watch(inputValue1, () => {
  try {
    const stored =
      inputValue1.value === '' ? 'All' : inputValue1.value || 'All Processing'
    localStorage.setItem(STATUS_FILTER_KEY, stored)
  } catch (e) {
    // ignore storage errors
  }
  onFilterClick()
})

// Apply background color based on order status
const normalizeStatus = (status) =>
  (status || '').toString().replace(/\s+/g, ' ').trim()

const getBadgeStyle = (status) => {
  const map = {
    'Cancelled in Branch': { backgroundColor: '#A11717', color: 'white' },
    'Sent for Delivery': { backgroundColor: '#66ffff', color: 'black' },
    Delivered: { backgroundColor: '#008000', color: 'white' },
    'Pickup on Process': { backgroundColor: '#b3b3ff', color: 'black' },
    'Failed Attempt': { backgroundColor: '#e79aff', color: 'black' },
    'Failed Attempt & Return to Branch': {
      backgroundColor: '#ff8746',
      color: 'black',
    },
    'Order Created': { backgroundColor: 'grey', color: 'white' },
    Received: { backgroundColor: '#00cccc', color: 'black' },
    'Return To Vendor': { backgroundColor: '#FFA500', color: 'black' },
    'Processing in Branch': { backgroundColor: '#65fffd', color: 'black' },
    'Delivered To Vendor': { backgroundColor: '#008000', color: 'white' },
    'Disabled Order': { backgroundColor: 'black', color: 'white' },
    'Return Received': { backgroundColor: 'rgb(5 131 131)', color: 'white' },
    'Lost Package': { backgroundColor: 'darkred', color: 'white' },
    'Exchange Return': { backgroundColor: '#b388ff', color: 'black' },
    'Waiting for Received': { backgroundColor: '#b3e5fc', color: '#0f172a' },
    'Assigned For Pickup': { backgroundColor: '#d1fae5', color: '#065f46' },
    'Waiting To Assigned': { backgroundColor: '#fef3c7', color: '#92400e' },
    'In Transit': { backgroundColor: '#e0f2fe', color: '#0c4a6e' },
  }
  const key = normalizeStatus(status)
  return map[key] || { backgroundColor: '#e5e7eb', color: '#111827' }
}
</script>

<style scoped>
/* Custom table and row styles */
table {
  border-collapse: collapse;
  width: 100%;
}

.table-spacing {
  border-collapse: separate;
  border-spacing: 0 10px;
  /* 10px is the gap between rows */
}

th,
td {
  border-bottom: 1px solid #ddd;
  padding: 10px;
}

td a {
  text-decoration: none;
}

tbody tr:hover {
  background-color: rgba(0, 0, 0, 0.1);
  /* Add hover effect */
}

.white-border-all-sides {
  border-style: solid;
  border-color: white;
  border-width: 1px;
}

.vertical-divider {
  border-left: 1px solid #d1d5db;
  /* Tailwind's gray-300 color */
  height: auto;
  margin: 0 1rem;
  /* Adjust the margin as needed */
}

.pnd-scrollbar {
  overflow-x: auto;
}

/* WebKit (Chrome, Safari, Edge) */
.pnd-scrollbar::-webkit-scrollbar {
  height: 1px; /* Horizontal scrollbar height */
}

.pnd-scrollbar::-webkit-scrollbar-track {
  background: #e5e7eb; /* Tailwind gray-200 */
}

.pnd-scrollbar::-webkit-scrollbar-thumb {
  background-color: #3b82f6; /* Tailwind blue-500 */
  border-radius: 9999px;
  border: 2px solid transparent;
  background-clip: content-box;
}

/* Firefox */
.pnd-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #3b82f6 #e5e7eb;
}

.timeline-slide-enter-active,
.timeline-slide-leave-active {
  transition:
    opacity 0.22s ease,
    transform 0.22s ease;
}

.timeline-slide-enter-from,
.timeline-slide-leave-to {
  opacity: 0;
  transform: translateX(-12px);
}

.timeline-active-panel {
  animation: timelinePanelPulse 2.2s ease-in-out infinite;
}

.timeline-active-pill {
  animation: timelineActivePillPulse 1.6s ease-in-out infinite;
}

@keyframes timelinePanelPulse {
  0%,
  100% {
    box-shadow:
      0 18px 32px rgba(0, 0, 0, 0.12),
      0 0 0 0 rgba(34, 197, 94, 0.14);
  }
  50% {
    box-shadow:
      0 18px 32px rgba(0, 0, 0, 0.12),
      0 0 0 6px rgba(34, 197, 94, 0.06);
  }
}

@keyframes timelineActivePillPulse {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.28);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.08);
    transform: scale(1.04);
  }
}
</style>
