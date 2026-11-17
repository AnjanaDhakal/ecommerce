<template>
  <div class="p-6 max-w-3xl mx-auto">
    <!-- Recipient Details -->
    <div class="bg-white shadow-sm rounded-lg p-6 border">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">
        Recipient Details
      </h2>
      <div class="grid grid-cols-2 gap-4 text-sm text-gray-700">
            <div><span class="font-medium">Tracking ID:</span> {{ trackingOrder  }}</div>
        <div><span class="font-medium">Name:</span> {{ customerInfo.name }}</div>
        <div><span class="font-medium">Phone:</span> {{ customerInfo.phone }}</div>
        <div><span class="font-medium">Address:</span> {{ customerInfo.address }}</div>
      </div>
    </div>

    <!-- Timeline -->
    <div class="bg-white shadow-sm rounded-lg p-6 border mt-6">
      <h2 class="text-lg font-semibold text-gray-800 mb-4">Timeline</h2>
      <div class="flex items-center justify-between">
        <!-- Order Steps -->
        <div
          v-for="(step, index) in steps"
          :key="index"
          class="flex items-center relative"
        >
          <div class="flex flex-col items-center relative">
            <img
              :src="getIcon(step.key, step.status)"
              :alt="step.label"
              class="w-12 h-12"
            />
            <div
              :class="isActive(step.status) ? 'text-red-500' : 'text-gray-500'"
              class="font-medium"
            >
              {{ step.label }}
            </div>
          </div>

          <!-- Line between steps -->
          <div
            v-if="index < steps.length - 1"
            class="relative flex items-center"
          >
            <div
              :class="
                isCompleted(steps[index], steps[index + 1])
                  ? 'border-green-500'
                  : 'border-gray-300'
              "
              class="h-1 w-16 border-dashed border-2 mt-3"
            ></div>

            <!-- Checkmark Positioned Above the Line -->
            <svg
              v-if="isCompleted(steps[index], steps[index + 1])"
              class="w-5 h-5 text-green-500 absolute -top-3 left-1/2 transform -translate-x-1/2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M5 13l4 4L19 7"
              ></path>
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import tracking from '../data/tracking' // Assuming tracking module contains the URL
import { useRoute } from 'vue-router'

const route = useRoute()

// Get the 'tracking_order' parameter from the query string
const trackingOrder = route.query.tracking_order;


//console.log("Tracking Order:", trackingOrder);

const loading = ref(true); // Loading state
const currentStatus = ref(''); // Status is now a string instead of an array
const error = ref(null); // Error state
const customerInfo = ref({}); // Customer Info object to hold customer details

// Fetch tracking data function

async function getOrderStatus(trackingOrder) {
  const url = `/api/method/ecommerce.api.track_order?tracking_order=${trackingOrder}`;

  try {
    const response = await fetch(url, {
      method: 'GET', // GET request method
    });

    // Check if the response is OK (status code 200-299)
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json(); // Parse the JSON response

   //  //console.log("Tracking Data:", data.message.data); // Log the data to check its structure

    if (data && data.message.data && data.message.data) {
      currentStatus.value = data.message.data.status; // Assigning the actual order status from data.data.status

      // Assuming customer info is inside data.data
      customerInfo.value = {
        name: data.message.data.customerName || 'N/A',
        phone: data.message.data.phone || 'N/A',
        address: data.message.data.address || 'N/A',
      };
    } else {
      error.value = "Invalid data format from API.";
    }
  } catch (err) {
    console.error("Error fetching tracking data:", err);
    error.value = "Failed to fetch tracking data.";
  } finally {
    loading.value = false;
  }
};
const fetchTrackingData = async () => {
  if (!trackingOrder) {
    error.value = "Tracking order not found in the URL.";
    return;
  }

  getOrderStatus(trackingOrder)

  const trackingUrlWithParams = `${tracking.url}?tracking_order=${trackingOrder}`; // Construct the URL with query params
}

// Call API when component is mounted
onMounted(fetchTrackingData);

// Function to check if a step is active
const isActive = (status) => currentStatus.value === status;

const steps = [
  { key: 'box', label: 'Accepted', status: 'Accepted' },
  { key: 'cart', label: 'Picked', status: 'Picked' },
  { key: 'truck', label: 'Processing', status: 'Processing' },
  { key: 'scooter', label: 'Out for Delivery', status: 'Out for Delivery' },
  { key: 'package', label: 'Delivered', status: 'Delivered' },
]

// Function to check if a step and the next step are both completed
const isCompleted = (step, nextStep) =>
  isActive(step.status) && isActive(nextStep.status)

// Function to get icon color based on active status
const getIcon = (key, status) => {
  const baseUrl = 'https://img.icons8.com/'
  const iconMap = {
    box: isActive(status) ? 'fluency/48/box.png' : 'ios-filled/48/gray/box.png',
    cart: isActive(status)
      ? 'color/48/shopping-cart-loaded.png'
      : 'ios-filled/48/gray/shopping-cart.png',
    truck: isActive(status)
      ? 'ios-filled/48/shipping.png'
      : 'https://icons8.com/icons/set/truck',
    scooter: isActive(status)
      ? 'ios-filled/48/motorcycle.png'
      : 'ios-filled/48/gray/scooter.png',
    package: isActive(status)
      ? 'color/48/package.png'
      : 'ios-filled/48/gray/package.png',
  }
  return baseUrl + iconMap[key]
}
</script>
