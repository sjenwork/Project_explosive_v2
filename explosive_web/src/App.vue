<template>
  <backgroundMap
    :plotdata="plotdata"
    :focusdata="focusdata"
  />
  <Suspense>
    <Controller
      @queryResult="handleQueryData"
      @focusResult="handleFocusResult"
    />
  </Suspense>
</template>

<script setup>
import backgroundMap from './components/backgroundMap.vue';
import Controller from './components/Controller.vue';
import { ref } from "@vue/reactivity";

var plotdata = ref()
var focusdata = ref()

function handleQueryData(data) {
  console.log(`  >> got queryData from Controller.vue`)
  plotdata.value = data.value
}

function handleFocusResult(data) {
  console.log(`  >> got focusdata from Controller.vue`)
  // console.log(data)
  focusdata.value = data
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

::v-deep(.multiselect__select) {
  background-color: none;
}
</style>
<!-- ./components/sliderController.vue./components/sliderController.vue -->