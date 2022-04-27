<template>
    <!-- NavBar -->
    <transition name="slide">
        <div
            id="navbar"
            v-show="navbarStatus"
            class="fixed-top"
        >
            <!-- 圖表結果 -->
            <div id="searchResult">
                <ul
                    class="nav nav-tabs"
                    id="myTab"
                    role="tablist"
                >
                    <li
                        class="nav-item w-50"
                        role="presentation"
                    >
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
                    <li
                        class="nav-item w-50"
                        role="presentation"
                    >
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
                <div
                    class="tab-content"
                    id="myTabContent"
                >
                    <div
                        class="tab-pane fade show active"
                        id="home"
                        role="tabpanel"
                        aria-labelledby="home-tab"
                        style="height: calc(100vh - 200px); overflow: scroll"
                    >
                        <div
                            style="text-align: left; margin: 5px; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center;">
                            <label>查詢：
                                <input v-model="searchInTable" />
                            </label>
                            <span
                                class="download"
                                @click="downloadResult"
                            >
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
                                    style="background-color: rgba(200,240,200,.5);overflow-x:scroll; overflow-x: scroll;"
                                >
                                    <div style="margin-top:10px; margin-bottom: 30px;width:240%">
                                        <table
                                            class="table table-hover"
                                            style="table-layout: fixed;width:100%"
                                        >
                                            <thead>
                                                <tr>
                                                    <th>資料來源</th>
                                                    <th>運作行為</th>
                                                    <th>申報期別</th>
                                                    <th>化學物質</th>
                                                    <th>運作量</th>
                                                    <th>廠商名稱</th>
                                                    <th>統一編號</th>
                                                    <th style="width:20%">廠商名稱列表</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <template v-for="comfac in comFacDetail">
                                                    <tr>
                                                        <td>{{ dept_e2c[comfac.deptid] }}</td>
                                                        <td>{{
                                                                operationOptions.filter(i => i.eng ===
                                                                    comfac.operation)[0].chn
                                                        }}</td>
                                                        <td>{{
                                                                String(comfac.time)
                                                                    .replace(/01$/, 'Q1').replace(/04$/, 'Q2')
                                                                    .replace(/07$/, 'Q3').replace(/10$/, 'Q4')
                                                        }}</td>
                                                        <td>{{ comfac.name }}</td>
                                                        <td>{{ comfac.Quantity }}</td>
                                                        <td>{{ comfac.ComFacBizName }}</td>
                                                        <td>{{ comfac.BusinessAdminNo }}</td>
                                                        <td>{{ comfac.ComFacBizName_list }}</td>
                                                    </tr>
                                                </template>

                                            </tbody>
                                        </table>
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
                        >&#9776;</div>
                        <div class="col-10 border-end ps-0">
                            <multiselect
                                v-model="selectedQuery"
                                placeholder="依...查詢"
                                :options="queryOptions.map((i) => i.method)"
                                :searchable="false"
                                :close-on-select="true"
                                :show-labels="false"
                                @Select="handleSelectQuery"
                                :allowEmpty=false
                            ></multiselect>
                        </div>
                    </div>
                </template>
                <template v-if="selectedQuery === '運作行為 與 化學物質'">
                    <div class="row rounded-lg mx-0 border-top">
                        <div class="col-5 border-end  ps-0">
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
                                <template
                                    slot="tag"
                                    slot-scope="{ option, remove }"
                                >
                                    <span class="custom__tag">
                                        <span>{{ option.name }}</span>
                                        <span
                                            class="custom__remove"
                                            @click="remove(option)"
                                        >❌</span>
                                    </span>
                                </template>
                                <template
                                    slot="clear"
                                    slot-scope="props"
                                >
                                    <div
                                        class="multiselect__clear"
                                        v-if="selectedChem.length"
                                        @mousedown.prevent.stop="clearAll(props.search)"
                                    ></div>
                                </template>
                                <span slot="noResult">
                                    Oops! No elements found. Consider changing the search
                                    query.
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
                                label="ComFacBizName"
                                :searchable="true"
                                :loading="isLoadingFacCom"
                                :close-on-select="true"
                                :show-labels="false"
                                @search-change="asyncGetFacCom"
                            >
                                <template
                                    slot="tag"
                                    slot-scope="{ option, remove }"
                                >
                                    <span class="custom__tag">
                                        <span>{{ option.name }}</span>
                                        <span
                                            class="custom__remove"
                                            @click="remove(option)"
                                        >❌</span>
                                    </span>
                                </template>
                                <template
                                    slot="clear"
                                    slot-scope="props"
                                >
                                    <div
                                        class="multiselect__clear"
                                        v-if="selectedChem.length"
                                        @mousedown.prevent.stop="clearAll(props.search)"
                                    ></div>
                                </template>
                                <span slot="noResult">
                                    Oops! No elements found. Consider changing the search
                                    query.
                                </span>
                            </multiselect>
                        </div>
                    </div>
                </template>
                <template v-if="true">
                    <div class="row rounded-lg mx-0">
                        <div
                            class="col-12 border-top ps-0"
                            id="timeslider"
                        >
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
import { clearPlotlyTrace } from "./js/utility.js"
import { faArrowCircleDown } from '@fortawesome/free-solid-svg-icons'
import { utils, write } from "xlsx";
import { saveAs } from "file-saver";

onMounted(() => {
    // click point in map
    let mymap = document.querySelector('#map')

    mymap.on('plotly_click', (i) => {
        try {
            if (selectedQuery.value === '運作行為 與 化學物質') {
                if (toggleOpen.value) {
                    toggleOpen.value = false
                    document.querySelector('.vtl-tbody tr').click()
                }
                var clickpoint = i.points[0].text.split(':')[0]
                console.log(clickpoint)
                searchInTable.value = clickpoint
                toggleOpen.value = true
                setTimeout(() => {
                    document.querySelector('.vtl-tbody tr').click()
                }, 500);
            }
        } catch (e) {
            toggleOpen.value = true
            document.querySelector('.vtl-tbody tr').click()
            searchInTable.value = ''
        }
    })

});


// emit and props
const emit = defineEmits(['queryFromChemSearch', 'queryFromFacSearch', 'focusResult']);
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
var navbarStatus = document.querySelector('body').clientWidth > 760 ? ref(true) : ref(false)

// toggle table-lite row
var handleToggleInfoFromSearchChem
var handleToggleInfoFromSearchFac
var comFacDetail = ref([])
var toggleOpen = ref(false)
var searchInTable = ref('')
var tableData = reactive({ rows: [] })


var handleSelectQuery
var handleSelectChem
// var clearPlotlyTrace

var downloadResult

// table

var dept_e2c = ref({
    'MND': '國防部',
    'MOEA005': '經濟部礦務局',
    'MOEA001': '經濟部中部辦公室',
    'EPZA': '"科技產業園區(經濟部加工出口區)"',
    'MOST001': '科技部竹科管理局',
    'MOST002': '科技部中科管理局',
    'MOST003': '科技部南科管理局',
    'MOI001': '內政部消防署',
    'MOL001': '勞動部職安署',
    'COA001': '農委會防檢局',
    'TCSB': '環保署化學局',
    'MOTC001': '交通部臺灣港務公司',
    'MOF001': '財政部關務署'
})


const json2arr = async (data) => {
    // console.log(data);
    // const buildData = (data) => {
    return new Promise((resolve, reject) => {
        // 最後所有的資料會存在這
        let arrayData = [];

        // 取 data 的第一個 Object 的 key 當表頭
        let arrayTitle = Object.keys(data[0]);
        console.log(arrayTitle)
        arrayData.push(arrayTitle);

        // 取出每一個 Object 裡的 value，push 進新的 Array 裡
        Array.prototype.forEach.call(data, (d) => {
            let items = [];
            Array.prototype.forEach.call(arrayTitle, (title) => {
                let item = d[title] || "無";
                items.push(item);
            });
            arrayData.push(items);
        });

        resolve(arrayData);
    });
    // };
};


var defineParameter = true
//  ------------------ 參數初始值給定 ------------------
if (defineParameter) {

    // 搜尋方式選擇：廠商 or 化學物質
    queryOptions.value = [
        { method: '運作行為 與 化學物質' },
        { method: '廠商名稱 或 統一編號' }
    ]
    selectedQuery.value = "運作行為 與 化學物質"
    selectedQuery.value = "廠商名稱 或 統一編號"

    // 取得運作行為列表
    operationOptions.value = [
        { chn: "輸入", eng: "import" },
        { chn: "貯存", eng: "storage" },
        { chn: "製造", eng: "produce" },
        { chn: "使用", eng: "usage" },
    ];
    selectedOperation.value = { chn: "貯存", eng: "storage" }
    selectedOperation.value = { chn: "使用", eng: "usage" }

    // 取得化學物質列表
    asyncGetChem = async (query) => {
        isLoadingChem.value = true;
        let res = await fetch(`${baseurl}/chemilist`).then((res) => res.json());
        chemOptions.value = res;
        isLoadingChem.value = false;
    };

    // 取得廠商列表
    asyncGetFacCom = async (query) => {
        isLoadingFacCom.value = true;
        let res = await fetch(`${baseurl}/records_fac`).then((res) => res.json());
        comFacOptions.value = res;
        isLoadingFacCom.value = false;
    };

    // 取得時間列表
    asyncGetTime = async () => {
        var response = await fetch(`${baseurl}/records_time`)
        var time = await response.json();
        return time
    };
    timeOptions.value = await asyncGetTime()

    // 取得時間軸標籤
    timeTick = (val) => {
        return [...timeOptions.value].filter(i => i.index === val)[0]['label']
    }

    // 初始化時間
    selectedTime.value = [timeOptions.value.length - 1, timeOptions.value.length - 1]

    // 處理選擇Query選項
    handleSelectQuery = (selected) => {
        if (selected !== selectedQuery.value) {
            clearPlotlyTrace('all')
            tableData.rows = []
            selectedChem.value = ''
            searchInTable.value = ''
        }
    };





    // handle toggle row from table-lite
    handleToggleInfoFromSearchChem = async (info) => {
        let state = info.state
        if (state) {
            let row = info.row
            let tmp, url
            // 取得廠商統計資料
            url = `${baseurl}/statistic_fac_merged?groupid=${row.group}`
            tmp = await fetch(url).then(res => res.json())
            tmp = new DataFrame(tmp)
                .sortBy(["name", "operation", "time", "deptid"])
                .toCollection();
            comFacDetail.value = tmp
            toggleOpen.value = true
            tmp = [...emitData.value.data[1].proc].filter(i => i.group === row.group)
            emit('focusResult', { state: state, row: tmp })
        } else {
            toggleOpen.value = false
            console.log(toggleOpen.value)
            clearPlotlyTrace('fac')
        }
    }

    handleToggleInfoFromSearchFac = (info) => {
        let state = info.state
        if (state) {
            let row = { ...info.row }
            console.log(row)
            // tmp = [...emitData.value.data[1].proc].filter(i => i.group === row.group)
            emit('focusResult', { state: true, row: [row] })
        } else {
            clearPlotlyTrace('fac')
        }
    }

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
            var savedata
            if (selectedQuery === '運作行為 與 化學物質') {
                savedata = data[2].proc
            } else {
                savedata = data[0].proc
            }
            console.log(savedata)
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
            // saveAs(
            //     new Blob([s2ab(wbout)], { type: "application/octet-stream" }),
            //     "易爆物與高風險化學物質統計報表.xlsx"
            // );


        } else {
            alert("尚未查詢出任何結果。\n此下載檔案功能為輸出查詢結果，請先進行查詢後再進行下載！")
        }
    }
}
//  ---------------------------------
//  -----------  表格清單  -----------
var tableForChemSearch = reactive({
    isloading: false,
    columns: [
        {
            label: "統一編號",
            field: "BusinessAdminNo",
            width: "35%",
            sortable: true,
            // display: (row) => {
            //   return `${row.Quantity} 公噸`;
            // },
        },
        {
            label: "廠商名稱",
            field: "ComFacBizName",
            width: "35%",
            sortable: true,
            display: (row) => {
                return `${row.ComFacBizName}`;
            },
        },
        {
            label: "運作量",
            field: "Quantity",
            width: "30%",
            sortable: true,
            display: (row) => {
                return `${row.Quantity.toFixed(2)} 公噸`;
            },
        },

    ],
    rows: computed(() => {

        return tableData.rows.filter(
            x =>
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
            label: "期別",
            field: "time",
            width: "20%",
            sortable: true,
            // display: (row) => {
            //   return `${row.Quantity} 公噸`;
            // },
        },
        {
            label: "化學物質(資料來源)",
            field: "name",
            width: "30%",
            sortable: true,
            display: (row) => {
                return `${row.name}<br>(${row.deptid})`;
            },
        },
        // {
        //     label: "運作行為",
        //     field: "operation",
        //     width: "35%",
        //     sortable: true,
        // },
        {
            label: "運作量",
            field: "Quantity",
            width: "50%",
            sortable: true,
            display: (row) => {
                return `${row.operation} <br> ${row.Quantity.toFixed(2)} 公噸`;
                // return ` (${row.lon.toFixed(2)}, ${row.lat.toFixed(2)})<br> ${row.operation}<br> ${row.Quantity.toFixed(2)} 公噸`;
            },
        },

    ],
    rows: computed(() => {

        return tableData.rows.filter(
            x =>
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
    console.log(newVal, oldVal)
    if (newVal && oldVal) {
        if (newVal.chnname !== oldVal.chnname) {
            clearPlotlyTrace('all')
            // tableData.rows = []
            toggleOpen.value = false
        }
    } else {
        clearPlotlyTrace('all')
        tableData.rows = []
        toggleOpen.value = false
    }
    console.log(searchInTable.value)
    searchInTable.value = ''
    console.log(toggleOpen.value)
});


// 監控運作行為選項model狀態
watch([selectedOperation], ([newVal], [oldVal]) => {
    console.log(newVal, oldVal)
    if (newVal && oldVal) {
        if (newVal.chnname !== oldVal.chnname) {
            clearPlotlyTrace('all')
            // tableData.rows = []
            toggleOpen.value = false
        }
    } else {
        clearPlotlyTrace('all')
        tableData.rows = []
        toggleOpen.value = false
    }
    searchInTable.value = ''
});

// 監控時間選項model狀態
watch(selectedTime,
    (newTime, oldTime) => {
        // console.log(newTime[0], oldTime[0], newTime[1], oldTime[1])
        if (
            newTime[0] !== oldTime[0] || newTime[1] !== oldTime[1]
        ) {

            clearPlotlyTrace('all')
            // tableData.rows = []
            toggleOpen.value = false
        }
        searchInTable.value = ''
    })

// watch 表格搜尋選項
watch(
    () => searchInTable.value,
    (val_old, val_new) => {
        if (
            val_old.length > 0 ||
            val_old !== val_new
        ) {
            toggleOpen.value = false
            clearPlotlyTrace('fac')
        }
    }

);

// watch 化學物質與廠商搜尋
watch(
    [selectedQuery, selectedOperation, selectedChem, selectedComFac, selectedTime],
    async (newVal, oldVal) => {
        var [newQuery, newOperation, newChem, newComFac, newTime] = newVal
        var [oldQuery, oldOperation, oldChem, oldComFac, oldTime] = oldVal
        let newTimeObject = []
        // console.log(newChem)

        // 將時間index轉為時間
        for (let i = 0; i < newTime.length; i++) {
            for (let j = 0; j < timeOptions.value.length; j++) {
                if (timeOptions.value[j].index === newTime[i]) {
                    newTimeObject.push({ ...timeOptions.value[j] })
                }
            }
        }
        var [t0, t1] = newTimeObject.map(i => i.time)

        if (newQuery === '運作行為 與 化學物質') {
            if (
                (
                    (newChem && oldChem && (newChem.chnname !== oldChem.chnname)) ||
                    (newOperation && oldOperation && (newOperation.chn !== oldOperation.chn)) ||
                    (oldTime[0] !== newTime[0] || oldTime[1] !== newTime[1])
                ) ||
                (
                    (!oldChem && newChem) || (!oldOperation && newOperation)
                )
            ) {

                let chnChemName = newChem.chnname
                let operation = newOperation.eng

                // descripition 
                console.log(" >> 化學物查詢 ")
                console.log(`    >> 搜尋 --> ${newTimeObject[0].time}~${newTimeObject[1].time}： ${chnChemName} --> ${operation}`)

                // fetch data
                data = [
                    {
                        dataType: 'city',
                        url: `${baseurl}/statistic_city`,
                        para: `?name=${chnChemName}&operation=${operation}&time_ge=${t0}&time_le=${t1}`
                    },
                    {
                        dataType: 'faccon',
                        url: `${baseurl}/statistic_fac`,
                        para: `?name=${chnChemName}&operation=${operation}&time_ge=${t0}&time_le=${t1}`
                    },
                    {
                        dataType: 'faccon_merged',
                        url: `${baseurl}/statistic_fac_merged`,
                        para: `?name=${chnChemName}&operation=${operation}&time_ge=${t0}&time_le=${t1}`
                    },

                ];
                for (let ind of data.keys()) {
                    var fullUrl = `${data[ind]['url']}${data[ind]['para']}`
                    data[ind].fullUrl = fullUrl;
                    data[ind].data = await fetch(fullUrl).then(res => res.json())

                }
                // 
                let data_city = data[0].data
                let data_fac = data[1].data//.filter(i => i.lon != '')
                let data_fac_merged = data[2].data//.filter(i => i.lon != '')
                console.log(data_fac)
                console.log(data_fac_merged)
                console.log(data[1].fullUrl)
                if (t0 !== '最新申報') {
                    console.log('      >> 非查詢「最新申報」，結果包含不同季度，需做額外統計：')
                    if (operation === 'storage') {
                        console.log('        >> 查詢貯存量，選擇「最大貯存量」')

                        data_city = new DataFrame(data_city)
                            .sortBy(["Quantity", "time", "operation", "name", "city"], true)
                            .dropDuplicates("operation", "name", "city")
                            .toCollection();

                        data_fac = new DataFrame(data_fac)
                            .sortBy(["Quantity", "time"], true)
                            .dropDuplicates("operation", "name", "group", "lon", "lat")
                            .toCollection();

                        data_fac_merged = new DataFrame(data_fac_merged)
                            .sortBy(["Quantity", "time",], true)
                            .dropDuplicates("operation", "name", "group")
                            .toCollection();

                    } else {
                        console.log('        >> 非查詢貯存量，計算「總運作量」')

                        data_city = new DataFrame(data_city)
                            .groupBy("operation", "name", "city")
                            .aggregate((group) => group.stat.sum("Quantity"))
                            .rename("aggregation", "Quantity")
                            .toCollection();

                        data_fac = new DataFrame(data_fac)
                            .groupBy("operation", "name", "group", "deptid", "lon", "lat", "ComFacBizName", "BusinessAdminNo")
                            .aggregate((group) => group.stat.sum("Quantity"))
                            .rename("aggregation", "Quantity")
                            .map(row => row.set("time", `${t0}-${t1}`))
                            .toCollection();

                        var tmp = new DataFrame(data_fac_merged)
                        data_fac_merged = tmp
                            .groupBy("operation", "name", "group")
                            .aggregate((group) => group.stat.sum("Quantity"))
                            .rename("aggregation", "Quantity")
                            .join(tmp.select('ComFacBizName', 'BusinessAdminNo', 'lon', 'lat', 'group'), 'group', 'left')
                            .toCollection();
                    }
                } else {
                    console.log('      >> 查詢結果為最新季度，可直接使用：')
                }


                data[0].proc = data_city
                data[1].proc = data_fac
                data[2].proc = data_fac_merged//.map(i => i.operation = operationOptions.value.filter(j => j.eng === i.operation))

                console.log(`        >> 行政區統計：共${data[0].data.length}筆`)
                console.log(`        >> 廠商統計：共${data[1].data.length}筆`)
                console.log(`        >> 行政區統計：去重複後：共${data[0].proc.length}筆`)
                console.log(`        >> 廠商統計：去重複後：共${data[1].proc.length}筆`)
                // console.log(data)
                emitData.value = { time: newTimeObject, chem: newChem, operation: newOperation, data: data }
                emit('queryFromChemSearch', emitData)
                tableData.rows = data_fac_merged
                console.log(toggleOpen.value)
            }

        } else if (newQuery === '廠商名稱 或 統一編號') {

            if (
                newComFac !== '' &&
                (
                    newComFac !== oldComFac ||
                    newTime !== oldTime
                )
            ) {
                console.log(" >> 廠商查詢 ")
                console.log(`    >> 搜尋${newComFac}、${newTime}`)
                console.log(newComFac)
                data = [
                    {
                        dataType: 'faccon',
                        url: `${baseurl}/statistic_fac`,
                        para: `?time_ge=${t0}&time_le=${t1}&groupid=${newComFac.group}`
                        // para: `?time_ge=${t0}&time_le=${t1}&ComFacBizName=${newComFac}`
                    },
                    {
                        dataType: 'faccon',
                        url: `${baseurl}/statistic_fac_merged`,
                        para: `?time_ge=${t0}&time_le=${t1}&groupid=${newComFac.group}`
                        // para: `?time_ge=${t0}&time_le=${t1}&ComFacBizName=${newComFac}`
                    },
                ];
                for (let ind of data.keys()) {
                    var fullUrl = `${data[ind]['url']}${data[ind]['para']}`
                    data[ind].fullUrl = fullUrl;
                    data[ind].data = await fetch(fullUrl).then(res => res.json())

                }
                // console.log(data)
                var data_fac = data[0].data
                var data_fac_merged = data[1].data

                if (t0 !== '最新申報') {
                    console.log('      >> 非查詢「最新申報」，結果包含不同季度，需做額外統計：')
                    console.log(data_fac)
                    console.log(data_fac_merged)

                    let storage
                    let other

                    // 處理「未把座標不同但group相同的合併的」
                    storage = data_fac.filter(i => i.operation === 'storage')
                    other = data_fac.filter(i => i.operation !== 'storage')

                    // console.log(storage)
                    storage = new DataFrame(storage)
                        .sortBy(["Quantity", "time", "operation", "name",], true)
                        .dropDuplicates("operation", "name", "lon")
                        .toCollection();
                    // console.log(storage)

                    // console.log(other)
                    other = new DataFrame(other)
                        .groupBy("operation", "name", "group", "deptid", "lon", "lat", "ComFacBizName", "BusinessAdminNo", "RegionType")
                        .aggregate((group) => group.stat.sum("Quantity"))
                        .rename("aggregation", "Quantity")
                        .map(row => row.set("time", `${t0}-${t1}`))
                        .toCollection();
                    // console.log(other)
                    data_fac = [...storage, ...other]


                    // 處理「已把座標不同但group相同的合併的」
                    storage = data_fac_merged.filter(i => i.operation === 'storage')
                    other = data_fac_merged.filter(i => i.operation !== 'storage')

                    // console.log(storage)
                    storage = new DataFrame(storage)
                        .sortBy(["Quantity", "time", "operation", "name",], true)
                        .dropDuplicates("operation", "name", "lon")
                        .toCollection();
                    // console.log(storage)

                    // console.log(other)
                    other = new DataFrame(other)
                        .groupBy("operation", "name", "group", "deptid", "lon", "lat", "ComFacBizName", "BusinessAdminNo")
                        .aggregate((group) => group.stat.sum("Quantity"))
                        .rename("aggregation", "Quantity")
                        .map(row => row.set("time", `${t0}-${t1}`))
                        .toCollection();
                    // console.log(other)
                    console.log(data_fac_merged)
                    data_fac_merged = [...storage, ...other]
                    console.log(data_fac_merged)

                } else {
                    console.log('      >> 查詢結果為最新季度，可直接使用：')
                }
                data_fac_merged.map(i => i.operation = operationOptions.value.filter(j => j.eng === i.operation)[0]['chn'])
                data_fac_merged.map(i => i.deptid = dept_e2c.value[i.deptid])
                data_fac.map(i => i.operation = operationOptions.value.filter(j => j.eng === i.operation)[0]['chn'])
                data_fac.map(i => i.deptid = dept_e2c.value[i.deptid])

                data[0].proc = data_fac
                // console.log(data_fac_merged)
                data[1].proc = data_fac_merged
                // console.log(data[1].proc)
                console.log(data)
                // console.log(data_fac_merged)
                // console.log(data[1].proc)
                tableData.rows = data_fac
                emitData.value = { time: newTimeObject, comFac: newComFac, data: data }
                emit('queryFromFacSearch', emitData)
            }

        }

    }
);




function tableLoadingFinish() {
    // 修改換頁樣式
    let pagination = document.querySelector(".vtl-paging");
    [...pagination.children].forEach((i) => {
        i.className = i.className
            .replace("col-sm-12", "col-12")
            .replace("col-md-4", "");
    });
}

</script>


<style scoped >
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


@media screen and (min-width: 768px) {}

@media screen and (max-width: 768px) {}

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
    overflow-x: scroll;
    max-height: 48px;
}

::v-deep(.multiselect__single) {
    padding: 0px;
    padding-left: 15px;
    margin: 0px;
    width: auto;
    line-height: 41px;
    background-color: none;
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

.row>* {
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
    --slider-connect-bg: #EF4444;
    --slider-tooltip-bg: #EF4444;
    --slider-handle-ring-color: #EF444430;
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
    background-color: rgba(200, 240, 200, .5);
    padding: 2px;
    border-radius: 5px;
}

.download:hover {
    color: red
}

.tab-content input {
    width: 130px;
}
</style>