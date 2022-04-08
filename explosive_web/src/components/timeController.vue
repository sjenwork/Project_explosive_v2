<template>
  <div class="fixed-bottom" id="timeslider">
    <Slider
      v-model="value"
      :min="0"
      :max="4"
      :format="format"
      @change="changetime"
    >
    </Slider>
  </div>
</template>

<script setup>
import { ref } from "@vue/reactivity";
import Slider from "@vueform/slider";
import { onMounted } from "vue";
import { time } from "/src/components/js/data.js";

// 定義 emit 與 props
const emit = defineEmits(["time"]);
const props = defineProps({ selectedtime: Array });

// 定義時間，之後會需要以api更新
// const time = [
//   { index: 0, label: "2021 第一季" },
//   { index: 1, label: "2021 第二季" },
//   { index: 2, label: "2021 第三季" },
//   { index: 3, label: "2021 第四季" },
//   { index: 4, label: "最新申報" },
// ];

// 從App.vue傳入的初始時間
function getPropTime() {
  let res = time
    .filter((i) => {
      return props.selectedtime.includes(i.label);
    })
    .map((i) => {
      return i.index;
    });
  return res.length == 1 ? [...res, ...res] : res;
}
const value = ref(getPropTime());

// 時間軸tooltip文字
function format(val) {
  return time.filter((i) => i.index === val)[0].label;
}

// 時間調整，傳回App.vue
function changetime(val) {
  console.log(val);
  emit(
    "time",
    time.filter((i) => val.includes(i.index))
  );
}

onMounted(() => {});
</script>

<style scoped>
@media screen and (min-width: 440px) {
  #timeslider {
    margin: 10px;
    z-index: 1000;
    width: calc(100%-200px);
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    margin-left: 100px;
    margin-right: 100px;
    margin-bottom: 30px;
    /* bottom: 10px; */
  }
}
@media screen and (max-width: 440px) {
  #timeslider {
    margin: 10px;
    z-index: 1000;
    width: calc(100%-40px);
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    margin-left: 20px;
    margin-right: 20px;
    margin-bottom: 20px;
    /* bottom: 10px; */
  }
}
</style>