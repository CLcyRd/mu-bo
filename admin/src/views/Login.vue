<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>Admin Login</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="Username">
          <el-input v-model="form.username"></el-input>
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleLogin">Login</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  try {
    const formData = new FormData()
    formData.append('username', form.username)
    formData.append('password', form.password)
    
    const response = await api.post('/token', formData)
    const token = response.data.access_token
    localStorage.setItem('token', token)
    localStorage.setItem('username', form.username) // Store username for basic role check if needed
    
    ElMessage.success('Login successful')
    router.push('/')
  } catch (error) {
    console.error(error)
    ElMessage.error('Invalid credentials or server error')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}
.login-card {
  width: 400px;
}
</style>
