<template>
  <Dialog :options="dialogOptions" v-model="isDisplay">
    <template #body-content>
      <p>
        Thank you for registering with us! We have sent a message to set a
        password to your email. Please check your inbox. If you have any
        questions, feel free to call us at
        <a href="tel:9801235801" class="text-blue-500 underline">9801235801</a>.
        We look forward to working with you!
      </p>
    </template>
  </Dialog>
</template>
<script setup>
import { ref, defineProps, watch } from 'vue'
import { Dialog } from 'frappe-ui' // Make sure the path is correct

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const close = () => {
  window.location.href = '/login?redirect-to=/dashboard'
}
const dialogOptions = {
  title: 'Welcome to PickNDrop Nepal',
  actions: [
    {
      label: 'OK',
      variant: 'solid',
      onClick: close,
    },
  ],
}
const isDisplay = ref(props.modelValue)

watch(
  () => props.modelValue,
  (newValue) => {
    isDisplay.value = newValue
  },
)

const closeDialog = () => {
  isDisplay.value = false
  //emit('update:modelValue', false);
}
</script>
