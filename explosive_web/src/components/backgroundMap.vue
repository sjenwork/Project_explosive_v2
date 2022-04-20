<template>
  <div
    id="map"
    style="width: 100vw"
  ></div>
</template>

<script setup>
import Plotly from "plotly.js-dist-min";
import { onMounted, watch } from "vue";

const props = defineProps({ plotdata: Object });

watch(
  () => [props.plotdata],
  ([newVal], [oldVal]) => {
    var time = newVal.time
    var chem = newVal.chem
    var operation = newVal.operation
    var [data_city, data_fac] = newVal.data

    var data_city_plot = data_city.proc
    var data_fac_plot = data_fac.proc

    var hovertemplate = "%{location}<br>TIMEINFO%{z:.2f}公噸";
    if (operation.chn === "貯存") {
      if (time[0].time === "最新申報") {
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

    let size = [...data_fac_plot].map((i) => i.Quantity);
    size = size.map((j) => j / Math.max(...size) + 16);
    var plot = [
      {
        name: "",
        type: "choroplethmapbox",
        geojson: "./taiwan_county_geojson_mini.json",
        locations: [...data_city_plot].map((i) => i.city),
        text: operation.chn === "貯存" ? [...data_city_plot].map((i) => i.time) : " ",
        hovertemplate: hovertemplate,
        hoverlabel: { font: { size: 22 } },
        featureidkey: "properties.NAME_2014",
        z: [...data_city_plot].map((i) => i.Quantity),
        showscale: false,
        zmin: 0,
        colorscale: [
          [0, "rgba(255,200,200,.5)"],
          [1, "rgba(222,30,20,.7)"],
        ],
      },
      {
        lon: [...data_fac_plot].map((i) => i.lon),
        lat: [...data_fac_plot].map((i) => i.lat),
        text: [...data_fac_plot].map((i) => `${i.ComFacBizName}:<br> ${i.time} <br> ${i.Quantity}`),
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




  })


function initMap(center = { lon: 121, lat: 23.7 }) {
  var data = [
    {
      type: "scattermapbox",
      text: [],
      lon: [],
      lat: [],
    },
  ];

  var layout = {
    dragmode: "zoom",
    mapbox: {
      center: { lon: center.lon, lat: center.lat },
      zoom: 6.8,
      style: "white-bg",
      layers: [
        {
          sourcetype: "raster",
          source: [
            "https://wmts.nlsc.gov.tw/wmts/EMAP/default/EPSG:3857/{z}/{y}/{x}",
          ],
          below: "traces",
        },
        {
          below: "traces",
          sourcetype: "geojson",
          source: "./taiwan_county_geojson_mini.json",
          type: "line",
          color: "purple",
          opacity: 0.4,
          line: { width: 1 },
        },
      ],
    },
    margin: {
      r: 0,
      t: 0,
      b: 0,
      l: 0,
    },
    showlegend: false,
  };
  var config = {
    doubleClick: true,
    doubleClickDelay: 10,
    responsive: true,
    autosize: true, // set autosize to rescale
    displayModeBar: false,
  };
  Plotly.newPlot("map", data, layout, config);
}

onMounted(() => {
  initMap();
});


</script>

<style scoped>
#map {
  width: 100%;
  height: 100vh;
}
</style>