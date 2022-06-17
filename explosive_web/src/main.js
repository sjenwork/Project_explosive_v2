import {
    createApp
} from "vue";
import App from "./App.vue";
// import * as bootstrap from "bootstrap"; // Import js file
import "bootstrap"; // Import js filebe
import "bootstrap/dist/css/bootstrap.min.css"; // Import css file
import "vue-multiselect/dist/vue-multiselect.css"; // Import css file
import "@vueform/slider/themes/default.css"; // Import css file
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import './assets/css/style.css';
import { library, dom } from '@fortawesome/fontawesome-svg-core'
import { fas } from '@fortawesome/free-solid-svg-icons'
import { far } from '@fortawesome/free-regular-svg-icons'
import { fab } from '@fortawesome/free-brands-svg-icons'
// import {Vue} from "vue";
import Vue3TouchEvents from "vue3-touch-events";


dom.watch();
library.add(fas, far, fab)


let app = createApp(App);
app.component("font-awesome-icon", FontAwesomeIcon)
app.use(Vue3TouchEvents);
app.mount("#app");
