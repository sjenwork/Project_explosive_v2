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
                        <table-lite
                            :is-static-mode="true"
                            :is-loading="table.isLoading"
                            :columns="table.columns"
                            :rows="table.rows"
                            :total="table.totalRecordCount"
                            :sortable="table.sortable"
                            @is-finished="tableLoadingFinish"
                            @toggleinfo="handleToggleInfo"
                        >
                            <td
                                colspan="3"
                                style="background-color: rgba(200,200,200,.8);"
                            >
                                <table
                                    class="table table-hover"
                                    style="margin-top:30px; margin-bottom: 30px;"
                                >
                                    <thead>
                                        <tr>
                                            <th>資料來源</th>
                                            <th>申報期別</th>
                                            <th>運作行為</th>
                                            <th>化學物質</th>
                                            <th>運作量</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <template v-for="comfac in comFacDetail">
                                            <tr>
                                                <td>{{ comfac.deptid }}</td>
                                                <td>{{
                                                    operationOptions.filter(i => i.eng === comfac.operation)[0].chn
                                                }}</td>
                                                <td>{{
                                                    String(comfac.time)
                                                        .replace(/01$/, 'Q1').replace(/04$/, 'Q2')
                                                        .replace(/07$/, 'Q3').replace(/10$/, 'Q4')
                                                }}</td>
                                                <td>{{ comfac.name }}</td>
                                                <td>{{ comfac.Quantity }}</td>
                                            </tr>
                                        </template>

                                    </tbody>
                                </table>
                            </td>
                        </table-lite>
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
import { watch } from "vue";
import Multiselect from "vue-multiselect";
import TableLite from "vue3-table-lite";
import Slider from "@vueform/slider";
import DataFrame from "dataframe-js";


onMounted(() => {
    // timeOptions.value = await asyncGetTime()

});



// emit and props
const emit = defineEmits(['queryResult']);
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
var navbarStatus = ref(false)
// toggle table-lite row
var handleToggleInfo
var comFacDetail = ref([])






var defineParameter = true
//  ------------------ 參數初始值給定 ------------------
if (defineParameter) {

    // 搜尋方式選擇：廠商 or 化學物質
    queryOptions.value = [
        { method: '運作行為 與 化學物質' },
        { method: '廠商名稱 或 統一編號' }
    ]
    selectedQuery.value = "運作行為 與 化學物質"

    // 取得運作行為列表
    operationOptions.value = [
        { chn: "輸入", eng: "import" },
        { chn: "貯存", eng: "storage" },
        { chn: "製造", eng: "produce" },
        { chn: "使用", eng: "usage" },
    ];
    selectedOperation.value = { chn: "貯存", eng: "storage" }

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

    // handle toggle row from table-lite
    handleToggleInfo = async (row) => {
        console.log(row)
        let url = `${baseurl}/statistic_fac_merged?groupid=${row.group}`
        let tmp = await fetch(url).then(res => res.json())
        console.log(tmp)
        tmp = new DataFrame(tmp)
            .sortBy(["name", "operation", "time", "deptid"])
            .toCollection();
        console.log(tmp)
        comFacDetail.value = tmp
    }
}

var table = reactive({
    isloading: false,
    columns: [
        {
            label: "統一編號",
            field: "BusinessAdminNo",
            width: "10%",
            sortable: true,
            // display: (row) => {
            //   return `${row.Quantity} 公噸`;
            // },
        },
        {
            label: "廠商名稱",
            field: "ComFacBizName",
            width: "50%",
            sortable: true,
            display: (row) => {
                return `${row.ComFacBizName}`;
            },
        },
        {
            label: "運作量",
            field: "Quantity",
            width: "40%",
            sortable: true,
            display: (row) => {
                return `${row.Quantity.toFixed(2)} 公噸`;
            },
        },

    ],
    rows: [],
    // totalRecordCount: computed(() => {
    //   return table.rows.length;
    // }),
    sortable: {
        order: "id",
        sort: "asc",
    },
});

watch(
    [selectedQuery, selectedOperation, selectedChem, selectedComFac, selectedTime],
    async (newVal, oldVal) => {
        var [newQuery, newOperation, newChem, newComFac, newTime] = newVal
        var [oldQuery, oldOperation, oldChem, oldComFac, oldTime] = oldVal
        let newTimeObject = []
        // console.log(newChem)
        if (newQuery === '運作行為 與 化學物質') {
            if (
                newChem !== '' &&
                newChem !== null &&
                newOperation !== '' &&
                newOperation !== null &&
                (
                    newChem !== oldChem ||
                    newOperation.chn !== oldOperation.chn ||
                    newTime[0] !== oldTime[0] ||
                    newTime[1] !== oldTime[1]
                )
            ) {
                // 將時間index轉為時間

                for (let i = 0; i < newTime.length; i++) {
                    for (let j = 0; j < timeOptions.value.length; j++) {
                        if (timeOptions.value[j].index === newTime[i]) {
                            newTimeObject.push({ ...timeOptions.value[j] })
                        }
                    }
                }
                let [t0, t1] = newTimeObject.map(i => i.time)
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
                    data[ind].fullurl = fullUrl;
                    data[ind].data = await fetch(fullUrl).then(res => res.json())

                }
                // 
                let data_city = data[0].data
                let data_fac = data[1].data//.filter(i => i.lon != '')
                let data_fac_merged = data[2].data//.filter(i => i.lon != '')
                if (t0 !== '最新申報') {
                    console.log('      >> 查詢結果包含不同季度，需做額外統計：')
                    if (operation === 'storage') {
                        console.log('        >> 非查詢「最新申報」，選擇「最大貯存量」')

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
                        console.log('        >> 非查詢「最新申報」，計算「總運作量」')

                        data_city = new DataFrame(data_city)
                            .groupBy("operation", "name", "city")
                            .aggregate((group) => group.stat.sum("Quantity"))
                            .rename("aggregation", "Quantity")
                            .toCollection();

                        data_fac = new DataFrame(data_fac)
                            .groupBy("operation", "name", "group", "deptid", "lon", "lat", "ComFacBizName", "BusinessAdminNo")
                            .aggregate((group) => group.stat.sum("Quantity"))
                            .rename("aggregation", "Quantity")
                            .toCollection();

                        // console.log(data_fac_merged)
                        data_fac_merged = new DataFrame(data_fac_merged)
                            .groupBy("operation", "name", "group")
                            .aggregate((group) => group.stat.sum("Quantity"))
                            .rename("aggregation", "Quantity")
                            .toCollection();


                    }
                } else {
                    // data_fac_merged_proc = data_fac_merged

                    console.log('      >> 查詢結果為最新季度，可直接使用：')
                    console.log('        >> 查詢「最新申報」')

                }
                console.log(`        >> 行政區統計：共${data[0].data.length}筆`)
                console.log(`        >> 廠商統計：共${data[1].data.length}筆`)

                data[0].proc = data_city
                data[1].proc = data_fac
                data[2].proc = data_fac_merged
                // console.log(data)
                emitData.value = { time: newTimeObject, chem: newChem, operation: newOperation, data: data }
                emit('queryResult', emitData)
                console.log(data_fac)
                table.rows = data_fac_merged
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
            }
            // console.log(newQuery)
            // console.log(newChem)
            // console.log(newComFac)
            // console.log(newTime)
        }


    }
);





function tableLoadingFinish() {
    let pagination = document.querySelector(".vtl-paging");
    [...pagination.children].forEach((i) => {
        i.className = i.className
            .replace("col-sm-12", "col-12")
            .replace("col-md-4", "");
    });
    console.log(pagination);
}

</script>


<style scoped >
@media screen and (min-width: 340px) {
    #searchPannel {
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
}

::v-deep(.multiselect__tags) {
    padding: 0px;
    padding-left: 15px;
    line-height: 41px;
    height: 41px;
}

::v-deep(.multiselect__placeholder) {
    padding-left: 15px;
    margin: 0px;
}

::v-deep(.multiselect__input) {
    padding-left: 15px;
    margin: 0px;
    line-height: 41px;
    height: 41px;
    width: auto;
    /* width: calc(100%-20px); */
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

::v-deep(.multiselect__tags) {
    background: rgba(255, 255, 255, 0);
    border-radius: 0px;
    border-width: 0px;
}

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
    margin-top: 135px;
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
    background-color: rgba(240, 245, 240, 0.95);
    box-shadow: 0 -1px 24px rgba(0, 0, 0, 0.4);
}
</style>