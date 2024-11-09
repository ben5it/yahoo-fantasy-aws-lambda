import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../pages/HomePage.vue";
import AboutPage from "../pages/AboutPage.vue";
import ContactPage from "../pages/ContactPage.vue";
import UserPage from "../pages/UserPage.vue";
import auth from "../auth";

const routes = [
  { path: "/", component: HomePage },
  {
    path: "/home",
    component: HomePage
  },
  {
    path: "/about",
    component: AboutPage
  },
  {
    path: "/contact",
    component: ContactPage
  },
  {
    path: "/user",
    component: UserPage,
    meta: { requiresAuth: true },
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !auth.isAuthenticated()) {
    next({ path: "/" });
  } else {
    next();
  }
});

export default router;