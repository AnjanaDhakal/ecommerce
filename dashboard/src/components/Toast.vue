<template>
  <div class="">
    <p class="mb-4">
      Customer exists with this phone number. Do you want to proceed?
    </p>
    <div class="flex justify-end space-x-2">
      <button
        @click="confirm(true)"
        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700"
      >
        Yes
      </button>
      <button
        @click="confirm(false)"
        class="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-700"
      >
        No
      </button>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    resolve: {
      type: Function,
      required: true,
    },
  },
  methods: {
    confirm(choice) {
      this.resolve(choice) // Resolve the promise with the user's choice
    },
  },
}
</script>
