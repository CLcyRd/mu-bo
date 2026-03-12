<template>
  <div class="create-blog-page">
    <div class="page-header">
      <h2>发布咨询</h2>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>资讯管理</el-breadcrumb-item>
        <el-breadcrumb-item>发布咨询</el-breadcrumb-item>
      </el-breadcrumb>
    </div>

    <div class="page-content">
      <BlogEditor
        :key="editorKey"
        mode="create"
        :loading="loading"
        @publish="handlePublish"
        @save="handleSave"
        @cancel="handleCancel"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import BlogEditor from '../components/BlogEditor.vue'
import api from '../api'

type EditorPayload = { title: string; content: string; cover: string }
type ApiResponse<T> = { code: number; message: string; data: T }

const router = useRouter()
const loading = ref(false)
const editorKey = ref(0)

const createIdempotencyKey = () => {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

const createNews = async (payload: EditorPayload, status: 0 | 1) => {
  const response = await api.post<ApiResponse<{ id: number; status: number }>>(
    '/consultations',
    {
      title: payload.title,
      cover: payload.cover,
      content: payload.content,
      status
    },
    {
      headers: {
        'Idempotency-Key': createIdempotencyKey()
      }
    }
  )
  if (response.data.code !== 0) {
    throw new Error(response.data.message || '请求失败')
  }
  return response.data
}

const handlePublish = async (data: EditorPayload) => {
  try {
    await ElMessageBox.confirm(
      '确定要发布这篇咨询吗？发布后用户将立即可见。',
      '确认发布',
      {
        confirmButtonText: '确认发布',
        cancelButtonText: '再想想',
        type: 'warning',
      }
    )

    loading.value = true
    await createNews(data, 1)
    ElMessage.success('咨询发布成功')
    editorKey.value += 1
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    const message = error instanceof Error ? error.message : '发布失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleSave = async (data: EditorPayload) => {
  loading.value = true
  try {
    await createNews(data, 0)
    ElMessage.success('草稿保存成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '保存失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  router.back()
}
</script>

<style scoped>
.create-blog-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 16px 0;
  font-size: 24px;
  color: #303133;
}

.page-content {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
