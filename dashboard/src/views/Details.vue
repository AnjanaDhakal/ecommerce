<template>
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen">
    <div v-if="isLoading" class="mt-40 text-center">
      <PageLoader />
    </div>
    <div v-if="detail.length">
      <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen">
        <div
          class="flex items-center justify-between h-15 rounded bg-gray-50 p-5 mb-5"
        >
          <BreadCrums />
        </div>
        <div
          class="grid sm:grid-cols-1 md:grid-cols-3 gap-4 mb-4"
          v-for="(item, index) in detail"
          :key="index"
        >
          <div class="md:grid grid-rows-2 gap-4 mb-4">
          <div
            class="min-h-[200px] bg-white rounded-lg border border-gray-200 "
            style="max-height: 600px"
          >
            <div
              class="rounded-t-md bg-gray-100 flex justify-between items-center p-2"
            >
              <p class="text-xl text-gray-800 font-semibold">
                Order Details
                <span
                  v-if="item.green_delivery === 1"
                  class="material-symbols-outlined text-green-600"
                  style="font-size: 24px"
                  >eco</span
                >
                <Rocket
                  v-if="Number(item.express_delivery) === 1"
                  class="inline-block h-5 w-5 text-rose-600 ml-1"
                  title="Express Delivery"
                />
              </p>

              <div>
                <div>
                  <Popover placement="bottom-start">
                    <template #target="{ togglePopover }">
                      <Button
                        @click="(togglePopover(), openShareMenu())"
                        title="Click here to send the tracking link to the customer."
                        ><span class="material-symbols-outlined">
                          content_copy
                        </span>
                      </Button>
                    </template>
                    <template #body-main>
                      <div class="p-2 text-sm">
                        <p>Share Copied Link With</p>
                        <div class="share-menu p-2 flex flex-row gap-4">
                          <!-- Share on WhatsApp -->
                          <ShareNetwork
                            network="whatsapp"
                            :url="urlToShare"
                            :title="`Hi ${item.customer_name}!,
                           Your package is on its way. 📦 Track it here:`"
                            :description="`We’re here if you need anything! Best, ${item.vendor_name}`"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 448 512"
                              width="25"
                              height="25"
                            >
                              <path
                                fill="green"
                                d="M380.9 97.1C339 55.1 283.2 32 223.9 32c-122.4 0-222 99.6-222 222 0 39.1 10.2 77.3 29.6 111L0 480l117.7-30.9c32.4 17.7 68.9 27 106.1 27h.1c122.3 0 224.1-99.6 224.1-222 0-59.3-25.2-115-67.1-157zm-157 341.6c-33.2 0-65.7-8.9-94-25.7l-6.7-4-69.8 18.3L72 359.2l-4.4-7c-18.5-29.4-28.2-63.3-28.2-98.2 0-101.7 82.8-184.5 184.6-184.5 49.3 0 95.6 19.2 130.4 54.1 34.8 34.9 56.2 81.2 56.1 130.5 0 101.8-84.9 184.6-186.6 184.6zm101.2-138.2c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8-3.7 5.6-14.3 18-17.6 21.8-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7 .9-6.9-.5-9.7-1.4-2.8-12.5-30.1-17.1-41.2-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2-3.7 0-9.7 1.4-14.8 6.9-5.1 5.6-19.4 19-19.4 46.3 0 27.3 19.9 53.7 22.6 57.4 2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4 4.6-13 4.6-24.1 3.2-26.4-1.3-2.5-5-3.9-10.5-6.6z"
                              />
                            </svg>
                          </ShareNetwork>

                          <ShareNetwork
                            network="viber"
                            :url="urlToShare"
                            :title="`Hi ${item.customer_name}!,
                           Your package is on its way. 📦 Track it here:`"
                            :description="`We’re here if you need anything! Best, ${item.vendor_name}`"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 512 512"
                              width="25"
                              height="25"
                            >
                              <path
                                fill="purple"
                                d="M444 49.9C431.3 38.2 379.9 .9 265.3 .4c0 0-135.1-8.1-200.9 52.3C27.8 89.3 14.9 143 13.5 209.5c-1.4 66.5-3.1 191.1 117 224.9h.1l-.1 51.6s-.8 20.9 13 25.1c16.6 5.2 26.4-10.7 42.3-27.8 8.7-9.4 20.7-23.2 29.8-33.7 82.2 6.9 145.3-8.9 152.5-11.2 16.6-5.4 110.5-17.4 125.7-142 15.8-128.6-7.6-209.8-49.8-246.5zM457.9 287c-12.9 104-89 110.6-103 115.1-6 1.9-61.5 15.7-131.2 11.2 0 0-52 62.7-68.2 79-5.3 5.3-11.1 4.8-11-5.7 0-6.9 .4-85.7 .4-85.7-.1 0-.1 0 0 0-101.8-28.2-95.8-134.3-94.7-189.8 1.1-55.5 11.6-101 42.6-131.6 55.7-50.5 170.4-43 170.4-43 96.9 .4 143.3 29.6 154.1 39.4 35.7 30.6 53.9 103.8 40.6 211.1zm-139-80.8c.4 8.6-12.5 9.2-12.9 .6-1.1-22-11.4-32.7-32.6-33.9-8.6-.5-7.8-13.4 .7-12.9 27.9 1.5 43.4 17.5 44.8 46.2zm20.3 11.3c1-42.4-25.5-75.6-75.8-79.3-8.5-.6-7.6-13.5 .9-12.9 58 4.2 88.9 44.1 87.8 92.5-.1 8.6-13.1 8.2-12.9-.3zm47 13.4c.1 8.6-12.9 8.7-12.9 .1-.6-81.5-54.9-125.9-120.8-126.4-8.5-.1-8.5-12.9 0-12.9 73.7 .5 133 51.4 133.7 139.2zM374.9 329v.2c-10.8 19-31 40-51.8 33.3l-.2-.3c-21.1-5.9-70.8-31.5-102.2-56.5-16.2-12.8-31-27.9-42.4-42.4-10.3-12.9-20.7-28.2-30.8-46.6-21.3-38.5-26-55.7-26-55.7-6.7-20.8 14.2-41 33.3-51.8h.2c9.2-4.8 18-3.2 23.9 3.9 0 0 12.4 14.8 17.7 22.1 5 6.8 11.7 17.7 15.2 23.8 6.1 10.9 2.3 22-3.7 26.6l-12 9.6c-6.1 4.9-5.3 14-5.3 14s17.8 67.3 84.3 84.3c0 0 9.1 .8 14-5.3l9.6-12c4.6-6 15.7-9.8 26.6-3.7 14.7 8.3 33.4 21.2 45.8 32.9 7 5.7 8.6 14.4 3.8 23.6z"
                              />
                            </svg>
                          </ShareNetwork>

                          <ShareNetwork
                            network="facebook"
                            :url="urlToShare"
                            :title="`Hi ${item.customer_name}!,
                           Your package is on its way. 📦 Track it here:`"
                            :description="`We’re here if you need anything! Best, ${item.vendor_name}`"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 512 512"
                              width="25"
                              height="25"
                            >
                              <path
                                fill="#1877F2"
                                d="M512 256C512 114.6 397.4 0 256 0S0 114.6 0 256C0 376 82.7 476.8 194.2 504.5V334.2H141.4V256h52.8V222.3c0-87.1 39.4-127.5 125-127.5c16.2 0 44.2 3.2 55.7 6.4V172c-6-.6-16.5-1-29.6-1c-42 0-58.2 15.9-58.2 57.2V256h83.6l-14.4 78.2H287V510.1C413.8 494.8 512 386.9 512 256h0z"
                              />
                            </svg>
                          </ShareNetwork>

                          <ShareNetwork
                            network="sms"
                            :url="urlToShare"
                            :title="`Hi ${item.customer_name}!,
                           Your package is on its way. 📦 Track it here:`"
                            :description="`We’re here if you need anything! Best, ${item.vendor_name}`"
                          >
                            <svg
                              xmlns="http://www.w3.org/2000/svg"
                              viewBox="0 0 512 512"
                              width="25"
                              height="25"
                            >
                              <path
                                fill="green"
                                d="M256 448c141.4 0 256-93.1 256-208S397.4 32 256 32S0 125.1 0 240c0 45.1 17.7 86.8 47.7 120.9c-1.9 24.5-11.4 46.3-21.4 62.9c-5.5 9.2-11.1 16.6-15.2 21.6c-2.1 2.5-3.7 4.4-4.9 5.7c-.6 .6-1 1.1-1.3 1.4l-.3 .3c0 0 0 0 0 0c0 0 0 0 0 0s0 0 0 0s0 0 0 0c-4.6 4.6-5.9 11.4-3.4 17.4c2.5 6 8.3 9.9 14.8 9.9c28.7 0 57.6-8.9 81.6-19.3c22.9-10 42.4-21.9 54.3-30.6c31.8 11.5 67 17.9 104.1 17.9zM96 212.8c0-20.3 16.5-36.8 36.8-36.8l19.2 0c8.8 0 16 7.2 16 16s-7.2 16-16 16l-19.2 0c-2.7 0-4.8 2.2-4.8 4.8c0 1.6 .8 3.2 2.2 4.1l18.2 11.5c5.9 3.8 5.3 11.8-1.5 15.6l-3.6 2.3c-5.5 3.4-12.7 2.7-17.2-1.7l-6.6-6.7c-3.4-3.4-3.7-7.5-1.2-12.1l13.6-19.6z"
                              />
                            </svg>
                          </ShareNetwork>
                        </div>
                      </div>
                    </template>
                  </Popover>
                </div>
              </div>
              <Toast v-if="showToast" message="Copied to clipboard!" />
            </div>
            <div class="mb-4 p-3">
              <table class="min-w-full divide-y divide-gray-200 p-2">
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Order Code
                    </td>
                    <td class="text-gray-800 text-lg font-bold">
                      <span class="inline-flex items-center gap-2">
                        <span>{{ item.order_name }}</span>
                        <span
                          v-if="Number(item.express_delivery) === 1"
                          class="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2 py-0.5 text-xs font-semibold text-rose-700"
                        >
                          <Rocket class="h-3.5 w-3.5" />
                          Express
                        </span>
                      </span>
                    </td>
                  </tr>
                  <tr class="h-8" v-if="item.vendor_tracking_number">
                    <td class="font-semibold text-gray-800 text-base">
                      Reference Code
                    </td>
                    <td class="text-gray-800 text-lg font-bold break-all">
                      {{ item.vendor_tracking_number }}
                    </td>
                  </tr>
                  <tr class="h-8" v-if="item.customer_tracking_number">
                    <td class="font-semibold text-gray-800 text-base">
                      Customer Tracking number
                    </td>
                    <td class="text-gray-800 text-lg font-bold">
                      <a
                        :href="`/tracking/${item.customer_tracking_number}`"
                        target="_blank"
                        class="text-blue-600 hover:underline"
                      >
                        {{ item.customer_tracking_number }}
                      </a>
                    </td>
                  </tr>
                  <tr class="h-8" v-if="item.return_with_exchange_order">
                    <td class="font-semibold text-gray-800 text-base">
                      Exchange Order Id
                    </td>
                    <td class="text-gray-800 text-lg font-bold">
                    <a
                      :href="`/dashboard/main/${item.return_with_exchange_order}`"
                      target="_blank"
                      class="text-blue-600 text-lg font-bold hover:underline"
                    >
                      {{ item.return_with_exchange_order }}
                    </a>
                    </td>
                  </tr>
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">Name</td>
                    <td class="text-gray-800 text-lg font-bold">
                      {{ item.customer_name }}
                    </td>
                  </tr>
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Mobile
                    </td>
                    <td class="text-gray-800 text-base">
                      <a
                        :href="`tel:${item.primary_mobile_no}`"
                        class="text-blue-600 hover:underline"
                      >
                         {{ item.primary_mobile_no }}
                      </a>
                    </td>
                  </tr>
                  <tr class="h-8" v-if="item.secondary_mobile_no">
                    <td class="font-semibold text-gray-800 text-base">
                      Secondary Phone
                    </td>
                    <td class="text-gray-800 text-base">
                      <a
                        :href="`tel:${item.secondary_mobile_no}`"
                        class="text-blue-600 hover:underline"
                      >
                      {{ item.secondary_mobile_no }}
                      </a>
                    </td>
                  </tr>
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Location
                    </td>
                    <td class="text-gray-800 text-base">
                      {{ item.location }}
                    </td>
                  </tr>
                  <tr class="h-8" v-if="item.name_of_city_area">
                    <td class="font-semibold text-gray-800 text-base">
                      City Area
                    </td>
                    <td class="text-gray-800 text-base">
                      {{ item.name_of_city_area }}
                    </td>
                  </tr>

                  <!-- <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Vendor:
                    </td>
                    <td class="text-gray-800 text-base">
                      {{ item.vendor_name }}
                    </td>
                  </tr> -->
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Destination Branch
                    </td>
                    <td class="text-gray-800 font-bold text-base">
                      {{ item.destination_branch }}
                    </td>
                  </tr>
                  <!-- <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Is Vendor Paid:
                    </td>
                    <td class="text-gray-800 font-plight text-base">
                      {{ item.is_paid_order }}
                    </td>
                  </tr> -->
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Amount
                    </td>
                    <td class="text-gray-800 text-base">
                      {{ item.cod_amount }}
                    </td>
                  </tr>
                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Delivery Charge
                    </td>
                    <td class="text-gray-800 text-base">
                      Rs {{ getDeliveryAmount(item) }}
                    </td>
                  </tr>

                  <tr class="h-8">
                    <td class="font-semibold text-gray-800 text-base">
                      Order Status
                    </td>
                    <td
                      class="font-semibold rounded-full px-2 my-2 inline-block text-xs text-white p-2"
                      :class="statusClass(item.status_after_warehouse)"
                    >
                      {{ item.status_after_warehouse }}
                    </td>
                  </tr>
                  <tr
                    v-if="item.duration && item.duration !== '0 m'"
                    class="h-8"
                  >
                    <td class="font-semibold text-gray-800 text-base">
                    Delivery Duration
                    </td>
                    <td class="text-gray-800 text-base">
                      {{ item.duration }}
                    </td>
                  </tr>

                  <tr
                    v-if="item.instruction !== null && item.instruction !== ''"
                    class="h-8"
                  >
                    <td class="font-semibold text-gray-800 text-base">
                      Instruction
                    </td>
                    <td class="text-gray-800 text-base break-words">
                      {{ item.instruction }}
                    </td>
                  </tr>
                  <tr
                    v-if="
                      item.order_description !== null &&
                      item.order_description !== ''
                    "
                    class="h-8"
                  >
                    <td class="font-semibold text-gray-800 text-base">
                      Order Description
                    </td>
                    <td class="text-gray-800 text-base break-words">
                      {{ item.order_description }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div
            class="md:flex-row bg-white rounded-lg min-h-fit sm:block hidden border border-gray-200"
            style="max-height: 600px"
          >
            <div class="rounded-t-md bg-gray-100">
              <p class="p-3 text-xl text-gray-800 font-semibold">
                {{ item.pickup_branch }}-{{ item.destination_branch }}
              </p>
            </div>
            <div class="mb-4 p-3 min-h-[200px]">
              <div class="divide-x-2"></div>
              <div class="flex justify-center mt-2">
                <img
                  class="bg-gray-900 h-48 w-full object-contain md:w-48"
                  :src="qrCodes[index]"
                  alt="QR Code"
                />
              </div>
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <p class="mt-2 break-words">{{ item.pickup_branch }}- KTM</p>
                  <p
                    class="mt-2 text-gray-700 text-sm break-words overflow-auto max-h-48"
                  >
                    {{ item.pickup_branch_details.description }}
                  </p>
                </div>
                <div>
                  <p class="mt-2 break-words">
                    {{ item.destination_branch }}- {{ item.location }}
                  </p>
                  <p
                    class="mt-2 text-gray-700 text-sm break-words overflow-auto max-h-48"
                  >
                    {{ item.destination_branch_details.description }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="md:grid grid-rows-2 gap-4 mb-4">
          <div
            class="bg-white rounded-lg min-h-fit sm:block hidden border border-gray-200"
            style="max-height: 600px"
          >
            <div class="rounded-t-md bg-gray-100">
              <p class="p-3 text-xl text-gray-800 font-semibold">
                COD And Delivery Charge
              </p>
            </div>

            <div class="mb-4 p-3">
              <div class="divide-x-2"></div>
              <div class="card-body">
                <section class=" pr-2">
                  <div class="logOrBx">
                    <ul class="deli_list space-y-2">
                      <li class="flex items-center gap-2">
                        <strong class="font-semibold text-gray-800 text-base"
                          >COD Amount:</strong
                        >
                        <span class="font-bold flex items-center gap-2">
                          {{ item.cod_amount }}

                          <span
                            v-if="item.status === 'Completed'"
                            class="font-semibold rounded-full px-3 py-1 text-xs text-white bg-[#04c27f]"
                          >
                            {{ item.paid_to_vendor === 'Yes' ? 'Final COD Setteled' : 'Not Setteled' }}
                          </span>
                        </span>
                      </li>

                      <li>
                        <strong class="font-semibold text-gray-800 text-base"
                          >Delivery Charge :</strong
                        >
                        <span class="font-bold">
                          Rs {{ item.delivery_amount }}
                        </span>
                      </li>
                      <li>
                        <strong class="font-semibold text-gray-800 text-base"
                          >Package Weight:
                        </strong>
                        <span class="font-bold">
                          {{ item.package_weight }} {{ item.weight_uom }}
                        </span>
                      </li>
                    </ul>
                    <table
                      class="table-auto w-full text-sm bg-white mt-4 border border-gray-200 rounded-md overflow-hidden border-separate"
                      style="border-collapse: separate; border-spacing: 0"
                    >
                      <thead class="bg-gray-100 border-b border-gray-200">
                        <tr>
                          <th class="px-4 py-2">
                            Source Branch ({{ item.pickup_branch }})
                          </th>
                          <th class="px-4 py-2">
                            Destination Branch ({{ item.destination_branch }})
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td class="px-4 py-2 border-b border-gray-200">
                            Code : {{ item.pickup_branch_details.code }}
                          </td>
                          <td class="px-4 py-2 border-b border-gray-200">
                            Code : {{ item.destination_branch_details.code }}
                          </td>
                        </tr>
                        <tr>
                          <td class="px-4 py-2">Type : BRANCH</td>
                          <td class="px-4 py-2">Type : BRANCH</td>
                        </tr>
                      </tbody>
                    </table>
                    <ul class="deli_list space-y-2 mt-4">
                      <li class="flex items-center gap-2">
                        <strong class="font-psemibold text-gray-800 text-base">
                          Type :
                        </strong>

                        <span
                          class="px-2 py-2 rounded-full text-white font-semibold text-sm bg-gradient-to-r from-blue-500 to-blue-700"
                        >
                          {{ item.order_type }}
                        </span>
                      </li>

                      <li>
                        <strong class="font-psemibold text-gray-800 text-base"
                          >Created at :</strong
                        >
                        {{ formatDate(item.creation) }}
                      </li>
                    </ul>

                     <table
                      v-if="hasVisibleDeliveryChargeLog(item.DeliveryChargeLog)"
                      class="table-auto w-full text-sm bg-white my-4 border border-gray-200 rounded-md overflow-hidden border-separate"
                      style="border-collapse: separate; border-spacing: 0"
                    >
                      <thead class="bg-gray-100 border-b border-gray-200 text-left">
                        <tr>
                          <th class="px-4 py-2">SN</th>
                          <th class="px-4 py-2">Variable</th>
                          <th class="px-4 py-2">Value</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr
                          v-for="(log, idx) in item.DeliveryChargeLog"
                          :key="idx"
                        >
                          <td class=" px-4 py-2">{{ Number(log.value) === 0 ? '' : idx + 1 }}</td>
                          <td class=" px-4 py-2">{{ Number(log.value) === 0 ? '' : log.variable }}</td>
                          <td class=" px-4 py-2">{{ Number(log.value) === 0 ? '' : log.value }}</td>
                        </tr>
                      </tbody>
                    </table>

                  </div>
                </section>
                <div class="item-center flex justify-center pt-2">
                  <div v-if="item.signature !== null && item.signature !== ''">
                    <div class="text-gray-800 text-base flex justify-center">
                      <img
                        class="w-20"
                        :src="item.signature"
                        alt="Signature Image"
                        v-if="item.signature"
                      />
                    </div>
                    <div class="font-semibold text-gray-800 text-base">
                      Customer Signature
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="md:grid min-h-[200px] mb-4">
            <div class="bg-white rounded-lg border border-gray-200 " style="max-height: 600px">
              <div class="rounded-t-md bg-gray-100">
                <p class="p-3 text-xl text-gray-800 font-semibold">
                  Status Logs
                </p>
              </div>

              <div class="px-1">
                <div class="divide-x-2"></div>
                <div class="">
                  <div
                    class="border-0 shadow-none h-[530px] overflow-y-scroll mt-3"
                  >
                    <ul
                      class="relative ml-2 border-s border-gray-200 dark:border-gray-700"
                    >
                      <li
                        class="relative flex-row"
                        v-for="(log, index) in item.status_logs"
                        :key="index"
                      >
                        <!-- Circle with line cutting through the middle -->
                        <div class="relative">
                          <div
                            class="absolute w-3 h-3 bg-gray-400 rounded-full mt-1.5 -start-1.5 border border-white"
                          ></div>
                        </div>
                        <div class="ml-4">
                          <div class="inline-flex gap-3">
                            <div>
                              <div
                                class="text-sm  text-white font-semibold rounded-full p-1 inline-block"
                                :class="statusClass(splitLog(log).status)"
                              >
                                {{ splitLog(log).status }}
                              </div>
                            </div>
                          </div>
                          <div>
                            <time
                              class="mb-1 text-sm font-normal leading-none text-gray-800"
                              >{{ splitLog(log).date }}</time
                            >
                          </div>
                          <p class="mb-4 text-base font-normal text-gray-800">
                            {{ splitLog(log).message }}
                          </p>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <!-- <div class="px-6">
                  <div class="divide-x-2"></div>
                  <div class="">
                    <div class="border-0 shadow-none h-[530px] overflow-y-scroll mt-3">
                      <ul class="relative border-s border-gray-200 dark:border-gray-700">
                        <li
                          class="relative flex-row"
                          v-for="(log, index) in item.status_logs"
                          :key="index"
                        >

                          <div class="relative">
                            <div
                              class="absolute w-3 h-3 bg-gray-400 rounded-full mt-1.5 -start-0 border border-white"
                            ></div>

                          </div>
                          <div class="ml-4">
                            <div class="inline-flex gap-3">

                            <div>
                              <div
                                class="text-sm font-semibold rounded-full p-1 inline-block"
                                :class="statusClass(splitLog(log).status)"
                              >
                                {{ splitLog(log).status }}
                              </div>
                            </div>
                          </div>
                          <div>
                              <time
                                class="mb-1 text-sm font-normal leading-none text-gray-800"
                                >{{ splitLog(log).date }}</time
                              >
                            </div>
                          <p class="mb-4 text-base font-normal text-gray-800">
                            {{ splitLog(log).message }}
                          </p>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div> -->
            </div>
          </div>
        </div>

        <div class="grid grid-rows-2 gap-4 mb-4">
          <div class="">
            <div class="bg-white rounded-lg border border-gray-200 flex flex-col min-h-[600px] max-h-[600px] overflow-hidden">
              <div class="rounded-t-md bg-gray-100">
                <p class="p-3 text-xl text-gray-800 font-semibold">
                  Comments Details
                </p>
              </div>
              <div class="mb-4 flex-1 flex flex-col min-h-0">
                <div class="divide-x-2"></div>

                <div class="p-0 shadow-none border-none flex-1 flex flex-col min-h-0">
                  <div
                    class="flex-1 overflow-y-auto mb-4 p-1 min-h-0"
                    id="comment_scroll"
                    ref="commentScroll"
                  >
                    <div
                      class="my-2"
                      v-for="(commentList, index) in commentsDetails"
                      :key="index"
                    >
                      <!-- <div v-for="(comment, idx) in commentList" :key="idx">
                        <div :class="comment.commentUser == 'PickNDrop'
                          ? 'pickndrop'
                          : 'others'
                          ">
                          <div class="p-2 rounded-lg text-right">
                            <p class="text-white text-base inline-block" :class="comment.commentUser == 'PickNDrop'
                              ? 'bg-green-500 p-2 rounded-lg'
                              : 'bg-gray-500 p-2 rounded-lg'
                              " v-html="comment.content"></p>
                          </div>
                          <div class="text-right mt-1">
                            <h4 class="text-xs m-0">
                              {{ comment.commentUser }}
                            </h4>
                            <small class="block mb-1">
                              <i class="fa fa-calendar text-xs"></i>
                              {{ comment.date }}
                            </small>
                          </div>
                        </div>
                      </div> -->
                      <div v-for="(comment, idx) in commentList" :key="idx">
                        <div v-if="comment.data == 'Like'">
                          <div class="text-right">
                            <span
                              class="material-symbols-outlined text-green-500"
                            >
                              done_all
                            </span>
                          </div>
                        </div>
                        <div
                          v-else
                          :class="
                            comment.commentUser == 'PickNDrop'
                              ? 'pickndrop'
                              : 'others'
                          "
                        >
                          <div class="p-2 rounded-lg text-right">
                            <p
                              class="text-white text-base inline-block"
                              :class="[
                                comment.commentUser == 'PickNDrop'
                                  ? 'bg-green-500 p-2 rounded-lg'
                                  : 'bg-gray-500 p-2 rounded-lg',
                              ]"
                              v-html="comment.content"
                            ></p>
                          </div>
                          <div class="text-right mt-1">
                            <h4 class="text-xs m-0">
                              {{ comment.commentUser }}
                            </h4>
                            <small class="block mb-1">
                              <i class="fa fa-calendar text-xs"></i>
                              {{ comment.date }}
                            </small>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div
                      class="font-semibold text-gray-800 text-base text-center mt-2"
                      v-if="commentsDetails.length === 0"
                    >
                      <p>Comments Not Available</p>
                    </div>
                  </div>

                  <div class="rounded p-2">
                    <NewComment
                      @fetchComments="fetchComments"
                      :referenceName="route.params.name"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-white rounded-lg border border-gray-200 flex flex-col h-[600px] overflow-hidden">
            <div class="rounded-t-md bg-gray-100">
              <p class="p-3 text-xl text-gray-800 font-semibold">SMS Logs</p>
            </div>
            <div class="flex-1 overflow-y-auto p-1 min-h-0 space-y-2">
              <div v-if="smsLogs.length">
                <div v-for="(sms, idx) in smsLogs" :key="idx">
                  <div class="p-4 bg-white rounded-lg m-2 shadow-sm">
                    <div class="flex justify-between items-center mb-4">
                      <div class="text-sm text-gray-600 break-words">
                        <span class="font-semibold"></span>
                        {{ formatDateTime(sms.creation) }}
                      </div>
                      <div class="text-sm text-gray-600 break-words">
                        <span class="font-semibold">To:</span> {{ sms.sent_to }}
                      </div>
                    </div>
                    <div class="bg-gray-50 p-3 rounded-lg">
                      <p class="text-base text-gray-800 break-words">
                        <span class="font-semibold">Message:</span>
                        <span class="block mt-1">{{ sms.message }}</span>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div
                class="font-semibold text-gray-800 text-base text-center mt-2"
                v-else
              >
                <p>SMS Not Available</p>
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
import { ref, computed, onMounted, watch, nextTick, h } from 'vue'
import { Popover, Button } from 'frappe-ui'
import { useRoute } from 'vue-router'
import NewComment from '../components/NewComment.vue'
import details from '../data/details'
import QRCode from 'qrcode'
import BreadCrums from '../components/BreadCrums.vue'
import FoundNot from '../components/FoundNot.vue'
import PageLoader from '../components/PageLoader.vue'
import dayjs from 'dayjs'
import { useToast } from 'vue-toastification'
import { ShareNetwork } from 'vue-social-sharing'
import { Rocket } from 'lucide-vue-next'
const item = ref(null)
const toast = useToast()

const statusColorMap = {
  Cancelled: 'bg-[#A11717] text-white',
  'Cancelled in Branch': 'bg-[#A11717] text-white',
  'Sent for Delivery': 'bg-[#66ffff] text-black',
  Delivered: 'bg-[#008000] text-white',
  'Pickup on Process': 'bg-[#b3b3ff] text-black',
  'Failed Attempt': 'bg-[#e79aff] text-black',
  'Failed Attempt & Return to Branch': 'bg-[#ff8746] text-black',
  'Order Created': 'bg-[grey] text-white',
  Received: 'bg-[#00cccc] text-black',
  'Return To Vendor': 'bg-[#FFA500] text-black',
  'Processing in Branch': 'bg-[#65fffd] text-black',
  'Delivered To Vendor': 'bg-[#008000] text-white',
  'Disabled Order': 'bg-[black] text-white',
  'Return Received': 'bg-[rgb(5,131,131)] text-white',
  'Lost Package': 'bg-[darkred] text-white',
  'Exchange Return': 'bg-[#b388ff] text-black',
  'Waiting for Received': 'bg-[#b3e5fc] text-[#0f172a]',
  'Assigned For Pickup': 'bg-[#d1fae5] text-[#065f46]',
  'Waiting To Assigned': 'bg-[#fef3c7] text-[#92400e]',
  'In Transit': 'bg-[#e0f2fe] text-[#0c4a6e]',
  'Received at Branch': 'bg-[#00cccc] text-black',
}

const statusClass = (status) => statusColorMap[status] || 'bg-[#FF4500]'

const showMenu = ref(false)

const urlToShare = ref('')
let isLoading = ref(true)
const detail = ref([])
const route = useRoute()
const name = ref(route.params.name)
const qrCodes = ref([])
let commentsDetails = ref([])
const smsLogs = ref([])

const getDeliveryAmount = (item) => {
  if (
    item.status_after_warehouse === 'Return To Vendor' ||
    item.status_after_warehouse === 'Delivered To Vendor'
  ) {
    return 0
  }
  return item.delivery_amount
}

// const fetchDetail = async () => {
//   try {
//     isLoading.value = true
//     const response = await fetch(
//       `/api/method/ecommerce.api.get_vendor_order_status_comment_details?ordername=${encodeURIComponent(name.value)}`,
//       {
//         method: 'GET',
//       },
//     )
//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`)
//     }
//     const data = await response.json()
//      console.log('detail', data.message.data)
//     item.value = data;
//     if (data.message && data.message.data && Array.isArray(data.message.data)) {
//       detail.value = data.message.data

//       const computedData = data.message.data
//         .filter((item) => item.comments && item.comments.length > 0)
//         .map((item) => {
//           return {
//             comments: item.comments.sort((a, b) => {
//               const dateA = new Date(a.split(': ')[0]);
//               const dateB = new Date(b.split(': ')[0]);
//               return dateA - dateB;
//             }),
//           };
//         });

//       // Ensure to access the value correctly
//       commentsDetails.value = computeComments(computedData)
//       console.log('computedData', computedData)
//       // console.log('commentsDetails', commentsDetails.value)
//     } else {
//       console.error('Invalid data format')
//     }
//   } catch (error) {
//     console.error('Error fetching details:', error)
//   } finally {
//     isLoading.value = false
//   }
// }

const statusReadableNames = {
  Completed: 'Delivered',
  Processing: 'Sent for Delivery',
  Received: 'Received',
  Initiated: 'Pickup on Process',
  Open: 'Order Created',
  Cancelled: 'Cancelled',
  'Cancelled in Branch': 'Cancelled in Branch',
  'Re-Processing': 'Processing in Branch',
  'Failed Attempt': 'Failed Attempt',
  'Failed Attempt & Return to Branch': 'Failed Attempt & Return to Branch',
  'Return To Vendor': 'Return To Vendor',
  'Delivered To Vendor': 'Delivered To Vendor',
  'Lost Package': 'Lost Package',
  'Exchange Return': 'Exchange Return',
  'Waiting for Received': 'Waiting for Received',
  'Assigned For Pickup': 'Assigned For Pickup',
  'Waiting To Assigned': 'Waiting To Assigned',
  'In Transit': 'In Transit',
  'Received at Branch': 'Received at Branch',
}

// case 'Open': return 'Order Created';
//     case 'Initiated': return 'Pickup on Process';
//     case 'Received': return 'Received';
//     case 'Processing': return 'Sent for Delivery';
//     case 'Re-Processing': return 'Processing on Branch';
//     case 'Failed Attempt': return 'Failed Attempt & Return to Branch';
//     case 'Return To Vendor': return 'Return To Vendor';
//     case 'Delivered To Vendor': return 'Delivered To Vendor';
//     case 'Cancelled': return 'Cancelled';
//     case 'Completed': return 'Delivered';
//     default: return status;

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')
const getTrackingLink = (trackingNumber) => {
  const encodedTrackingNumber = encodeURIComponent(trackingNumber || '')
  return `${window.location.origin}/tracking/${encodedTrackingNumber}`
}

////console.log('Frappe_URL', Frappe_URL)
//console.log('token', token)

const fetchDetail = async () => {
  try {
    isLoading.value = true
    const response = await fetch(
      `${Frappe_URL}/api/method/ecommerce.api.get_vendor_order_status_comment_details?ordername=${encodeURIComponent(name.value)}`,
      {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
   //  //console.log('detail', data)
    item.value = data

    if (data.message && data.message.data && Array.isArray(data.message.data)) {
      detail.value = data.message.data

      // Process the status logs for human readability
      detail.value = detail.value.map((orderDetail) => {
        if (orderDetail.status_logs) {
          orderDetail.status_logs = orderDetail.status_logs.map((log) => {
            const [datePart, statusPart] = log.split(': ')
            const readableStatus = statusReadableNames[statusPart] || statusPart
            return `${datePart}: ${readableStatus}`
          })
        }
        return orderDetail
      })

      const computedData = data.message.data
        .filter((item) => item.comments && item.comments.length > 0)
        .map((item) => {
          return {
            comments: item.comments.sort((a, b) => {
              const dateA = new Date(a.split('| ')[0])
              const dateB = new Date(b.split('| ')[0])
              return dateA - dateB
            }),
          }
        })
      // Ensure to access the value correctly
      commentsDetails.value = computeComments(computedData)
     //  //  console.log('computedData', computedData)
     //  //  console.log('commentsDetails', commentsDetails.value)
    }

    if (data.message && data.message.SMS && Array.isArray(data.message.SMS)) {
      smsLogs.value = data.message.SMS
     //  // console.log('smsLogs', smsLogs.value)
    } else {
      // Fallback samples to visualize layout/scrolling when no SMS exists
      const now = dayjs()
      smsLogs.value = Array.from({ length: 5 }).map((_, i) => ({
        creation: now.subtract(i, 'hour').toISOString(),
        sent_to: `98000000${i}${i}`,
        message:
          'Sample SMS preview to check wrapping and scrolling. This text is intentionally long to ensure it wraps across multiple lines without overflowing the container. Track here: https://pnd.bz/tracking/PND-TEST-123',
      }))
    }
  } catch (error) {
    // console.error('Error fetching details:', error)
  } finally {
    isLoading.value = false
  }
}

const formatDateTime = (dateTimeString) => {
  return dayjs(dateTimeString).format('YYYY-MM-DD hh:mm A')
}

const copyLinkToClipboard = () => {
  const itemData = item.value?.message?.data?.[0] // Get the first object from the data array safely
 //  // console.log('Item Data:', itemData); // Log itemData to check if it's valid

  if (itemData) {
    const link = getTrackingLink(itemData.customer_tracking_number)
   //  // console.log('Generated link:', link);

    // Update urlToShare with the generated link
    urlToShare.value = link
   //  // console.log('urlToShare', urlToShare.value)

    // Modern Clipboard API
    if (
      navigator.clipboard &&
      typeof navigator.clipboard.writeText === 'function'
    ) {
      navigator.clipboard
        .writeText(link)
        .then(() => {
          toast.success('Copied to clipboard!')
        })
        .catch((err) => {
          // console.error('Failed to copy using Clipboard API:', err)
          toast.error('Failed to copy link.')
        })
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea')
      textArea.value = link
      document.body.appendChild(textArea)
      textArea.select()
      try {
        const successful = document.execCommand('copy')
        if (successful) {
          toast.success('Copied to clipboard!')
        } else {
          //  console.error('Failed to copy using fallback method')
          toast.error('Failed to copy link.')
        }
      } catch (err) {
        //  console.error('Error with fallback method:', err)
        toast.error('Failed to copy link.')
      } finally {
        document.body.removeChild(textArea)
      }
    }
  } else {
    //console.error('Item data is missing or invalid')
    toast.error('No valid data available to copy.')
  }
}

const togglePopover = () => {
  //copyLinkToClipboard(); // Copy the link to clipboard
  showMenu.value = !showMenu.value // Toggle popover visibility
}

const openShareMenu = () => {
  copyLinkToClipboard() // Copy the link first
  showMenu.value = !showMenu.value // Toggle the visibility of the share menu
}
// const copyLinkToClipboard = () => {
//   const itemData = item.value.message.data[0]; // Get the first object from the data array

//   if (itemData) {
//     const link = `https://pickndropnepal.com/package-track?mobile=${itemData.primary_mobile_no}&order_id=${itemData.order_name}`;
//     console.log('link', link);

//     if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
//       // Modern method
//       navigator.clipboard.writeText(link).then(() => {
//         toast.success('Copied to clipboard!');
//       }).catch(err => {
//         console.error('Failed to copy: ', err);
//       });
//     } else {
//       // Fallback for unsupported browsers
//       const textArea = document.createElement('textarea');
//       textArea.value = link;
//       document.body.appendChild(textArea);
//       textArea.select();
//       try {
//         document.execCommand('copy');
//         toast.success('Copied to clipboard!');
//       } catch (err) {
//         console.error('Failed to copy using fallback method: ', err);
//       }
//       document.body.removeChild(textArea);
//     }
//   } else {
//     console.error('Item data is undefined or empty');
//   }
// };

watch(commentsDetails, () => {
  scrollToBottom()
})

const scrollToBottom = () => {
  nextTick(() => {
    const commentScroll = document.getElementById('comment_scroll')
    if (commentScroll) {
      commentScroll.scrollTop = commentScroll.scrollHeight
    }
  })
}

function formatDate(dateString) {
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString(undefined, options)
}

function computeComments(data) {
  return data.map((item) => {
    return item.comments.map((comment) => {
      try {
        const [date, rest] = comment.split('| ')
       //  // console.log('rest', rest)
        const [content, user, commentUser, commenttype, data] =
          rest.split(' - ')
        if ((!date || !content || !user || !commentUser, !commenttype, !data)) {
          throw new Error('Incomplete comment data')
        }
        return {
          date,
          content: formatCommentContent(content),
          user,
          commentUser,
          data,
        }
      } catch (error) {
        // console.error('Error parsing comment:', comment, error)
        return {
          date: 'N/A',
          content: formatCommentContent(comment),
          user: 'Unknown',
          commentUser: 'Unknown',
        }
      }
    })
  })
}

function formatCommentContent(html) {
  const div = document.createElement('div')
  div.innerHTML = html || ''

  const failedImage = div.querySelector('.failed-img')
  if (failedImage) {
    return div.innerHTML
  }

  return div.textContent || div.innerText || ''
}

const DeliveryCharge = computed(
  () => details.data.data[0].DeliveryChargeLog || {},
)

const splitComment = (comment) => {
  const [dateTime, commentHtmlAndUser] = comment.split(': ')
  const [commentHtml, user] = commentHtmlAndUser.split(' - ')
  const date = new Date(dateTime).toLocaleString()
  return { date, comment: commentHtml, user }
}

const splitLog = (log) => {
  if (!log) {
    // console.error('Log is undefined')
    return { date: '', status: '', message: '' }
  }

  // Split the log string to get date, status, and message
  const [dateTime, statusMessagePart] = log.split(': ')
  const [status, message] = statusMessagePart
    ? statusMessagePart.split(' - ')
    : ['', '']

  // Format date and time
  const dateObj = new Date(dateTime)
  const date = dateObj.toLocaleDateString()
  const time = dateObj.toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  })

  return {
    date: `${date} ${time}`,
    status: statusReadableNames[status] || status, // Map to readable name or use the original
    message: message || '',
  }
}
// const splitLog = (log) => {
//   if (!log) {
//     console.error('Log is undefined')
//     return { date: '', status: '', message: '' }
//   }
//   const [dateTime, rest] = log.split(': ')
//   const [status, message] = rest.split(' - ')
//   const dateObj = new Date(dateTime)
//   const date = dateObj.toLocaleDateString()
//   const time = dateObj.toLocaleTimeString([], {
//     hour: '2-digit',
//     minute: '2-digit',
//   })
//   return { date: `${date} ${time}`, status, message }
// }

// const generateQRCode = async (item, index) => {
//   try {
//     const url = await QRCode.toDataURL(item.order_name)
//     qrCodes.value[index] = url
//   } catch (err) {
//     // console.error(err)
//   }
// }

const generateQRCode = async (item, index) => {
  try {
    // Generate the tracking link
    const link = getTrackingLink(item.customer_tracking_number)

    // Generate the QR code for the link
    const url = await QRCode.toDataURL(link)

    // Store the generated QR code in the qrCodes array
    qrCodes.value[index] = url
  } catch (err) {
    // console.error('Error generating QR code:', err);
  }
}

function hasVisibleDeliveryChargeLog(logs) {
  if (!Array.isArray(logs)) return false
  return logs.some((log) => Number(log?.value) !== 0)
}

onMounted(async () => {
  await fetchDetail()
  detail.value.forEach((item, index) => generateQRCode(item, index))
})

function fetchComments() {
  fetchDetail()
}
</script>
