import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import MapView from '../views/MapView.vue'
import ProfileView from '../views/ProfileView.vue' 
import AdminView from '../views/AdminView.vue'  // 👈 Импортируем


const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/map', name: 'Map', component: MapView },
  { path: '/profile', name: 'Profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: AdminView }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 🛡️ Глобальная защита маршрутов
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('auth_token')
  
  if (to.meta.requiresAuth && !token) {
    next('/auth')
  } else {
    next()
  }
})

export default router