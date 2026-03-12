<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu router :default-active="$route.path" class="el-menu-vertical">
        <el-menu-item index="/bookings">
          <el-icon><calendar /></el-icon>
          <span>Bookings</span>
        </el-menu-item>
        <el-menu-item index="/blog/create">
          <el-icon><edit-pen /></el-icon>
          <span>发布咨询</span>
        </el-menu-item>
        <el-menu-item index="/blog/manage">
          <el-icon><management /></el-icon>
          <span>咨询管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <h3>Museum Admin</h3>
          <el-button type="text" @click="logout">Logout</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Document, Calendar, EditPen, Management } from '@element-plus/icons-vue'

const router = useRouter()

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.el-menu-vertical {
  height: 100%;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
  border-bottom: 1px solid #dcdfe6;
}
</style>
