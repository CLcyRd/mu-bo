import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Exhibits from '../views/Exhibits.vue'
import Bookings from '../views/Bookings.vue'

const routes = [
  { path: '/login', component: Login },
  { 
    path: '/', 
    component: Dashboard,
    children: [
      { path: 'exhibits', component: Exhibits },
      { path: 'bookings', component: Bookings }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const username = localStorage.getItem('username')
  
  if (to.path !== '/login') {
    if (!token) {
      next('/login')
    } else if (username !== 'admin') {
      // Simple role check on frontend, backend does real check
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      alert('Access Denied: You are not an admin.')
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
