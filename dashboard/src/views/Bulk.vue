<template>
  <div class="p-2 mt-1 lg:bg-gray-200 min-h-screen">
    <div class="p-3 lg:p-4 border-gray-200 rounded-lg bg-white min-h-screen">
      <div class="rounded-lg">
        <div class="mb-6 flex items-center justify-between gap-4">
          <div>
            <h1 class="text-2xl font-semibold text-slate-900">Bulk Upload Orders</h1>
            <p class="mt-1 text-sm text-slate-500">
              Upload an Excel file and import orders in batch.
            </p>
          </div>
          <router-link to="/order">
            <Button variant="outline">Back</Button>
          </router-link>
        </div>

        <DialogBulkOrder />
      </div>
    </div>
  </div>
</template>

<script setup>
import DialogBulkOrder from '@/components/DialogBulkOrder.vue'
import { Button } from 'frappe-ui'
</script>

<style></style>
