import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Bookings from '../views/Bookings.vue'
import CreateBlog from '../views/CreateBlog.vue'
import ConsultationManage from '../views/ConsultationManage.vue'
import ConsultationEdit from '../views/ConsultationEdit.vue'
import VolunteersManage from '../views/VolunteersManage.vue'

const routes: RouteRecordRaw[] = [
  { path: '/login', component: Login },
  { 
    path: '/', 
    component: Dashboard,
    children: [
      { path: 'bookings', component: Bookings },
      { path: 'blog/create', component: CreateBlog },
      { path: 'blog/manage', component: ConsultationManage },
      { path: 'blog/edit/:id', component: ConsultationEdit },
      { path: 'volunteers', component: VolunteersManage }
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
