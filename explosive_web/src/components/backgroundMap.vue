<template>
  <div id="map"></div>
  <!-- style="width: 100vw" -->
</template>

<script setup>
import Plotly from "plotly.js-dist-min";
// import * as am5 from "@amcharts/amcharts5";
// import * as am5map from "@amcharts/amcharts5/map";
// import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";
// import am5geodata_worldLow from "@amcharts/amcharts5-geodata/worldLow";


// import * as L from "leaflet"
// import "leaflet/dist/leaflet.css"
// import { LMap, LGeoJson } from "@vue-leaflet/vue-leaflet";

import { onMounted, watch } from "vue";
import { clearPlotlyTrace, calculateCenter, response2Resize } from "./js/utility.js"

const props = defineProps({ plotFromChemSearch: Object, plotFromFacSearch: Object, focusdata: Object });
var render_lib = "plotly"


watch(
  () => [props.focusdata],
  ([newfocusdata], [oldfocusdata]) => {
    // ------------------------------------------------------
    // 標記選取的廠商
    if (newfocusdata) {
      clearPlotlyTrace('fac')

      if (newfocusdata.state) {
        var data = newfocusdata.row
        console.log(data)
        var plot = [
          {
            lon: data.map((i) => i.lon),
            lat: data.map((i) => i.lat),
            text: data.map((i) => `${i.ComFacBizName}`),
            type: "scattermapbox",
            // hoverinfo: "text",
            name: "使用者查詢",
            // hovertext: data_fac.map((i) => i.ComFacBizName),
            // hovertemplate: "%{text}",
            marker: {
              color: "rgb(21,100,255)",
              size: 20,
              opacity: .7
              // symbol: 'x',
            },
          },
        ];

        Plotly.addTraces("map", plot);

        var focus = false
        if (focus) {
          if (data.map((i) => i.lat)[0]) {
            var method = 'relayout';

            if (method === 'animate') {
              Plotly.animate('map',
                {
                  layout: {
                    mapbox: {
                      zoom: 9,
                      center: {
                        lon: data.map((i) => i.lon)[0] - 0.2,
                        lat: data.map((i) => i.lat)[0]
                      }
                    }
                  }
                },
              )
            } else if (method === 'relayout') {
              Plotly.relayout('map', {

                'mapbox.zoom': 9,
                'mapbox.center.lon': data.map((i) => i.lon)[0] - 0.2,
                'mapbox.center.lat': data.map((i) => i.lat)[0],
              }
              )
            }
          }

        }
      }
    }
    // 標記選取的廠商 end
    // ------------------------------------------------------
  });
watch(
  () => [props.plotFromChemSearch],
  ([newPlotVal], [oldPlotVal]) => {
    // ------------------------------------------------------
    // 繪製
    if (oldPlotVal !== newPlotVal) {

      var time = newPlotVal.time
      var chem = newPlotVal.chem
      var operation = newPlotVal.operation
      var [data_city, data_fac] = newPlotVal.data

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

      let RegionType = [...new Set([...data_fac_plot].map(i => i.RegionType))]
      let size = [...data_fac_plot].map((i) => i.Quantity);
      size = size.map((j) => j / Math.max(...size) + 10);
      var plot1 = [
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
            [0, "rgba(255,250,205,.7)"],
            [1, "rgba(222,230,52,.7)"],
          ],
        }]
      var plot2 = []
      RegionType.forEach(rt => {
        var lon = [...data_fac_plot].filter(i => i.RegionType === rt).map((i) => i.lon)
        var lat = [...data_fac_plot].filter(i => i.RegionType === rt).map((i) => i.lat)
        var text = [...data_fac_plot].filter(i => i.RegionType === rt).map((i) => `${i.ComFacBizName}:<br> ${i.time} <br> ${i.Quantity}`)
        plot2.push(
          {
            lon: lon,
            lat: lat,
            text: text,
            type: "scattermapbox",
            name: rt,
            hovertemplate: "%{text} 公噸",
            marker: {
              size: size,
            },
            selected: {
              color: 'red',
              size: 20
            }
          }
        )
      })
      var plot = [...plot1, ...plot2]
      clearPlotlyTrace('all')
      Plotly.addTraces("map", plot);


    }
    // 繪製 end
    // ------------------------------------------------------
    // console.log(document.querySelector("#map").data.length)
  })
watch(
  () => [props.plotFromFacSearch],
  ([newPlotVal], [oldPlotVal]) => {
    if (oldPlotVal !== newPlotVal) {

      // ---
      var time = newPlotVal.time
      var data_fac = newPlotVal.data[0].data

      var data_fac_plot = data_fac


      let RegionType = [...new Set([...data_fac_plot].map(i => i.RegionType))]
      let size = [...data_fac_plot].map((i) => i.Quantity);
      size = size.map((j) => j / Math.max(...size) + 20);

      var plot2 = []
      RegionType.forEach(rt => {
        var lon = [...data_fac_plot].filter(i => i.RegionType === rt).map((i) => i.lon)
        var lat = [...data_fac_plot].filter(i => i.RegionType === rt).map((i) => i.lat)
        var text = [...data_fac_plot].filter(i => i.RegionType === rt).map((i) => `${i.name}:<br> ${i.time} <br> ${i.operation} ${i.Quantity.toFixed(2)}`)
        plot2.push(
          {
            lon: lon,
            lat: lat,
            text: text,
            type: "scattermapbox",
            name: rt,
            hovertemplate: "%{text} 公噸",
            marker: {
              size: size,
            },
            selected: {
              color: 'red',
              size: 20
            }
          }
        )
      })
      var plot = [...plot2]
      clearPlotlyTrace('all')
      Plotly.addTraces("map", plot);

      // ---


    }
  })

function initMap(center = { lon: 121, lat: 23.7 }) {

  if (render_lib === 'plotly') {
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
      showlegend: true,
      legend: {
        bgcolor: 'rgba(255,255,220,.6)',
        bordercolor: 'black',
        borderwidth: 1,
        x: 0.99,
        y: 0.01,
        xanchor: 'right',
        yanchor: 'bottom',
        font: {
          size: 20
        }


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
    //   console.log(clickpoint)
    // })
  } else if (render_lib === 'leaflet') {
    var root = am5.Root.new("map");

    // Set themes
    root.setThemes([
      am5themes_Animated.new(root)
    ]);

    var chart = root.container.children.push(
      am5map.MapChart.new(root, {
        panX: "rotateX",
        projection: am5map.geoNaturalEarth1()
      })
    );

    // Create polygon series
    var polygonSeries = chart.series.push(
      am5map.MapPolygonSeries.new(root, {
        geoJSON: am5geodata_worldLow,
        exclude: ["AQ"]
      })
    );

    polygonSeries.mapPolygons.template.setAll({
      tooltipText: "{name}",
      interactive: true
    });

    polygonSeries.mapPolygons.template.states.create("hover", {
      fill: am5.color(0x677935)
    });



  }
}


onMounted(() => {
  response2Resize()
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