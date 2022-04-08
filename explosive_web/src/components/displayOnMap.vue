<template></template>
<script setup>
import { ref, watch } from "vue";
import Plotly, { reverse } from "plotly.js-dist";
// import { Series, DataFrame } from "pandas-js";
// import { DataFrame } from "danfojs";
import DataFrame from "dataframe-js";

const props = defineProps({
  data: Object,
  time: Array,
  chem: String,
  operation: String,
});
var data = ref([]);

watch(
  () => {
    return [props.data, props.time, props.chem, props.operation];
  },
  (newval, oldval) => {
    let [data, time, chem, operation] = newval;
    var df = new DataFrame(data)
      .groupBy("time", "operation", "name", "city")
      .aggregate((group) => group.stat.sum("Quantity"))
      .rename("aggregation", "Quantity");

    new DataFrame(data);
    var df_all = new DataFrame(data)
      .cast("lon", (i) => String(i))
      .cast("lat", (i) => String(i))
      .groupBy("time", "operation", "name", "lon", "lat", "ComFacBizName_m")
      .aggregate((group) => group.stat.sum("Quantity"))
      .rename("aggregation", "Quantity");

    if (time[0] === "最新申報") {
      df = df.sortBy(["time", "operation", "name", "city"], true);
      df = df.dropDuplicates("operation", "name", "city");

      df_all = df_all.sortBy(["time", "operation", "name"], true);
      df_all = df_all.dropDuplicates("operation", "name", "lon", "lat");
    } else {
      if (operation === "貯存") {
        df = df
          .sortBy(["Quantity", "time", "operation", "name", "city"], true)
          .dropDuplicates("operation", "name", "city");

        df_all = df_all
          .sortBy(["Quantity", "time", "operation", "name", "lon", "lat"], true)
          .dropDuplicates("operation", "name", "lon", "lat");
      } else {
        df = df
          .groupBy("operation", "name", "city")
          .aggregate((group) => group.stat.sum("Quantity"))
          .rename("aggregation", "Quantity");
        df_all = df_all
          .groupBy("operation", "name", "lon", "lat")
          .aggregate((group) => group.stat.sum("Quantity"))
          .rename("aggregation", "Quantity");
      }
    }
    var df2 = df.toCollection();
    var df_all2 = df_all.toCollection();

    // -----
    var hovertemplate = "%{location}<br>TIMEINFO%{z:.2f}公噸";
    if (operation === "貯存") {
      if (time[0] === "最新申報") {
        hovertemplate = hovertemplate.replace(
          "TIMEINFO",
          "最新期別：%{text}<br>"
        );
      } else {
        hovertemplate = hovertemplate.replace(
          "TIMEINFO",
          "最大期別：%{text}<br>"
        );
      }
    } else {
      hovertemplate = hovertemplate.replace("TIMEINFO", "");
    }

    let size = df_all2.map((i) => i.Quantity);
    size = size.map((j) => j / Math.max(...size) + 16);
    var plot = [
      {
        name: "",
        type: "choroplethmapbox",
        geojson: "/taiwan_county_geojson_mini.json",
        locations: df2.map((i) => i.city),
        text: operation === "貯存" ? df2.map((i) => i.time) : " ",
        hovertemplate: hovertemplate,
        hoverlabel: { font: { size: 22 } },
        featureidkey: "properties.NAME_2014",
        z: df2.map((i) => i.Quantity),
        showscale: false,
        zmin: 0,
        colorscale: [
          [0, "rgba(255,200,200,.5)"],
          [1, "rgba(222,30,20,.7)"],
        ],
      },
      {
        lon: df_all2.map((i) => i.lon),
        lat: df_all2.map((i) => i.lat),
        text: df_all2.map((i) => `${i.ComFacBizName_m}:<br> ${i.Quantity}`),
        type: "scattermapbox",
        // hoverinfo: "text",
        name: "",
        // hovertext: df_all2.map((i) => i.ComFacBizName_m),
        hovertemplate: "%{text} 公噸",
        marker: {
          color: "rgba(58,99,73,.95)",
          size: size,
        },
      },
    ];

    // 移除前一次的圖層
    let traceLen = document.querySelector("#map").data.length;
    let drop = [];
    for (let i = 1; i < traceLen; i++) {
      drop.push(-i);
    }
    Plotly.deleteTraces("map", drop);
    Plotly.addTraces("map", plot);
  }
);
</script>