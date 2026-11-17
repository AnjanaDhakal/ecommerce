<template>
  <PageLoader v-if="isLoading" />
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen dark:bg-[#222526]">
    <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen dark:bg-[#181A1B]">

      <div class="flex justify-between items-center gap-4">
   <strong class="text-gray-800">Dashboard</strong>
        <div class="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-200">
          <span v-if="lastSync">
            Last synced: {{ dayjs(lastSync).format('YYYY-MM-DD HH:mm') }}
          </span>
          <Button size="sm"  @click="handleRefresh">
            <RefreshCw class="size-4 mr-1" />
          </Button>
        </div>
      </div>

      <!-- first section of Cards -->
      <section class="mt-4 grid grid-cols-2 gap-4 md:grid md:grid-cols-4 md:gap-4">

        <!-- total customers -->
        <Card v-if="totalCustomersCard">
          <CardHeader class="py-3">
            <CardTitle
              class="flex text-[#71717A] font-medium gap-1 text-sm justify-center items-center md:justify-start"
              ><Users class="size-4 text-[#8985F9]" />
              <p class=" dark:text-white">{{ totalCustomersCard.title }}</p>
              </CardTitle
            >
          </CardHeader>
          <CardContent class="text-xl py-0 font-bold text-center md:text-left"
            >{{ totalCustomersCard.value }}</CardContent
          >
          <CardFooter
            class="flex gap-1 py-3 text-[10px] font-medium text-[#71717A] justify-center md:justify-start"
            ><TrendingUp
              v-if="totalCustomersCard.trend?.direction === 'up'"
              class="size-4 text-[#10B981]"
            />
            <span class="text-[#10B981]">{{ totalCustomersCard.trend?.percentage}}</span>
            <span class="dark:text-white">{{ totalCustomersCard.trend?.label}}</span></CardFooter
          >
        </Card>

        <!-- total orders -->
        <Card v-if="totalOrdersCard">
          <CardHeader class="py-3">
            <CardTitle
              class="flex text-[#71717A] font-medium gap-1 text-sm justify-center items-center md:justify-start"
              ><Package
                class="size-4 text-[#EFC04C] text-center md:text-left"
              />{{ totalOrdersCard.title }}
                  </CardTitle
            >
          </CardHeader>
          <CardContent class="text-xl py-0 font-bold text-center md:text-left"
            >{{ totalOrdersCard.value }}</CardContent
          >
          <CardFooter
            class="flex gap-1 py-3 text-[10px] font-medium text-[#71717A] justify-center md:justify-start"
            ><TrendingUp v-if="totalOrdersCard.trend?.direction === 'up'"
            class="size-4 text-[#10B981]" />
            <span class="text-[#10B981]">{{ totalOrdersCard.trend?.percentage }}</span>
            <span>{{ totalOrdersCard.trend?.label }}</span></CardFooter
          >
        </Card>

        <!-- total revenue -->
        <Card v-if="totalRevenueCard">
          <CardHeader class="py-3">
            <CardTitle
              class="flex text-[#71717A] font-medium gap-1 text-sm justify-center items-center md:justify-start"
              ><CircleDollarSign
                class="size-4 text-[#52D496] text-center md:text-left"
              />{{ totalRevenueCard.title }}
                  </CardTitle
            >
          </CardHeader>
          <CardContent class="font-bold text-xl py-0 text-center md:text-left"
            >NPR {{ totalRevenueCard.value }}</CardContent
          >
          <CardFooter
            class="flex gap-1 py-3 text-[10px] font-medium text-[#71717A] justify-center md:justify-start"
            ><TrendingDown class="size-4 text-red-500" />
            <span class="text-red-500">{{ totalRevenueCard.trend?.percentage }}</span>
            <span>{{ totalRevenueCard.trend?.label }}</span></CardFooter
          >
        </Card>

        <!-- total pending -->
        <Card v-if="totalPendingCard">
          <CardHeader class="py-3">
            <CardTitle
              class="flex text-[#71717A] font-medium gap-1 text-sm justify-center items-center md:justify-start"
              ><History class="size-4 text-[#F0987A]" />{{ totalPendingCard.title }}
              </CardTitle
            >
          </CardHeader>
          <CardContent class="font-bold text-xl py-0 text-center md:text-left"
            >NPR {{ totalPendingCard.value }}</CardContent
          >

          <CardFooter
            class="flex gap-1 py-3 text-[10px] font-medium text-[#71717A] justify-center md:justify-start"
            ><Minus class="size-4 text-gray-700" />
            <span class="text-gray-700">{{ totalPendingCard.trend?.percentage }}</span>
            <span>{{ totalPendingCard.trend?.label }}</span></CardFooter
          >
        </Card>
      </section>

      <!-- second section of Cards -->
      <section class="grid grid-cols-1 md:grid-cols-4 md:gap-4 mt-4">


  <!-- order status overview -->
        <div class="col-span-3">
          <Card>
            <CardHeader
              >              <CardTitle class="flex gap-1 items-center">
                <p class="text-xl font-semibold">
                  {{ orderStatusChart?.title }}
                </p>
                <div class="mt-1">
                    <ToolTip
                    tooltipId="order-status-overview"
                    label="Order Status Overview"
                    :text="orderStatusChart?.description"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <div class="overflow-x-auto">
              <div class="min-w-[700px]">
                <CardContent>
                  <BarChart
                    class="h-[300px] md:h-[370px]"
                    :data="orderStatusData"
                    index="status"
                    :categories="['count']"
                    :colors="['#10b981']"
                    :y-formatter="
                      (tick) => {
                        return typeof tick === 'number'
                          ? new Intl.NumberFormat('en-US').format(tick)
                          : ''
                      }
                    "
                    :show-legend="false"
                    :show-grid-line="true"
                    :rounded-corners="5"
                  >
                    <template #default>
                      <VisAxis
                        type="x"
                        :tick-values="orderStatusData.map((_, i) => i)"
                        :tick-format="(v) => {
                          const label = orderStatusData[v]?.status || ''
                          return label.length > 15 ? label.slice(0, 12) + '...' : label
                        }"
                        :grid-line="false"
                        :tick-line="false"
                        tick-text-color="hsl(var(--vis-text-color))"
                        tick-text-angle="-30"
                      />
                    </template>
                  </BarChart>
                </CardContent>
              </div>
            </div>
          </Card>
        </div>

        <!-- delivery statistics -->
        <div class="col-span-1 mt-4 md:mt-0">
          <Card class="pb-4.5" v-if="deliveryStatisticsTable">
            <CardHeader>
              <CardTitle class="flex gap-1 items-center">
                <p class="text-xl font-semibold">
                 {{ deliveryStatisticsTable.title }}
                </p>
                <div class="mt-1">
                   <ToolTip
                    tooltipId="delivery-statistics"
                    label="Delivery Statistics"
                    :text="deliveryStatisticsTable.description"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent class="">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead class="font-bold-">Metric</TableHead>
                    <TableHead class="font-bold text-center">Value</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow v-for="(metric, index) in deliveryStatisticsTable.data || []" :key="metric.id || index">
                    <TableCell class="font-medium">{{ metric.title }}</TableCell>
                    <TableCell class="text-center text-sm">
                      {{ metric.value }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      </section>

      <!-- third section of Cards -->
      <section class="grid grid-cols-1 md:grid-cols-4 md:gap-4 mt-4">
 <!-- today's Delivery Curve -->
        <div class="col-span-3 mr-0">
          <Card class="">
            <CardHeader>
                <CardTitle class="flex gap-1 items-center">
                 <p class="text-xl font-semibold">
                  {{ deliveryCurveChart?.title }}
                 </p>
                <div class="mt-1">
                  <ToolTip
                    tooltipId="todays-delivery-curve"
                    label="Today's Delivery curve"
                    :text="deliveryCurveChart?.description"
                  />
                </div>
              </CardTitle>
            </CardHeader class=px-0>
            <div class="overflow-x-auto">
              <div class="min-w-[700px]">
                <CardContent>
                  <div class="">
                    <div class="relative">
                      <AreaChart
                        v-if="deliveryCurveData?.length"
                        :data="deliveryCurveData"
                        index="time"
                        :categories="deliveryCurveCategories"
                        :colors="['#3b82f6', '#10b981']"
                        :show-tooltip="true"
                        :show-legend="true"
                        :show-grid-line="true"
                        :show-x-axis="true"
                        :show-y-axis="true"
                        :show-points="true"
                        :point-size="6"
                        :y-formatter="
                          (tick) => {
                            return typeof tick === 'number'
                              ? new Intl.NumberFormat('en-US').format(tick)
                              : ''
                          }
                        "
                        :x-formatter="
                          (tick) => {
                            return typeof tick === 'number'
                              ? deliveryCurveData[tick]?.time || ''
                              : ''
                          }
                        "
                        :margin="{ left: 60, right: 20, top: 20, bottom: 60 }"
                        class="h-[300px] mb-5 md:h-full md:mb-0"
                      >
                        <template #default>
                          <VisAxis
                            type="x"
                            :tick-format="(v) => deliveryCurveData[v]?.time || ''"
                            :grid-line="false"
                            :tick-line="false"
                            tick-text-color="hsl(var(--vis-text-color))"
                          />
                        </template>
                      </AreaChart>
                      <div
                        v-else
                        class="flex h-[300px] items-center justify-center rounded-md border border-dashed border-gray-200 bg-white text-sm text-gray-500 dark:border-gray-700 dark:bg-[#181A1B] dark:text-gray-300"
                      >
                        No data available
                      </div>
                    </div>
                  </div>
                </CardContent>
              </div>
            </div>
          </Card>
        </div>


        <div class="col-span-1 grid grid-cols-1 gap-4 mt-4 md:mt-0">
          <!-- top 5 destinations -->
          <Card v-if="topDestinationsTable">
            <CardHeader class="pb-0">
               <CardTitle class="flex gap-1 items-center">
                <p class="text-xl font-semibold">
                 {{ topDestinationsTable.title }}
                </p>
                <div class="mt-">
                  <ToolTip
                    tooltipId="top-5-destinations"
                    label="Top 5 Destinations"
                    :text="topDestinationsTable.description"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent class="px-1">
              <div class="min-h-[220px]">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead class="font-bold-">#</TableHead>
                      <TableHead class="font-bold-">Destinations</TableHead>
                      <TableHead class="font-bold- text-center">Orders</TableHead>
                      <TableHead class="font-bold- text-center"
                        >Avg Delivery Hours</TableHead
                      >
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <template v-if="topDestinationsTable?.data?.length">
                      <TableRow
                        v-for="(destination, index) in topDestinationsTable.data || []"
                        :key="destination.id || index"
                      >
                        <TableCell class="font-medium">{{ index + 1 }}</TableCell>
                        <TableCell class="font-medium">{{ destination.name }}</TableCell>
                        <TableCell class="text-center text-sm">
                          {{ destination.orders }}
                        </TableCell>
                        <TableCell class="text-center text-sm">
                          {{ destination.avgDeliveryHours }}
                        </TableCell>
                      </TableRow>
                    </template>
                    <TableRow v-else>
                      <TableCell
                        colspan="4"
                        class="text-center text-sm text-gray-500 dark:text-gray-300"
                      >
                        <div class="flex h-[180px] items-center justify-center">
                          No data available
                        </div>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <!-- fourth section of Cards -->
      <section class="grid grid-cols-1 md:grid-cols-4 md:gap-4 mt-4">

        <!-- orders: inside vs outside valley -->
        <div class="col-span-1">
          <Card>
            <CardHeader class="pb-0.5">              <CardTitle class="">
                <p class="text-xl font-semibold">
                {{ ordersValleyChart?.title }}
                 <span class="inline-block align-top mt-0.5">
                  <ToolTip
                    tooltipId="orders-inside-vs-outside-valley"
                    label="Orders: Inside vs Outside Valley"
                    :text="ordersValleyChart?.description"
                  />
                 </span>
                </p>
              </CardTitle>
            </CardHeader>
            <CardContent class="py-6">
              <DonutChart
                v-if="donutData?.length"
                index="name"
                :category="'orders'"
                :data="donutData"
                :colors="['#059669', '#6ee7b7']"
                :show-tooltip="true"
                :value-formatter="valueFormatter"
                class=""
              />
              <div
                v-else
                class="flex h-[260px] items-center justify-center rounded-md border border-dashed border-gray-200 bg-white text-sm text-gray-500 dark:border-gray-700 dark:bg-[#181A1B] dark:text-gray-300"
              >
                No data available
              </div>
            </CardContent>
            <CardContent class="py-5">
              <div class="space-y-2">
                <template v-if="donutData?.length">
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
                            'bg-[#6ee7b7]': index === 1,
                          },
                        ]"
                      ></span>
                      <span class="text-[12px]">{{ category.name }}</span>
                    </div>
                    <span class="text-[12px] font-semibold">
                      {{ category.displayLabel || `${category.orders}%` }}
                    </span>
                  </div>
                </template>
                <div
                  v-else
                  class="text-center text-sm text-gray-500 dark:text-gray-300"
                >
                  No data available
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- peak order hours -->
        <div class="col-span-2 mt-4 md:mt-0">
          <Card>
            <CardHeader>
              <CardTitle class="flex gap-1 items-center">
                <p class="text-xl font-semibold">{{ peakOrderHoursChart?.title }}</p>
                <div class="mt-1">
                  <ToolTip
                      tooltipId="peak-order-hours"
                      label="Peak Order Hours"
                      :text="peakOrderHoursChart?.description"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <div class="overflow-x-auto">
              <div class="min-w-[500px]">
                <CardContent>
                  <div class="">
                    <BarChart
                      class="h-[300px]"
                      :data="peakHoursData"
                      index="timeSlot"
                      :categories="['orders']"
                      :colors="['#10b981']"
                      :y-formatter="
                        (tick) => {
                          return typeof tick === 'number'
                            ? new Intl.NumberFormat('en-US').format(tick)
                            : ''
                        }
                      "
                      :show-legend="false"
                      :show-grid-line="true"
                      :rounded-corners="5"
                    >
                      <template #default>
                        <VisAxis
                          type="x"
                          :tick-values="peakHoursData.map((_, i) => i)"
                          :tick-format="(v) => peakHoursData[v]?.timeSlot || ''"
                          :grid-line="false"
                          :tick-line="false"
                          tick-text-color="hsl(var(--vis-text-color))"
                        />
                      </template>
                    </BarChart>
                  </div>
                </CardContent>
              </div>
            </div>
          </Card>
        </div>

        <!-- return to origin reasons -->
        <div class="col-span-1 mt-4 md:mt-0">
          <Card>
            <CardHeader class="pb-0">
              <CardTitle class="flex gap-1 items-center">
                <p class="text-xl font-semibold">
                  {{ rtoReasonsChart?.title }}
                </p>
                <div class="mt-1">
                  <ToolTip
                      tooltipId="return-to-origin-reasons"
                      label="Return To Origin Reasons"
                      :text="rtoReasonsChart?.description"
                  />
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent class="pt-6">
              <!-- :colors="['#059669', '#3b82f6', '#f59e0b', '#ef4444']" -->
              <DonutChart
                v-if="rtoReasonsData?.length"
                :data="rtoReasonsData"
                index="reason"
                :category="'count'"
                :colors="['#059669', '#10b981', '#34d399', '#6ee7b7', '#0ea5e9']"
                :show-tooltip="true"
                :value-formatter="rtoValueFormatter"
                :type="'pie'"
                class=" "
              />
              <div
                v-else
                class="flex h-[300px] items-center justify-center rounded-md border border-dashed border-gray-200 bg-white text-sm text-gray-500 dark:border-gray-700 dark:bg-[#181A1B] dark:text-gray-300"
              >
                No data available
              </div>
            </CardContent>
            <CardContent class="pb-3">
              <div class="mx-auto w-full max-w-md">
                <div
                  class="relative max-h-[95px] overflow-y-auto pr-1 space-y-3"
                >
                  <div class="mt- space-y-2">
                    <div
                      v-if="rtoReasonsData?.length"
                      v-for="(item, index) in rtoReasonsData"
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
                            'bg-[#0ea5e9]': index === 4,
                          },
                        ]"
                      ></span>
                        <span class="text-[12px]">{{ item.reason }}</span>
                      </div>
                      <span class="text-[12px] font-semibold">
                        {{ new Intl.NumberFormat('en-US').format(item.count) }}
                      </span>
                    </div>

                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <!-- fifth section of Cards -->
      <section class="grid grid-cols-1 md:grid-cols-2 md:gap-4 mt-4">

        <!-- delivered order trend -->
        <div>
          <Card>
            <CardHeader>
              <CardTitle class="flex justify-between">

                  <p class="text-xl font-semibold break-words ">
                    {{ deliveredOrderChart?.title }}
                    <span class="inline-block align-top mt-0.5">
                    <ToolTip
                      tooltipId="delivered-order-trend"
                      label="Delivered Order Trend"
                      :text="deliveredOrderChart?.description"
                  />
                 </span>
                  </p>
                <!-- <Select>
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
                </Select> -->
              </CardTitle>
            </CardHeader>
            <div class="overflow-x-auto">
              <div class="min-w-[700px] md:min-w-[500px]">
                <CardContent>
                  <LineChart
                    class="h-[300px] md:h-[400px]"
                    :data="deliveredOrderData"
                    index="date"
                    :categories="['delivered_orders','day']"
                    :colors="['#3b82f6']"
                    :x-formatter="
                      (v) =>
                        typeof v === 'number'
                          ? deliveredOrderData[v]?.day || ''
                          : ''
                    "
                    :y-formatter="
                      (tick) => {
                        return typeof tick === 'number'
                          ? new Intl.NumberFormat('en-US').format(tick)
                          : ''
                      }
                    "
                    :show-legend="false"
                    :show-grid-line="true"
                    :show-points="true"
                    :point-size="6"
                  >
                    <template #default>
                      <VisAxis
                        type="x"
                        :tick-values="deliveredOrderData.map((_, i) => i)"
                        :tick-format="(v) => deliveredOrderData[v]?.day || ''"
                        :grid-line="false"
                        :tick-line="false"
                        tick-text-color="hsl(var(--vis-text-color))"
                      />
                    </template>
                  </LineChart>
                </CardContent>
              </div>
            </div>
          </Card>
        </div>

        <!-- revenue trend -->
        <div class="mt-4 md:mt-0">
          <Card>
            <CardHeader class="">
              <CardTitle class="flex justify-between">
                <div class="flex gap-1 items-center">
                  <p class="text-xl font-semibold">{{ revenueTrendChart?.title }}</p>
                  <div class="">
                     <ToolTip
                        tooltipId="revenue-trend"
                        label="Revenue Trend"
                        :text="revenueTrendChart?.description"
                  />
                  </div>
                </div>
                <!-- <Select class="">
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
                </Select> -->
              </CardTitle>
            </CardHeader>
            <div class="overflow-x-auto">
              <div class="min-w-[700px] md:min-w-[500px]">
                <CardContent class="">
                  <div class="w-full">
                    <AreaChart
                      class="h-[300px] md:h-[400px]"
                      :data="revenueData"
                      index="month"
                      :categories="['revenue']"
                      :colors="['#10b981']"
                      :show-tooltip="true"
                      :show-legend="false"
                      :show-grid-line="true"
                      :show-x-axis="true"
                      :show-y-axis="true"
                      :show-points="true"
                      :point-size="6"
                      :y-formatter="
                        (tick) => {
                          return typeof tick === 'number'
                            ? new Intl.NumberFormat('en-US').format(tick)
                            : ''
                        }
                      "
                      :x-formatter="
                        (tick) => {
                          return typeof tick === 'number'
                            ? revenueData[tick]?.month || ''
                            : ''
                        }
                      "
                      :margin="{ left: 60, right: 20, top: 20, bottom: 40 }"
                    >
                      <template #default>
                        <VisAxis
                          type="x"
                          :tick-values="[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]"
                          :tick-format="(v) => revenueData[v]?.month || ''"
                          :grid-line="false"
                          :tick-line="false"
                          tick-text-color="hsl(var(--vis-text-color))"
                        />
                      </template>
                    </AreaChart>
                  </div>
                </CardContent>
              </div>
            </div>
          </Card>
        </div>
      </section>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import dayjs from 'dayjs'
import PageLoader from '@/components/PageLoader.vue'
import dashboardReport from '@/data/dashboard'
import { LineChart } from '@/components/ui/chart-line'
import { AreaChart } from '@/components/ui/chart-area'
import { VisAxis } from '@unovis/vue'
import { BarChart } from '@/components/ui/chart-bar'
import { DonutChart } from '@/components/ui/chart-donut'
import ToolTip from '@/components/ToolTip.vue'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'

import {
  Users,
  TrendingUp,
  Package,
  CircleDollarSign,
  TrendingDown,
  History,
  Minus,
  RefreshCw,
} from 'lucide-vue-next'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

// Data refs
const numberCards = ref([])
const listCards = ref([])
const tables = ref([])
const charts = ref<any[]>([])

// Chart data refs - storing processed data for each chart
const orderStatusData = ref([])
const deliveredOrderData = ref([])
const deliveryCurveData = ref([])
const deliveryCurveCategories = computed(() => {
  if (!deliveryCurveData.value?.length) return ['Delivered']
  return Object.keys(deliveryCurveData.value[0]).filter((key) => key !== 'time')
})
const donutData = ref([])
const peakHoursData = ref([])
const rtoReasonsData = ref([])
const revenueData = ref([])

const isLoading = ref(true)
const lastSync = ref<string | null>(null)

// Helper function to extract API data consistently
const extractApiData = (response: any) => {
  if (response?.message?.data) {
    return response.message.data
  }

  if (response?.data) {
    return response.data
  }

  if (response) {
    return response
  }
  return {}
}

const DASHBOARD_CACHE_KEY = 'dashboard_report_cache'

const loadDashboardCache = () => {
  try {
    const raw = localStorage.getItem(DASHBOARD_CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    const apiData = extractApiData(parsed)
    if (!apiData?.charts || apiData.charts.length === 0) return null
    return parsed
  } catch (e) {
    return null
  }
}

const saveDashboardCache = (data: any) => {
  try {
    const apiData = extractApiData(data)
    if (!apiData?.charts || apiData.charts.length === 0) return
    localStorage.setItem(DASHBOARD_CACHE_KEY, JSON.stringify(data))
  } catch (e) {
    // ignore storage errors
  }
}

// Helper function to parse chart data consistently
const parseChartData = (chart: any) => {
  if (!chart || !chart.data) {
    return null
  }

  const chartId = chart.id

  switch (chartId) {
    case 'order_status_summary':
      // Convert object to array format
      if (typeof chart.data === 'object' && !Array.isArray(chart.data)) {
        return Object.entries(chart.data).map(([status, count]) => ({
          status,
          count,
        }))
      }
      return chart.data

    case 'delivered_order_summary':
    case 'delivery_curve':
    case 'revenue_trend':
    case 'peak_order_hours':
    case 'orders_valley_comparison':
    case 'rto_reasons':
      // These charts already have array data
      return Array.isArray(chart.data) ? chart.data : []

    default:
      return chart.data
  }
}

const updateLastSync = (response: any) => {
  lastSync.value =
    response?.message?.last_sync ||
    response?.last_sync ||
    null
}

const applyDashboardData = (sourceData: any) => {
  if (!sourceData) return

  updateLastSync(sourceData)

  const apiData = extractApiData(sourceData)

  numberCards.value = apiData.cards?.number_cards || []
  listCards.value = apiData.cards?.list_cards || []
  tables.value = apiData.tables ? Object.values(apiData.tables) : []

  const chartsData = apiData.charts || []
  charts.value = chartsData

  const chartMap: Record<string, any> = {}
  chartsData.forEach((chart: any) => {
    if (chart?.id) {
      chartMap[chart.id] = chart
    }
  })

  const orderChart = chartMap['order_status_summary']
  if (orderChart) {
    const parsedData = parseChartData(orderChart)
    if (parsedData) {
      orderStatusData.value = parsedData
    }
  }

  const deliveredChart = chartMap['delivered_order_summary']
  if (deliveredChart) {
    const parsedData = parseChartData(deliveredChart)
    if (parsedData) {
      deliveredOrderData.value = parsedData
    }
  }

  const deliveryCurveChart = chartMap['delivery_curve']
  if (deliveryCurveChart) {
    const parsedData = parseChartData(deliveryCurveChart)
    if (parsedData) {
      deliveryCurveData.value = parsedData
    }
  }

  const ordersValleyChart = chartMap['orders_valley_comparison']
  if (ordersValleyChart) {
    const parsedData = parseChartData(ordersValleyChart)
    if (parsedData) {
      donutData.value = parsedData.map((item: any) => {
        const numeric = Number(item.orders ?? 0)
        const display =
          typeof item.display === 'string' ? item.display : `${numeric}%`
        return {
          ...item,
          orders: numeric,
          displayLabel: display,
        }
      })
    }
  }

  const peakOrderHoursChart = chartMap['peak_order_hours']
  if (peakOrderHoursChart) {
    const parsedData = parseChartData(peakOrderHoursChart)
    if (parsedData) {
      peakHoursData.value = parsedData
    }
  }

  const rtoReasonsChart = chartMap['rto_reasons']
  if (rtoReasonsChart) {
    const parsedData = parseChartData(rtoReasonsChart)
    if (parsedData) {
      rtoReasonsData.value = parsedData
    }
  }

  const revenueTrendChart = chartMap['revenue_trend']
  if (revenueTrendChart) {
    const parsedData = parseChartData(revenueTrendChart)
    if (parsedData) {
      revenueData.value = parsedData
    }
  }
}

const fetchReport = async (force = false) => {
  try {
    const cached = loadDashboardCache()
    const hasCache = Boolean(cached)
    if (hasCache) {
      applyDashboardData(cached)
      // show cached view immediately without blocking on network
      isLoading.value = false
    } else {
      isLoading.value = true
    }

    await dashboardReport.fetch({ force })

    applyDashboardData(dashboardReport.data)
    saveDashboardCache(dashboardReport.data)
  } catch (error) {
    console.error('Failed to fetch dashboard report:', error)
  } finally {
    isLoading.value = false
  }
}

// Computed properties for consistent chart access by ID
const getChartById = (id: string) => {
  return computed(() => charts.value.find((chart: any) => chart.id === id) || null)
}

// Chart computed properties for template access
const orderStatusChart = getChartById('order_status_summary')
const deliveredOrderChart = getChartById('delivered_order_summary')
const deliveryCurveChart = getChartById('delivery_curve')
const revenueTrendChart = getChartById('revenue_trend')
const peakOrderHoursChart = getChartById('peak_order_hours')
const ordersValleyChart = getChartById('orders_valley_comparison')
const rtoReasonsChart = getChartById('rto_reasons')

// Number card computed properties for consistent access
const getNumberCardById = (id: string) => {
  return computed(() => numberCards.value.find((card: any) => card.id === id) || null)
}

const totalCustomersCard = getNumberCardById('total_customers')
const totalOrdersCard = getNumberCardById('total_orders')
const totalRevenueCard = getNumberCardById('total_balance_receivable')
const totalPendingCard = getNumberCardById('total_pending')

// List card computed properties for consistent access
const codSummaryCard = computed(() =>
  listCards.value.find((card: any) => card.id === 'cod_summary') || null
)

// Table computed properties for consistent access
const getTableById = (id: string) => {
  return computed(() => tables.value.find((table: any) => table.id === id) || null)
}

const deliveryStatisticsTable = getTableById('delivery_statistics')
const topDestinationsTable = getTableById('top_destinations')

onMounted(() => {
  fetchReport()
})

const handleRefresh = () => {
  isLoading.value = true
  fetchReport(true)
}

const valueFormatter = (tick: number | Date) =>
  typeof tick === 'number'
    ? `${new Intl.NumberFormat('us').format(tick).toString()}`
    : ''

const rtoValueFormatter = (tick: number | Date, i?: number) => {
  if (typeof tick === 'number') {
    // Find the reason for this count
    const item = rtoReasonsData.value.find((d) => d.count === tick)
    return item ? `${tick} - ${item.reason}` : tick.toString()
  }
  return ''
}
</script>
