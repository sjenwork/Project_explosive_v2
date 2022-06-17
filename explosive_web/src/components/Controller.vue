<template>
  <!-- NavBar -->
  <transition name="slide">
    <div
      id="navbar"
      v-show="navbarStatus"
      class="fixed"
      :class="{ withAuto: isExpand }"
      v-touch:swipe.left="swipeHandler"
    >
      <!-- 圖表結果 -->
      <div id="searchResult">
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <!-- 表格資訊標籤 -->
          <li class="nav-item w-50" role="presentation">
            <button
              class="nav-link w-100 active"
              id="table-tab"
              data-bs-toggle="tab"
              data-bs-target="#table"
              type="button"
              role="tab"
              aria-controls="table"
              aria-selected="true"
            >
              廠商列表
            </button>
          </li>
          <!-- 圖資訊標籤 -->
          <li class="nav-item w-50" role="presentation">
            <button
              class="nav-link w-100"
              id="chart-tab"
              data-bs-toggle="tab"
              data-bs-target="#chart"
              type="button"
              role="tab"
              aria-controls="chart"
              aria-selected="false"
            >
              統計圖
            </button>
          </li>
        </ul>
        <div class="tab-content" id="myTabContent">
          <!-- 表格資訊 -->
          <div
            class="tab-pane fade show active"
            id="table"
            role="tabpanel"
            aria-labelledby="table-tab"
            style="height: calc(100vh - 230px); overflow-y: scroll"
          >
            <template v-if="tableData.rows.length > 0">
              <!-- <div class="m-3 row">
                <label for="searchInTable" class="col-2 col-form-label">查詢：</label>
                <div class="col-sm-10">
                  <input
                    type="text"
                    class="form-control"
                    id="searchInTable"
                    v-model="searchInTable"
                    @click="clickSearchInput"
                    onfocus="this.value=''"
                  />
                </div>
              </div> -->
              <div class="btn-box d-flex justify-content-start mx-3 my-1">
                <!-- <button
                  type="button"
                  class="btn btn-secondary mx-2 btn-sm"
                  @click="latestDeclaration"
                >
                  最新申報
                </button> -->
                <button
                  type="button"
                  class="btn btn-secondary ml-2 btn-sm"
                  @click="downloadResult"
                >
                  報表下載
                  <font-awesome-icon :icon="faArrowCircleDown" />
                </button>
              </div>
              <!-- </div> -->
              <template v-if="isLoadingChemData">
                <div style="margin-top: 100px">讀取中...</div>
              </template>
              <template v-if="!isLoadingChemData">
                <template v-if="selectedQuery === '運作行為 與 化學物質'">
                  <table-lite
                    :is-static-mode="true"
                    :is-loading="tableForChemSearch.isLoading"
                    :columns="tableForChemSearch.columns"
                    :rows="tableForChemSearch.rows"
                    :total="tableForChemSearch.totalRecordCount"
                    :sortable="tableForChemSearch.sortable"
                    @is-finished="tableLoadingFinish"
                    @row-clicked="handleToggleInfoFromSearchChem"
                  >
                  </table-lite>
                </template>

                <template v-else-if="selectedQuery === '廠商名稱 或 統一編號'">
                  <div style="padding-left: 16px; padding-top: 0px; text-align: left">
                    共運作
                    <span style="color: red; font-weight: bold">
                      {{
                        [...new Set(tableForFacSearch.rows.map((i) => i.cname))].length
                      }}
                    </span>
                    項化學物質
                  </div>
                  <table-lite
                    :is-static-mode="true"
                    :is-loading="tableForFacSearch.isLoading"
                    :columns="tableForFacSearch.columns"
                    :rows="tableForFacSearch.rows"
                    :total="tableForFacSearch.totalRecordCount"
                    :sortable="tableForFacSearch.sortable"
                    @is-finished="tableLoadingFinish"
                  >
                    <!-- @row-clicked="handleToggleInfoFromSearchFac" -->
                    <!-- :toggleOpen="toggleOpen" -->
                  </table-lite>
                </template>
              </template>
            </template>
            <!-- <template v-if="tableData.rows.length === 0">
              <template v-if="selectedChem.length !== 0">
                <div style="padding: 20px; margin-top: 10px">
                  廠商與此期間並未申報任何化學物質，請調整申報時間，以作進一步的查詢。
                </div>
              </template>
              <template v-if="selectedOperation.length !== 0">
                <div style="padding: 20px; margin-top: 10px">
                  廠商與此期間並未申報任何化學物質，請調整申報時間，以作進一步的查詢。
                </div>
              </template>
            </template> -->
          </div>
          <!-- 圖資訊 -->
          <div
            class="tab-pane fade"
            id="chart"
            role="tabpanel"
            aria-labelledby="chart-tab"
            style="height: calc(100vh - 230px); overflow-y: scroll"
          >
            <template v-if="tableData.rows.length > 0">
              <div style="padding: 5px; margin-top: 10px; font-size: 19px">
                廠商運作化學物質
              </div>
              <div id="chart"></div>
            </template>
            <!-- <template v-if="tableData.rows.length === 0">
              <template v-if="selectedChem.length !== 0">
                <div style="padding: 20px; margin-top: 10px">
                  廠商與此期間並未申報任何化學物質，請調整申報時間，以作進一步的查詢。
                </div>
              </template>
              <template v-if="selectedOperation.length !== 0">
                <div style="padding: 20px; margin-top: 10px">
                  廠商與此期間並未申報任何化學物質，請調整申報時間，以作進一步的查詢。
                </div>
              </template>
            </template> -->
          </div>
        </div>
      </div>
    </div>
  </transition>
  <!-- 搜尋選單 -->
  <div class="fixed">
    <!-- :class="{'withAuto': isExpand}" -->
    <div id="searchPannel">
      <div class="container-xs px-0">
        <template v-if="true">
          <div class="row rounded-lg mx-0">
            <!-- 選單 -->
            <div
              class="col-2 togglebtn noselect border-end"
              @click="navbarStatus = !navbarStatus"
              @dblclick="handleNavbar"
            >
              &#9776;
            </div>
            <div class="col-10 border-end ps-0 d-flex">
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
              <div class="btn-box">
                <span @click="handleFullScreen" v-if="isFullscreen">
                  <i class="fa-solid fa-compress"></i>
                </span>
                <span @click="handleFullScreen" v-if="!isFullscreen">
                  <!-- <template > -->
                  <i class="fa-solid fa-expand"></i>
                </span>
                <!-- </template>
                  <template v-if="!isFullscreen">
                    <i class="fa-solid fa-compress"></i>
                  </template> -->
                <!-- <span v-if="isFullscreen" @click="handleFullScreen">
                </span> -->
              </div>
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
                <span slot="noResult"> 未找到任何資訊 </span>
              </multiselect>
            </div>
          </div>
        </template>
        <template v-else-if="selectedQuery === '廠商名稱 或 統一編號'">
          <div class="row rounded-lg mx-0">
            <div class="col-12 border-top ps-0">
              <multiselect
                v-model="selectedComFac"
                placeholder="請輸入統一編號、廠商名稱或工登"
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
                <span slot="noResult"> 未找到任何資訊 </span>
                <!-- <template v-slot:no-result>
                                    此為無效值，請更改搜索
                                </template>
                                  <template v-slot:no-options>
                                    此無清單列表
                                  </template> -->
              </multiselect>
            </div>
          </div>
        </template>
        <template v-if="true">
          <div class="row rounded-lg mx-0 row rounded-lg mx-0 border-top">
            <!-- <div class="col-12 border-top ps-0" id="latestBox"> -->
            <div class="" id="latestBox">
              <input
                class=""
                type="checkbox"
                value=""
                id="flexCheckChecked"
                style="width: 16px; height: 16px; margin-right: 6px"
                v-model="isLatest"
              />
              <label
                class=""
                for="flexCheckChecked"
                style="height: 16px; margin-right: 6px"
              >
                以各廠商最新申報期別查詢
              </label>
            </div>
            <!-- </div> -->
          </div>
        </template>
        <template v-if="!isLatest">
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
        <template v-if="isLatest">
          <div class="row rounded-lg mx-0">
            <div class="col-12 border-top ps-0" id="latestBox">最新申報期別</div>
          </div>
        </template>
      </div>
    </div>
  </div>
  <!-- 點擊廠商彈出列表modal -->
  <div
    id="tableDetails"
    class="modal fade"
    data-bs-keyboard="false"
    tabindex="-1"
    aria-labelledby="staticBackdropLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-dialog-centered modal-xl">
      <div class="modal-content" style="background-color: rgba(244, 244, 244, 0.8)">
        <div class="modal-header">
          <h5 class="modal-title" id="staticBackdropLabel">
            {{ selectedComFacInChemSearch }}
          </h5>

          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <template v-if="tableData.rows.length > 0 && selectedComFacInChemSearch">
          <div>
            <div
              style="
                font-size: 16px;
                padding-left: 16px;
                padding-top: 0px;
                text-align: left;
              "
            >
              統編：{{
                tableData.rows.filter((i) => i.comname === selectedComFacInChemSearch)[0]
                  .adminno
              }}
            </div>
            <div
              style="
                font-size: 16px;
                padding-left: 16px;
                padding-top: 0px;
                text-align: left;
              "
            >
              地址：{{
                tableData.rows.filter((i) => i.comname === selectedComFacInChemSearch)[0]
                  .addr
              }}
            </div>
            <div
              style="
                font-size: 16px;
                padding-left: 16px;
                padding-top: 0px;
                text-align: left;
              "
            >
              裁罰資料：共
              <span style="color: red; font-weight: bold">{{
                PunishmentDataCnt.cnt
              }}</span>
              筆
            </div>
          </div>
        </template>
        <div style="padding-left: 16px; padding-top: 10px; text-align: left">
          共運作
          <span style="color: red; font-weight: bold">
            {{ [...new Set(comFacDetail.map((i) => i.cname))].length }}
          </span>
          項化學物質
        </div>
        <div
          style="padding-left: 16px; padding-top: 0px; text-align: left; font-size: 0.8em"
        >
          (註：以下列出皆為原始資料，但不顯示運作量為 0 的數據。)
        </div>
        <div class="modal-body">
          <div style="margin-top: 10px; margin-bottom: 30px; width: 100%">
            <div
              style="
                width: 100%;
                overflow-x: hidden;
                background-color: rgba(255, 255, 255, 0.5);
              "
              class="card"
              :value="chem"
              v-for="(chem, index) in [...new Set(comFacDetail.map((i) => i.cname))]"
              :key="index"
            >
              <div v-if="!chem">
                廠商未運作任何化學物質
                <span style="color: rgba(244, 244, 244, 0)">（ps.理論上是錯的））</span>
              </div>

              <div
                v-if="chem"
                class="card-header"
                style="text-align: left"
                @click="HandleSelectedChemInChemSearch"
              >
                <span> {{ index + 1 }}. {{ chem }} </span>
                <span
                  style="
                    margin-left: 20px;
                    background-color: rgb(238, 180, 18);
                    border-radius: 10px;
                    padding: 2px;
                    font-size: 0.3rem;
                    padding-left: 5px;
                    padding-right: 5px;
                  "
                  v-for="cat in [
                    ...new Set(
                      comFacDetail.filter((i) => i.cname === chem).map((i) => i.cat)
                    ),
                  ]"
                >
                  {{ catlist[cat] }}
                </span>
              </div>
              <div
                :id="chem"
                v-if="
                  selectedChemInChemSearchStatus && chem === selectedChemInChemSearchName
                "
              >
                <div
                  class="card-body"
                  style="overflow-x: scroll background-color: rgba(255, 255, 255, 0.7)"
                >
                  <table
                    class="table table-hover"
                    style="table-layout: fixed; width: 100%"
                  >
                    <thead>
                      <tr>
                        <th class="col-3" style="text-align: left; width: 10%">#</th>
                        <th class="col-3" style="text-align: left; width: 20%">
                          上傳期別
                        </th>
                        <th class="col-3" style="text-align: left; width: 20%">來源</th>
                        <!-- <th class="col-3" style="text-align: left; width: 20%">
                          化學物質類型
                        </th> -->
                        <th class="col-3" style="text-align: left; width: 30%">
                          運作狀況
                        </th>
                        <th>id</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="(item, index) in comFacDetail.filter(
                          (i) => i.cname == chem
                        )"
                        :value="item.name"
                        :key="index"
                      >
                        <td class="text-left" style="width: 10%">{{ index + 1 }}</td>
                        <td class="text-left" style="width: 20%">
                          {{ item.declaretime }}
                        </td>
                        <td class="text-left" style="width: 20%">
                          {{ dept_e2c[item.deptid] }}
                        </td>
                        <!-- <td class="text-left" style="width: 20%">
                          {{ catlist[item.cat] }}
                        </td> -->
                        <td class="text-left" style="width: 30%">
                          <!-- <template v-if="item.storageQ > 0"> -->
                          <div style="padding: 0px">貯存 {{ item.storageQ }} 公噸</div>
                          <!-- </template> -->
                          <!-- <template v-if="item.prodQ > 0"> -->
                          <div style="padding: 0px">製造 {{ item.prodQ }} 公噸</div>
                          <!-- </template> -->
                          <!-- <template v-if="item.usageQ > 0"> -->
                          <div style="padding: 0px">製造 {{ item.usageQ }} 公噸</div>
                          <!-- </template> -->
                          <!-- <template v-if="item.importQ > 0"> -->
                          <div style="padding: 0px">製造 {{ item.importQ }} 公噸</div>
                          <!-- </template> -->
                        </td>
                        <td>{{ item.id }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer justify-content-center">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            關閉
          </button>
        </div>
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
import { clearPlotlyTrace } from "./js/utility.js";
import { faArrowCircleDown } from "@fortawesome/free-solid-svg-icons";
import { utils, write } from "xlsx";
import { saveAs } from "file-saver";
import { Modal, Tab } from "bootstrap";
import Plotly from "plotly.js-dist-min";
import screenfull from "screenfull";

var explosive_list = [
  { casno: "67-64-1", cname: "丙酮", ename: "acetone" },
  { casno: "74-86-2", cname: "乙炔", ename: "Acetylene" },
  { casno: "6484-52-2", cname: "硝酸銨", ename: "Ammonium nitrate" },
  { casno: "12190-79-3", cname: "鋰電池", ename: "Lithium cobaltate" },
  { casno: "7439-93-2", cname: "鋰", ename: "Lithium" },
  { casno: "1333-74-0", cname: "氫氣", ename: "hydrogen" },
  { casno: "108-88-3", cname: "甲苯", ename: "methyl-Benzene" },
  { casno: "67-63-0", cname: "異丙醇", ename: "Isopropanol" },
  { casno: "7775-09-9", cname: "氯酸鈉", ename: "Sodium chlorate" },
  { casno: "7803-62-5", cname: "矽甲烷", ename: "Silane" },
  { casno: "107-13-1", cname: "丙烯腈", ename: "Cyanoethylene" },
  { casno: "75-21-8", cname: "環氧乙烷", ename: "Ethene oxide" },
  { casno: "75-56-9", cname: "環氧丙烷", ename: "Propyleneoxide" },
  { casno: "7722-84-1", cname: "過氧化氫", ename: "Hydrogen peroxide" },
  { casno: "1338-23-4", cname: "過氧化丁酮", ename: "2-Butanone peroxide" },
];

onMounted(() => {
  // click point in map
  let mymap = document.querySelector("#map");
  // let piechart = document.querySelector("#piechart");

  // mymap.on("plotly_click", (i) => {
  //   try {
  //     if (selectedQuery.value === "運作行為 與 化學物質") {
  //       if (toggleOpen.value) {
  //         toggleOpen.value = false;
  //         // document.querySelector('.vtl-tbody tr').click()
  //       }
  //       var clickpoint = i.points[0].text.split(":")[0];
  //       // console.log(clickpoint)
  //       searchInTable.value = clickpoint;
  //       // toggleOpen.value = true
  //       // setTimeout(() => {
  //       //     document.querySelector('.vtl-tbody tr').click()
  //       // }, 500);
  //     }
  //   } catch (e) {
  //     if (toggleOpen.value) {
  //       // console.log(1)
  //       // toggleOpen.value = false
  //       // document.querySelector('.vtl-tbody tr').click()
  //       searchInTable.value = "";
  //       clearPlotlyTrace("fac");
  //     }
  //   }
  // });

  window.addEventListener("keydown", (i) => {
    var className = document.querySelector("div.modal").className;
    // document.querySelector("div.modal .modal-footer button").click();
    if (i.key === "Enter") {
      if (className.includes("show")) {
        document.querySelector("div.modal .modal-footer button").click();
      } else {
        // research();
      }
    } else if (i.key === "Escape") {
      data.value = [];
      tableData.rows = [];
      clearPlotlyTrace("all");
      clearPlotlyTrace("chart");
      // selectedChems.value = [];
      // selectedFacs.value = [];
      // displayedChem.value = {};
      // displayedFac.value = {};
    }
  });

  //初始化
  asyncGetChem("1"); //初始化化學物質下拉選單，隨意key
  asyncGetFacCom("1");
  getTime();

  // getWidth();
  // window.addEventListener('resize', getWidth);
  // var triggerEl = document.querySelector("#myTab #chart-tab");
  // var tab = new Tab(triggerEl);
  // tab.show();
  // console.log(Tab.getInstance(triggerEl));
  // Tab.getInstance(triggerEl); // Select tab by name
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
var timeLen = ref("");
var selectedTime = ref([0, 0]); // 選擇的時間
var isExpand = ref(false); // 是否要全屏
var isFullscreen = ref(false); // 是否要全屏
var selectedComFacInChemSearch = ref(""); // 化學物質搜尋時點擊的廠商
var selectedChemInChemSearchStatus = ref(false); // 化學物質搜尋時點擊廠商後選定的化學物質
var selectedChemInChemSearchName = ref(""); // 化學物質搜尋時點擊廠商後選定的化學物質
var selectedChemInChemSearchName0 = ref(""); // 化學物質搜尋時點擊廠商後選定的化學物質 前一個

// base url
var baseurl = import.meta.env.VITE_API_BASE_URL;
var baseurl_ver2 = import.meta.env.VITE_API_BASE_URL_ver2;
var baseurl_ver4 = import.meta.env.VITE_API_BASE_URL_ver4;
var baseurl_ver5 = import.meta.env.VITE_API_BASE_URL_ver5;

// 函數 與 相關參數
var isLoadingChem = ref(false);
var isLoadingChemData = ref(false);
var isLoadingFacCom = ref(false);
var asyncGetChem; // 取得化學物質列表
var asyncGetFacCom; // 取得廠商列表
var getTime; // 取得時間列表

var timeTick;

var data;
var emitData = ref();
// toggle navbar
var navbarStatus = ref(
  document.querySelector("body").clientWidth > 760 ? ref(true) : ref(false)
);

// toggle table-lite row
var handleToggleInfoFromSearchChem;
var handleToggleInfoFromSearchFac;
var comFacDetail = ref([]);
var comFacDetail2 = ref([]);
var toggleOpen = ref(false);
var searchInTable = ref("");
var tableData = reactive({ rows: [] });
var clickSearchInput;
// console.log(tableData.rows.length)

var handleSelectQuery;
var handleSelectChem;
// var clearPlotlyTrace

var downloadResult;
var latestDeclaration;
var isLatest = ref(false);
var PunishmentDataCnt = ref("");

// table

var catlist = ref({
  explosive: "易爆物",
  hazardous: "高風險",
});

var dept_e2c = ref({
  COA001: "農委會防檢局",
  EPZA: '"科技產業園區(經濟部加工出口區)"',
  MND: "國防部",
  MOEA001: "經濟部中部辦公室",
  MOEA002: "經濟部工業局(自行設置)", //
  MOEA005: "經濟部礦務局",
  MOF001: "財政部關務署",
  MOF002: "財政部國庫署", //
  MOI001: "內政部消防署",
  MOL001: "勞動部職安署",
  MOST001: "科技部竹科管理局",
  MOST002: "科技部中科管理局",
  MOST003: "科技部南科管理局",
  MOTC001: "交通部臺灣港務公司",
  TCSB: "環保署化學局",
  CAA: "交通部民用航空局",
  EPA003: "環保署土基會",
});

// 需要優化....
var HandleSelectedChemInChemSearch = (i) => {
  // console.log(i.target.innerHTML);
  //console.log(i.target.tagName.toLowerCase());
  selectedChemInChemSearchName0.value = selectedChemInChemSearchName.value;
  if (i.target.tagName.toLowerCase() === "span") {
    selectedChemInChemSearchName.value = i.target.innerText.split(".")[1].trim();
  } else {
    selectedChemInChemSearchName.value = i.target
      .querySelector("span")
      .innerHTML.split(".")[1]
      .trim();
  }
  //console.log(selectedChemInChemSearchName0.value, selectedChemInChemSearchName.value);
  if (
    selectedChemInChemSearchName0.value === selectedChemInChemSearchName.value ||
    selectedChemInChemSearchName0.value === ""
  ) {
    selectedChemInChemSearchStatus.value = !selectedChemInChemSearchStatus.value;
  } else if (
    selectedChemInChemSearchName0.value !== selectedChemInChemSearchName.value &&
    !selectedChemInChemSearchStatus.value
  ) {
    selectedChemInChemSearchStatus.value = true;
  }
};

var handleFullScreen = (i) => {
  isFullscreen.value = !isFullscreen.value;
  if (screenfull.isEnabled) {
    if (isFullscreen.value) {
      screenfull.request();
    } else {
      screenfull.exit();
    }
  }
};

var handleNavbar = (i) => {
  //console.log(i);
};

var swipeHandler = (i) => {
  navbarStatus.value = !navbarStatus.value;
  //console.log(i);
};

const getWidth = () => {
  setTimeout(() => {
    let newWidth = document.querySelector("body").clientWidth;
    // console.log("newWidth-", newWidth);
    if (newWidth <= 450 && isExpand.value) {
      isExpand.value = false;
      // console.log("isExpand-", isExpand.value);
    } else if (newWidth > 451 && !isExpand.value) {
      isExpand.value = true;
    }
  }, 10);
};
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

var object2para = (obj) => {
  let res = [];
  Object.entries(obj).forEach((i) => {
    res.push(`${i[0]}=${i[1]}`);
  });
  return res.join("&");
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
  // selectedQuery.value = "廠商名稱 或 統一編號";

  // 取得運作行為列表
  operationOptions.value = [
    { chn: "輸入", eng: "import" },
    { chn: "貯存", eng: "storage" },
    { chn: "製造", eng: "prod" },
    { chn: "使用", eng: "usage" },
  ];
  selectedOperation.value = { chn: "貯存", eng: "storage" };
  selectedOperation.value = { chn: "使用", eng: "usage" };

  // 處理選擇Query選項
  handleSelectQuery = (selected) => {
    if (selected !== selectedQuery.value) {
      clearPlotlyTrace("all");
      clearPlotlyTrace("chart");
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
    var tableDetailsModal = new Modal(document.getElementById("tableDetails"));
    tableDetailsModal.show();
    // console.log("info", info);
    let state = info.state;
    let id = info.id;
    if (state) {
      let row = info.row;
      if (row.X === "") {
        alert("此廠商無座標資訊，將不標記廠商位置");
      }
      // console.log(row);
      let tmp, url;
      // 取得廠商統計資料
      url = `${baseurl_ver4}/mergedRecords/data_list?company_name=${row.comname_merged}&limit=1000&display=False`;
      //  console.log(url);
      tmp = await fetch(url).then((res) => res.json());
      console.log(tmp);
      tmp = tmp.sort((a, b) => a.cname.localeCompare(b.cname, "zh-hant"));

      // 取得裁罰資料
      let adminno = tmp[0].adminno;
      selectedComFacInChemSearch.value = row.comname;
      url = `${baseurl_ver5}/Punishment/${adminno}`;
      var tmp2 = await fetch(url).then((res) => res.json());
      PunishmentDataCnt.value = tmp2;
      //  console.log(url);
      // tmp = new DataFrame(tmp)
      //   .sortBy(["declaretime", "deptid", "operation"])
      //   .toCollection();
      // comFacDetail2.value = {};
      // tmp.forEach((item) => {
      //   if (!Object.keys(comFacDetail2.value).includes(item.name)) {
      //     comFacDetail2.value[item.name] = [];
      //   }
      //   comFacDetail2.value[item.name].push(item);
      // });
      comFacDetail.value = tmp;
      // // toggleOpen.value = true
      // // console.log(emitData.value)
      // tmp = [...emitData.value.data[1].data].filter((i) => i.group === row.group);
      emit("focusResult", { state: state, row: row, id: id });
    } else {
      // toggleOpen.value = false
      // console.log(toggleOpen.value)
      //  console.log("============");
      clearPlotlyTrace("fac");
    }
  };

  handleToggleInfoFromSearchFac = (info) => {
    //  console.log(info);
    var tableDetailsModal = new Modal(document.getElementById("tableDetails"));
    tableDetailsModal.show();
    let state = info.state;
    if (state) {
      let row = { ...info.row };
      //  console.log(row);
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

  // 最新期別
  latestDeclaration = () => {
    selectedTime.value = [timeOptions.value.length - 1, timeOptions.value.length - 1];
  };
}
// --------------------------------------------------------------------------------
//  -----------  表格清單  -----------
var tableForChemSearch = reactive({
  isloading: false,
  columns: [
    {
      label: "廠商資訊",
      // field: "comname",
      width: "60%",
      sortable: true,
      display: (row) => {
        return ` <h5>${row.comname}</h5>
        <div>期別：${row.declaretime}</div>
        <div>資料來源：${dept_e2c.value[row.deptid]}</div>
        <div>(統編：${row.adminno})</div>
        `;
      },
    },
    {
      label: "運作資訊",
      width: "40%",
      sortable: true,
      display: (row) => {
        return `${
          operationOptions.value.filter((i) => i.eng == row.operation)[0]["chn"]
        } ${row.Q.toFixed(2)} 公噸`;
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
    {
      label: "運作資訊",
      width: "60%",
      sortable: true,
      display: (row) => {
        return `
            <h5>${row.cname}</h5>
            <div>期別：${row.declaretime}</div>
            <div>資料來源：${dept_e2c.value[row.deptid]}</div>
            `;
      },
    },
    {
      label: "運作量",
      width: "40%",
      sortable: true,
      display: (row) => {
        return `${
          operationOptions.value.filter((i) => i.eng == row.operation)[0]["chn"]
        } <br> ${row.Q.toFixed(2)} 公噸`;
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
// --------------------------------------------------------------------------------

// --------------------------------------------------------------------------------
//  ---------- 以下為 Watch ----------

// 監控化學物質選項model狀態
watch([selectedChem], ([newVal], [oldVal]) => {
  // console.log("newVal", newVal);
  // console.log("oldVal", oldVal);
  if (newVal && oldVal) {
    if (newVal !== oldVal) {
      clearPlotlyTrace("all");
      clearPlotlyTrace("chart");
      // tableData.rows = []
      toggleOpen.value = false;
    }
  } else {
    clearPlotlyTrace("all");
    clearPlotlyTrace("chart");
    tableData.rows = [];
    toggleOpen.value = false;
  }
  searchInTable.value = "";
});

// 監控運作行為選項model狀態
watch([selectedOperation], ([newVal], [oldVal]) => {
  // console.log(newVal, oldVal)
  if (newVal && oldVal) {
    if (newVal !== oldVal) {
      clearPlotlyTrace("all");
      clearPlotlyTrace("chart");
      // tableData.rows = []
      toggleOpen.value = false;
    }
  } else {
    clearPlotlyTrace("all");
    clearPlotlyTrace("chart");
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
    clearPlotlyTrace("chart");
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

watch(isLatest, (newval, oldval) => {
  clearPlotlyTrace("all");
  clearPlotlyTrace("chart");
  // tableData.rows = []
  toggleOpen.value = false;
  //console.log(newval);
});

// watch 化學物質與廠商搜尋
watch(
  [
    selectedQuery,
    selectedOperation,
    selectedChem,
    selectedComFac,
    selectedTime,
    isLatest,
  ],
  async (newVal, oldVal) => {
    var [newQuery, newOperation, newChem, newComFac, newTime, newIsLatest] = newVal;
    var [oldQuery, oldOperation, oldChem, oldComFac, oldTime, oldIsLatest] = oldVal;

    var t0 = timeOptions.value[selectedTime.value[0]];
    var t1 = timeOptions.value[selectedTime.value[1]];
    //  console.log(t0, t1);
    // tableData.rows = [];
    isLoadingChemData.value = true;

    //  console.log(newIsLatest, newQuery);
    var para_latest = "";
    if (newIsLatest) {
      para_latest = "&time_latest=True";
    }

    if (newQuery === "運作行為 與 化學物質") {
      //  console.log(123, newChem, oldChem);
      if (
        (newChem && oldChem && newChem !== oldChem) ||
        (newOperation && oldOperation && newOperation.chn !== oldOperation.chn) ||
        oldTime[0] !== newTime[0] ||
        oldTime[1] !== newTime[1] ||
        (!oldChem && newChem) ||
        (!oldOperation && newOperation) ||
        newIsLatest !== oldIsLatest
      ) {
        let chem = newChem.chem_merged;
        let operation = newOperation.eng;
        // console.log(" >> 化學物查詢 ")
        // console.log(`    >> 搜尋 --> ${newTimeObject[0].time}~${newTimeObject[1].time}： ${chnChemName} --> ${operation}`)

        data = [
          {
            dataType: "city",
            url: `${baseurl_ver4}/mergedRecords/city_count`,
            para:
              `?chemical_name=${chem}&operation=${operation}&time_ge=${t0}&time_le=${t1}` +
              para_latest,
          },
          {
            dataType: "faccon",
            url: `${baseurl_ver4}/mergedRecords/data_list`,
            para:
              `?chemical_name=${chem}&operation=${operation}&time_ge=${t0}&time_le=${t1}` +
              para_latest,
          },
        ];
        // console.log(data.keys());
        for (let ind of Object.keys(data)) {
          //  console.log(ind);
          var fullUrl = `${data[ind]["url"]}${data[ind]["para"]}`;
          data[ind].fullUrl = fullUrl;
          //  console.log(fullUrl);
          data[ind].data = await fetch(fullUrl).then((res) => res.json());
        }
        let data_fac = data[1].data;
        emitData.value = {
          time: [t0, t1],
          chem: newChem,
          operation: newOperation,
          data: data,
        };
        data_fac = data_fac.sort((a, b) => a.comname.localeCompare(b.comname, "zh-hant"));
        tableData.rows = data_fac;
        //  console.log(tableData.rows);
        emit("queryFromChemSearch", emitData);
        //  console.log(data[0].data);
        if (data[0].data.length) {
          plotchart(data[0].data);
        }
      }
    }
    if (newQuery === "廠商名稱 或 統一編號") {
      if (
        (newComFac !== "" && (newComFac !== oldComFac || newTime !== oldTime)) ||
        newIsLatest !== oldIsLatest
      ) {
        // console.log(" >> 廠商查詢 ")
        // console.log(`    >> 搜尋${newComFac}、${newTime}`)
        // console.log(newComFac)
        var com = newComFac.comname_merged;
        data = [
          {
            dataType: "city",
            url: `${baseurl_ver4}/mergedRecords/city_count`,
            para: `?company_name=${com}&time_ge=${t0}&time_le=${t1}` + para_latest,
          },
          {
            dataType: "faccon",
            url: `${baseurl_ver4}/mergedRecords/data_list`,
            para: `?company_name=${com}&time_ge=${t0}&time_le=${t1}` + para_latest,
            // para: `?time_ge=${t0}&time_le=${t1}&ComFacBizName=${newComFac}`
          },
        ];
        for (let ind of data.keys()) {
          var fullUrl = `${data[ind]["url"]}${data[ind]["para"]}`;
          //  console.log(fullUrl);
          data[ind].fullUrl = fullUrl;
          data[ind].data = await fetch(fullUrl).then((res) => res.json());
        }
        // console.log(data)
        // console.log(data)
        var data_fac = data[1].data;
        //  console.log(data_fac);
        //  console.log(data[0].data);

        data_fac = data_fac.sort((a, b) => a.cname.localeCompare(b.cname, "zh-hant"));
        tableData.rows = data_fac;
        emitData.value = { time: [t0, t1], comFac: newComFac, data: data };
        emit("queryFromFacSearch", emitData);
        if (data[1].data.length) {
          plotchart(data[1].data);
        }
      }
    }
    isLoadingChemData.value = false;
  }
);

function tableLoadingFinish() {
  // 修改換頁樣式
  let pagination = document.querySelector(".vtl-paging");
  [...pagination.children].forEach((i) => {
    i.className = i.className.replace("col-sm-12", "col-12").replace("col-md-4", "");
  });
}

// --------------------------------------------------------------------------------
//  ---------- 以下為下拉選單功能相關 ----------

// 取得化學物質列表
asyncGetChem = (query) => {
  isLoadingChem.value = true;
  let apiurl = baseurl_ver4 + "/mergedRecords";
  let param = {
    offset: 0,
    limit: 100,
    display: "True",
    time_latest: "False",
    to_html: "False",
    chemical_name: query,
  };
  let url = `${apiurl}/chemical_list?${object2para(param)}`;
  console.log(url);
  fetch(url)
    .then((res) => res.json())
    .then((res) => {
      res.map(
        (i) => (i.label = `${i.casno.trim()} ${i.cname.trim()} ${i.ename.trim()}`)

        // (i.label = `
        // ${
        //   catlist.value[i.cat]
        // } > ${i.cname.trim()} ${i.ename.trim()} ${i.casno.trim()}`)
      );
      // 移除不在13+1列表中的casno
      let res2 = [...res].map((i) => {
        if (i.cat === "explosive") {
          let name = explosive_list.filter((j) => j.casno === i.casno);
          if (name.length > 0) {
            i.cname = name[0].cname;
          }
        }
        return i;
      });

      res2 = res2.filter((i) => explosive_list.map((j) => j.casno).includes(i.casno));
      // console.log(res.map((i) => i.cname));
      // console.log(res.map((i) => i.cname).length);
      // console.log(res2.map((i) => i.cname));
      // console.log(res2.map((i) => i.cname).length);

      res = res.sort((a, b) => a.cname.localeCompare(b.cname));
      chemOptions.value = res;
      isLoadingChem.value = false;
    });
};

// 取得廠商列表
asyncGetFacCom = async (query) => {
  let apiurl = baseurl_ver4 + "/mergedRecords";
  let param = {
    offset: 0,
    limit: 100,
    display: "True",
    time_latest: "False",
    to_html: "False",
    company_name: query,
  };
  // let param = `offset=0&limit=100&display=true&time_latest=false&to_html=false&chemical_name=${query}`;
  let url = `${apiurl}/company_list?${object2para(param)}`;
  fetch(url)
    .then((res) => res.json())
    .then((res) => {
      isLoadingFacCom.value = true;
      res.map(
        (i) =>
          (i.label = `${i.adminno ? i.adminno : ""} ${i.comname ? i.comname : ""} ${
            i.regno ? i.regno : ""
          }`)
      );
      comFacOptions.value = res;
      isLoadingFacCom.value = false;
    });
};

// 取得時間列表
getTime = () => {
  let apiurl = baseurl_ver4 + "/mergedRecords";
  let param = {
    offset: 0,
    limit: 100,
    display: "True",
    time_latest: "False",
    to_html: "False",
  };
  let url = `${apiurl}/time_list?${object2para(param)}`;
  fetch(url)
    .then((res) => res.json())
    .then((res) => {
      //  console.log(res);
      timeLen.value = res.length;
      res = res.map((i) => i.declaretime);
      timeOptions.value = res;
      selectedTime.value = [0, timeLen.value - 1];
    });
};

// 取得時間軸標籤
timeTick = (val) => {
  val = parseInt(val.toFixed());
  return { ...timeOptions.value }[val];
};

// 繪圖

var plotchart = (data) => {
  let chart = document.querySelector("#chart");
  if (selectedQuery.value === "運作行為 與 化學物質") {
    let div = document.createElement("div");
    div.id = "piechart";
    chart.append(div);
    var colormap = {
      基隆市: "rgba(220, 80,75, .8)",
      臺北市: "rgba(220, 53,69, .8)",
      新北市: "rgba(180,50,120, .8)",
      桃園市: "rgba(232,62,141, .8)",
      新竹市: "rgba(220,110,205, .8)",
      新竹縣: "rgba(239,134, 54, .8)",
      苗栗縣: "rgba(98,190, 95, .8)",
      臺中市: "rgba(32,201,150, .8)",
      南投縣: "rgba(40,167, 70, .8)",
      彰化縣: "rgba(9,200, 205, .8)",
      雲林縣: "rgba(59,117,145, .8)",
      嘉義縣: "rgba(0, 70, 120, .8)",
      嘉義市: "rgba(20, 90, 175, .8)",
      臺南市: "rgba(0, 123,255, .8)",
      高雄市: "rgba(255, 193,7, .8)",
      屏東縣: "rgba(253,125,20, .8)",
      臺東縣: "rgba(102,16,242, .8)",
      花蓮縣: "rgba(110,66, 193, .8)",
      宜蘭縣: "rgba(23,163,184, .8)",
      澎湖縣: "rgba(108,117,125, .8)",
      連江縣: "rgba(52, 58, 64, .8)",
      金門縣: "rgba(0, 123,255, .8)",
    };

    var data2 = [];
    var operation = selectedOperation.value;

    Object.entries(colormap).forEach(([city, color]) => {
      let citydata = data.filter((j) => j.City === city);
      if (citydata.length > 0) {
        citydata[0]["color"] = color;
        data2.push(citydata[0]);
      }
    });
    // data.forEach((i) => {
    //   if (i.City !== "-") {
    //     i["color"] = colormap[i.City];
    //     data2.push(i);
    //   }
    // });
    //  console.log(data2);
    var values = data2.map((i) => i.Q);
    var labels = data2.map((i) => i.City);
    var colors = data2.map((i) => i.color);
    //  console.log(labels, values, colors);
    var trace = [
      {
        type: "pie",
        name: "piechart",
        values: values,
        labels: labels,
        marker: {
          colors: colors,
          line: {
            width: 1.5,
          },
        },
        textinfo: "label+percent",
        textposition: "inside",
        // automargin: true,
        sort: false,
      },
    ];

    var layout = {
      title: "運作化學物質分佈圖",
      width: 340,
      margin: { t: 50, b: 10, l: 20, r: 20 },
      showlegend: true,
      // plot_bgcolor: "#FFF3",
      // paper_bgcolor: "#FFF3",
      legend: {
        x: 0.5,
        y: -0.1,
        xanchor: "center",
        yanchor: "top",
        orientation: "h",
        itemwidth: 40,
      },
    };
    var config = {
      responsive: true,
      // autosize: true, // set autosize to rescale
      displayModeBar: false,
    };

    Plotly.newPlot("piechart", trace, layout, config);
  }

  if (selectedQuery.value === "廠商名稱 或 統一編號") {
    //  console.log(data);
    var div;

    // chart.append(div);

    // div = document.createElement("div");
    // div.innerText = "廠商運作化學物質";
    // div.style.padding = "5px";
    // div.style.marginTop = "10px";
    // div.style.fontSize = "18px";
    // document.querySelector("#barchart").append(div);

    div = document.createElement("div");
    div.id = "barchart";
    chart.append(div);

    var trace = [];
    var data2;
    var cnt = 0;
    operationOptions.value.forEach((operation) => {
      data2 = [];
      data.forEach((idata) => {
        if (idata.operation === operation.eng) {
          data2.push(idata);
        }
      });
      var x = data2.map((i) => i.Q);
      var y = data2.map((i) => `${dept_e2c.value[i.deptid]}<br>${i.cname}`);
      x = x.length ? x : [0];
      y = y.length ? y : [""];
      cnt += y.length;
      //  console.log(x.length);
      trace.push({
        x: x,
        // y: data2.map((i) => `${i.cname}`),
        y: y,
        // width: data2.length ? Array(data.length).fill(1) : [],
        name: operation.chn,
        type: "bar",
        orientation: "h",
        marker: {
          // color: colors[ind],
          line: {
            // color: 'rgb(230,200,17)',
            width: 1.5,
          },
        },
      });
    });

    var height = 50 * cnt;
    //  console.log(trace);
    var layout = {
      // title: {
      //   pad: {
      //     b: 20,
      //   },
      //   y: 1.2,
      //   text: "廠商運作化學物質",
      // },
      // barmode: "group",
      height: height,
      width: 340,
      legend: {
        x: -0.25,
        y: 1 + 10 / (cnt + 5 * cnt),
        orientation: "h",
        itemwidth: 20,
        xanchor: "left",
        yanchor: "center",
        font: {
          size: 16,
          family: "Times New Roman",
        },
      },
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(0,0,0,0)",
      font: {
        family: "Courier New, monospace",
        size: 14,
        color: "rgb(30,20,28)",
      },
      margin: {
        l: 80,
        r: 10,
        b: 40,
        t: 0,
        // pad: 4
      },
      yaxis: {
        tickfont: {
          size: 10,
        },
      },
      xaxis: {
        gridcolor: "rgba(200, 200, 200, .9)",
        rangemode: "nonnegative",
        tickfont: {
          size: 15,
          family: "Times New Roman",
        },
        side: "top",
      },
      // annotations: [
      //   {
      //     xref: "paper",
      //     yref: "paper",
      //     x: 0.02,
      //     xanchor: "right",
      //     y: 1.1,
      //     yanchor: "center",
      //     text: "公噸",
      //     showarrow: false,
      //   },
      // ],
    };
    var config = {
      responsive: true,
      // autosize: true, // set autosize to rescale
      displayModeBar: false,
    };
    Plotly.newPlot("barchart", trace, layout, config);
    // Plotly.newPlot("piechart", trace, layout, config);
  }
};
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
  overflow-x: hidden;
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
  /* overflow-x: scroll; */
  /* max-height: 72px; */
  /* max-width: 300px; */
}

::v-deep(.multiselect__single) {
  padding: 0px;
  padding-left: 15px;
  margin: 0px;
  width: auto;
  line-height: 41px;
  max-height: 41px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0);
}

::v-deep(.multiselect__tags) {
  padding: 0px;
  padding-left: 15px;
  line-height: 41px;
  height: 41px;
  background: rgba(255, 255, 255, 0);
  border-radius: 0px;
  border-width: 0px;
  font-size: 16px;
}

::v-deep(.multiselect__placeholder) {
  padding-left: 15px;
  margin: 0px;
  background-color: none;
  padding-top: 0px;
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

#latestBox {
  line-height: 41px;
  height: 41px;
  vertical-align: middle;
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
  margin-top: 190px;
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
  height: 106vh;
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
  /* width: 130px; */
}

.form-select {
  width: 40%;
  margin-left: 10px;
  display: inline-block;
}
.fa-expand,
.fa-compress {
  font-size: 20px;
  padding: 8px;
  vertical-align: text-top;
  cursor: pointer;
}
#navbar.withAuto {
  width: 100%;
  /* animation: popup 0.5s; */
}
.fixed {
  -webkit-transition: all 1s ease;
  -moz-transition: all 1s ease;
  transition: all 1s ease;
}
@keyframes popup {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(0.95);
  }
  100% {
    transform: scale(1);
  }
}
.d-none-table {
  display: none;
}
@media (min-width: 576px) {
  .d-sm-none-table {
    display: none;
  }
  .d-sm-block-table {
    display: block;
  }
}

@media (max-width: 360px) {
  #navbar {
    width: 340px !important;
  }
}

.card-header:hover {
  cursor: pointer;
  background-color: rgba(255, 255, 255, 0.5);
}
.card-header span:nth-child(1):hover {
  cursor: pointer;
  cursor: pointer;
  color: red;
}
table tbody td {
  vertical-align: middle;
}
table thead th {
  vertical-align: middle;
  text-align: center;
}
</style>
