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


let app = createApp(App);
app.component("font-awesome-icon", FontAwesomeIcon)
app.mount("#app");