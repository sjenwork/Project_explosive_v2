<template>
  <div id="map"></div>
  <!-- style="width: 100vw" -->
</template>

<script setup>
import Plotly from "plotly.js-dist-min";
import { onMounted, watch, ref } from "vue";
import { clearPlotlyTrace, response2Resize } from "./js/utility.js";

const props = defineProps({
  plotFromChemSearch: Object,
  plotFromFacSearch: Object,
  focusdata: Object,
});
var render_lib = "plotly";

var operationOptions = ref([
  { chn: "輸入", eng: "import" },
  { chn: "貯存", eng: "storage" },
  { chn: "製造", eng: "prod" },
  { chn: "使用", eng: "usage" },
]);

watch(
  () => [props.focusdata],
  ([newfocusdata], [oldfocusdata]) => {
    //  console.log(newfocusdata);
    // ------------------------------------------------------
    // 標記選取的廠商
    if (newfocusdata) {
      clearPlotlyTrace("fac");

      if (newfocusdata.state) {
        var data = { ...newfocusdata.row };
        //  console.log(data);
        var plot = {
          lon: [data.X],
          lat: [data.Y],
          text: [data.comname],
          type: "scattermapbox",
          hoverinfo: "text",
          name: "使用者查詢",
          // hovertext: data_fac.map((i) => i.ComFacBizName),
          hovertemplate: "%{text}",
          marker: {
            color: "rgb(21,100,255)",
            size: 20,
            opacity: 0.7,
            // symbol: 'x',
          },
        };
        //  console.log(plot);
        Plotly.addTraces("map", plot);

        var focus = true;
        if (focus) {
          if (data) {
            var method = "relayout";
            if (method === "animate") {
              Plotly.animate("map", {
                layout: {
                  mapbox: {
                    zoom: 9,
                    center: {
                      lon: data.map((i) => i.lon)[0] - 0.2,
                      lat: data.map((i) => i.lat)[0],
                    },
                  },
                },
              });
            } else if (method === "relayout") {
              Plotly.animate("map", {
                transition: {
                  duration: 500,
                  easing: "linear",
                },
                frame: {
                  duration: 500,
                  redraw: false,
                },
                mode: "next",
              });
              //  console.log(data.X);
              if (data.X != "") {
                Plotly.relayout("map", {
                  "mapbox.zoom": 9,
                  "mapbox.center.lon": data.X - 0.2,
                  "mapbox.center.lat": data.Y,
                });
              }
            }
          }
        }
      }
    }
    // 標記選取的廠商 end
    // ------------------------------------------------------
  }
);
watch(
  () => [props.plotFromChemSearch],
  ([newPlotVal], [oldPlotVal]) => {
    // console.log(newPlotVal);
    // ------------------------------------------------------
    // 繪製
    if (oldPlotVal !== newPlotVal) {
      var time = newPlotVal.time;
      var chem = newPlotVal.chem;
      var operation = newPlotVal.operation;
      var [data_city, data_fac] = newPlotVal.data;
      var data_city_plot = data_city.data;
      var data_fac_plot = data_fac.data;

      var hovertemplate = "%{location}<br>%{z:.2f}公噸";
      // if (operation.chn === "貯存") {
      //   hovertemplate = hovertemplate.replace("TIMEINFO", "最大期別：%{text}<br>");
      // } else {
      //   hovertemplate = hovertemplate.replace("TIMEINFO", "");
      // }

      let RegionType = [...new Set([...data_fac_plot].map((i) => i.regiontype))];
      let size = [...data_fac_plot].map((i) => i.Q);
      size = size.map((j) => j / Math.max(...size) + 10);

      var plot1 = [
        {
          name: "",
          type: "choroplethmapbox",
          geojson: "./taiwan_county_geojson_mini.json",
          locations: [...data_city_plot].map((i) => i.City),
          // text: operation.chn === "貯存" ? [...data_city_plot].map((i) => i.time) : " ",
          hovertemplate: hovertemplate,
          hoverlabel: { font: { size: 22 } },
          featureidkey: "properties.NAME_2014",
          z: [...data_city_plot].map((i) => i.Q),
          showscale: false,
          zmin: 0,
          colorscale: [
            [0, "rgba(255,250,205,.7)"],
            [1, "rgba(222,230,52,.7)"],
          ],
        },
      ];
      var plot2 = [];
      RegionType.forEach((rt) => {
        //  console.log("rt-", rt);
        var X = [...data_fac_plot].filter((i) => i.regiontype === rt).map((i) => i.X);
        var Y = [...data_fac_plot].filter((i) => i.regiontype === rt).map((i) => i.Y);
        var text = [...data_fac_plot]
          .filter((i) => i.regiontype === rt)
          .map((i) => `${i.comname}:<br> ${i.declaretime} <br> ${i.Q}`);
        var color = [...data_fac_plot]
          .filter((i) => i.regiontype === rt)
          .map((i) => {
            if (i.regiontype === "科學園區") {
              return "#41b6bd";
            } else if (i.regiontype === "工業區") {
              return "#dc3545";
            } else if (i.regiontype === "加工出口區") {
              return "#5b2b75";
            } else if (i.regiontype === "礦區") {
              return "#eeb412";
            } else if (i.regiontype === "其他") {
              return "#84c779";
            } else if (i.regiontype === "港區") {
              return "#f171ae";
            }
          });
        plot2.push({
          lon: X,
          lat: Y,
          text: text,
          type: "scattermapbox",
          name: rt,
          hovertemplate: "%{text} 公噸",
          marker: {
            size: size,
            color: color,
          },
          selected: {
            color: "red",
            size: 20,
          },
        });
      });

      var plot = [...plot1, ...plot2];
      clearPlotlyTrace("all");
      Plotly.addTraces("map", plot);
    }
    // 繪製 end
    // ------------------------------------------------------
    // console.log(document.querySelector("#map").data.length)
  }
);
watch(
  () => [props.plotFromFacSearch],
  ([newPlotVal], [oldPlotVal]) => {
    if (oldPlotVal !== newPlotVal) {
      // ---
      var time = newPlotVal.time;
      var data_city = newPlotVal.data[0].data;
      var data_fac = newPlotVal.data[1].data;

      var data_city_plot = data_city;
      var data_fac_plot = data_fac;

      let regiontype = [...new Set([...data_fac_plot].map((i) => i.regiontype))];
      let size = [...data_fac_plot].map((i) => i.Q);
      size = size.map((j) => j / Math.max(...size) + 10);

      var locations = [...new Set([...data_city_plot].map((i) => i.City))];
      var zs = locations.length ? Array(locations.length).fill(0) : [];
      var plot1 = [
        {
          name: "",
          type: "choroplethmapbox",
          geojson: "./taiwan_county_geojson_mini.json",
          locations: locations,
          // text: operation.chn === "貯存" ? [...data_city_plot].map((i) => i.time) : " ",
          hovertemplate: "%{location}",
          hoverlabel: { font: { size: 22 } },
          featureidkey: "properties.NAME_2014",
          z: zs,
          showscale: false,
          zmin: 0,
          colorscale: [
            [0, "rgba(255,250,205,.7)"],
            [1, "rgba(222,230,52,.7)"],
          ],
        },
      ];

      var plot2 = [];
      regiontype.forEach((rt) => {
        var lon = [...data_fac_plot].filter((i) => i.regiontype === rt).map((i) => i.X);
        var lat = [...data_fac_plot].filter((i) => i.regiontype === rt).map((i) => i.Y);
        var hovertemplate = [...data_fac_plot]
          .filter((i) => i.regiontype === rt)
          .map((i) => {
            return (
              `${i.comname}` +
              `<br>${i.declaretime}` +
              `<br>${
                operationOptions.value.filter((j) => j.eng === i.operation)[0]["chn"]
              }` +
              `${i.Q.toFixed(2)} 公噸`
            );
          });
        const color = [...data_fac_plot]
          .filter((i) => i.regiontype === rt)
          .map((i) => {
            if (i.regiontype === "科學園區") {
              return "#41b6bd";
            } else if (i.regiontype === "工業區") {
              return "#dc3545";
            } else if (i.regiontype === "加工出口區") {
              return "#5b2b75";
            } else if (i.regiontype === "礦區") {
              return "#eeb412";
            } else if (i.regiontype === "其他") {
              return "#84c779";
            } else if (i.regiontype === "港區") {
              return "#f171ae";
            }
          });

        plot2.push({
          lon: lon,
          lat: lat,
          // text: text,
          type: "scattermapbox",
          name: rt,
          hovertemplate: hovertemplate,
          marker: {
            size: size,
            color: color,
          },
          selected: {
            color: "red",
            size: 20,
          },
        });
      });

      var plot = [...plot1, ...plot2];
      clearPlotlyTrace("all");
      Plotly.addTraces("map", plot);

      // ---
    }
  }
);

function initMap(center = { lon: 121, lat: 23.7 }) {
  if (render_lib === "plotly") {
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
            source: ["https://wmts.nlsc.gov.tw/wmts/EMAP/default/EPSG:3857/{z}/{y}/{x}"],
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
      showlegend: true,
      legend: {
        bgcolor: "rgba(240,240,240,1)",
        bordercolor: "black",
        borderwidth: 1,
        x: 0.99,
        y: 0.01,
        xanchor: "right",
        yanchor: "bottom",
        font: {
          size: 24,
        },
      },
    };

    var config = {
      doubleClick: true,
      doubleClickDelay: 10,
      responsive: true,
      autosize: true, // set autosize to rescale
      displayModeBar: false,
    };
    Plotly.newPlot("map", data, layout, config);

    // let mymap = document.querySelector('#map')
    // mymap.on('plotly_click', (i) => {
    //   var clickpoint = i.points[0].text.split(':')[0]
    // //  console.log(clickpoint)
    // })
  } else if (render_lib === "leaflet") {
    var root = am5.Root.new("map");

    // Set themes
    root.setThemes([am5themes_Animated.new(root)]);

    var chart = root.container.children.push(
      am5map.MapChart.new(root, {
        panX: "rotateX",
        projection: am5map.geoNaturalEarth1(),
      })
    );

    // Create polygon series
    var polygonSeries = chart.series.push(
      am5map.MapPolygonSeries.new(root, {
        geoJSON: am5geodata_worldLow,
        exclude: ["AQ"],
      })
    );

    polygonSeries.mapPolygons.template.setAll({
      tooltipText: "{name}",
      interactive: true,
    });

    polygonSeries.mapPolygons.template.states.create("hover", {
      fill: am5.color(0x677935),
    });
  }
}

onMounted(() => {
  response2Resize();
  initMap();
  // initMap({ lon: 120, lat: 23.7 });
  // initMap({ lon: calculateCenter(), lat: 23.7 });
});
</script>

<style scoped>
#map {
  width: 100vw;
  height: 100vh;
}

/* g.infolayer {
  border-color: black;
} */
</style>
