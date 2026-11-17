<template>
  <div
    class="lg:p-4 flex justify-center items-center min-h-screen lg:bg-gray-200"
  >
    <div class="bg-white p-8 rounded shadow-md w-full max-w-4xl">
      <div class="flex text-lg font-pregular font-bold mb-4">
        Register Your Business
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

          <div class="">
            <label class="text-sm font-base text-gray-500"
              >City <span class="text-red-500">*</span></label
            >
            <FormControl
              v-model="formData.city"
              type="text"
              size="sm"
              variant="subtle"
              placeholder="Enter city"
              :disabled="false"
            />
          </div>
          <div>
            <label class="text-sm font-base text-gray-500"
              >Street <span class="text-red-500">*</span></label
            >
            <FormControl
              v-model="formData.street"
              type="text"
              size="sm"
              variant="subtle"
              placeholder="Enter street"
              :disabled="false"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
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
          <div>
            <label class="text-sm font-base text-gray-500"
              >Citizenship <span class="text-red-500">*</span></label
            >
            <FileUploader
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
            <a
              v-if="formData.uploadCitizenship"
              :href="formData.uploadCitizenship"
              target="_blank"
              >View Uploaded Image</a
            >
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div>
            <label class="text-sm font-base text-gray-500">Pan Image</label>
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
            <a
              v-if="formData.uploadPanImage"
              :href="formData.uploadPanImage"
              target="_blank"
              >View Uploaded Image</a
            >
          </div>
          <div>
            <label class="text-sm font-base text-gray-500">Company Logo</label>
            <FileUploader
              v-model="formData.uploadLogo"
              :fileTypes="['image/*']"
              @input="handleFileUpload3"
            >
              <template #default="{ openFileSelector, progress, uploading }">
                <Button @click="openFileSelector" :loading="uploading">
                  {{ uploading ? `Uploading ${progress}%` : 'Upload Image' }}
                </Button>
              </template>
            </FileUploader>
            <a
              v-if="formData.uploadLogo"
              :href="formData.uploadLogo"
              target="_blank"
              >View Uploaded Image</a
            >
          </div>
        </div>

        <ErrorMessage :message="errorMessage" class="mt-6" />

        <div class="flex justify-end items-center mt-8">
          <Button
            :variant="'solid'"
            theme="gray"
            size="sm"
            :disabled="false"
            @click="register"
          >
            Update Business Information
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useToast } from 'vue-toastification'
import { ref, onMounted } from 'vue'
import { FormControl, FileUploader, Button, ErrorMessage } from 'frappe-ui'
import kyc from '../data/kyc'

//console.log('datakyc', kyc)
const toast = useToast()

const fetchKycData = async () => {
  try {
    const response = await kyc.fetch()

    const data = response.data[0]

    if (response) {
      const kyc = data

      formData.value.contact_person = kyc.contact_person || ''
      formData.value.email = kyc.email || ''
      formData.value.store_name = kyc.store_name || ''
      formData.value.panNumber = kyc.pan_number || ''
      formData.value.secondaryPhone = kyc.secondary_phone || ''
      formData.value.secondaryEmail = kyc.secondary_email || ''
      formData.value.website = kyc.website || ''
      formData.value.city = kyc.city || ''
      formData.value.street = kyc.street || ''
      formData.value.facebookLinks = kyc.facebook_links || ''
      formData.value.instagramLinks = kyc.instagram_links || ''
      formData.value.uploadCitizenship = kyc.upload_citizenship || null
      formData.value.uploadPanImage = kyc.uploadPanImage || null
      formData.value.uploadLogo = kyc.uploadLogo || null
    }
  } catch (error) {
    //  console.error('Error fetching KYC data:', error)
    errorMessage.value = `Error fetching KYC data: ${error.message || error}`
  }
}

onMounted(() => {
  fetchKycData()
})

const formData = ref({
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
})

const errorMessage = ref('')

const validateForm = () => {
  if (!formData.value.city) {
    errorMessage.value = 'Please enter city'
    return false
  }
  if (!formData.value.street) {
    errorMessage.value = 'Please enter street'
    return false
  }
  if (!formData.value.uploadCitizenship) {
    errorMessage.value = 'Please upload citizenship'
    return false
  }

  errorMessage.value = '' // Clear any previous error message
  return true
}

const handleFileUpload = (event) => {
  const file = '/files/' + event.target.files[0].name
  formData.value.uploadCitizenship = file
 //  // console.log('Uploaded file:', file)
}
const handleFileUpload2 = (event) => {
  const file = '/files/' + event.target.files[0].name
  formData.value.uploadPanImage = file
 //  //console.log('Uploaded file:', file)
}
const handleFileUpload3 = (event) => {
  const file = '/files/' + event.target.files[0].name
  formData.value.uploadLogo = file
 //  //console.log('Uploaded file:', file)
}
const register = async () => {
  if (!validateForm()) {
    return
  }
  const apiUrl = '/api/method/ecommerce.api.update_kyc'
 //  // console.log('formData', formData.value)

  try {
    const response = await fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData.value),
    })
    const responseData = await response.json()

    if (response.ok) {
     //  //  console.log('Business registered:', responseData)

      toast.success('You have successfully applied for registration.')
      //resetForm()
    } else {
      errorMessage.value = `Error registering business: ${responseData.message}`
    }
  } catch (error) {
    //console.error('Error registering business:', error)
    errorMessage.value = `Error registering business: ${error.message || error}`
  }
}

const resetForm = () => {
  formData.value = {
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
  }
  errorMessage.value = ''
}
</script>

<style scoped>
/* Add any styles you need for your form */
</style>
