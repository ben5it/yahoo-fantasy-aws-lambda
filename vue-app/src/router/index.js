import { createRouter, createWebHistory } from "vue-router";
import AboutPage from "../pages/AboutPage.vue";
import LeagueListPage from "../pages/LeagueListPage.vue";
import ContactPage from "../pages/ContactPage.vue";
import HomePage from "../pages/HomePage.vue";  
import ToolPage from "../pages/ToolPage.vue";
import AnalysisResult from "../pages/AnalysisResult.vue";

import auth from "../store/auth";

const routes = [
  { path: "/", component: HomePage },
  { path: "/leagues", component: LeagueListPage, meta: { requiresAuth: true } },
  { path: '/result', component: AnalysisResult, meta: { requiresAuth: true } },
  { path: "/tools", component: ToolPage },
  { path: "/about", component: AboutPage },
  { path: "/contact", component: ContactPage }
];



const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!auth.state.authenticated) {
      next({ path: '/' });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;