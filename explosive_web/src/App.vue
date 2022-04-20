<template>
  <backgroundMap :plotdata="plotdata" />
  <Suspense>
    <Controller @queryResult="handleQueryData" />
  </Suspense>
</template>

<script setup>
import backgroundMap from './components/backgroundMap.vue';
import Controller from './components/Controller.vue';
import { ref } from "@vue/reactivity";

var plotdata = ref()

function handleQueryData(data) {
  console.log(`  >> got queryDaya from Controller.vue`)
  plotdata.value = data.value
}


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