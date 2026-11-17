<template>
  <section class="my-14">
    <Card>
      <CardHeader>
        <CardTitle class="text-2xl">Order Status Summary</CardTitle>
      </CardHeader>

      <CardContent>
        <div v-if="isLoading" class="text-center text-gray-500 py-10">
          Loading order summary...
        </div>

        <div v-else class="h-[400px] w-full">
          <BarChart
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
                :tick-format="(v) => orderStatusData[v]?.status || ''"
                :grid-line="false"
                :tick-line="false"
                tick-text-color="hsl(var(--vis-text-color))"
              />
            </template>
          </BarChart>
        </div>
      </CardContent>
    </Card>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import vendorReport from '@/data/vendorReport'
import { BarChart } from '@/components/ui/chart-bar'
import { DonutChart } from '@/components/ui/chart-donut'

const orderStatusData = ref([])
const isLoading = ref(true)

const fetchReport = async () => {
  try {
    await vendorReport.fetch()
    // console.log('✅ Full vendorReport:', vendorReport.data)

    const charts = vendorReport.data?.data?.charts || []
    // console.log('🧾 Charts array:', charts)

    // 🎯 Find specific charts
    const orderChart = charts.find((c) => c.id === 'order_status_summary')
    const deliveredChart = charts.find(
      (c) => c.id === 'delivered_order_summary',
    )

    // 🟢 Order Status Summary
    if (orderChart?.data) {
      orderStatusData.value = Object.entries(orderChart.data).map(
        ([status, count]) => ({
          status,
          count,
        }),
      )
      // console.log('📊 orderStatusData:', orderStatusData.value)
    } else {
      console.warn('⚠️ No data found for order_status_summary')
    }

    // // 🔵 Delivered Order Summary
    // if (deliveredChart?.data) {
    //   orderDelivery.value = Object.entries(deliveredChart.data).map(([status, count]) => ({
    //     status,
    //     count,
    //   }))
   //  //   console.log("🚚 orderDelivery:", orderDelivery.value)
    // } else {
    //   console.warn("⚠️ No data found for delivered_order_summary")
    // }
  } catch (error) {
    console.error('❌ Failed to fetch report:', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(fetchReport)
</script>
