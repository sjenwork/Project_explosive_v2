<template>
  <backgroundMap />
  <Suspense>
    <Controller />

  </Suspense>
</template>

<script setup>
import backgroundMap from './components/backgroundMap.vue';
import Controller from './components/Controller.vue';

</script>


<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
./components/sliderController.vue./components/sliderController.vue