<script setup>
import { computed } from 'vue'
import {
  Table,
  TableBody,
  TableCell,
  TableEmpty,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

const props = defineProps({
  columns: {
    type: Array,
    default: () => [],
  },
  rows: {
    type: Array,
    default: () => [],
  },
  rowKey: {
    type: String,
    default: 'id',
  },
  loading: {
    type: Boolean,
    default: false,
  },
  emptyText: {
    type: String,
    default: 'No records found',
  },
  tableClass: {
    type: String,
    default: '',
  },
  wrapperClass: {
    type: String,
    default: '',
  },
  stickyHeader: {
    type: Boolean,
    default: true,
  },
  stackOnMobile: {
    type: Boolean,
    default: true,
  },
})

const visibleDesktopColumns = computed(() =>
  props.columns.filter((column) => column?.mobileOnly !== true),
)

const visibleMobileColumns = computed(() =>
  props.columns.filter((column) => column?.mobileOnly === true),
)

const getRowKey = (row, index) => row?.[props.rowKey] ?? row?.name ?? index
</script>

<template>
  <div class="space-y-3">
    <slot name="toolbar" />

    <div :class="['overflow-hidden rounded-xl border border-gray-200 bg-white ', wrapperClass]">
      <div v-if="loading" class="flex items-center justify-center px-4 py-10 text-sm text-gray-500">
        <slot name="loading">Loading...</slot>
      </div>

      <template v-else>
        <div
          :class="stackOnMobile ? 'hidden sm:block' : 'block overflow-x-auto'"
        >
          <Table :class="tableClass">
            <TableHeader :class="stickyHeader ? 'sticky top-0 z-10 bg-gray-50' : 'bg-gray-50'">
              <TableRow class="border-b border-gray-200 hover:bg-gray-50">
                <TableHead
                  v-for="column in visibleDesktopColumns"
                  :key="column.key"
                  :class="[
                    'bg-gray-50 px-6 py-3 text-xs font-semibold uppercase tracking-wider text-gray-700',
                    column.headerClass,
                  ]"
                >
                  {{ column.label }}
                </TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              <template v-if="rows.length">
                <TableRow
                  v-for="(row, index) in rows"
                  :key="getRowKey(row, index)"
                  class="border-b border-gray-200 align-top hover:bg-[#f8faf9]"
                >
                  <TableCell
                    v-for="column in visibleDesktopColumns"
                    :key="column.key"
                    :class="['px-6 py-4 text-xs text-gray-700', column.cellClass]"
                  >
                    <slot
                      :name="`cell-${column.key}`"
                      :row="row"
                      :value="row[column.key]"
                      :column="column"
                      :index="index"
                    >
                      {{ row[column.key] }}
                    </slot>
                  </TableCell>
                </TableRow>
              </template>

              <TableEmpty v-else :colspan="visibleDesktopColumns.length">
                {{ emptyText }}
              </TableEmpty>
            </TableBody>
          </Table>
        </div>

        <div v-if="stackOnMobile" class="sm:hidden">
          <div v-if="rows.length" class="divide-y divide-gray-200">
            <div
              v-for="(row, index) in rows"
              :key="getRowKey(row, index)"
              class="px-4 py-3"
            >
              <slot name="mobile-row" :row="row" :index="index">
                <div class="space-y-2">
                  <div
                    v-for="column in visibleMobileColumns.length ? visibleMobileColumns : visibleDesktopColumns"
                    :key="column.key"
                    class="space-y-1"
                  >
                    <p class="text-[11px] font-medium uppercase tracking-wide text-gray-400">
                      {{ column.label }}
                    </p>
                    <div class="text-sm text-gray-700">
                      <slot
                        :name="`mobile-cell-${column.key}`"
                        :row="row"
                        :value="row[column.key]"
                        :column="column"
                        :index="index"
                      >
                        {{ row[column.key] }}
                      </slot>
                    </div>
                  </div>
                </div>
              </slot>
            </div>
          </div>

          <div v-else class="px-4 py-10 text-center text-sm text-gray-500">
            {{ emptyText }}
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
