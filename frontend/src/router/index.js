import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/login", name: "Login", component: () => import("../views/Login.vue") },
  { path: "/", name: "Dashboard", component: () => import("../views/Dashboard.vue"), meta: { auth: true } },
  { path: "/analysis", name: "Analysis", component: () => import("../views/Analysis.vue"), meta: { auth: true } },
  { path: "/market", name: "Market", component: () => import("../views/Market.vue"), meta: { auth: true } },
  { path: "/cars", name: "Cars", component: () => import("../views/Cars.vue"), meta: { auth: true } },
  { path: "/cars/:id", name: "CarDetail", component: () => import("../views/CarDetail.vue"), meta: { auth: true } },
  { path: "/recommendations", name: "Rec", component: () => import("../views/Recommendations.vue"), meta: { auth: true } },
  { path: "/admin", name: "Admin", component: () => import("../views/Admin.vue"), meta: { auth: true } },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (to.meta.auth && !token) next("/login");
  else next();
});

export default router;
