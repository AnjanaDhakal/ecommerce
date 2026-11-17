<template>
  <div class="animate-pulse px-4 py-2">
    <div class="flex flex-row gap-4 overflow-x-auto">
      <div v-for="i in 4" :key="i" class="w-[360px] space-y-4">
        <div class="rounded-md bg-gray-200 h-6 w-3/4"></div>
        <div class="rounded-md bg-gray-200 h-24 w-full"></div>
        <div class="rounded-md bg-gray-200 h-4 w-full"></div>
        <div class="flex justify-end">
          <div class="h-6 w-20 bg-gray-200 rounded-md"></div>
        </div>
      </div>
    </div>

    <!-- Live Status Section Skeleton -->
    <div class="mt-5 bg-white p-3 rounded shadow-sm">
      <div class="h-5 bg-gray-200 w-32 mb-4 rounded"></div>
      <div class="flex flex-wrap gap-2">
        <div v-for="i in 6" :key="i" class="flex items-center gap-2">
          <div class="w-6 h-6 bg-gray-300 rounded-full"></div>
          <div class="w-24 h-4 bg-gray-200 rounded"></div>
        </div>
      </div>
    </div>

    <!-- Filters Skeleton -->
    <div class="mt-4 flex flex-wrap gap-4">
      <div class="space-y-2">
        <div class="h-4 w-24 bg-gray-200 rounded"></div>
        <div class="h-10 w-36 bg-gray-300 rounded-md"></div>
      </div>
      <div class="space-y-2">
        <div class="h-4 w-24 bg-gray-200 rounded"></div>
        <div class="h-10 w-36 bg-gray-300 rounded-md"></div>
      </div>
      <div class="space-y-2">
        <div class="h-4 w-24 bg-gray-200 rounded"></div>
        <div class="h-10 w-40 bg-gray-300 rounded-md"></div>
      </div>
      <div class="space-y-2">
        <div class="h-4 w-24 bg-gray-200 rounded"></div>
        <div class="h-10 w-40 bg-gray-300 rounded-md"></div>
      </div>
    </div>
  </div>
</template>
