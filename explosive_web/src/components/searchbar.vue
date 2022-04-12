<template>
  <div id="searchbar" class="fixed-top">
    <div class="container-xs px-0">
      <div class="row rounded-lg mx-0">
        <!-- 選單 -->
        <div class="col-2 togglebtn noselect">&#9776;</div>
        <!-- <div class="col-sm-2 col-2 togglebtn noselect">&#9776;</div> -->
        <!-- 運作行為 -->
        <div class="col-3 border-end ps-2">
          <!-- <div class="col-sm-3 col-10 border-end ps-2"> -->
          <multiselect v-model="selectedOperation" placeholder="行為" :options="operationOptions.map((i) => i.chn)"
            :searchable="false" :close-on-select="true" :show-labels="false"></multiselect>
        </div>
        <!-- 化學物質 -->
        <div class="col-7 ps-2">
          <!-- <div class="offset-sm-0 col-sm-7 offset-2 col-10 ps-2"> -->
          <multiselect v-model="selectedChem" placeholder="化學物質" open-direction="bottom" :options="chemicallist"
            :searchable="true" :loading="isLoading" :close-on-select="true" :show-labels="false"
            @search-change="asyncFind">
            <template slot="tag" slot-scope="{ option, remove }">
              <span class="custom__tag">
                <span>{{ option.name }}</span>
                <span class="custom__remove" @click="remove(option)">❌</span>
              </span>
            </template>
            <template slot="clear" slot-scope="props">
              <div class="multiselect__clear" v-if="selectedChem.length"
                @mousedown.prevent.stop="clearAll(props.search)"></div>
            </template>
            <span slot="noResult">
              Oops! No elements found. Consider changing the search
              query.
            </span>
          </multiselect>
        </div>
      </div>
    </div>
  </div>
  <!-- </div> -->
</template>

<script setup>
import { ref, reactive } from "@vue/reactivity";
import Multiselect from "vue-multiselect";
import { watch } from "vue";
import { onMounted } from "vue";
import { time } from "/src/components/js/data.js";

const emit = defineEmits(["item"]);
const props = defineProps({ selectedtime: Array });

// 參數定義
var nfac = ref("");

// 運作行為選單
const operationOptions = [
  { chn: "輸入", eng: "import" },
  { chn: "貯存", eng: "storage" },
  { chn: "製造", eng: "produce" },
  { chn: "使用", eng: "usage" },
];
var selectedOperation = ref("");

// 化學物質選單
var selectedChem = ref("");
var chemicallist = ref([]);
var isLoading = ref(false);
const asyncFind = async (query) => {
  isLoading.value = true;
  let baseurl = import.meta.env.VITE_API_BASE_URL;
  console.log(`${baseurl}/chemilist`);
  let res = await fetch(
    // "https://jenicksun.xn--kpry57d/explosive/statistic/chemlist/"
    `${baseurl}/chemilist`
  ).then((res) => res.json());
  chemicallist.value = res.map((i) => i["label"]);
  isLoading.value = false;
};

// 函數
function groupBy(data, index) {
  return data.reduce(function (a, b) {
    if (a[b[index]]) {
      a[b[index]].push(b);
    } else {
      a[b[index]] = [b];
    }
    return a;
  }, {});
}

function range(start, stop, step) {
  if (typeof stop == "undefined") {
    // one param defined
    stop = start;
    start = 0;
  }

  if (typeof step == "undefined") {
    step = 1;
  }

  if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
    return [];
  }

  var result = [];
  for (var i = start; step > 0 ? i < stop : i > stop; i += step) {
    result.push(i);
  }

  return result;
}

// 監看輸入值
watch(
  // () => {
  //   return [selectedOperation, selectedChem, props.selectedtime];
  // },
  [selectedOperation, selectedChem, () => props.selectedtime],
  async (
    [newOperation, newChem, newTime],
    [oldOperation, oldChem, oldTime]
  ) => {
    if (
      (newOperation != "") &
      (newChem != "") &
      ((oldOperation != newOperation) |
        (oldChem != newChem) |
        (oldTime != newTime))
    ) {
      // 取得對應資料
      let chemname = newChem.split(" ")[1];
      let operation = operationOptions.filter((i) => {
        return i.chn === newOperation;
      })[0].eng;

      var finalres = [];
      let baseurl = `${import.meta.env.VITE_API_BASE_URL}/records_all`;
      let url = `${baseurl}?name=${chemname}&operation=${operation}`;
      if (newTime[0] === "最新申報") {
        // 取得最新一期的
        let res = await fetch(url).then((res) => res.json());
        console.log(res)

        var res2 = groupBy(res, "ComFacBizName");
        nfac.value = Object.keys(res2).length;
        Object.values(res2).forEach((i) => {
          var res3 = groupBy(i, "deptid");
          Object.values(res3).forEach((j) => {
            finalres.push(
              j.sort(function (a, b) {
                return parseFloat(b.time) - parseFloat(a.time);
              })[0]
            );
          });
        });
        console.log(res2)
      } else {
        // 依據時間範圍取得資料
        var paras;
        var time = [];
        newTime.forEach((i) => {
          time.push(
            i
              .replace(" 第一季", "01")
              .replace(" 第二季", "04")
              .replace(" 第三季", "07")
              .replace(" 第四季", "10")
          );
        });
        if (time[1] === "最新申報") {
          // let time = newTime[0];
          paras = `Time_gte=${time[0]}`;
        } else {
          paras = `Time_gte=${time[0]}&Time_lte=${time[1]}`;
        }
        url = `${url}&${paras}`;
        finalres = await fetch(url).then((res) => res.json());
      }
      emit("item", {
        res: finalres,
        selected: {
          operation: newOperation,
          chem: newChem,
        },
      });
    }
  }
);

onMounted(() => { });
</script>

<style scoped>
@media screen and (min-width: 340px) {
  #searchbar {
    z-index: 1000;
    width: 320px;
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    background-color: white;
    border-radius: 5px;
    /* border: 1px solid grey; */
    margin: 10px;
  }
}

@media screen and (max-width: 340px) {
  #searchbar {
    z-index: 1000;
    width: 100%;
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    background-color: white;
    border-radius: 5px;
    /* border: 1px solid grey; */
  }
}

.row>* {
  padding-left: 0px;
  padding-right: 0px;
}

::v-deep(.multiselect__tags) {
  background: rgba(255, 255, 255, 0);
  border-radius: 0px;
  border-width: 0px;
}

.togglebtn {
  /* position: fixed; */
  cursor: pointer;
  /* margin: 5px; */
  font-size: 25px;
  z-index: 2000;
  /* vertical-align: middle; */
  line-height: 41px;
}

.noselect {
  -webkit-touch-callout: none;
  /* iOS Safari */
  -webkit-user-select: none;
  /* Safari */
  -khtml-user-select: none;
  /* Konqueror HTML */
  -moz-user-select: none;
  /* Old versions of Firefox */
  -ms-user-select: none;
  /* Internet Explorer/Edge */
  user-select: none;
  /* Non-prefixed version, currently
                                  supported by Chrome, Edge, Opera and Firefox */
}

::v-deep(.multiselect__single) {
  margin: 0px;
  width: auto;
  /* width: calc(100%-20px); */
}

::v-deep(.multiselect__tags) {
  padding: 0px;
  line-height: 41px;
  height: 41px;
}

::v-deep(.multiselect__single) {
  line-height: 41px;
}

::v-deep(.multiselect__placeholder) {
  padding: 0px;
  margin: 0px;
}

::v-deep(.multiselect__input) {
  margin: 0px;
  line-height: 41px;
  height: 41px;
  width: auto;
  /* width: calc(100%-20px); */
}
</style>