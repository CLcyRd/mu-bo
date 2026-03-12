<template>
  <div class="consultation-edit-page">
    <div class="page-header">
      <el-button type="primary" link @click="goBack">返回咨询管理</el-button>
      <h2>编辑咨询</h2>
    </div>

    <BlogEditor
      :key="editorKey"
      mode="edit"
      :initial-data="initialData"
      :loading="loading"
      @save="handleSave"
      @publish="handlePublish"
      @cancel="goBack"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import BlogEditor from '../components/BlogEditor.vue'
import api from '../api'

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type NewsDetail = {
  id: string
  title: string
  cover: string
  content: string
  status: 0 | 1
}

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const editorKey = ref(0)
const newsId = String(route.params.id || '')
const currentStatus = ref<0 | 1>(0)
const initialData = ref({
  title: '',
  cover: '',
  content: ''
})

const goBack = () => {
  router.push('/blog/manage')
}

const loadNewsDetail = async () => {
  if (!newsId) {
    ElMessage.error('咨询ID无效')
    goBack()
    return
  }
  loading.value = true
  try {
    const response = await api.get<ApiResponse<NewsDetail>>(`/consultations/${newsId}`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '加载咨询失败')
    }
    initialData.value = {
      title: response.data.data.title,
      cover: response.data.data.cover || '',
      content: response.data.data.content
    }
    currentStatus.value = response.data.data.status
    editorKey.value += 1
  } catch (error) {
    const message = error instanceof Error ? error.message : '加载咨询失败'
    ElMessage.error(message)
    goBack()
  } finally {
    loading.value = false
  }
}

const updateNews = async (payload: { title: string; content: string; cover: string }, statusValue: 0 | 1) => {
  const response = await api.put<ApiResponse<{ id: string; status: number; updated_at: string }>>(
    `/consultations/${newsId}`,
    {
      title: payload.title,
      cover: payload.cover,
      content: payload.content,
      status: statusValue
    }
  )
  if (response.data.code !== 0) {
    throw new Error(response.data.message || '保存失败')
  }
  currentStatus.value = statusValue
}

const handleSave = async (payload: { title: string; content: string; cover: string }) => {
  loading.value = true
  try {
    await updateNews(payload, currentStatus.value)
    ElMessage.success('保存成功')
    goBack()
  } catch (error) {
    const message = error instanceof Error ? error.message : '保存失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handlePublish = async (payload: { title: string; content: string; cover: string }) => {
  loading.value = true
  try {
    await updateNews(payload, 1)
    ElMessage.success('保存并发布成功')
    goBack()
  } catch (error) {
    const message = error instanceof Error ? error.message : '保存失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadNewsDetail()
})
</script>

<style scoped>
.consultation-edit-page {
  padding: 20px;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}
</style>
