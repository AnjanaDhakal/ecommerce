<template>
  <div :class="embedded ? '' : 'p-4 lg:bg-gray-200 min-h-screen'">
    <div :class="embedded ? 'bg-white rounded-lg border border-gray-200 p-4 sm:p-5' : 'p-3 lg:p-4 rounded-lg bg-white min-h-screen'">
      <div class="flex justify-between items-center mb-4">
        <div class="text-lg font-pregular font-bold">Business Information</div>
        <Button
          :variant="'solid'"
          theme="gray"
          size="sm"
          :disabled="false"
          @click="register"
        >
          Submit
        </Button>
      </div>

      <div class="my-3">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <FormControl
            v-model="formData.store_name"
            label="Store Name"
            type="text"
            size="sm"
            variant="subtle"
            :disabled="true"
          />
          <FormControl
            v-model="formData.contact_person"
            label="Contact Person"
            type="text"
            size="sm"
            variant="subtle"
            :disabled="true"
          />
          <FormControl
            v-model="formData.email"
            label="Primary Email"
            type="text"
            size="sm"
            variant="subtle"
            :disabled="true"
          />
          <FormControl
            v-model="formData.primaryPhone"
            label="Primary Phone"
            type="tel"
            size="sm"
            variant="subtle"
            :disabled="true"
          />
          <div>
            <label class="text-sm font-base text-gray-500">City</label>
            <FormControl
              v-model="formData.city"
              type="text"
              size="sm"
              variant="subtle"
              placeholder="Enter city"
              :disabled="true"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <FormControl
            v-model="formData.panNumber"
            label="PAN No/VAT No"
            type="text"
            size="sm"
            variant="subtle"
            placeholder="Enter PAN No"
            :disabled="false"
          />
          <FormControl
            v-model="formData.secondaryPhone"
            label="Secondary Phone"
            type="tel"
            size="sm"
            variant="subtle"
            placeholder="Enter phone number"
            :disabled="false"
          />
          <FormControl
            v-model="formData.secondaryEmail"
            label="Secondary Email"
            type="email"
            size="sm"
            variant="subtle"
            placeholder="Enter email"
            :disabled="false"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <FormControl
            v-model="formData.website"
            label="Website"
            type="url"
            size="sm"
            variant="subtle"
            placeholder="Enter website URL"
            :disabled="false"
          />
          <FormControl
            v-model="formData.facebookLinks"
            label="Facebook"
            type="url"
            size="sm"
            variant="subtle"
            placeholder="Enter Facebook URL"
            :disabled="false"
          />
          <FormControl
            v-model="formData.instagramLinks"
            label="Instagram"
            type="url"
            size="sm"
            variant="subtle"
            placeholder="Enter Instagram URL"
            :disabled="false"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div>
            <label class="text-sm font-base text-gray-500">Citizenship</label>

            <!-- Show image only if it's NOT the sample citizenship image -->
            <div
              v-if="
                formData.uploadCitizenship &&
                formData.uploadCitizenship !==
                  'https://pickndropnepal.com/files/sample_citizenship.jpg'
              "
            >
              <img
                class="h-40 w-full max-w-[260px] rounded-sm object-contain"
                :src="formData.uploadCitizenship"
                @error="setDefaultImage"
                alt="Citizenship"
              />
            </div>

            <!-- Show uploader only if the citizenship is the sample one -->
            <FileUploader
              v-if="
                formData.uploadCitizenship ===
                'https://pickndropnepal.com/files/sample_citizenship.jpg'
              "
              v-model="formData.uploadCitizenship"
              :fileTypes="['image/*']"
              @input="handleFileUpload"
            >
              <template #default="{ openFileSelector, progress, uploading }">
                <Button @click="openFileSelector" :loading="uploading">
                  {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
                </Button>
              </template>
            </FileUploader>
          </div>

          <div>
            <label class="text-sm font-base text-gray-500">PAN Image</label>
            <div v-if="formData.uploadPanImage">
              <!-- Show the image if it exists -->
              <img
                class="h-40 w-full max-w-[260px] rounded-sm object-contain"
                :src="formData.uploadPanImage"
                @error="setDefaultImage"
                alt="Pan Image"
              />
            </div>
            <div v-else>
              <!-- Show the upload button if the image does not exist -->
              <FileUploader
                v-model="formData.uploadPanImage"
                :fileTypes="['image/*']"
                @input="handleFileUpload2"
              >
                <template #default="{ openFileSelector, progress, uploading }">
                  <Button @click="openFileSelector" :loading="uploading">
                    {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
                  </Button>
                </template>
              </FileUploader>
            </div>
          </div>
          <div>
            <label class="text-sm font-base text-gray-500">Company Logo</label>
            <div v-if="formData.uploadLogo">
              <!-- Show the logo if it exists -->
              <img
                class="h-40 w-full max-w-[260px] rounded-sm object-contain"
                :src="formData.uploadLogo"
                @error="setDefaultImage"
                alt="Company Logo"
              />
            </div>
            <div v-else>
              <!-- Show the upload button if the logo does not exist -->
              <FileUploader
                v-model="formData.uploadLogo"
                :fileTypes="['image/*']"
                @input="handleFileUpload3"
              >
                <template #default="{ openFileSelector, progress, uploading }">
                  <Button @click="openFileSelector" :loading="uploading">
                    {{ uploading ? `Uploading ${progress}%` : 'Upload Logo' }}
                  </Button>
                </template>
              </FileUploader>
            </div>
          </div>
        </div>

        <ErrorMessage :message="errorMessage" class="mt-6" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToast } from 'vue-toastification'
import { ref, onMounted } from 'vue'
import { FormControl, FileUploader, Button, ErrorMessage } from 'frappe-ui'
import editaccount from '../data/editaccount'

defineProps({
  embedded: {
    type: Boolean,
    default: false,
  },
})

const toast = useToast()

const formData = ref({
  primaryPhone: '',
  panNumber: '',
  secondaryPhone: '',
  secondaryEmail: '',
  website: '',
  city: '',
  street: '',
  facebookLinks: '',
  instagramLinks: '',
  uploadCitizenship: null,
  uploadPanImage: null,
  uploadLogo: null,
  contact_person: '',
  email: '',
  store_name: '',
})

const originalData = ref({})
const errorMessage = ref('')

const fetchKycData = async () => {
  try {
    const response = await editaccount.fetch()
    const payload = response?.data ? response : editaccount.data

    if (payload?.status !== 'success' || !payload?.data?.length) {
      errorMessage.value = payload?.message || 'No business information found.'
      return
    }

    const data = payload.data[0]

    formData.value = {
      contact_person: data.contact_person || '',
      email: data.primary_email || '',
      primaryPhone: data.primary_phone || '',
      store_name: data.vendor_name || '',
      panNumber: data.pan_number || '',
      secondaryPhone: data.secondary_phone || '',
      secondaryEmail: data.secondary_email || '',
      website: data.website || '',
      city: data.vendor_address || '',
      street: '',
      facebookLinks: data.facebook || '',
      instagramLinks: data.instagram || '',
      uploadCitizenship: data.citizenship || null,
      uploadPanImage: data.pan || null,
      uploadLogo: data.logo || null,
    }
    originalData.value = { ...formData.value }
  } catch (error) {
    errorMessage.value = `Error fetching KYC data: ${error.message || error}`
  }
}

onMounted(() => {
  fetchKycData()
})

const handleFileUpload = (event) => {
  const file = '/files/' + event.target.files[0].name
  formData.value.uploadCitizenship = file
}
const handleFileUpload2 = (event) => {
  const file = '/files/' + event.target.files[0].name
  formData.value.uploadPanImage = file
}
const handleFileUpload3 = (event) => {
  const file = '/files/' + event.target.files[0].name
  formData.value.uploadLogo = file
}

const getChangedFields = () => {
  const changed = {}
  const current = formData.value
  const original = originalData.value

  for (const key in current) {
    if (current[key] !== original[key]) {
      changed[key] = current[key]
    }
  }

  return changed
}

const validateForm = () => {
  errorMessage.value = ''
  return true
}

const register = async () => {
  if (!validateForm()) return

  const apiUrl = '/api/method/ecommerce.api.edit_account'
  const changedFields = getChangedFields()

  if (Object.keys(changedFields).length === 0) {
    toast.info('No changes detected.')
    return
  }
  // console.log('total field:', formData.value)
  // console.log('Changed Fields:', changedFields)
  try {
    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(changedFields),
    })

    const responseData = await response.json()
    // console.log('Response Data:', responseData)

    if (response.ok) {
      toast.success('Business information updated successfully.')
      window.location.reload() // Reload the page to reflect changes
      originalData.value = { ...formData.value } // Update originalData
    } else {
      errorMessage.value = `Error: ${responseData.message}`
    }
  } catch (error) {
    errorMessage.value = `Error: ${error.message || error}`
  }
}
</script>

<style scoped>
/* Add custom styles if needed */
</style>
