<template></template>
<script setup>
import { ref, watch } from "vue";
import Plotly from "plotly.js-dist-min";
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
    console.log(data)
    console.log(time)
    console.log(chem)
    console.log(operation)
    if (data.res_city) {

      var data_city_all = data.res_city;
      var data_fac_all = data.res_fac;

      var data_city;
      var data_fac;
      var cityList = [...new Set(data_city_all.map(i => i.city))];

      if (operation == '貯存') {
        data_city = new DataFrame(data_city_all)
          .sortBy(["Quantity", "time", "operation", "name", "city"], true)
          .dropDuplicates("operation", "name", "city")
          .toCollection();

        data_fac_all = data_fac_all.filter(i => i.lon != '')
        data_fac = new DataFrame(data_fac_all)
          .sortBy(["Quantity", "time", "operation", "name", "lon", "lat"], true)
          .dropDuplicates("operation", "name", "lon", "lat")
          .toCollection();
        // data_fac.show()

      } else {
        data_city = new DataFrame(data_city_all)
          .groupBy("operation", "name", "city")
          .aggregate((group) => group.stat.sum("Quantity"))
          .rename("aggregation", "Quantity")
          .toCollection();
        data_fac = new DataFrame(data_fac_all)
          .groupBy("operation", "name", "lon", "lat")
          .aggregate((group) => group.stat.sum("Quantity"))
          .rename("aggregation", "Quantity")
          .toCollection();

      }
      console.log(data_city)
      console.log(data_fac)

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

      let size = data_fac.map((i) => i.Quantity);
      size = size.map((j) => j / Math.max(...size) + 16);
      var plot = [
        {
          name: "",
          type: "choroplethmapbox",
          geojson: "./taiwan_county_geojson_mini.json",
          locations: data_city.map((i) => i.city),
          text: operation === "貯存" ? data_city.map((i) => i.time) : " ",
          hovertemplate: hovertemplate,
          hoverlabel: { font: { size: 22 } },
          featureidkey: "properties.NAME_2014",
          z: data_city.map((i) => i.Quantity),
          showscale: false,
          zmin: 0,
          colorscale: [
            [0, "rgba(255,200,200,.5)"],
            [1, "rgba(222,30,20,.7)"],
          ],
        },
        {
          lon: data_fac.map((i) => i.lon),
          lat: data_fac.map((i) => i.lat),
          text: data_fac.map((i) => `${i.ComFacBizName}:<br> ${i.Quantity}`),
          type: "scattermapbox",
          // hoverinfo: "text",
          name: "",
          // hovertext: data_fac.map((i) => i.ComFacBizName),
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
  }
);
</script>