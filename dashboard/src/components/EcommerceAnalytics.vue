<template>
  <div class="space-y-4">
    <!-- Header Section -->
    <div v-if="!embedded" class="bg-white">
      <h2 class="font-bold text-gray-800">Ecommerce Analytics</h2>
      <p class="text-sm text-gray-600 mt-1">
        Select the website to see the analytics
      </p>
    </div>

    <!-- Search Section -->
    <div class="bg-white relative">
      <div
        class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div class="w-full sm:w-[1200px] space-y-1">
          <input
            type="search"
            v-model="inputValue"
            placeholder="Search..."
            class="w-full border border-gray-300 rounded-md px-4 py-3 text-base shadow-sm focus:outline-none focus:ring-2 focus:ring-green-200"
            @focus="onFocus"
            @blur="handleBlur"
            @input="filterSuggestions"
          />

          <!-- Autocomplete Dropdown -->
          <ul
            v-if="showSuggestions && filteredSuggestions.length"
            class="absolute z-10 bg-white border border-gray-200 rounded-md mt-1 w-full shadow-md max-h-60 overflow-auto"
          >
            <li
              v-for="(item, index) in filteredSuggestions"
              :key="item.value || index"
              @mousedown.prevent="selectSuggestion(item)"
              class="px-4 py-2 hover:bg-green-100 cursor-pointer text-sm"
            >
              {{ item.label }}
            </li>
          </ul>
        </div>
      </div>
    </div>

    <p
      v-if="analyticsError"
      class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
    >
      {{ analyticsError }}
    </p>
    <p v-if="analyticsLoading" class="text-sm text-gray-500">
      Loading live ecommerce analytics…
    </p>

    <div class="grid grid-cols-1 gap-4 xl:grid-cols-12">
      <div class="contents">
        <!-- Quick Statistics -->
        <section
          class="grid grid-cols-1 gap-4 sm:grid-cols-3 xl:col-span-12"
        >
          <!-- total sales -->
          <Card class="h-full">
            <CardHeader class="pt-3 px-3">
              <CardTitle
                class="flex text-[#71717A] font-medium gap-1 text-sm justify-between items-center"
              >
                <div class="flex items-center justify-center gap-1">
                  <p class="dark:text-white">Total Sales</p>
                  <!-- <TooltipProvider :delayDuration="100">
                    <Tooltip
                      :open="isTouchDevice ? infoTooltipOpen === 'ea-total-sales' : undefined"
                      :disable-closing-trigger="isTouchDevice"
                      @update:open="(value) => handleInfoTooltipOpenChange('ea-total-sales', value)"
                    >
                      <TooltipTrigger as-child>
                        <button
                          type="button"
                          class="size-3 inline-flex items-center justify-center shrink-0"
                          aria-label="Today's delivery curve info"
                          @click="handleInfoTooltipClick('ea-total-sales')"
                        >
                          <svg
                            class="w-full h-full"
                            fill="#3b82f6"
                            viewBox="0 0 1920 1920"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g
                              id="SVGRepo_tracerCarrier"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            ></g>
                            <g id="SVGRepo_iconCarrier">
                              <path
                                d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                fill-rule="evenodd"
                              ></path>
                            </g>
                          </svg>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent class="w-40">
                        <p class="break-words">
                          Total value of all successful transactions
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider> -->
                </div>
                <CircleDollarSignIcon class="size-4 text-[#27b67c]" />
              </CardTitle>
            </CardHeader>
            <CardContent
              class="text-xl py-0 font-bold text-center md:text-left flex justify-between pb-3 px-3"
              ><span
                >NPR
                {{
                  new Intl.NumberFormat('en-IN').format(
                    dashboardData.summary.totalSales.value,
                  )
                }}</span
              >
              <div class="grid grid-cols-1">
                <span
                  :class="[
                    'text-xs md:text-[10px] text-right',
                    dashboardData.summary.totalSales.change.startsWith('+')
                      ? 'text-green-500'
                      : 'text-red-500',
                  ]"
                  >{{ dashboardData.summary.totalSales.change }}</span
                >
                <span class="text-xs md:text-[10px] text-gray-700">{{
                  dashboardData.summary.totalSales.comparisonText
                }}</span>
              </div></CardContent
            >
          </Card>

          <!-- total orders -->
          <Card class="h-full">
            <CardHeader class="pt-3 px-3">
              <CardTitle
                class="flex text-[#71717A] font-medium gap-1 text-sm justify-between"
              >
                <div class="flex justify-center items-center gap-1">
                  <p class="dark:text-white">Total Orders</p>
                  <!-- <TooltipProvider :delayDuration="100">
                    <Tooltip
                      :open="isTouchDevice ? infoTooltipOpen === 'ea-total-orders' : undefined"
                      :disable-closing-trigger="isTouchDevice"
                      @update:open="(value) => handleInfoTooltipOpenChange('ea-total-orders', value)"
                    >
                      <TooltipTrigger as-child>
                        <button
                          type="button"
                          class="size-3 inline-flex items-center justify-center shrink-0"
                          aria-label="Today's delivery curve info"
                          @click="handleInfoTooltipClick('ea-total-orders')"
                        >
                          <svg
                            class="w-full h-full"
                            fill="#3b82f6"
                            viewBox="0 0 1920 1920"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g
                              id="SVGRepo_tracerCarrier"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            ></g>
                            <g id="SVGRepo_iconCarrier">
                              <path
                                d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                fill-rule="evenodd"
                              ></path>
                            </g>
                          </svg>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent class="w-40">
                        <p class="break-words">
                          Cumulative count of all orders placed
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider> -->
                </div>
                <ShoppingCart class="size-4 text-[#EFC04C]" />
              </CardTitle>
            </CardHeader>
            <CardContent
              class="text-xl py-0 font-bold text-center md:text-left flex justify-between pb-3 px-3"
              ><span>{{
                new Intl.NumberFormat('en-IN').format(
                  dashboardData.summary.totalOrders.value,
                )
              }}</span>
              <div class="grid grid-cols-1">
                <span
                  :class="[
                    'text-xs md:text-[10px] text-right',
                    dashboardData.summary.totalOrders.change.startsWith('+')
                      ? 'text-green-500'
                      : 'text-red-500',
                  ]"
                  >{{ dashboardData.summary.totalOrders.change }}</span
                >
                <span class="text-xs md:text-[10px] text-gray-700">{{
                  dashboardData.summary.totalOrders.comparisonText
                }}</span>
              </div></CardContent
            >
          </Card>

          <!-- total visitors -->
          <Card class="h-full">
            <CardHeader class="pt-3 px-3">
              <CardTitle
                class="flex text-[#71717A] font-medium gap-1 text-base justify-between"
              >
                <div class="flex justify-center items-center gap-1">
                  <p class="dark:text-white">Total Visitors</p>
                  <!-- <TooltipProvider :delayDuration="100">
                    <Tooltip
                      :open="isTouchDevice ? infoTooltipOpen === 'ea-total-visitors' : undefined"
                      :disable-closing-trigger="isTouchDevice"
                      @update:open="(value) => handleInfoTooltipOpenChange('ea-total-visitors', value)"
                    >
                      <TooltipTrigger as-child>
                        <button
                          type="button"
                          class="size-3 inline-flex items-center justify-center shrink-0"
                          aria-label="Today's delivery curve info"
                          @click="handleInfoTooltipClick('ea-total-visitors')"
                        >
                          <svg
                            class="w-full h-full"
                            fill="#3b82f6"
                            viewBox="0 0 1920 1920"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g
                              id="SVGRepo_tracerCarrier"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            ></g>
                            <g id="SVGRepo_iconCarrier">
                              <path
                                d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                fill-rule="evenodd"
                              ></path>
                            </g>
                          </svg>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent class="w-40">
                        <p class="break-words">
                          Total number of users who have visited the platform
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider> -->
                </div>
                <Eye class="size-4 text-[#8985F9]" />
              </CardTitle>
            </CardHeader>
            <CardContent
              class="text-xl py-0 font-bold text-center md:text-left flex justify-between pb-3 px-3"
              ><span>{{
                new Intl.NumberFormat('en-IN').format(
                  dashboardData.summary.totalVisitors.value,
                )
              }}</span>
              <div class="grid grid-cols-1">
                <span
                  :class="[
                    'text-xs md:text-[10px] text-right',
                    dashboardData.summary.totalVisitors.change.startsWith('+')
                      ? 'text-green-500'
                      : 'text-red-500',
                  ]"
                  >{{ dashboardData.summary.totalVisitors.change }}</span
                >
                <span class="text-xs md:text-[10px] text-gray-700">{{
                  dashboardData.summary.totalVisitors.comparisonText
                }}</span>
              </div></CardContent
            >
          </Card>

          <!-- fourth card if necessary -->
          <!-- <Card>
            <CardHeader class="pt-3 px-3">
              <CardTitle
                class="flex text-[#71717A] font-medium gap-1 text-base justify-between"
                ><p class="dark:text-white">Total Visitors</p>
                <Eye class="size-4 text-[#8985F9]" />
              </CardTitle>
            </CardHeader>
            <CardContent
              class="text-xl py-0 font-bold text-center md:text-left flex justify-between pb-3 px-3"
              ><span>{{
                new Intl.NumberFormat('en-IN').format(
                  dashboardData.summary.totalVisitors.value,
                )
              }}</span>
              <div class="grid grid-cols-1">
                <span
                  :class="[
                    'text-xs md:text-[10px] text-right',
                    dashboardData.summary.totalVisitors.change.startsWith('+')
                      ? 'text-green-500'
                      : 'text-red-500',
                  ]"
                  >{{ dashboardData.summary.totalVisitors.change }}</span
                >
                <span class="text-xs md:text-[10px] text-gray-700">{{
                  dashboardData.summary.totalVisitors.comparisonText
                }}</span>
              </div></CardContent
            >
          </Card> -->
        </section>
        <div class="xl:col-span-12">
          <section class="grid h-full grid-cols-1 gap-4 lg:grid-cols-3">
            <Card class="h-full lg:col-span-1">
              <CardHeader class="pb-0">
                <CardTitle class="flex gap-1 items-center">
                  <p class="">Weekly Visitors</p>
                  <div class="">
                    <TooltipProvider :delayDuration="100">
                      <Tooltip
                        :open="
                          isTouchDevice
                            ? infoTooltipOpen === 'ea-recent-orders'
                            : undefined
                        "
                        :disable-closing-trigger="isTouchDevice"
                        @update:open="
                          (value) =>
                            handleInfoTooltipOpenChange(
                              'ea-recent-orders',
                              value,
                            )
                        "
                      >
                        <TooltipTrigger as-child>
                          <button
                            type="button"
                            class="size-4 inline-flex items-center justify-center"
                            aria-label="Today's delivery curve info"
                            @click="handleInfoTooltipClick('ea-recent-orders')"
                          >
                            <svg
                              fill="#3b82f6"
                              viewBox="0 0 1920 1920"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                              <g
                                id="SVGRepo_tracerCarrier"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                              ></g>
                              <g id="SVGRepo_iconCarrier">
                                <path
                                  d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                  fill-rule="evenodd"
                                ></path>
                              </g>
                            </svg>
                            <!-- <Info class="w-4 text-gray-800 p-0"/> -->
                          </button>
                        </TooltipTrigger>
                        <TooltipContent class="w-40">
                          <p class="break-words">
                            Number of users currently engaged with the platform
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div class="font-bold grid grid-cols-1">
                  <div class="flex justify-between">
                    <span class="text-2xl font-bold">{{
                      new Intl.NumberFormat('en-IN').format(
                        dashboardData.activeUser.total,
                      )
                    }}</span>
                    <span
                      :class="[
                        'text-base font-bold flex items-center bg-[#dff4eb] rounded-md px-1',
                        dashboardData.summary.totalVisitors.change.startsWith(
                          '+',
                        )
                          ? 'text-green-500'
                          : 'text-red-500',
                      ]"
                      >{{ dashboardData.activeUser.change }}</span
                    >
                  </div>

                  <div class="flex justify-between">
                    <span class="text-xs md:text-[10px] text-gray-600"
                      >Users</span
                    >
                    <span class="text-xs md:text-[10px] text-gray-600">{{
                      dashboardData.activeUser.comparisonText
                    }}</span>
                  </div>
                </div>

                <div class="mx-auto w-full max-w-md">
                  <div
                    class="relative max-h-[165px] overflow-y-auto pr-1 space-y-3"
                  >
                    <div class="flex flex-col gap-3 mt-5">
                      <div
                        v-for="location in dashboardData.activeUser.countries"
                        :key="location.name"
                      >
                        <div class="flex justify-between">
                          <p class="text-sm text-gray-700">
                            {{ location.name }}
                          </p>
                          <span class="text-sm text-gray-700 font-bold"
                            >{{ location.percentage }}%</span
                          >
                        </div>
                        <LinearProgress
                          :model-value="location.percentage"
                          class="mt-1 h-2"
                        />
                      </div>
                      <p
                        v-if="!dashboardData.activeUser.countries.length"
                        class="text-xs text-gray-500"
                      >
                        Customer locations will appear after orders are placed.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card class="h-full lg:col-span-2">
              <CardHeader class="pb-2 pt-4">
                <CardTitle class="flex justify-between">
                  <div class="flex gap-1 items-center">
                    <p class="">Conversion Funnel</p>
                    <div class="">
                      <TooltipProvider :delayDuration="100">
                        <Tooltip
                          :open="
                            isTouchDevice
                              ? infoTooltipOpen === 'ea-recent-activity'
                              : undefined
                          "
                          :disable-closing-trigger="isTouchDevice"
                          @update:open="
                            (value) =>
                              handleInfoTooltipOpenChange(
                                'ea-recent-activity',
                                value,
                              )
                          "
                        >
                          <TooltipTrigger as-child>
                            <button
                              type="button"
                              class="size-4 inline-flex items-center justify-center"
                              aria-label="Today's delivery curve info"
                              @click="
                                handleInfoTooltipClick('ea-recent-activity')
                              "
                            >
                              <svg
                                fill="#3b82f6"
                                viewBox="0 0 1920 1920"
                                xmlns="http://www.w3.org/2000/svg"
                              >
                                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                <g
                                  id="SVGRepo_tracerCarrier"
                                  stroke-linecap="round"
                                  stroke-linejoin="round"
                                ></g>
                                <g id="SVGRepo_iconCarrier">
                                  <path
                                    d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                    fill-rule="evenodd"
                                  ></path>
                                </g>
                              </svg>
                            </button>
                          </TooltipTrigger>
                          <TooltipContent class="w-40">
                            <p class="break-words">
                              Percentage of orders successfully completed out of
                              total orders placed
                            </p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                  </div>
                  <Select class="">
                    <SelectTrigger class="w-[110px]">
                      <SelectValue placeholder="This Week" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        <SelectLabel>Sort By</SelectLabel>
                        <SelectItem value="apple"> Today </SelectItem>
                        <SelectItem value="banana"> This Week </SelectItem>
                        <SelectItem value="blueberry"> This Month </SelectItem>
                        <SelectItem value="grapes"> This Year </SelectItem>
                        <SelectItem value="pineapple"> All Time </SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </CardTitle>
              </CardHeader>
              <div class="overflow-x-auto">
                <div class="min-w-[500px]">
                  <CardContent class="mt-2 md:mt-0">
                    <div class="grid grid-cols-5 gap-4">
                      <div
                        v-for="(metric, index) in dashboardData.conversionRate.metrics"
                        :key="metric.name"
                        class="flex flex-col gap-2"
                        :class="{
                          'border-r-2 border-gray-200':
                            index !== dashboardData.conversionRate.metrics.length - 1,
                        }"
                      >
                        <span class="text-[10px] text-gray-600">
                          {{ metric.name }}
                        </span>
                        <span class="text-2xl font-bold">{{
                          new Intl.NumberFormat('en-IN').format(metric.value)
                        }}</span>
                        <span
                          class="inline-flex w-fit items-center rounded-md px-1 text-[10px] font-bold"
                          :class="
                            metric.change.startsWith('+')
                              ? 'bg-[#dff4eb] text-green-500'
                              : metric.change.startsWith('-')
                                ? 'bg-red-100 text-red-500'
                                : 'bg-gray-100 text-gray-500'
                          "
                        >
                          {{ metric.change }}
                        </span>
                        <div class="h-24 flex items-end">
                          <div
                            class="w-full rounded-t-2xl bg-emerald-400"
                            :style="{
                              height: `${conversionBarHeight(metric.value)}%`,
                            }"
                          ></div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </div>
              </div>
            </Card>
          </section>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4">
      <section
        class="grid w-full grid-cols-1 gap-4 lg:grid-cols-3"
      >
        <Card class="h-full lg:col-span-2">
          <CardHeader class="pb-2 pt-4">
            <CardTitle class="flex justify-between">
              <div class="flex gap-1 items-center">
                <p class="">Revenue Analytics</p>
                <div class="">
                  <TooltipProvider :delayDuration="100">
                    <Tooltip
                      :open="
                        isTouchDevice
                          ? infoTooltipOpen === 'ea-revenue-analytics'
                          : undefined
                      "
                      :disable-closing-trigger="isTouchDevice"
                      @update:open="
                        (value) =>
                          handleInfoTooltipOpenChange(
                            'ea-revenue-analytics',
                            value,
                          )
                      "
                    >
                      <TooltipTrigger as-child>
                        <button
                          type="button"
                          class="size-4 inline-flex items-center justify-center"
                          aria-label="Today's delivery curve info"
                          @click="
                            handleInfoTooltipClick('ea-revenue-analytics')
                          "
                        >
                          <svg
                            fill="#3b82f6"
                            viewBox="0 0 1920 1920"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g
                              id="SVGRepo_tracerCarrier"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            ></g>
                            <g id="SVGRepo_iconCarrier">
                              <path
                                d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                fill-rule="evenodd"
                              ></path>
                            </g>
                          </svg>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent class="w-40">
                        <p class="break-words">
                          Provides insights into earnings, trends, and financial
                          performance
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </div>
              <Select class="">
                <SelectTrigger class="w-[110px]">
                  <SelectValue placeholder="This Week" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Sort By</SelectLabel>
                    <SelectItem value="apple"> Today </SelectItem>
                    <SelectItem value="banana"> This Week </SelectItem>
                    <SelectItem value="blueberry"> This Month </SelectItem>
                    <SelectItem value="grapes"> This Year </SelectItem>
                    <SelectItem value="pineapple"> All Time </SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </CardTitle>
            <!-- <CardTitle class="flex gap-1 items-center">
                <p class="">Revenue Analytics</p>
                <div class="mt-1">
                  <TooltipProvider :delayDuration="100">
                    <Tooltip
                      :open="isTouchDevice ? infoTooltipOpen === 'ea-monthly-target' : undefined"
                      :disable-closing-trigger="isTouchDevice"
                      @update:open="(value) => handleInfoTooltipOpenChange('ea-monthly-target', value)"
                    >
                      <TooltipTrigger as-child>
                        <button
                          type="button"
                          class="size-4 inline-flex items-center justify-center"
                          aria-label="Today's delivery curve info"
                          @click="handleInfoTooltipClick('ea-monthly-target')"
                        >
                          <svg
                            fill="#3b82f6"
                            viewBox="0 0 1920 1920"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g
                              id="SVGRepo_tracerCarrier"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            ></g>
                            <g id="SVGRepo_iconCarrier">
                              <path
                                d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                fill-rule="evenodd"
                              ></path>
                            </g>
                          </svg>
                        </button>
                      </TooltipTrigger>
                      <TooltipContent class="w-40">
                        <p class="break-words">
                          Provides insights into earnings, trends, and financial
                          performance
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </CardTitle> -->
          </CardHeader>
          <div class="overflow-x-auto">
            <div class="min-w-[500px]">
              <AreaChart
                :data="revenueAnalytics"
                index="name"
                :show-tooltip="true"
                :show-legend="true"
                :show-grid-line="true"
                :show-x-axis="false"
                :show-y-axis="true"
                :show-points="true"
                :point-size="6"
                :categories="['revenue', 'order']"
                :colors="['#27b67c', '#EFC04C']"
                class="h-[300px] pb-10 w-full"
              >
                <template #default>
                  <VisAxis
                    type="x"
                    :tick-values="[0, 1, 2, 3, 4, 5, 6, 7]"
                    :tick-format="(v) => revenueAnalytics[v]?.name || ''"
                    :grid-line="false"
                    :tick-line="false"
                    tick-text-color="hsl(var(--vis-text-color))"
                  />
                </template>
              </AreaChart>
            </div>
          </div>
        </Card>
        <Card class="h-full lg:col-span-1">
          <CardHeader class="py-5">
            <CardTitle class="flex gap-1 items-center">
              <p class="">Monthly Target</p>
              <div class="">
                <TooltipProvider :delayDuration="100">
                  <Tooltip
                    :open="
                      isTouchDevice
                        ? infoTooltipOpen === 'ea-active-user'
                        : undefined
                    "
                    :disable-closing-trigger="isTouchDevice"
                    @update:open="
                      (value) =>
                        handleInfoTooltipOpenChange('ea-active-user', value)
                    "
                  >
                    <TooltipTrigger as-child>
                      <button
                        type="button"
                        class="size-4 inline-flex items-center justify-center"
                        aria-label="Today's delivery curve info"
                        @click="handleInfoTooltipClick('ea-active-user')"
                      >
                        <svg
                          fill="#3b82f6"
                          viewBox="0 0 1920 1920"
                          xmlns="http://www.w3.org/2000/svg"
                        >
                          <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                          <g
                            id="SVGRepo_tracerCarrier"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                          ></g>
                          <g id="SVGRepo_iconCarrier">
                            <path
                              d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                              fill-rule="evenodd"
                            ></path>
                          </g>
                        </svg>
                        <!-- <Info class="w-4 text-gray-800 p-0"/> -->
                      </button>
                    </TooltipTrigger>
                    <TooltipContent class="w-40">
                      <p class="break-words">
                        Shows progress toward the revenue goal set for this
                        month
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </TooltipProvider>
              </div>
            </CardTitle>
          </CardHeader>
          <CardContent class="px-5 0"
            ><Progress
              :model-value="dashboardData.monthlyTarget.percentage"
              class=""
            />
            <div class="mt-4">
              <h1 class="text-center text-sm font-bold">
                {{ dashboardData.monthlyTarget.status }} 🎊
              </h1>
              <p class="text-[11px] text-center mt-1 font-medium">
                {{ dashboardData.monthlyTarget.message }}
              </p>
            </div>
            <div class="grid grid-cols-2 mt-5 gap-3">
              <div
                class="flex flex-col items-center bg-[#6ee7b7] p-2 rounded-lg"
              >
                <h2 class="text-xs mb-1.5">Target</h2>
                <p class="text-sm font-bold">
                  NPR
                  {{
                    new Intl.NumberFormat('en-IN').format(
                      dashboardData.monthlyTarget.target,
                    )
                  }}
                </p>
              </div>
              <div
                class="flex flex-col items-center bg-[#6ee7b7] p-2 rounded-lg"
              >
                <h2 class="text-xs mb-1.5">Revenue</h2>
                <p class="text-sm font-bold">
                  NPR
                  {{
                    new Intl.NumberFormat('en-IN').format(
                      dashboardData.monthlyTarget.revenue,
                    )
                  }}
                </p>
              </div>
            </div>
            <div class="mt-4 border-t border-gray-100 pt-3">
              <div
                v-if="dashboardData.monthlyTarget.canEdit"
                class="flex gap-2"
              >
                <input
                  v-model="monthlyTargetInput"
                  type="number"
                  min="0"
                  step="1000"
                  class="min-w-0 flex-1 rounded-md border border-gray-200 px-3 py-2 text-xs outline-none focus:border-emerald-500"
                  placeholder="Monthly target"
                />
                <Button
                  size="sm"
                  :disabled="monthlyTargetSaving"
                  @click="saveMonthlyTarget"
                >
                  {{ monthlyTargetSaving ? 'Saving…' : 'Set target' }}
                </Button>
              </div>
              <p v-else class="text-center text-[11px] text-gray-500">
                Select one ecommerce website above to configure its target.
              </p>
              <p
                v-if="monthlyTargetMessage"
                class="mt-2 text-center text-[11px]"
                :class="
                  monthlyTargetError ? 'text-red-600' : 'text-emerald-700'
                "
              >
                {{ monthlyTargetMessage }}
              </p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>

    <div class="grid grid-cols-1 gap-4 xl:grid-cols-12">
      <div class="xl:col-span-12">
        <section class="grid grid-cols-1 gap-4">
          <Card class="h-full">
            <CardHeader class="pb-2">
              <CardTitle
                class="flex flex-col sm:flex-row justify-between gap-2"
              >
                <div class="flex items-center gap-1">
                  <p class="">Recent Orders</p>
                  <div>
                    <TooltipProvider :delayDuration="100">
                      <Tooltip
                        :open="
                          isTouchDevice
                            ? infoTooltipOpen === 'ea-recent-orders'
                            : undefined
                        "
                        :disable-closing-trigger="isTouchDevice"
                        @update:open="
                          (value) =>
                            handleInfoTooltipOpenChange(
                              'ea-recent-orders',
                              value,
                            )
                        "
                      >
                        <TooltipTrigger as-child>
                          <button
                            type="button"
                            class="size-4 inline-flex items-center justify-center"
                            aria-label="Today's delivery curve info"
                            @click="handleInfoTooltipClick('ea-recent-orders')"
                          >
                            <svg
                              fill="#3b82f6"
                              viewBox="0 0 1920 1920"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                              <g
                                id="SVGRepo_tracerCarrier"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                              ></g>
                              <g id="SVGRepo_iconCarrier">
                                <path
                                  d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                  fill-rule="evenodd"
                                ></path>
                              </g>
                            </svg>
                          </button>
                        </TooltipTrigger>
                        <TooltipContent class="w-40">
                          <p class="break-words">
                            Most recently placed or updated orders
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </div>

                <div class="flex flex-col sm:flex-row gap-2 w-full sm:w-auto">
                  <div class="relative w-full sm:max-w-sm items-center">
                    <Input
                      class="pl-9 w-full"
                      placeholder="Search product,customer, etc"
                      :model-value="
                        table.getColumn('customer')?.getFilterValue() as string
                      "
                      @update:model-value="
                        table.getColumn('customer')?.setFilterValue($event)
                      "
                    />
                    <span
                      class="absolute start-0 inset-y-0 flex items-center justify-center px-3"
                    >
                      <Search class="size-4 text-muted-foreground" />
                    </span>
                  </div>

                  <Select class="w-full sm:w-[130px]">
                    <SelectTrigger class="w-full sm:w-[130px]">
                      <SelectValue placeholder="All Categories" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        <SelectLabel>Sort By</SelectLabel>
                        <SelectItem value="allcategories">
                          All Categories
                        </SelectItem>
                        <SelectItem value="consoles"> Consoles</SelectItem>
                        <SelectItem value="macbooks"> Macbooks </SelectItem>
                        <SelectItem value="laptops"> Laptops </SelectItem>
                        <SelectItem value="speakers"> Speakers </SelectItem>
                        <SelectItem value="iphones"> iPhones </SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent
              ><div class="w-full">
                <div class="flex items-center pt-2"></div>
                <div class="rounded-md border overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow
                        v-for="headerGroup in table.getHeaderGroups()"
                        :key="headerGroup.id"
                      >
                        <TableHead
                          v-for="header in headerGroup.headers"
                          :key="header.id"
                        >
                          <FlexRender
                            v-if="!header.isPlaceholder"
                            :render="header.column.columnDef.header"
                            :props="header.getContext()"
                          />
                        </TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      <template v-if="table.getRowModel().rows?.length">
                        <template
                          v-for="row in table.getRowModel().rows"
                          :key="row.id"
                        >
                          <TableRow>
                            <TableCell
                              v-for="cell in row.getVisibleCells()"
                              :key="cell.id"
                            >
                              <FlexRender
                                :render="cell.column.columnDef.cell"
                                :props="cell.getContext()"
                              />
                            </TableCell>
                          </TableRow>
                          <TableRow v-if="row.getIsExpanded()">
                            <TableCell :colspan="row.getAllCells().length">
                              {{ JSON.stringify(row.original) }}
                            </TableCell>
                          </TableRow>
                        </template>
                      </template>

                      <TableRow v-else>
                        <TableCell
                          :colspan="columns.length"
                          class="h-24 text-center"
                        >
                          No results.
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>

                <div class="flex items-center justify-end space-x-2 py-4">
                  <!-- <div class="flex-1 text-sm text-muted-foreground">
                    {{ table.getFilteredSelectedRowModel().rows.length }} of
                    {{ table.getFilteredRowModel().rows.length }} row(s)
                    selected.
                  </div> -->
                  <div class="space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      :disabled="!table.getCanPreviousPage()"
                      @click="table.previousPage()"
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      :disabled="!table.getCanNextPage()"
                      @click="table.nextPage()"
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </div></CardContent
            >
          </Card>
        </section>
      </div>
      <div
        class="grid grid-cols-1 gap-4 xl:col-span-12 xl:grid-cols-2"
      >
        <section>
          <Card class="h-full pb-9.5">
            <CardHeader class="pb-0">
              <CardTitle class="flex justify-between">
                <div class="flex gap-1 items-center">
                  <p class="">Top Categories</p>
                  <div class="">
                    <TooltipProvider :delayDuration="100">
                      <Tooltip
                        :open="
                          isTouchDevice
                            ? infoTooltipOpen === 'ea-conversion-rate'
                            : undefined
                        "
                        :disable-closing-trigger="isTouchDevice"
                        @update:open="
                          (value) =>
                            handleInfoTooltipOpenChange(
                              'ea-conversion-rate',
                              value,
                            )
                        "
                      >
                        <TooltipTrigger as-child>
                          <button
                            type="button"
                            class="size-4 inline-flex items-center justify-center"
                            aria-label="Today's delivery curve info"
                            @click="handleInfoTooltipClick('ea-conversion-rate')"
                          >
                            <svg
                              fill="#3b82f6"
                              viewBox="0 0 1920 1920"
                              xmlns="http://www.w3.org/2000/svg"
                            >
                              <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                              <g
                                id="SVGRepo_tracerCarrier"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                              ></g>
                              <g id="SVGRepo_iconCarrier">
                                <path
                                  d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                  fill-rule="evenodd"
                                ></path>
                              </g>
                            </svg>
                          </button>
                        </TooltipTrigger>
                        <TooltipContent class="w-40">
                          <p class="break-words">
                            Best-performing product categories by sales or order
                            volume
                          </p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                </div>
                <p class="text-sm text-gray-700">See all</p>
              </CardTitle>
              <!-- <CardTitle class="flex justify-between"
                ><p class="">Top Categories</p>
                <p class="text-sm text-gray-700">See all</p>
              </CardTitle> -->
            </CardHeader>
            <CardContent class="py-6">
              <!-- :colors="['#059669', '#3b82f6', '#f59e0b', '#ef4444']" -->
              <DonutChart
                index="name"
                :category="'sales'"
                :data="donutData"
                :colors="['#059669', '#10b981', '#34d399', '#6ee7b7']"
                :show-tooltip="true"
                :value-formatter="valueFormatter"
                class=""
              />
            </CardContent>
            <CardContent class="pb-4">
              <div class="mx-auto w-full max-w-md">
                <div
                  class="relative max-h-[165px] overflow-y-auto pr-1 space-y-3"
                >
                  <div class="mt-6 space-y-3">
                    <div
                      v-for="(category, index) in donutData"
                      :key="index"
                      class="flex items-center justify-between"
                    >
                      <div class="flex items-center gap-2">
                        <span
                          :class="[
                            'w-3 h-3 rounded-full',
                            {
                              'bg-[#059669]': index === 0,
                              'bg-[#10b981]': index === 1,
                              'bg-[#34d399]': index === 2,
                              'bg-[#6ee7b7]': index === 3,
                            },
                          ]"
                        ></span>
                        <span class="text-[12px]">{{ category.name }}</span>
                      </div>
                      <span class="text-[12px] font-semibold"
                        >NPR
                        {{
                          new Intl.NumberFormat('en-IN').format(category.sales)
                        }}</span
                      >
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
        <div>
          <Card class="h-full">
            <CardHeader class="pb-4">
              <CardTitle class="flex gap-1 items-center">
                <p class="">Recent Activity</p>
                <div class="">
                  <TooltipProvider :delayDuration="100">
                    <Tooltip
                      :open="
                        isTouchDevice
                          ? infoTooltipOpen === 'ea-traffic-sources'
                          : undefined
                      "
                      :disable-closing-trigger="isTouchDevice"
                      @update:open="
                        (value) =>
                          handleInfoTooltipOpenChange('ea-traffic-sources', value)
                      "
                    >
                      <TooltipTrigger as-child>
                        <button
                          type="button"
                          class="size-4 inline-flex items-center justify-center"
                          aria-label="Today's delivery curve info"
                          @click="handleInfoTooltipClick('ea-traffic-sources')"
                        >
                          <svg
                            fill="#3b82f6"
                            viewBox="0 0 1920 1920"
                            xmlns="http://www.w3.org/2000/svg"
                          >
                            <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                            <g
                              id="SVGRepo_tracerCarrier"
                              stroke-linecap="round"
                              stroke-linejoin="round"
                            ></g>
                            <g id="SVGRepo_iconCarrier">
                              <path
                                d="M960 0c530.193 0 960 429.807 960 960s-429.807 960-960 960S0 1490.193 0 960 429.807 0 960 0Zm0 101.053c-474.384 0-858.947 384.563-858.947 858.947S485.616 1818.947 960 1818.947 1818.947 1434.384 1818.947 960 1434.384 101.053 960 101.053Zm-42.074 626.795c-85.075 39.632-157.432 107.975-229.844 207.898-10.327 14.249-10.744 22.907-.135 30.565 7.458 5.384 11.792 3.662 22.656-7.928 1.453-1.562 1.453-1.562 2.94-3.174 9.391-10.17 16.956-18.8 33.115-37.565 53.392-62.005 79.472-87.526 120.003-110.867 35.075-20.198 65.9 9.485 60.03 47.471-1.647 10.664-4.483 18.534-11.791 35.432-2.907 6.722-4.133 9.646-5.496 13.23-13.173 34.63-24.269 63.518-47.519 123.85l-1.112 2.886c-7.03 18.242-7.03 18.242-14.053 36.48-30.45 79.138-48.927 127.666-67.991 178.988l-1.118 3.008a10180.575 10180.575 0 0 0-10.189 27.469c-21.844 59.238-34.337 97.729-43.838 138.668-1.484 6.37-1.484 6.37-2.988 12.845-5.353 23.158-8.218 38.081-9.82 53.42-2.77 26.522-.543 48.24 7.792 66.493 9.432 20.655 29.697 35.43 52.819 38.786 38.518 5.592 75.683 5.194 107.515-2.048 17.914-4.073 35.638-9.405 53.03-15.942 50.352-18.932 98.861-48.472 145.846-87.52 41.11-34.26 80.008-76 120.788-127.872 3.555-4.492 3.555-4.492 7.098-8.976 12.318-15.707 18.352-25.908 20.605-36.683 2.45-11.698-7.439-23.554-15.343-19.587-3.907 1.96-7.993 6.018-14.22 13.872-4.454 5.715-6.875 8.77-9.298 11.514-9.671 10.95-19.883 22.157-30.947 33.998-18.241 19.513-36.775 38.608-63.656 65.789-13.69 13.844-30.908 25.947-49.42 35.046-29.63 14.559-56.358-3.792-53.148-36.635 2.118-21.681 7.37-44.096 15.224-65.767 17.156-47.367 31.183-85.659 62.216-170.048 13.459-36.6 19.27-52.41 26.528-72.201 21.518-58.652 38.696-105.868 55.04-151.425 20.19-56.275 31.596-98.224 36.877-141.543 3.987-32.673-5.103-63.922-25.834-85.405-22.986-23.816-55.68-34.787-96.399-34.305-45.053.535-97.607 15.256-145.963 37.783Zm308.381-388.422c-80.963-31.5-178.114 22.616-194.382 108.33-11.795 62.124 11.412 115.76 58.78 138.225 93.898 44.531 206.587-26.823 206.592-130.826.005-57.855-24.705-97.718-70.99-115.729Z"
                                fill-rule="evenodd"
                              ></path>
                            </g>
                          </svg>
                          <!-- <Info class="w-4 text-gray-800 p-0"/> -->
                        </button>
                      </TooltipTrigger>
                      <TooltipContent class="w-40">
                        <p class="break-words">
                          Latest actions and updates across the system
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="mx-auto w-full max-w-md">
                <ul class="relative max-h-[470px] overflow-y-auto pr-1">
                  <li
                    v-for="(step, idx) in steps"
                    :key="step.step"
                    class="relative flex items-start gap-4 pb-7 last:pb-0"
                  >
                    <span
                      :class="[
                        'relative z-10 mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full',
                        getActivityClasses(step, idx),
                      ]"
                    >
                      <component
                        :is="getActivityIcon(step, idx)"
                        class="size-4"
                      />
                    </span>
                    <span
                      v-if="idx !== steps.length - 1"
                      class="absolute left-[14px] top-6 h-[calc(100%-1.25rem)] w-0.5 bg-muted"
                    ></span>
                    <div class="flex flex-col gap-1">
                      <p class="text-sm font-semibold md:text-base">
                        {{ step.title }}
                      </p>
                      <p class="text-xs text-muted-foreground md:text-sm">
                        {{ step.description }}
                      </p>
                    </div>
                  </li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
// import { DatePicker } from 'frappe-ui'
import { Progress, LinearProgress } from '@/components/ui/progress'

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

import {
  TrendingUp,
  Minus,
  CircleDollarSignIcon,
  ShoppingCart,
  Eye,
  ArrowDownUp,
  Banknote,
  Package,
  Truck,
  CreditCard,
  UserRound,
  CheckCircle2,
  AlertCircle,
  Circle as CircleIcon,
  X,
  Star,
  CircleDashed,
} from 'lucide-vue-next'

import { AreaChart } from '@/components/ui/chart-area'
import { VisAxis } from '@unovis/vue'

import { DonutChart } from '@/components/ui/chart-donut'

import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import { Button } from '@/components/ui/button'

import { Search } from 'lucide-vue-next'
// import {
//   Combobox,
//   ComboboxAnchor,
//   ComboboxEmpty,
//   ComboboxGroup,
//   ComboboxInput,
//   ComboboxItem,
//   ComboboxItemIndicator,
//   ComboboxList,
// } from '@/components/ui/combobox'

// interface Framework {
//   value: string
//   label: string
// }

// const frameworks: Framework[] = [
//   { value: 'ayushk', label: 'Ayush Karanjit' },
//   { value: 'budsa', label: 'Pixel Buds A series' },
//   { value: 'gpro', label: 'Logitech G Pro Wireless' },
//   { value: 'airpods', label: 'Airpods' },
//   { value: 'iphone13', label: 'iPhone 13' },
// ]

// const value = ref<Framework | undefined>()

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const emptyDashboard = {
  summary: {
    totalSales: { value: 0, change: '0.00%', comparisonText: 'vs last week' },
    totalOrders: { value: 0, change: '0.00%', comparisonText: 'vs last week' },
    totalVisitors: {
      value: 0,
      change: '0.00%',
      comparisonText: 'vs last week',
    },
  },
  revenueAnalytics: { dataPoints: [] },
  monthlyTarget: {
    percentage: 0,
    status: 'No target configured',
    message: "Showing this month's confirmed storefront revenue.",
    target: 0,
    revenue: 0,
    canEdit: false,
  },
  topCategories: { categories: [] },
  activeUser: {
    total: 0,
    change: '0.00%',
    comparisonText: 'vs last week',
    countries: [],
  },
  conversionRate: { period: 'This Week', metrics: [] },
  trafficSources: { sources: [] },
  recentOrders: [],
  recentActivity: [],
  websites: [],
}
const ecommerceData = ref<any>({ dashboard: emptyDashboard })
const analyticsLoading = ref(false)
const analyticsError = ref('')
const selectedAnalyticsWebsite = ref('')
const monthlyTargetInput = ref('')
const monthlyTargetSaving = ref(false)
const monthlyTargetMessage = ref('')
const monthlyTargetError = ref(false)

const dashboardData = computed(() => {
  return ecommerceData.value?.dashboard || emptyDashboard
})

// Transform revenueAnalytics dataPoints to AreaChart format
const revenueAnalytics = computed(() => {
  const dataPoints = dashboardData.value.revenueAnalytics?.dataPoints || []
  return dataPoints.map((point: any) => ({
    name: point.date,
    revenue: point.revenue,
    order: point.order,
  }))
})

// Transform topCategories to donutData format
const donutData = computed(() => {
  const categories = dashboardData.value.topCategories?.categories || []
  return categories.map((category: any) => ({
    name: category.name,
    sales: category.value,
  }))
})

function conversionBarHeight(value: number) {
  const metrics = dashboardData.value.conversionRate?.metrics || []
  const maximum = Math.max(
    ...metrics.map((metric: any) => Number(metric.value || 0)),
    1,
  )
  return Math.max(4, (Number(value || 0) / maximum) * 100)
}

function trafficSourceColor(index: number) {
  return (
    [
      'bg-[#a7f3d0]',
      'bg-[#6ee7b7]',
      'bg-[#34d399]',
      'bg-[#10b981]',
      'bg-[#059669]',
    ][index] || 'bg-emerald-800'
  )
}

// Recent activity -> Stepper steps
const steps = computed(() => {
  const items = ((dashboardData.value as any)?.recentActivity || []) as Array<{
    timestamp: string
    message: string
  }>
  return items.map((item, index) => ({
    step: index + 1,
    title: item.timestamp,
    description: item.message,
  }))
})

// Choose an icon for each activity. First item uses Banknote.
function getActivityIcon(
  step: { title: string; description: string; step: number },
  idx: number,
) {
  if (idx === 0) return Banknote
  const text = `${step.title} ${step.description}`.toLowerCase()
  if (text.includes('cancelled')) return X
  if (text.includes('review')) return Star
  if (text.includes('pending')) return CircleDashed
  if (text.includes('shipped')) return Truck
  if (text.includes('below') || text.includes('failed')) return AlertCircle
  return CircleIcon
}

// Color classes per activity type (bg + icon color)
function getActivityClasses(
  step: { title: string; description: string; step: number },
  idx: number,
) {
  if (idx === 0) return 'bg-green-50 text-green-700'
  const text = `${step.title} ${step.description}`.toLowerCase()
  if (text.includes('cancelled')) return 'bg-red-50 text-red-700'
  if (text.includes('review')) return 'bg-amber-50 text-amber-700'
  if (text.includes('pending')) return 'bg-yellow-50 text-yellow-700'
  if (text.includes('shipped')) return 'bg-blue-50 text-blue-700'
  if (text.includes('below') || text.includes('failed'))
    return 'bg-red-50 text-red-700'
  return 'bg-slate-50 text-slate-700'
}

const donutValueFormatter = (tick: number | Date) =>
  typeof tick === 'number'
    ? ` ${new Intl.NumberFormat('us').format(tick).toString()}`
    : ''

function valueFormatter(tick: number | Date) {
  return typeof tick === 'number'
    ? `NPR ${new Intl.NumberFormat('en-IN').format(tick).toString()}`
    : ''
}

const inputValue = ref('')
const showSuggestions = ref(false)
type WebsiteSuggestion = { label: string; value: string }
const suggestions = computed<WebsiteSuggestion[]>(() => [
  { label: 'All ecommerce websites', value: '' },
  ...((dashboardData.value as any).websites || []).map((website: any) => ({
    label: website.website_link || `Website ${website.name}`,
    value: String(website.name),
  })),
])

const filteredSuggestions = ref<WebsiteSuggestion[]>([])

// Show all suggestions on focus
const onFocus = () => {
  filteredSuggestions.value = suggestions.value
  showSuggestions.value = true
}

// Filter suggestions based on input text
const filterSuggestions = () => {
  const query = inputValue.value.toLowerCase()
  if (!query) {
    filteredSuggestions.value = suggestions.value
    return
  }
  filteredSuggestions.value = suggestions.value.filter((item) =>
    item.label.toLowerCase().includes(query),
  )
}

const selectSuggestion = (item: WebsiteSuggestion) => {
  inputValue.value = item.label
  showSuggestions.value = false
  loadAnalytics(item.value)
}

const handleBlur = () => {
  // Delay hiding to allow click on suggestion
  setTimeout(() => {
    showSuggestions.value = false
  }, 100)
}

function analyticsHeaders() {
  const token = localStorage.getItem('access_token') || ''
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function loadAnalytics(websiteId = '') {
  analyticsLoading.value = true
  analyticsError.value = ''
  try {
    const query = websiteId
      ? `?website_id=${encodeURIComponent(websiteId)}`
      : ''
    const response = await fetch(
      `/api/method/ecommerce.api.get_ecommerce_analytics${query}`,
      { headers: analyticsHeaders() },
    )
    const body = await response.json().catch(() => ({}))
    const result = body?.message ?? body
    if (!response.ok || result?.status !== 'success') {
      throw new Error(result?.message || 'Unable to load ecommerce analytics.')
    }
    ecommerceData.value = { dashboard: result.data || emptyDashboard }
    selectedAnalyticsWebsite.value = websiteId
    monthlyTargetInput.value = String(result.data?.monthlyTarget?.target || '')
    monthlyTargetMessage.value = ''
    monthlyTargetError.value = false
    const selected = suggestions.value.find((item) => item.value === websiteId)
    inputValue.value = selected?.label || 'All ecommerce websites'
  } catch (error: any) {
    ecommerceData.value = { dashboard: emptyDashboard }
    analyticsError.value =
      error?.message || 'Unable to load ecommerce analytics.'
  } finally {
    analyticsLoading.value = false
  }
}

async function saveMonthlyTarget() {
  if (!selectedAnalyticsWebsite.value) return
  monthlyTargetSaving.value = true
  monthlyTargetMessage.value = ''
  monthlyTargetError.value = false
  try {
    const response = await fetch(
      '/api/method/ecommerce.api.set_ecommerce_monthly_target',
      {
        method: 'POST',
        headers: analyticsHeaders(),
        body: JSON.stringify({
          website_id: selectedAnalyticsWebsite.value,
          target: monthlyTargetInput.value || 0,
        }),
      },
    )
    const body = await response.json().catch(() => ({}))
    const result = body?.message ?? body
    if (!response.ok || result?.status !== 'success') {
      throw new Error(result?.message || 'Unable to update monthly target.')
    }
    monthlyTargetMessage.value = result.message || 'Monthly target updated.'
    await loadAnalytics(selectedAnalyticsWebsite.value)
    monthlyTargetMessage.value = result.message || 'Monthly target updated.'
  } catch (error: any) {
    monthlyTargetError.value = true
    monthlyTargetMessage.value =
      error?.message || 'Unable to update monthly target.'
  } finally {
    monthlyTargetSaving.value = false
  }
}

import type {
  ColumnDef,
  ColumnFiltersState,
  ExpandedState,
  SortingState,
  VisibilityState,
} from '@tanstack/vue-table'
import {
  FlexRender,
  getCoreRowModel,
  getExpandedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useVueTable,
} from '@tanstack/vue-table'
import { ArrowUpDown } from 'lucide-vue-next'
import { h } from 'vue'
import { valueUpdater } from '@/lib/utils'
import { Input } from '@/components/ui/input'

export interface RecentOrder {
  no: number
  orderId: string
  customer: string
  product: string
  qty: number
  total: number
  status: string
}

const recentOrders = computed<RecentOrder[]>(() => {
  return ((dashboardData.value as any)?.recentOrders || []) as RecentOrder[]
})

// const productIconMap: Record<string, string> = {
//   // 'iPhone 17 Pro Max': '📱',
//   // 'ASUS Vivobook': '💻',
//   // 'MacBook Air M3': '💻',
//   // 'PS5 Pro': '🎮',
//   // 'JBL Boombox 3': '🔊',
// }

function getStatusPill(status: string) {
  const s = (status || '').toLowerCase()
  if (s.includes('ship'))
    return { wrapper: 'bg-blue-100 text-blue-700', dot: 'bg-blue-500' }
  if (s.includes('process'))
    return { wrapper: 'bg-yellow-100 text-yellow-700', dot: 'bg-yellow-500' }
  if (s.includes('deliver'))
    return { wrapper: 'bg-green-100 text-green-700', dot: 'bg-green-500' }
  if (s.includes('pend'))
    return { wrapper: 'bg-orange-100 text-orange-700', dot: 'bg-orange-500' }
  if (s.includes('cancel'))
    return { wrapper: 'bg-red-100 text-red-700', dot: 'bg-red-500' }
  return { wrapper: 'bg-gray-100 text-gray-600', dot: 'bg-gray-400' }
}

const columns: ColumnDef<RecentOrder>[] = [
  {
    accessorKey: 'no',
    header: ({ column }) =>
      h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['No', h(ArrowDownUp, { class: 'h-12 w-12' })],
      ),
    cell: ({ row }) => h('div', { class: '' }, String(row.getValue('no'))),
  },
  {
    accessorKey: 'orderId',
    header: ({ column }) =>
      h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1 ',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['Order ID', h(ArrowUpDown, { class: 'w-1 h-1' })],
      ),
    cell: ({ row }) => h('div', { class: '' }, row.getValue('orderId')),
  },
  {
    accessorKey: 'customer',
    header: ({ column }) => {
      return h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['Customer', h(ArrowUpDown, { class: 'size-1' })],
      )
    },
    cell: ({ row }) => h('div', {}, row.getValue('customer')),
  },
  {
    accessorKey: 'product',
    header: ({ column }) =>
      h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['Product', h(ArrowUpDown, { size: 12 })],
      ),
    cell: ({ row }) => {
      const product = String(row.getValue('product'))
      // const icon = productIconMap[product] || '🛒'
      return h('div', { class: 'flex items-center' }, [
        h('span', { class: 'text-lg' }),
        h('span', {}, product),
      ])
    },
  },
  {
    accessorKey: 'qty',
    header: ({ column }) =>
      h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['Qty', h(ArrowUpDown, { size: 12 })],
      ),
    cell: ({ row }) =>
      h('div', { class: 'text-center' }, String(row.getValue('qty'))),
  },
  {
    accessorKey: 'total',
    header: ({ column }) =>
      h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['Total', h(ArrowUpDown, { size: 12 })],
      ),
    cell: ({ row }) => {
      const total = Number.parseFloat(row.getValue('total'))
      const formatted = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'NPR',
      }).format(total)
      return h('div', { class: 'text-left font-medium ' }, formatted)
    },
  },
  {
    accessorKey: 'status',
    header: ({ column }) =>
      h(
        Button,
        {
          variant: 'ghost',
          class: 'px-0 gap-1',
          onClick: () => column.toggleSorting(column.getIsSorted() === 'asc'),
        },
        () => ['Status', h(ArrowUpDown, { size: 12 })],
      ),
    cell: ({ row }) => {
      const status = String(row.getValue('status'))
      const { wrapper, dot } = getStatusPill(status)
      return h(
        'div',
        {
          class: `inline-flex items-center gap-2 rounded-full px-2 py-0.5 text-xs font-medium ${wrapper}`,
        },
        [
          h('span', { class: `size-2 rounded-full ${dot}` }),
          h('span', {}, status),
        ],
      )
    },
  },
]

const sorting = ref<SortingState>([])
const columnFilters = ref<ColumnFiltersState>([])
const columnVisibility = ref<VisibilityState>({})
const expanded = ref<ExpandedState>({})

const table = useVueTable({
  get data() {
    return recentOrders.value
  },
  columns,
  getCoreRowModel: getCoreRowModel(),
  getPaginationRowModel: getPaginationRowModel(),
  getSortedRowModel: getSortedRowModel(),
  getFilteredRowModel: getFilteredRowModel(),
  getExpandedRowModel: getExpandedRowModel(),
  onSortingChange: (updaterOrValue) => valueUpdater(updaterOrValue, sorting),
  onColumnFiltersChange: (updaterOrValue) =>
    valueUpdater(updaterOrValue, columnFilters),
  onColumnVisibilityChange: (updaterOrValue) =>
    valueUpdater(updaterOrValue, columnVisibility),
  onExpandedChange: (updaterOrValue) => valueUpdater(updaterOrValue, expanded),
  state: {
    get sorting() {
      return sorting.value
    },
    get columnFilters() {
      return columnFilters.value
    },
    get columnVisibility() {
      return columnVisibility.value
    },
    get expanded() {
      return expanded.value
    },
  },
})

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

const isTouchDevice = ref(false)
const infoTooltipOpen = ref<string | null>(null)

const updateIsTouchDevice = () => {
  if (typeof window === 'undefined') return

  isTouchDevice.value = window.matchMedia('(pointer: coarse)').matches
}

const handleInfoTooltipClick = (id: string) => {
  if (!isTouchDevice.value) return

  infoTooltipOpen.value = infoTooltipOpen.value === id ? null : id
}

const handleInfoTooltipOpenChange = (id: string, value: boolean) => {
  if (!isTouchDevice.value) return

  infoTooltipOpen.value = value ? id : null
}

onMounted(() => {
  updateIsTouchDevice()
  let selectedWebsiteId = ''
  try {
    const selectedWebsite = JSON.parse(
      localStorage.getItem('selectedWebsite') || '{}',
    )
    if (selectedWebsite?.type === 'Ecommerce') {
      selectedWebsiteId = String(selectedWebsite.name || '')
    }
  } catch {
    selectedWebsiteId = ''
  }
  loadAnalytics(selectedWebsiteId)
  if (typeof window !== 'undefined') {
    window.addEventListener('resize', updateIsTouchDevice)
    const closeTooltipOnScroll = () => {
      if (!isTouchDevice.value) return
      if (infoTooltipOpen.value !== null) {
        infoTooltipOpen.value = null
      }
    }
    ;(window as any).__eaCloseTooltipOnScroll__ = closeTooltipOnScroll
    window.addEventListener('scroll', closeTooltipOnScroll, { passive: true })
    window.addEventListener('touchmove', closeTooltipOnScroll, {
      passive: true,
    })
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', updateIsTouchDevice)
    const closeTooltipOnScroll = (window as any).__eaCloseTooltipOnScroll__
    if (closeTooltipOnScroll) {
      window.removeEventListener('scroll', closeTooltipOnScroll)
      window.removeEventListener('touchmove', closeTooltipOnScroll)
      ;(window as any).__eaCloseTooltipOnScroll__ = undefined
    }
  }
})

watch(isTouchDevice, (value) => {
  if (!value) infoTooltipOpen.value = null
})
</script>
