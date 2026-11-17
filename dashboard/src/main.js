import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import Toast from "vue-toastification";
// Import the CSS or use your own!
import "vue-toastification/dist/index.css";

import VueSocialSharing from 'vue-social-sharing';
import {
  Button,
  Card,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'


let app = createApp(App)



setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)
app.use(VueSocialSharing);
app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)



const options = {
  position: "bottom-right",
};

app.use(Toast, options);


app.mount('#app')
