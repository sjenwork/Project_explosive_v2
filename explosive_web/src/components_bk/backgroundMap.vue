<template>
  <div id="map" style="width: 100vw"></div>
</template>

<script setup>
import Plotly from "plotly.js-dist-min";
import { onMounted } from "vue";

function plotmap(center = { lon: 121, lat: 23.7 }) {
  var data = [
    {
      type: "scattermapbox",
      text: [],
      lon: [],
      lat: [],
    },
    //   {
    //     name: "",
    //     type: "choroplethmapbox",
    //     geojson: twbndUrl,
    //     locations: Object.keys(choroplethPlot.cnt),
    //     text: location,
    //     hovertemplate: "%{location}<br>%{z}公噸",
    //     hoverlabel: { font: { size: 22 } },
    //     featureidkey: "properties.NAME_2014",
    //     z: Object.values(choroplethPlot.cnt).map((i) => i.toFixed(2)),
    //     showscale: false,
    //     zmin: 0,
    //     // zmax: 1,
    //     colorscale:
    //       plotType === "newPlot"
    //         ? [
    //             [0, "rgba(255,200,200,.1)"],
    //             [1, "rgba(222,30,20,.2)"],
    //           ]
    //         : [
    //             [0, "rgba(255,200,200,.5)"],
    //             [1, "rgba(222,30,20,.7)"],
    //           ],
    //   },
    //   {
    //     lon: scatterPlot.all.map(({ X }) => X),
    //     lat: scatterPlot.all.map(({ Y }) => Y),
    //     type: "scattermapbox",
    //     hoverinfo: "text",
    //     hovertext: scatterPlot.all.map(({ ComFacBizName }) => ComFacBizName),
    //     marker: {
    //       color: "rgba(58,99,73,.95)",
    //       size: scatterPlot.quantity.map(
    //         (i) => i / Math.max(...scatterPlot.quantity) + 16
    //       ),
    //     },
    //   },
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
  // if (plotType === "newPlot") {
  //   Plotly.newPlot("map", data, layout, config);
  //   let map = document.querySelector("#map");
  //   map.on("plotly_relayout", (evt) => {
  //     if (evt["mapbox.zoom"] < 6.8) {
  //       if (document.body.clientWidth > 768) {
  //         lon = 121 - document.body.clientWidth / 768;
  //       } else {
  //         lon = 121;
  //       }
  //       Plotly.relayout("map", {
  //         "mapbox.zoom": 6.8,
  //         "mapbox.center.lon": lon,
  //         "mapbox.center.lat": 23.7,
  //       });
  //       //     evt["mapbox.zoom"] = 6.5;
  //     }
  //   });
  // } else if (plotType === "rePlot") {
  //   let traceLen = document.querySelector("#map").data.length;
  //   let drop = [];
  //   for (let i = 1; i < traceLen; i++) {
  //     drop.push(-i);
  //   }
  //   Plotly.deleteTraces("map", drop);
  //   Plotly.addTraces("map", data.slice(1));
  //   // Plotly.addTraces("map", data);
  // }
}

onMounted(() => {
  plotmap();
});
</script>

<style scoped>
#map {
  width: 100%;
  height: 100vh;
}
</style>