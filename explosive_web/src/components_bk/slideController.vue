<template>
  <div
    id="navbar"
    class="overlay"
    style="
      z-index: 100;
      background-color: rgba(240, 245, 240, 0.95);
      box-shadow: 0 -1px 24px rgba(0, 0, 0, 0.4);
    "
  >
    <!-- <a class="closebtn" style="cursor: pointer; z-index: 100" @click="closeNav"
      >&times;</a
    > -->
    <ul
      class="nav nav-tabs"
      id="myTab"
      role="tablist"
      style="margin-top: 120px;"
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
        ></table-lite>
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
</template>

<script setup>
import { onMounted, reactive, watch } from "@vue/runtime-core";
import TableLite from "vue3-table-lite";

const props = defineProps({
  data: Object,
  time: Array,
  chem: String,
  operation: String,
});

onMounted(() => {
  toggleNav();
  // closeNav();
  // controlStyle();
});

var table = reactive({
  isloading: false,
  columns: [
    {
      label: "ID",
      field: "Quantity",
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
        return `${row.Quantity} 公噸`;
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
  () => {
    return [props.data];
  },
  (newVal, oldVal) => {
    table.rows = newVal[0];
    // css
    let pagination = document.querySelector(".vtl-paging");
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
// table.rows = data;
// 收折navbar監聽
function toggleNav() {
  document.querySelector(".togglebtn").addEventListener("click", (evt) => {
    let width = document.getElementById("navbar").style.width;
    if (document.body.clientWidth > 768) {
      if ((width === "340px") | !width) {
        document.getElementById("navbar").style.width = "0%";
      } else {
        document.getElementById("navbar").style.width = "340px";
      }
    } else {
      if ((width === "0%") | !width) {
        document.getElementById("navbar").style.width = "100%";
      } else {
        document.getElementById("navbar").style.width = "0%";
      }
    }
  });
}

// function closeNav() {
//   document.getElementById("navbar").addEventListener("click", () => {
//     document.getElementById("navbar").style.width = "0%";
//   });
// }
</script>


<style scoped >
@media screen and (min-width: 768px) {
  .overlay {
    height: 100vh;
    width: 340px;
    position: fixed;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: rgb(0, 0, 0);
    background-color: rgba(0, 0, 0, 0.9);
    overflow-x: hidden;
    transition: 0.5s;
  }
}

@media screen and (max-width: 768px) {
  .overlay {
    height: 100vh;
    width: 0%;
    position: fixed;
    z-index: 1;
    top: 0;
    left: 0;
    background-color: rgba(0, 0, 0, 0.9);
    overflow-x: hidden;
    transition: 0.5s;
  }
}

.overlay-content {
  position: relative;
  /* top: 25%; */
  width: 100%;
  height: 100%;
  text-align: center;
  margin-top: 0px;
}

.overlay a {
  padding: 8px;
  text-decoration: none;
  font-size: 36px;
  color: #818181;
  display: block;
  transition: 0.3s;
}

.overlay a:hover,
.overlay a:focus {
  color: rgb(243, 200, 255);
}

.overlay .closebtn {
  position: absolute;
  top: 0px;
  right: 5px;
  font-size: 30px;
}

@media screen and (max-height: 450px) {
  .overlay a {
    font-size: 20px;
  }

  .overlay .closebtn {
    font-size: 40px;
    top: 5px;
    left: 5px;
  }
}

.togglebtn {
  position: fixed;
  cursor: pointer;
  margin: 5px;
  font-size: 30px;
  z-index: 2000;
}

div.card,
div.card-body {
  padding: 1px;
}

::v-deep(.vtl-tbody-td div) {
  /* background-color: red; */
  overflow-x: scroll;
  max-height: 24px;
}
</style>