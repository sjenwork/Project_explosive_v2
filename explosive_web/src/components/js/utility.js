import Plotly from "plotly.js-dist-min";

const range = n => Array.from(Array(n).keys())

const clearPlotlyTrace = (which = 'all') => {
    let trace = document.querySelector("#map").data;
    let traceLen = trace.length

    if (which === 'all') {
        Plotly.deleteTraces("map", range(traceLen).splice(1,))


    } else if (which === 'fac') {
        [...trace].forEach((elem, ind) => {
            if (elem.name === '使用者查詢') {
                Plotly.deleteTraces("map", [ind])
            }
        })
    }
    // Plotly.relayout("map", {
    //     'mapbox.center.lon': calculateCenter(),
    //     'mapbox.center.lat': 23.7,
    //     'mapbox.zoom': 6.8,
    // }
    // )
}

const response2Resize = () => {
    window.addEventListener('resize', () => {
        Plotly.relayout("map", { 'mapbox.center.lon': calculateCenter() })
    })
}

const calculateCenter = () => {
    let width = document.querySelector('body').clientWidth
    // 螢幕寬度1200 => lon=120
    // 螢幕寬度400 => lon=121
    let lon = (1200 - width) / (1200 - 400) * (121 - 119.4) + 119.4
    return lon
}
export { range, clearPlotlyTrace, calculateCenter, response2Resize }