<template>
  <!-- NavBar -->
  <transition name="slide">
    <div id="navbar" v-show="navbarStatus" class="fixed-top">
      <!-- 圖表結果 -->
      <div id="searchResult">
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li class="nav-item w-50" role="presentation">
            <button
              class="nav-link active w-100"
              id="home-tab"
              data-bs-toggle="tab"
              data-bs-target="#home"
              type="button"
              role="tab"
              aria-controls="home"
              aria-selected="true"
            >
              廠商列表
            </button>
          </li>
          <li class="nav-item w-50" role="presentation">
            <button
              class="nav-link w-100"
              id="profile-tab"
              data-bs-toggle="tab"
              data-bs-target="#profile"
              type="button"
              role="tab"
              aria-controls="profile"
              aria-selected="false"
            >
              統計圖
            </button>
          </li>
        </ul>
        <div class="tab-content" id="myTabContent">
          <div
            class="tab-pane fade show active"
            id="home"
            role="tabpanel"
            aria-labelledby="home-tab"
            style="height: calc(100vh - 200px); overflow: scroll"
          >
            <template v-if="tableData.rows.length > 0">
              <div
                style="
                  text-align: left;
                  margin: 5px;
                  margin-bottom: 5px;
                  display: flex;
                  justify-content: space-between;
                  align-items: center;
                "
              >
                <label
                  >查詢：
                  <input
                    v-model="searchInTable"
                    @click="clickSearchInput"
                    onfocus="this.value=''"
                  />
                </label>
                <span class="download" @click="downloadResult">
                  <label for="">報表下載</label>
                  <font-awesome-icon :icon="faArrowCircleDown" />
                </span>
                <!-- <font-awesome-icon :icon="['fas', 'bars']" /> -->
                <!-- <img
                                src="/src/assets/download.jpeg"
                                style="height:30px"
                            /> -->
              </div>
              <template v-if="selectedQuery === '運作行為 與 化學物質'">
                <table-lite
                  :is-static-mode="true"
                  :is-loading="tableForChemSearch.isLoading"
                  :columns="tableForChemSearch.columns"
                  :rows="tableForChemSearch.rows"
                  :total="tableForChemSearch.totalRecordCount"
                  :sortable="tableForChemSearch.sortable"
                  @is-finished="tableLoadingFinish"
                  @toggleinfo="handleToggleInfoFromSearchChem"
                  :toggleOpen="toggleOpen"
                >
                  <td
                    colspan="3"
                    style="
                      background-color: rgba(200, 240, 200, 0.5);
                      overflow-x: scroll;
                      overflow-x: scroll;
                    "
                  >
                    <div style="margin-top: 10px; margin-bottom: 30px; width: 100%">
                      <!-- <template> -->
                      <div
                        style="width: 130%; overflow-x: hidden"
                        class="card"
                        :value="chem"
                        v-for="chem in [...new Set(comFacDetail.map((i) => i.name))]"
                      >
                        <div
                          class="card-header"
                          style="text-align: left; padding-left: 40px"
                        >
                          {{ chem }}
                        </div>
                        <div class="card-body">
                          <table
                            class="table table-hover"
                            style="table-layout: fixed; width: 100%"
                          >
                            <thead>
                              <tr>
                                <th>來源</th>
                                <th>運作行為</th>
                                <th>申報期別</th>
                                <th>運作量</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-for="item in comFacDetail2[chem]" :value="item.name">
                                <th>{{ dept_e2c[item.deptid] }}</th>
                                <th>
                                  {{
                                    operationOptions.filter(
                                      (i) => i.eng == item.operation
                                    )[0]["chn"]
                                  }}
                                </th>
                                <th>{{ item.time }}</th>
                                <th>{{ item.Quantity }}</th>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </td>
                </table-lite>
              </template>

              <template v-else-if="selectedQuery === '廠商名稱 或 統一編號'">
                <table-lite
                  :is-static-mode="true"
                  :is-loading="tableForFacSearch.isLoading"
                  :columns="tableForFacSearch.columns"
                  :rows="tableForFacSearch.rows"
                  :total="tableForFacSearch.totalRecordCount"
                  :sortable="tableForFacSearch.sortable"
                  @is-finished="tableLoadingFinish"
                  @toggleinfo="handleToggleInfoFromSearchFac"
                >
                  <!-- :toggleOpen="toggleOpen" -->
                </table-lite>
              </template>
            </template>
          </div>

          <div
            class="tab-pane fade"
            id="profile"
            role="tabpanel"
            aria-labelledby="profile-tab"
          >
            ...
          </div>
        </div>
      </div>
    </div>
  </transition>
  <div class="fixed-top">
    <!-- 搜尋選單 -->
    <div id="searchPannel">
      <div class="container-xs px-0">
        <template v-if="true">
          <div class="row rounded-lg mx-0">
            <!-- 選單 -->
            <div
              class="col-2 togglebtn noselect border-end"
              @click="navbarStatus = !navbarStatus"
            >
              &#9776;
            </div>
            <div class="col-10 border-end ps-0">
              <multiselect
                v-model="selectedQuery"
                placeholder="依...查詢"
                :options="queryOptions.map((i) => i.method)"
                :searchable="false"
                :close-on-select="true"
                :show-labels="false"
                @Select="handleSelectQuery"
                :allowEmpty="false"
              ></multiselect>
            </div>
          </div>
        </template>
        <template v-if="selectedQuery === '運作行為 與 化學物質'">
          <div class="row rounded-lg mx-0 border-top">
            <div class="col-5 border-end ps-0">
              <multiselect
                v-model="selectedOperation"
                placeholder="運作行為"
                :options="operationOptions"
                label="chn"
                :searchable="false"
                :close-on-select="true"
                :show-labels="false"
              ></multiselect>
            </div>
            <!-- 化學物質 -->
            <div class="col-7 ps-0">
              <multiselect
                v-model="selectedChem"
                placeholder="化學物質"
                open-direction="bottom"
                :options="chemOptions"
                label="label"
                :searchable="true"
                :loading="isLoadingChem"
                :close-on-select="true"
                :show-labels="false"
                @search-change="asyncGetChem"
              >
                <template slot="tag" slot-scope="{ option, remove }">
                  <span class="custom__tag">
                    <span>{{ option.name }}</span>
                    <span class="custom__remove" @click="remove(option)">❌</span>
                  </span>
                </template>
                <template slot="clear" slot-scope="props">
                  <div
                    class="multiselect__clear"
                    v-if="selectedChem.length"
                    @mousedown.prevent.stop="clearAll(props.search)"
                  ></div>
                </template>
                <span slot="noResult">
                  Oops! No elements found. Consider changing the search query.
                </span>
              </multiselect>
            </div>
          </div>
        </template>
        <template v-else-if="selectedQuery === '廠商名稱 或 統一編號'">
          <div class="row rounded-lg mx-0">
            <div class="col-12 border-top ps-0">
              <multiselect
                v-model="selectedComFac"
                placeholder="廠商查詢"
                open-direction="bottom"
                :options="comFacOptions"
                label="label"
                :searchable="true"
                :loading="isLoadingFacCom"
                :close-on-select="true"
                :show-labels="false"
                @search-change="asyncGetFacCom"
              >
                <template slot="tag" slot-scope="{ option, remove }">
                  <span class="custom__tag">
                    <span>{{ option.name }}</span>
                    <span class="custom__remove" @click="remove(option)">❌</span>
                  </span>
                </template>
                <template slot="clear" slot-scope="props">
                  <div
                    class="multiselect__clear"
                    v-if="selectedChem.length"
                    @mousedown.prevent.stop="clearAll(props.search)"
                  ></div>
                </template>
                <span slot="noResult">
                  Oops! No elements found. Consider changing the search query.
                </span>
              </multiselect>
            </div>
          </div>
        </template>
        <template v-if="true">
          <div class="row rounded-lg mx-0">
            <div class="col-12 border-top ps-0" id="timeslider">
              <Slider
                showTooltip="always"
                tooltipPosition="bottom"
                v-model="selectedTime"
                :min="0"
                :max="timeOptions.length - 1"
                :format="timeTick"
              >
              </Slider>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "@vue/runtime-core";
import { watch, computed } from "vue";
import Multiselect from "vue-multiselect";
import TableLite from "vue3-table-lite";
import Slider from "@vueform/slider";
import DataFrame from "dataframe-js";
// import Plotly from "plotly.js-dist-min";
import { clearPlotlyTrace } from "./js/utility.js";
import { faArrowCircleDown } from "@fortawesome/free-solid-svg-icons";
import { utils, write } from "xlsx";
import { saveAs } from "file-saver";

onMounted(() => {
  // click point in map
  let mymap = document.querySelector("#map");

  mymap.on("plotly_click", (i) => {
    try {
      if (selectedQuery.value === "運作行為 與 化學物質") {
        if (toggleOpen.value) {
          toggleOpen.value = false;
          document.querySelector(".vtl-tbody tr").click();
        }
        var clickpoint = i.points[0].text.split(":")[0];
        // console.log(clickpoint)
        searchInTable.value = clickpoint;
        toggleOpen.value = true;
        setTimeout(() => {
          document.querySelector(".vtl-tbody tr").click();
        }, 500);
      }
    } catch (e) {
      if (toggleOpen.value) {
        // console.log(1)
        toggleOpen.value = false;
        document.querySelector(".vtl-tbody tr").click();
        searchInTable.value = "";
        clearPlotlyTrace("fac");
      }
    }
  });
});

// emit and props
const emit = defineEmits(["queryFromChemSearch", "queryFromFacSearch", "focusResult"]);
const props = defineProps();

// 查詢參數
var queryOptions = ref([]); //查詢方式選單
var selectedQuery = ref([]); // 選擇的查詢方式
var operationOptions = ref([]); // 運作行為選單
var selectedOperation = ref(""); // 選擇的運作行為
var chemOptions = ref([]); // 化學物質選單
var selectedChem = ref(""); // 選擇的化學物質
var comFacOptions = ref([]); // 廠商列表選單
var selectedComFac = ref(""); // 選擇的廠商
var timeOptions = ref([]); // 時間列表
var selectedTime = ref([]); // 選擇的時間

// base url
var baseurl = import.meta.env.VITE_API_BASE_URL;
var baseurl_ver2 = import.meta.env.VITE_API_BASE_URL_ver2;
console.log(baseurl);
console.log(baseurl_ver2);

// 函數 與 相關參數
var isLoadingChem = ref(false);
var isLoadingFacCom = ref(false);
var asyncGetChem; // 取得化學物質列表
var asyncGetFacCom; // 取得廠商列表
var asyncGetTime; // 取得時間列表

var timeTick;

var data;
var emitData = ref();
// toggle navbar
var navbarStatus =
  document.querySelector("body").clientWidth > 760 ? ref(true) : ref(false);

// toggle table-lite row
var handleToggleInfoFromSearchChem;
var handleToggleInfoFromSearchFac;
var comFacDetail = ref([]);
var comFacDetail2 = ref({});
var toggleOpen = ref(false);
var searchInTable = ref("");
var tableData = reactive({ rows: [] });
var clickSearchInput;
// console.log(tableData.rows.length)

var handleSelectQuery;
var handleSelectChem;
// var clearPlotlyTrace

var downloadResult;

// table

var dept_e2c = ref({
  CAA: "交通部民用航空局",
  COA001: "農委會防檢局",
  EPZA: '"科技產業園區(經濟部加工出口區)"',
  MND: "國防部",
  MOEA001: "經濟部中部辦公室",
  MOEA002: "經濟部工業局(自行設置)",
  MOEA005: "經濟部礦務局",
  MOF001: "財政部關務署",
  MOF002: "財政部國庫署",
  MOI001: "內政部消防署",
  MOL001: "勞動部職安署",
  MOST001: "科技部竹科管理局",
  MOST002: "科技部中科管理局",
  MOST003: "科技部南科管理局",
  MOTC001: "交通部臺灣港務公司",
  TCSB: "環保署化學局",
});

const json2arr = async (data) => {
  // console.log(data);
  // const buildData = (data) => {
  return new Promise((resolve, reject) => {
    // 最後所有的資料會存在這
    let arrayData = [];

    // 取 data 的第一個 Object 的 key 當表頭
    let arrayTitle = Object.keys(data[0]);
    // console.log(arrayTitle)
    arrayData.push(arrayTitle);

    // 取出每一個 Object 裡的 value，push 進新的 Array 裡
    Array.prototype.forEach.call(data, (d) => {
      let items = [];
      Array.prototype.forEach.call(arrayTitle, (title) => {
        // let item = d[title] || "無";
        let item = d[title];
        items.push(item);
      });
      arrayData.push(items);
    });

    resolve(arrayData);
  });
  // };
};

var defineParameter = true;
//  ------------------ 參數初始值給定 ------------------
if (defineParameter) {
  // 搜尋方式選擇：廠商 or 化學物質
  queryOptions.value = [
    { method: "運作行為 與 化學物質" },
    { method: "廠商名稱 或 統一編號" },
  ];
  selectedQuery.value = "運作行為 與 化學物質";
  // selectedQuery.value = "廠商名稱 或 統一編號"

  // 取得運作行為列表
  operationOptions.value = [
    { chn: "輸入", eng: "import" },
    { chn: "貯存", eng: "storage" },
    { chn: "製造", eng: "produce" },
    { chn: "使用", eng: "usage" },
  ];
  selectedOperation.value = { chn: "貯存", eng: "storage" };
  selectedOperation.value = { chn: "使用", eng: "usage" };

  // 取得化學物質列表
  asyncGetChem = async (query) => {
    isLoadingChem.value = true;
    let res;
    if (query !== "") {
      let url = `${baseurl_ver2}/chemList?label=${query}`;
      res = await fetch(url).then((res) => res.json());
    } else {
      res = [];
    }
    let mapping = { hazard: "高風險", explosive: "易爆物" };
    res.map((i) => (i.label = `${mapping[i.database]} ${i.label} ${i.engname}`));
    // console.log(res)
    chemOptions.value = res;
    isLoadingChem.value = false;
  };

  // 取得廠商列表
  asyncGetFacCom = async (query) => {
    isLoadingFacCom.value = true;
    let res;
    if (query !== "") {
      let url = `${baseurl_ver2}/ComFacBizList?label=${query}`;
      res = await fetch(url).then((res) => res.json());
    } else {
      res = [];
    }
    // console.log(res)
    comFacOptions.value = res;
    isLoadingFacCom.value = false;
  };

  // 取得時間列表
  asyncGetTime = async () => {
    var response = await fetch(`${baseurl_ver2}/timeList`);
    var time = await response.json();
    return time;
  };
  timeOptions.value = await asyncGetTime();

  // 取得時間軸標籤
  timeTick = (val) => {
    return [...timeOptions.value].filter((i) => i.index === val)[0]["label"];
  };

  // 初始化時間
  selectedTime.value = [timeOptions.value.length - 1, timeOptions.value.length - 1];

  // 處理選擇Query選項
  handleSelectQuery = (selected) => {
    if (selected !== selectedQuery.value) {
      clearPlotlyTrace("all");
      tableData.rows = [];
      selectedChem.value = "";
      searchInTable.value = "";
    }
  };

  // table搜尋相關
  clickSearchInput = (evt) => {
    // console.log(evt)
    searchInTable.value = "";
  };

  // handle toggle row from table-lite
  handleToggleInfoFromSearchChem = async (info) => {
    let state = info.state;
    if (state) {
      let row = info.row;
      let tmp, url;
      // 取得廠商統計資料
      url = `${baseurl_ver2}/ComFacBizHistory_allStatistic?group=${row.group}`;
      // console.log(url)
      tmp = await fetch(url).then((res) => res.json());
      tmp = new DataFrame(tmp).sortBy(["time", "deptid", "operation"]).toCollection();
      comFacDetail2.value = {};
      tmp.forEach((item) => {
        if (!Object.keys(comFacDetail2.value).includes(item.name)) {
          comFacDetail2.value[item.name] = [];
        }
        comFacDetail2.value[item.name].push(item);
      });
      comFacDetail.value = tmp;
      toggleOpen.value = true;
      // console.log(emitData.value)
      tmp = [...emitData.value.data[1].data].filter((i) => i.group === row.group);
      emit("focusResult", { state: state, row: tmp });
    } else {
      toggleOpen.value = false;
      // console.log(toggleOpen.value)
      clearPlotlyTrace("fac");
    }
  };

  handleToggleInfoFromSearchFac = (info) => {
    let state = info.state;
    if (state) {
      let row = { ...info.row };
      // console.log(row)
      // tmp = [...emitData.value.data[1].proc].filter(i => i.group === row.group)
      emit("focusResult", { state: true, row: [row] });
    } else {
      clearPlotlyTrace("fac");
    }
  };

  downloadResult = async (i) => {
    if (data) {
      var wb = utils.book_new();
      wb.Props = {
        Title: "整併報表",
        Subject: "易爆物統整",
        Author: "化學雲",
        CreatedDate: new Date(),
      };
      wb.SheetNames.push("Sheet 1");
      var savedata;
      if (selectedQuery === "運作行為 與 化學物質") {
        savedata = data[1].data;
      } else {
        savedata = data[1].data;
      }
      // console.log(savedata)
      var ws_data = await json2arr(savedata);
      var ws = utils.aoa_to_sheet(ws_data);
      wb.Sheets["Sheet 1"] = ws;
      var wbout = write(wb, { bookType: "xlsx", type: "binary" });
      function s2ab(s) {
        var buf = new ArrayBuffer(s.length); //convert s to arrayBuffer
        var view = new Uint8Array(buf); //create uint8array as viewer
        for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff; //convert to octet
        return buf;
      }
      saveAs(
        new Blob([s2ab(wbout)], { type: "application/octet-stream" }),
        "易爆物與高風險化學物質統計報表.xlsx"
      );
    } else {
      alert(
        "尚未查詢出任何結果。\n此下載檔案功能為輸出查詢結果，請先進行查詢後再進行下載！"
      );
    }
  };
}
//  ---------------------------------
//  -----------  表格清單  -----------
var tableForChemSearch = reactive({
  isloading: false,
  columns: [
    {
      label: "廠商資訊",
      field: "ComFacBizName",
      width: "60%",
      sortable: true,
      display: (row) => {
        return `
                    <h5>${row.ComFacBizName}</h5>
                    <div>期別：${row.time}</div>
                    <div>資料來源：${dept_e2c.value[row.deptid]}</div>
                    <div>(統編：${row.BusinessAdminNo})</div>
                    <div>(座標：[${row.lon !== "-" ? row.lon.toFixed(2) : ""}, ${
          row.lat !== "-" ? row.lat.toFixed(2) : ""
        }])</div>
                    `;
      },
    },
    {
      label: "運作資訊",
      width: "70%",
      sortable: true,
      display: (row) => {
        return `${
          operationOptions.value.filter((i) => i.eng == row.operation)[0]["chn"]
        } ${row.Quantity.toFixed(2)} 公噸`;
        // return `${operationOptions.filter(i => i.eng == row.operation)[0]['eng']} ${row.Quantity.toFixed(2)} 公噸`;
      },
    },
  ],
  rows: computed(() => {
    return tableData.rows.filter(
      (x) =>
        String(x.BusinessAdminNo).includes(String(searchInTable.value)) ||
        x.ComFacBizName.toLowerCase().includes(searchInTable.value.toLowerCase())
    );
  }),

  totalRecordCount: computed(() => {
    return tableData.rows.length;
  }),

  sortable: {
    order: "id",
    sort: "asc",
  },
});

var tableForFacSearch = reactive({
  isloading: false,
  columns: [
    // {
    //     label: "期別",
    //     field: "time",
    //     width: "20%",
    //     sortable: true,
    //     // display: (row) => {
    //     //   return `${row.Quantity} 公噸`;
    //     // },
    // },
    // {
    //     label: "化學物質(資料來源)",
    //     field: "name",
    //     width: "30%",
    //     sortable: true,
    //     display: (row) => {
    //         return `${row.name}<br>(${row.deptid})`;
    //     },
    // },
    // {
    //     label: "運作行為",
    //     field: "operation",
    //     width: "35%",
    //     sortable: true,
    // },

    {
      label: "運作資訊",
      field: "ComFacBizName",
      width: "60%",
      sortable: true,
      display: (row) => {
        return `
                    <h5>${row.cname}</h5>
                    <div>期別：${row.time}</div>
                    <div>資料來源：${dept_e2c.value[row.deptid]}</div>
                    <div>(座標：[${row.lon !== "-" ? row.lon.toFixed(2) : ""}, ${
          row.lat !== "-" ? row.lat.toFixed(2) : ""
        }])</div>
                    `;
      },
    },
    {
      label: "運作量",
      field: "Quantity",
      width: "40%",
      sortable: true,
      display: (row) => {
        return `${
          operationOptions.value.filter((i) => i.eng == row.operation)[0]["chn"]
        } <br> ${row.Quantity.toFixed(2)} 公噸`;
        // return ` (${row.lon.toFixed(2)}, ${row.lat.toFixed(2)})<br> ${row.operation}<br> ${row.Quantity.toFixed(2)} 公噸`;
      },
    },
  ],
  rows: computed(() => {
    return tableData.rows.filter(
      (x) =>
        x.operation.includes(String(searchInTable.value)) ||
        x.name.toLowerCase().includes(searchInTable.value.toLowerCase())
    );
  }),

  totalRecordCount: computed(() => {
    return tableData.rows.length;
  }),

  sortable: {
    order: "id",
    sort: "asc",
  },
});

//  -----------  表格清單  -----------
//  ---------------------------------

//  ---------------------------------
//  ---------- 以下為 Watch ----------

// 監控化學物質選項model狀態
watch([selectedChem], ([newVal], [oldVal]) => {
  if (newVal && oldVal) {
    if (newVal.chnname !== oldVal.chnname) {
      clearPlotlyTrace("all");
      // tableData.rows = []
      toggleOpen.value = false;
    }
  } else {
    clearPlotlyTrace("all");
    tableData.rows = [];
    toggleOpen.value = false;
  }
  searchInTable.value = "";
});

// 監控運作行為選項model狀態
watch([selectedOperation], ([newVal], [oldVal]) => {
  // console.log(newVal, oldVal)
  if (newVal && oldVal) {
    if (newVal.chnname !== oldVal.chnname) {
      clearPlotlyTrace("all");
      // tableData.rows = []
      toggleOpen.value = false;
    }
  } else {
    clearPlotlyTrace("all");
    tableData.rows = [];
    toggleOpen.value = false;
  }
  searchInTable.value = "";
});

// 監控時間選項model狀態
watch(selectedTime, (newTime, oldTime) => {
  // console.log(newTime[0], oldTime[0], newTime[1], oldTime[1])
  if (newTime[0] !== oldTime[0] || newTime[1] !== oldTime[1]) {
    clearPlotlyTrace("all");
    // tableData.rows = []
    toggleOpen.value = false;
  }
  searchInTable.value = "";
});

// watch 表格搜尋選項
watch(
  () => searchInTable.value,
  (val_old, val_new) => {
    if (val_old.length > 0 || val_old !== val_new) {
      toggleOpen.value = false;
      clearPlotlyTrace("fac");
    }
  }
);

// watch 化學物質與廠商搜尋
watch(
  [selectedQuery, selectedOperation, selectedChem, selectedComFac, selectedTime],
  async (newVal, oldVal) => {
    var [newQuery, newOperation, newChem, newComFac, newTime] = newVal;
    var [oldQuery, oldOperation, oldChem, oldComFac, oldTime] = oldVal;
    let newTimeObject = [];
    // console.log(newChem)

    // 將時間index轉為時間
    for (let i = 0; i < newTime.length; i++) {
      for (let j = 0; j < timeOptions.value.length; j++) {
        if (timeOptions.value[j].index === newTime[i]) {
          newTimeObject.push({ ...timeOptions.value[j] });
        }
      }
    }
    var [t0, t1] = newTimeObject.map((i) => i.time);

    if (newQuery === "運作行為 與 化學物質") {
      if (
        (newChem && oldChem && newChem.chnname !== oldChem.chnname) ||
        (newOperation && oldOperation && newOperation.chn !== oldOperation.chn) ||
        oldTime[0] !== newTime[0] ||
        oldTime[1] !== newTime[1] ||
        (!oldChem && newChem) ||
        (!oldOperation && newOperation)
      ) {
        // console.log(newChem)
        let chemCasno = newChem.casno;
        let chnChemName = newChem.chnname;
        let operation = newOperation.eng;

        // descripition
        // console.log(" >> 化學物查詢 ")
        // console.log(`    >> 搜尋 --> ${newTimeObject[0].time}~${newTimeObject[1].time}： ${chnChemName} --> ${operation}`)

        // fetch data
        data = [
          {
            dataType: "city",
            url: `${baseurl_ver2}/ComFacBizHistory_allStatistic`,
            para: `?casno=${chemCasno}&operation=${operation}&time_ge=${t0}&time_le=${t1}&method=city`,
          },
          {
            dataType: "faccon",
            url: `${baseurl_ver2}/ComFacBizHistory_allStatistic`,
            para: `?casno=${chemCasno}&operation=${operation}&time_ge=${t0}&time_le=${t1}&method=statistic`,
          },
        ];
        for (let ind of data.keys()) {
          var fullUrl = `${data[ind]["url"]}${data[ind]["para"]}`;
          data[ind].fullUrl = fullUrl;
          // console.log(fullUrl)
          data[ind].data = await fetch(fullUrl).then((res) => res.json());
        }

        //
        // console.log(data)
        let data_city = data[0].data;
        let data_fac = data[1].data;
        emitData.value = {
          time: newTimeObject,
          chem: newChem,
          operation: newOperation,
          data: data,
        };
        tableData.rows = data_fac;
        emit("queryFromChemSearch", emitData);
      }
    } else if (newQuery === "廠商名稱 或 統一編號") {
      if (newComFac !== "" && (newComFac !== oldComFac || newTime !== oldTime)) {
        // console.log(" >> 廠商查詢 ")
        // console.log(`    >> 搜尋${newComFac}、${newTime}`)
        // console.log(newComFac)
        data = [
          {
            dataType: "faccon",
            url: `${baseurl_ver2}/ComFacBizHistory_allStatistic`,
            para: `?time_ge=${t0}&time_le=${t1}&group=${newComFac.group}&method=statistic`,
            // para: `?time_ge=${t0}&time_le=${t1}&ComFacBizName=${newComFac}`
          },
        ];
        for (let ind of data.keys()) {
          var fullUrl = `${data[ind]["url"]}${data[ind]["para"]}`;
          // console.log(fullUrl)
          data[ind].fullUrl = fullUrl;
          data[ind].data = await fetch(fullUrl).then((res) => res.json());
        }
        // console.log(data)
        // console.log(data)
        var data_fac = data[0].data;
        console.log(data_fac);
        tableData.rows = data_fac;
        emitData.value = { time: newTimeObject, comFac: newComFac, data: data };
        emit("queryFromFacSearch", emitData);
        // var data_fac_merged = data[1].data

        // data_fac_merged.map(i => i.operation = operationOptions.value.filter(j => j.eng === i.operation)[0]['chn'])
        // data_fac_merged.map(i => i.deptid = dept_e2c.value[i.deptid])
        // data_fac.map(i => i.operation = operationOptions.value.filter(j => j.eng === i.operation)[0]['chn'])
        // data_fac.map(i => i.deptid = dept_e2c.value[i.deptid])

        // data[0].proc = data_fac
        // // console.log(data_fac_merged)
        // data[1].proc = data_fac_merged
        // // console.log(data[1].proc)
        // console.log(data)
        // // console.log(data_fac_merged)
        // // console.log(data[1].proc)
        // tableData.rows = data_fac
        // emitData.value = { time: newTimeObject, comFac: newComFac, data: data }
        // emit('queryFromFacSearch', emitData)
      }
    }
  }
);

function tableLoadingFinish() {
  // 修改換頁樣式
  let pagination = document.querySelector(".vtl-paging");
  [...pagination.children].forEach((i) => {
    i.className = i.className.replace("col-sm-12", "col-12").replace("col-md-4", "");
  });
}
</script>

<style scoped>
@media screen and (min-width: 340px) {
  #searchPannel {
    z-index: 1000;
    width: 320px;
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    background-color: rgba(255, 255, 255, 0.807);
    border-radius: 5px;
    /* border: 1px solid grey; */
    margin: 10px;
  }
}

@media screen and (max-width: 340px) {
  #searchPannel {
    z-index: 1000;
    width: 100%;
    box-shadow: 0 2px 4px rgb(0 0 0 / 20%), 0 -1px 0px rgb(0 0 0 / 2%);
    background-color: white;
    border-radius: 5px;
    /* border: 1px solid grey; */
  }
}

@media screen and (min-width: 768px) {
}

@media screen and (max-width: 768px) {
}

.togglebtn {
  cursor: pointer;
  font-size: 25px;
  z-index: 2000;
  line-height: 41px;
}

div.card,
div.card-body {
  padding: 1px;
}

::v-deep(.vtl-table) {
  /* overflow-x: hidden; */
}

::v-deep(.vtl-row),
::v-deep(.vtl-card),
::v-deep(.vtl),
::v-deep(.vtl-card-body),
::v-deep(.vtl-table),
::v-deep(.vtl-tbody-td),
::v-deep(.vtl-tbody) {
  background-color: rgba(240, 245, 240, 0);
}

::v-deep(.vtl-tbody-td div) {
  overflow-x: scroll;
  /* max-height: 72px; */
  /* max-width: 300px; */
}

::v-deep(.multiselect__single) {
  padding: 0px;
  padding-left: 15px;
  margin: 0px;
  width: auto;
  line-height: 41px;
  background-color: none;
  max-height: 41px;
  overflow: hidden;
}

::v-deep(.multiselect__tags) {
  padding: 0px;
  padding-left: 15px;
  line-height: 41px;
  height: 41px;
  background: rgba(255, 255, 255, 0);
  border-radius: 0px;
  border-width: 0px;
}

::v-deep(.multiselect__placeholder) {
  padding-left: 15px;
  margin: 0px;
  background-color: none;
}

::v-deep(.multiselect__input) {
  padding-left: 15px;
  margin: 0px;
  line-height: 41px;
  height: 41px;
  width: auto;
  /* width: calc(100%-20px); */
  background-color: none;
}

.noselect {
  -webkit-touch-callout: none;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

.row > * {
  padding-left: 0px;
  padding-right: 0px;
}

/* ::v-deep(.multiselect__tags) {
    background: rgba(255, 255, 255, 0);
    border-radius: 0px;
    border-width: 0px;
} */

@media screen and (min-width: 340px) {
  #timeslider {
    line-height: 41px;
    height: 41px;
    padding-top: 12px;
  }
}

@media screen and (max-width: 340px) {
  #timeslider {
    line-height: 41px;
    height: 41px;
    padding-top: 12px;
  }
}

.slider-target {
  padding-left: 20px;
  padding-right: 20px;
}

.slider-red {
  --slider-connect-bg: #ef4444;
  --slider-tooltip-bg: #ef4444;
  --slider-handle-ring-color: #ef444430;
}

#searchResult {
  /* width: */
  margin-top: 155px;
  margin-bottom: 40px;
}

.slide-leave-active,
.slide-enter-active {
  transition: all 1s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

#navbar {
  width: 340px;
  height: 100vh;
  background-color: rgb(0, 0, 0);
  background-color: rgba(0, 0, 0, 0.9);
  overflow-x: hidden;
  background-color: rgba(240, 245, 240, 0.9);
  box-shadow: 0 -1px 24px rgba(0, 0, 0, 0.4);
}

.download {
  border: 1px solid black;
  background-color: rgba(200, 240, 200, 0.5);
  padding: 2px;
  border-radius: 5px;
}

.download:hover {
  color: red;
}

.tab-content input {
  width: 130px;
}

.form-select {
  width: 40%;
  margin-left: 10px;
  display: inline-block;
}
</style>
