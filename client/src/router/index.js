import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import AboutPage from "../pages/AboutPage.vue";
import ContactPage from "../pages/ContactPage.vue";
import ToolPage from "../pages/ToolPage.vue";


const routes = [
  { path: "/", component: HomePage },
  {
    path: "/tools",
    component: ToolPage
  },
  {
    path: "/about",
    component: AboutPage
  },
  {
    path: "/contact",
    component: ContactPage
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});



export default router;