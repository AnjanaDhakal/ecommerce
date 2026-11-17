<template>
  <Dialog
    :options="{
      title: 'Confirm Cancel',
      message: `Are you sure you want to cancel ${props.selectname} order?`,
      size: 'xl',
      actions: [
        {
          label: 'Confirm',
          variant: 'solid',
          onClick: (close) => {
            cancelOrder()
            close()
          },
        },
      ],
    }"
  />
</template>

<script setup>
import { Dialog } from 'frappe-ui'
import { useToast } from 'vue-toastification'
const props = defineProps({
  selectname: {
    type: String,
    required: true,
  },
})
const toast = useToast()

const emit = defineEmits(['OrderCancelled'])

const cancelOrder = async () => {
  const apiUrl = '/api/method/ecommerce.api.cancel_order'
  const orderData = {
    orderID: props.selectname,
  }
  try {
    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
    })
    const data = await response.json()

    if (response.ok) {
      emit('OrderCancelled')
      toast.success('Order Cancelled successfully')
     //  //console.log("Order cancelled successfully", data);
    } else {
      toast.error(data?.message || 'Order cancellation failed')
    }
  } catch (error) {
    toast.error(error?.message || 'Order cancellation failed')
  }
}
</script>
