<template>
  <Dialog :options="dialogOptions" v-model="displayDialog.isDisplay">
    <template #body-content>
     <div class="p-2 space-y-4">
        <div class="text-sm">
          Full Name
          <label class="text-red-600">*</label>
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            placeholder="full name"
            :disabled="false"
            v-model="newData.user_name"
            @blur="newData.user_name = newData.user_name.trim()"
          />
        </div>
        <div class="text-sm">
          Email
          <label class="text-red-600">*</label>
          <FormControl
            type="text"
            size="sm"
            variant="subtle"

             :disabled="Boolean(props.editData?.name)"
            v-model="newData.email"
            @blur="newData.email = newData.email.trim()"
          />
        </div>

        <div class="text-sm">
          Mobile Number
          <label class="text-red-600">*</label>
          <FormControl
            type="text"
            size="sm"
            variant="subtle"
            placeholder="mobile number"
            :disabled="Boolean(props.editData?.name)"
            v-model="newData.phone"
            pattern="\d*"
            maxlength="10"
            @blur="newData.phone = newData.phone.trim()"
          />
        </div>
        <div class="text-sm">
          Role
          <label class="text-red-600">*</label>
          <Select v-model="newData.role">
            <SelectTrigger class="mt-1 h-8 border-0 bg-gray-100 shadow-none focus:ring-1">
              <SelectValue placeholder="Select role" />
            </SelectTrigger>
            <SelectContent
              side="bottom"
              align="start"
              :side-offset="6"
              class="z-[9999] border-gray-200 bg-white text-gray-900 opacity-100 shadow-xl"
              style="z-index: 9999; background-color: #ffffff; opacity: 1"
            >
              <SelectItem value="Admin">Admin</SelectItem>
              <SelectItem value="Accountant">Accountant</SelectItem>
              <SelectItem value="User">User</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useToast } from 'vue-toastification'
import { displayDialog } from '../composables/displayDialog'
import { FormControl, Dialog } from 'frappe-ui'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const toast = useToast()
const props = defineProps({
  editData: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['userCreated'])

const newData = ref({
  name: '',
  user_name: '',
  phone: '',
  role: 'User',
  email: '',
})
const errorMessage = ref('')

const validateForm = () => {
  if (!newData.value) {
    errorMessage.value = 'Please provide info.'
    return
  }
  errorMessage.value = ''
  return true
}

const submitUser = async () => {
  if (!validateForm()) {
    return
  }
  const isEdit = Boolean(props.editData?.name)
  const apiUrl = isEdit
    ? '/api/method/ecommerce.api.update_vendor_employee'
    : '/api/method/ecommerce.api.create_vendor_employee'
  const payload = {
    ...newData.value,
    disable: false,
  }

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    })
    const responseData = await response.json()

    if (responseData?.message?.status === 'success') {
      toast.success(isEdit ? 'User updated successfully' : 'User created successfully')
      emit('userCreated')
      displayDialog.isDisplay = false
      resetForm()
    } else {
      const msg =
        responseData?.message?.message ||
        responseData?.message ||
        'Error creating user'
      errorMessage.value = msg
      toast.error(msg)
    }
  } catch (error) {
      const msg = `Error saving user: ${error.message || error}`
      errorMessage.value = msg
      toast.error(msg)
  }
}

const resetForm = () => {
  newData.value = {
    name: '',
    user_name: '',
    phone: '',
    role: 'User',
    email: '',
  }
  errorMessage.value = ''
}

watch(
  () => props.editData,
  (value) => {
    if (value) {
      newData.value = {
        name: value.name || '',
        user_name: value.user_name || '',
        phone: value.employee_phone || value.phone || '',
        role: value.role || 'User',
        email: value.email || '',
      }
      return
    }

    resetForm()
  },
  { immediate: true },
)

const dialogOptions = ref({})

watch(
  () => props.editData,
  (value) => {
    const isEdit = Boolean(value?.name)
    dialogOptions.value = {
      title: isEdit ? 'Edit User' : 'Add User',
      description: isEdit ? 'Update user details' : 'Add a new user',
      size: 'xl',
      actions: [
        {
          label: 'Confirm',
          variant: 'solid',
          onClick: submitUser,
        },
      ],
    }
  },
  { immediate: true },
)
</script>
