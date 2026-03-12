<template>
  <div class="consultation-manage-page">
    <div class="page-header">
      <h2>咨询管理</h2>
      <el-button type="primary" @click="loadNewsList" :loading="loading">刷新</el-button>
    </div>

    <el-table :data="newsList" v-loading="loading" stripe>
      <el-table-column prop="id" label="咨询ID" width="210" />
      <el-table-column prop="title" label="标题" min-width="180" />
      <el-table-column label="正文前20字" min-width="220">
        <template #default="{ row }">
          <span>{{ row.contentPreview }}</span>
        </template>
      </el-table-column>
      <el-table-column label="发布时间" min-width="180">
        <template #default="{ row }">
          <span>{{ formatTime(row.updated_at || row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="发布状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'info'">
            {{ row.status === 1 ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          <el-button type="primary" link @click="handleToggleStatus(row)">
            切换为{{ row.status === 1 ? '草稿' : '已发布' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

type NewsItem = {
  id: string
  title: string
  content: string
  contentPreview: string
  created_at: string
  updated_at: string
  status: 0 | 1
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

const loading = ref(false)
const newsList = ref<NewsItem[]>([])
const router = useRouter()

const stripHtml = (html: string) => html.replace(/<[^>]+>/g, '')
const previewText = (text: string) => (text.length > 20 ? `${text.slice(0, 20)}...` : text)
const formatTime = (value: string) => new Date(value).toLocaleString()

const loadNewsList = async () => {
  loading.value = true
  try {
    const response = await api.get<ApiResponse<{ items: NewsItem[] }>>('/consultations', {
      params: { page: 1, page_size: 100 }
    })
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '加载咨询失败')
    }
    newsList.value = (response.data.data.items || []).map((item) => ({
      ...item,
      contentPreview: previewText(stripHtml(item.content || ''))
    }))
  } catch (error) {
    const message = error instanceof Error ? error.message : '加载咨询失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (row: NewsItem) => {
  try {
    await ElMessageBox.confirm(`确认删除咨询「${row.title}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
    await api.delete<ApiResponse<{ id: string }>>(`/consultations/${row.id}`)
    ElMessage.success('删除成功')
    await loadNewsList()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    const message = error instanceof Error ? error.message : '删除失败'
    ElMessage.error(message)
  }
}

const handleToggleStatus = async (row: NewsItem) => {
  const targetStatus: 0 | 1 = row.status === 1 ? 0 : 1
  try {
    await api.patch<ApiResponse<{ id: string; status: number }>>(`/consultations/${row.id}/status`, {
      status: targetStatus
    })
    ElMessage.success('状态更新成功')
    await loadNewsList()
  } catch (error) {
    const message = error instanceof Error ? error.message : '状态更新失败'
    ElMessage.error(message)
  }
}

const handleEdit = (row: NewsItem) => {
  router.push(`/blog/edit/${row.id}`)
}

onMounted(() => {
  loadNewsList()
})
</script>

<style scoped>
.consultation-manage-page {
  padding: 20px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0;
}
</style>
