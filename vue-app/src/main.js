import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import auth from './store/auth';
import leagueStore from './store/league';

// import './style.css'
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS

const app = createApp(App);
app.provide('auth', auth);
app.provide('leagueStore', leagueStore);

app.use(router);
app.mount('#app');


