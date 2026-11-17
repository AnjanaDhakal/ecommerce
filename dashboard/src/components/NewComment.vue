<template>
  <div class="flex w-full items-center gap-2">
    <div class="flex items-center gap-2 w-full border border-gray-300 rounded-md px-3 py-2 bg-white shadow-sm">
      <span class="material-symbols-outlined text-gray-500 text-xl">comment</span>
      <input
        type="text"
        placeholder="write comment here"
        v-model="newCommentData.content"
        class="w-full text-sm border-0 focus:ring-0 focus:outline-none"
        @keydown.enter.prevent="createNewComment"
      />
      <button
        type="button"
        @click="createNewComment"
        class="inline-flex items-center gap-1 bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-md text-sm"
      >
        <span class="material-symbols-outlined text-sm">send</span>
      </button>
    </div>
  </div>
  <div v-if="errorMessage" class="text-red-500 text-sm mt-2">
    {{ errorMessage }}
  </div>
</template>

<script setup>
import { useToast } from 'vue-toastification'
import { ref } from 'vue'
import { TextInput, FormControl } from 'frappe-ui'
import { Button } from 'frappe-ui'
import { useRoute } from 'vue-router'
const toast = useToast()
const props = defineProps({
  referenceName: String,
})

const route = useRoute()
const emit = defineEmits(['fetchComments'])
const newCommentData = ref({
  content: '',
  reference_name: props.referenceName,
})

const errorMessage = ref('')
const newComment = ref('')

const validateForm = () => {
  if (!newCommentData.value.content) {
    errorMessage.value = 'No comment found'
    return false
  }
  errorMessage.value = ''
  return true
}

const Frappe_URL = import.meta.env.VITE_FRAPPE_URL || ''
const token = localStorage.getItem('access_token')

const createNewComment = async () => {
 //  // console.log('New comment:', newCommentData.value)  // Log the correct variable
  if (!validateForm()) {
    return
  }
  const apiUrl = `${Frappe_URL}/api/method/ecommerce.api.create_comments`

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(newCommentData.value),
    })
    const responseData = await response.json()
   //  //console.log(responseData);  // Log the response data

    if (response.ok) {
      toast.success('Comment created successfully')
      emit('fetchComments')

      resetForm()
    } else {
      errorMessage.value = `Error creating issue: ${responseData.message}`
    }
  } catch (error) {
    //console.error('Error creating issue:', error);
    errorMessage.value = `Error creating issue: ${error.message || error}`
  }
}

const resetForm = () => {
  newCommentData.value = {
    content: '',
    reference_name: props.referenceName,
  }
  errorMessage.value = ''
}
</script>
