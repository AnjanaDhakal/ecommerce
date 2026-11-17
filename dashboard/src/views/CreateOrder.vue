<template>
  <div class="p-4 lg:bg-gray-200 min-h-screen">
    <div class="p-3 lg:p-4 border-2 rounded-lg">
      <div>
        <div
          class="flex items-center justify-center rounded mb-2 bg-gray-50 p-1"
        >
          <p class="">
            <span class="text-lg font-pbold"> Create New Order List </span>
          </p>
        </div>
        <div class="grid grid-cols-1 gap-4 mb-4 bg-gray-50 p-2 rounded">
          <div class="flex rounded flex-row">
            <div>
              <label for="name">Name:</label>
              <input type="text" id="name" v-model="form.name" required />
            </div>
            <div>
              <label for="name">Name:</label>
              <input type="text" id="name" v-model="form.name" required />
            </div>
            <div>
              <label for="name">Name:</label>
              <input type="text" id="name" v-model="form.name" required />
            </div>
          </div>
          <div class="flex rounded flex-row">
            <div>
              <label for="name">Name:</label>
              <input type="text" id="name" v-model="form.name" required />
            </div>
            <div>
              <label for="name">Name:</label>
              <input type="text" id="name" v-model="form.name" required />
            </div>
          </div>
        </div>
        <div class="flex items-center rounded mb-2">
          <div class="justify-between">
            <p>
              Select file upload
              <span class="text-lg font-pbold">Upload file</span>
              <input type="file" @change="handleFileUpload" />
            </p>
          </div>

          <div class="justify-end">
            <p class="text-lg font-pbold">
              <a href="/your-template.xlsx" download>Download excel Template</a>
            </p>
          </div>
        </div>
        <div class="rounded bg-gray-50 p-1 mt-5 flex justify-between mb-3">
          <h2>Create Order</h2>
          <div>
            <Button variant="solid">+ Add Order</Button>
          </div>
        </div>

        <form @submit.prevent="submitForm">
          <div>
            <label for="name">Name:</label>
            <input type="text" id="name" v-model="form.name" required />
          </div>
          <div>
            <label for="phone">Phone:</label>
            <select id="phone" v-model="form.phone" required>
              <option disabled value="">Please select one</option>
              <option>+1</option>
              <option>+44</option>
              <option>+91</option>
            </select>
          </div>
          <div>
            <label for="gender">Gender:</label>
            <input type="radio" id="male" value="Male" v-model="form.gender" />
            <label for="male">Male</label>
            <input
              type="radio"
              id="female"
              value="Female"
              v-model="form.gender"
            />
            <label for="female">Female</label>
          </div>
          <button type="submit">Submit</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { Button } from 'frappe-ui'
export default {
  data() {
    return {
      form: {
        name: '',
        phone: '',
        gender: '',
      },
    }
  },
  methods: {
    submitForm() {
     //  //console.log(this.form)
    },
  },
}

// Your existing code...

function handleFileUpload(event) {
  const file = event.target.files[0]
  // Handle the file upload here...
}

// Your existing code...
</script>
