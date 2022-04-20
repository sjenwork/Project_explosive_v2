<template>
  <div>
    <backgroundmap> </backgroundmap>
    <searchbar
      @item="searchitems"
      :selectedtime="selectedtime"
    > </searchbar>
    <Suspense>
      <timeController
        @time="handletime"
        :selectedtime="selectedtime"
      >
      </timeController>
    </Suspense>
    <slideController
      :data="data"
      :time="selectedtime"
      :chem="selectedchem"
      :operation="selectedoperation"
    >
    </slideController>
    <displayOnMap
      :data="data"
      :time="selectedtime"
      :chem="selectedchem"
      :operation="selectedoperation"
    >
    </displayOnMap>
  </div>
</template>

<script setup>
import backgroundmap from "./components/backgroundMap.vue";
import slideController from "./components/slideController.vue";
import searchbar from "./components/searchbar.vue";
import timeController from "./components/timeController.vue";
import displayOnMap from "./components/displayOnMap.vue";
import { ref } from "@vue/reactivity";

// var selectedtime = ref(["2021 第一季", "最新申報"]);
var selectedtime = ref(["最新申報", "最新申報"]);
var selectedchem = ref("");
var selectedoperation = ref("");
var data = ref({});

function searchitems(item) {
  console.log(item)
  selectedchem.value = item.selected.chem;
  selectedoperation.value = item.selected.operation;
  data.value.res_city = item.res_city;
  data.value.res_fac = item.res_fac;
  console.log(data.value.res_city.length)
  console.log(data.value.res_fac.length)
}
function handletime(item) {
  console.log(item)
  // if (item.length == 1) {
  //   item = [...item, ...item];
  // }
  selectedtime.value = item;
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