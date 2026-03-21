<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu router :default-active="$route.path" class="el-menu-vertical">
        <el-menu-item index="/bookings">
          <el-icon><calendar /></el-icon>
          <span>参馆预约</span>
        </el-menu-item>
        <el-menu-item index="/blog/create">
          <el-icon><edit-pen /></el-icon>
          <span>发布咨询</span>
        </el-menu-item>
        <el-menu-item index="/blog/manage">
          <el-icon><management /></el-icon>
          <span>咨询管理</span>
        </el-menu-item>
        <el-menu-item index="/volunteers">
          <el-icon><user /></el-icon>
          <span>志愿者管理</span>
        </el-menu-item>
        <el-menu-item index="/audio-explanations/create">
          <el-icon><mic /></el-icon>
          <span>上传讲解音频</span>
        </el-menu-item>
        <el-menu-item index="/audio-explanations/manage">
          <el-icon><headset /></el-icon>
          <span>讲解音频管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header>
        <div class="header-content">
          <h3>谢晋故居数据管理平台</h3>
          <el-button type="text" @click="logout">退出登录</el-button>
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
import { Calendar, EditPen, Management, User, Mic, Headset } from '@element-plus/icons-vue'

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
