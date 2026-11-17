<template>
  <div
    class="bg-gray-50 min-h-screen flex justify-center items-center overflow-hidden p-4"
  >
    <div class="px-4 mx-auto max-w-screen-lg lg:py-16 lg:px-6">
      <div class="mx-auto max-w-screen-md text-center">
        <!-- Image -->
        <div class="flex items-center justify-center mb-6">
          <img
            src="@/assets/notfound.png"
            class="h-40 w-40 md:h-60 md:w-60 lg:h-80 lg:w-80"
            alt="Not Found Logo"
          />
        </div>

        <!-- 404 Heading -->
        <h1
          class="text-7xl md:text-9xl lg:text-[100px] tracking-tight font-extrabold text-primary-600 mb-4"
        >
          404
        </h1>

        <!-- Description -->
        <p
          class="text-xl md:text-2xl lg:text-3xl tracking-tight font-bold text-gray-900 mb-2"
        >
          Something's missing.
        </p>
        <p
          class="text-sm md:text-base lg:text-lg font-light text-gray-500 mb-6"
        >
          Sorry, we can't find that page. You'll find lots to explore on the
          home page.
        </p>

        <!-- Button -->
        <router-link
          to="/"
          class="inline-flex items-center text-white bg-primary-600 hover:bg-primary-800 focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium rounded-lg text-sm md:text-base px-4 md:px-5 py-2 text-center"
        >
          <img src="@/assets/icon.png" class="h-8 w-8 mr-2" alt="Home Icon" />
        </router-link>
      </div>
    </div>
  </div>
</template>
