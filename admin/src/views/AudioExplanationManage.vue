<template>
  <div class="audio-explanation-manage-page">
    <div class="page-header">
      <h2>讲解音频管理</h2>
      <el-button type="primary" :loading="loading" @click="loadList">刷新</el-button>
    </div>

    <el-table :data="items" v-loading="loading" stripe>
      <el-table-column prop="id" label="音频ID" width="120" />
      <el-table-column prop="title" label="讲解标题" min-width="220" />
      <el-table-column label="发布状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'">
            {{ row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="640" fixed="right">
        <template #default="{ row }">
          <el-button type="info" link @click="openDescription(row)">查看简介</el-button>
          <el-button type="primary" link @click="openPlayer(row)">播放录音</el-button>
          <el-button type="primary" link :loading="row.togglingStatus" @click="handleToggleStatus(row)">
            切换为{{ row.status === 'published' ? '草稿' : '已发布' }}
          </el-button>
          <el-button v-if="!row.qr_code_url" type="success" link :loading="row.generatingCode" @click="handleGenerateMiniCode(row)">生成小程序码</el-button>
          <el-button v-if="row.qr_code_url" type="warning" link @click="handleViewMiniCode(row)">查看小程序码</el-button>
          <el-button v-if="row.qr_code_url" type="danger" link :loading="row.deletingCode" @click="handleDeleteMiniCode(row)">删除小程序码</el-button>
          <el-button type="danger" link :loading="row.deleting" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="descriptionDialogVisible" title="讲解简介" width="560px">
      <div class="description-text">{{ currentDescription || '暂无简介' }}</div>
      <template #footer>
        <el-button type="primary" @click="descriptionDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="playerDialogVisible" title="录音播放" width="640px">
      <div class="player-title">{{ currentPlayerTitle }}</div>
      <audio v-if="currentAudioUrl" class="audio-player" :src="resolveUploadUrl(currentAudioUrl)" controls preload="metadata" />
      <div v-else class="no-audio-text">当前记录无音频地址</div>
      <template #footer>
        <el-button type="primary" @click="playerDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="miniCodeDialogVisible" title="小程序码" width="420px">
      <div v-if="currentMiniCodeUrl" class="mini-code-wrap">
        <img class="mini-code-image" :src="resolveUploadUrl(currentMiniCodeUrl)" alt="小程序码" />
      </div>
      <div v-else class="no-audio-text">当前记录暂无小程序码</div>
      <template #footer>
        <el-button type="primary" @click="miniCodeDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

type AudioExplanationItem = {
  id: number
  title: string
  audio_url: string
  description: string | null
  status: 'draft' | 'published'
  qr_code_url?: string | null
  deleting?: boolean
  generatingCode?: boolean
  deletingCode?: boolean
  togglingStatus?: boolean
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

const loading = ref(false)
const items = ref<AudioExplanationItem[]>([])
const descriptionDialogVisible = ref(false)
const currentDescription = ref('')
const playerDialogVisible = ref(false)
const currentAudioUrl = ref('')
const currentPlayerTitle = ref('')
const miniCodeDialogVisible = ref(false)
const currentMiniCodeUrl = ref('')

const resolveUploadUrl = (url: string) => {
  if (!url) {
    return ''
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return url
}

const loadList = async () => {
  loading.value = true
  try {
    const response = await api.get<ApiResponse<{ items: AudioExplanationItem[] }>>('/audio-explanations')
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '加载失败')
    }
    items.value = (response.data.data.items || []).map((item) => ({
      ...item,
      deleting: false,
      generatingCode: false,
      deletingCode: false,
      togglingStatus: false,
    }))
  } catch (error) {
    const message = error instanceof Error ? error.message : '加载失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const handleToggleStatus = async (row: AudioExplanationItem) => {
  row.togglingStatus = true
  try {
    const response = await api.patch<ApiResponse<{ id: number; status: 'draft' | 'published' }>>(`/audio-explanations/${row.id}/status`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '状态切换失败')
    }
    row.status = response.data.data.status
    ElMessage.success('状态切换成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '状态切换失败'
    ElMessage.error(message)
  } finally {
    row.togglingStatus = false
  }
}

const openDescription = (row: AudioExplanationItem) => {
  currentDescription.value = row.description || ''
  descriptionDialogVisible.value = true
}

const openPlayer = (row: AudioExplanationItem) => {
  currentPlayerTitle.value = row.title
  currentAudioUrl.value = row.audio_url || ''
  playerDialogVisible.value = true
}

const handleGenerateMiniCode = async (row: AudioExplanationItem) => {
  row.generatingCode = true
  try {
    const response = await api.post<ApiResponse<{ id: number; qr_code_url: string }>>(`/audio-explanations/${row.id}/mini-code`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '生成失败')
    }
    row.qr_code_url = response.data.data.qr_code_url
    currentMiniCodeUrl.value = row.qr_code_url || ''
    miniCodeDialogVisible.value = true
    ElMessage.success('小程序码生成成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '生成失败'
    ElMessage.error(message)
  } finally {
    row.generatingCode = false
  }
}

const handleViewMiniCode = async (row: AudioExplanationItem) => {
  try {
    const response = await api.get<ApiResponse<{ id: number; qr_code_url: string | null }>>(`/audio-explanations/${row.id}/mini-code`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '查询失败')
    }
    row.qr_code_url = response.data.data.qr_code_url || ''
    currentMiniCodeUrl.value = row.qr_code_url || ''
    miniCodeDialogVisible.value = true
  } catch (error) {
    const message = error instanceof Error ? error.message : '查询失败'
    ElMessage.error(message)
  }
}

const handleDeleteMiniCode = async (row: AudioExplanationItem) => {
  row.deletingCode = true
  try {
    const response = await api.delete<ApiResponse<{ id: number }>>(`/audio-explanations/${row.id}/mini-code`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '删除失败')
    }
    row.qr_code_url = null
    if (currentMiniCodeUrl.value) {
      currentMiniCodeUrl.value = ''
    }
    ElMessage.success('小程序码删除成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '删除失败'
    ElMessage.error(message)
  } finally {
    row.deletingCode = false
  }
}

const handleDelete = async (row: AudioExplanationItem) => {
  try {
    await ElMessageBox.confirm(`确认删除讲解音频「${row.title}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
    row.deleting = true
    const response = await api.delete<ApiResponse<{ id: number }>>(`/audio-explanations/${row.id}`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '删除失败')
    }
    items.value = items.value.filter((item) => item.id !== row.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      return
    }
    const message = error instanceof Error ? error.message : '删除失败'
    ElMessage.error(message)
  } finally {
    row.deleting = false
  }
}

onMounted(() => {
  loadList()
})
</script>

<style scoped>
.audio-explanation-manage-page {
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

.description-text {
  min-height: 80px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-break: break-word;
}

.player-title {
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 12px;
}

.audio-player {
  width: 100%;
}

.no-audio-text {
  color: #909399;
}

.mini-code-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
}

.mini-code-image {
  width: 280px;
  height: 280px;
  object-fit: contain;
  border: 1px solid #ebeef5;
  border-radius: 8px;
}
</style>
