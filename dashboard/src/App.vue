<!-- src/App.vue -->
<template>
  <div>
    <PageLoader v-if="loading" />
    <router-view />
    <UnsavedChangesDialog />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import PageLoader from './components/PageLoader.vue';
import UnsavedChangesDialog from './components/UnsavedChangesDialog.vue';
import { useRouter } from 'vue-router';

const loading = ref(false);
const router = useRouter();

router.beforeEach((to, from, next) => {
  loading.value = true;
  next();
});

router.afterEach(() => {
  loading.value = false;
});

</script>
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "lnu677d2dh");
</script>

<style>
/* Add any global styles if necessary */
</style>
