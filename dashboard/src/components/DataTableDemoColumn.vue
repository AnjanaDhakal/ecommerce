<template>
  <DropdownMenu>
    <DropdownMenuTrigger as-child>
      <Button variant="ghost" size="sm" class="h-8 px-2"> Actions </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-40">
      <DropdownMenuCheckboxItem @click="copyId">
        Copy ID
      </DropdownMenuCheckboxItem>
      <DropdownMenuCheckboxItem @click="emitExpand">
        Toggle details
      </DropdownMenuCheckboxItem>
    </DropdownMenuContent>
  </DropdownMenu>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

interface PaymentRow {
  id: string
  amount: number
  status: 'pending' | 'processing' | 'success' | 'failed'
  email: string
}

const props = defineProps<{
  payment: PaymentRow
  onExpand: () => void
}>()

function copyId() {
  if (props.payment?.id) {
    navigator.clipboard?.writeText(props.payment.id)
  }
}

function emitExpand() {
  props.onExpand?.()
}
</script>
