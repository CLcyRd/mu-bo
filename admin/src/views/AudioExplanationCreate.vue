<template>
  <div class="audio-explanation-create-page">
    <div class="page-header">
      <h2>上传讲解音频</h2>
      <el-button @click="resetForm">重置</el-button>
    </div>

    <el-card class="form-card">
      <el-form label-width="120px">
        <el-form-item label="讲解标题" required>
          <el-input v-model="form.title" maxlength="255" placeholder="请输入讲解标题" />
        </el-form-item>

        <el-form-item label="音频文件" required>
          <el-upload
            class="audio-upload"
            action="#"
            :limit="1"
            accept=".mp3,.m4a,.aac,.wav,audio/*"
            :auto-upload="true"
            :show-file-list="true"
            :http-request="handleUploadAudio"
            :before-remove="handleBeforeRemove"
            :on-exceed="handleExceed"
          >
            <el-button type="primary" :loading="uploading">选择并上传音频</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 MP3/M4A/AAC/WAV，最大 20MB</div>
            </template>
          </el-upload>
          <div v-if="form.audio_url" class="audio-url">已上传：{{ form.audio_url }}</div>
        </el-form-item>

        <el-form-item label="简介">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            maxlength="2000"
            show-word-limit
            placeholder="请输入简介（可选）"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleCreate">创建讲解</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import api from '../api'

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

const form = reactive({
  title: '',
  audio_url: '',
  description: ''
})

const uploading = ref(false)
const saving = ref(false)

const resetForm = () => {
  form.title = ''
  form.audio_url = ''
  form.description = ''
}

const handleUploadAudio = async (options: UploadRequestOptions) => {
  const file = options.file as File
  const formData = new FormData()
  formData.append('file', file)
  uploading.value = true
  try {
    const response = await api.post<ApiResponse<{ url: string }>>('/audio-explanations/upload-audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000
    })
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '上传失败')
    }
    form.audio_url = response.data.data.url
    ElMessage.success('音频上传成功')
    options.onSuccess?.(response.data)
  } catch (error) {
    const message = error instanceof Error ? error.message : '上传失败'
    ElMessage.error(message)
    options.onError?.({ name: 'UploadError', message } as any)
  } finally {
    uploading.value = false
  }
}

const handleBeforeRemove = async () => {
  form.audio_url = ''
  return true
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个音频文件，请先移除当前文件')
}

const handleCreate = async () => {
  if (!form.title.trim()) {
    ElMessage.warning('请输入讲解标题')
    return
  }
  if (!form.audio_url.trim()) {
    ElMessage.warning('请先上传音频文件')
    return
  }
  if (saving.value) {
    return
  }
  saving.value = true
  try {
    const response = await api.post<ApiResponse<{ item: { id: number } }>>('/audio-explanations', {
      title: form.title.trim(),
      audio_url: form.audio_url.trim(),
      description: form.description.trim() || null,
      status: 'draft'
    })
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '创建失败')
    }
    ElMessage.success('讲解创建成功')
    resetForm()
  } catch (error) {
    const message = error instanceof Error ? error.message : '创建失败'
    ElMessage.error(message)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.audio-explanation-create-page {
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

.form-card {
  max-width: 900px;
  margin: 0 auto;
}

.audio-upload {
  width: 100%;
}

.audio-url {
  margin-top: 8px;
  color: #606266;
  word-break: break-all;
}
</style>
