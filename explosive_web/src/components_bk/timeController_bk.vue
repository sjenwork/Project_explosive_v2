<template>
  <!-- <div class="" id="timeslider"> -->
  <div
    class="fixed-top"
    id="timeslider"
  >
    <Slider
      showTooltip="focus"
      tooltipPosition="bottom"
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

const url = `${import.meta.env.VITE_API_BASE_URL}/records_time`;
var time2 = ref(await fetch(url).then(res => res.json()));
console.log(time2.value)

const value = ref([3, 3]);
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
  let res = []
  for (let i = 0; i < time2.value.length; i++) {
    for (let j = 0; j < props.selectedtime.length; j++) {
      if (time2.value[i].label === props.selectedtime[j]) {
        res.push(i)
      }
    }
  }
  console.log(res)
  return res
  // let res = time2
  //   .filter((i) => {
  //     return props.selectedtime.includes(i.label);
  //   })
  //   .map((i) => {
  //     return i.index;
  //   });
  // console.log(res)
  // return res.length == 1 ? [...res, ...res] : res;
}
// const value = ref(getPropTime());

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

onMounted(() => { });
</script>

<style scoped>
@media screen and (min-width: 340px) {
  #timeslider {
    padding-left: 40px;
    padding-right: 40px;
    padding-top: 20px;
    height: 40px;
    width: 320px;
    margin: 10px;
    top: 91px;
    border-radius: 5px;
    z-index: 900;
    background-color: rgba(255, 255, 255, 1);
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);

  }
}

@media screen and (max-width: 340px) {
  #timeslider {
    margin: 10px;
    z-index: 900;
    height: 40px;
    width: 100%;
    border-radius: 5px;
    background-color: rgba(255, 255, 255, 1);
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    margin: 0px;
    top: 91px;
    padding-top: 20px;
    padding-left: 40px;
    padding-right: 40px;
  }
}

.slider-red {
  --slider-connect-bg: #EF4444;
  --slider-tooltip-bg: #EF4444;
  --slider-handle-ring-color: #EF444430;
}
</style>