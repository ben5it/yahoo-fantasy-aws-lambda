import { createRouter, createWebHistory } from "vue-router";
import AboutPage from "../pages/AboutPage.vue";
import LeagueListPage from "../pages/LeagueListPage.vue";
import ContactPage from "../pages/ContactPage.vue";
import HomePage from "../pages/HomePage.vue";  
import ToolPage from "../pages/ToolPage.vue";

import auth from '../store/auth'; // Import the auth store

const routes = [
  { path: "/", component: HomePage },
  { 
    path: "/analysis", 
    component: LeagueListPage,
    beforeEnter: (to, from, next) => {
      if (auth.state.authenticated) {
        next();
      } else {
        next('/');
      }
    }
  },
  { path: "/tools", component: ToolPage },
  { path: "/about", component: AboutPage },
  { path: "/contact", component: ContactPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});



export default router;