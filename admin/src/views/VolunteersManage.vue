<template>
  <div class="volunteers-manage-page">
    <div class="page-header">
      <h2>志愿者管理</h2>
      <el-button type="primary" :loading="loading" @click="loadVolunteers">刷新</el-button>
    </div>

    <el-table :data="volunteers" v-loading="loading" stripe>
      <el-table-column prop="name" label="姓名" min-width="120" />
      <el-table-column prop="phone" label="手机号" min-width="140" />
      <el-table-column label="邮箱" min-width="220">
        <template #default="{ row }">
          <span>{{ row.email || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="注册时间" min-width="190">
        <template #default="{ row }">
          <span>{{ formatTime(row.created_at) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === '已审核' ? 'success' : 'info'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="360" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link :loading="row.updating" @click="toggleStatus(row)">
            切换为{{ row.status === '已审核' ? '未审核' : '已审核' }}
          </el-button>
          <el-button type="info" link @click="handleViewNote(row)">
            查看备注
          </el-button>
          <el-button type="danger" link :loading="row.deleting" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="noteDialogVisible" title="志愿者备注" width="520px">
      <el-input
        v-model="noteDraft"
        type="textarea"
        :rows="6"
        maxlength="2000"
        show-word-limit
        placeholder="请输入备注内容"
      />
      <template #footer>
        <el-button @click="noteDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="noteSaving" @click="handleSaveNote">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../api'

type VolunteerStatus = '已审核' | '未审核'

type VolunteerItem = {
  volunteer_id: number
  user_id: number
  name: string
  phone: string
  email: string | null
  status: VolunteerStatus
  note: string | null
  created_at: string
  updated_at: string
  updating?: boolean
  deleting?: boolean
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

const loading = ref(false)
const volunteers = ref<VolunteerItem[]>([])
const noteDialogVisible = ref(false)
const noteSaving = ref(false)
const noteDraft = ref('')
const editingVolunteerId = ref<number | null>(null)

const formatTime = (value: string) => {
  if (!value) {
    return '-'
  }
  return new Date(value).toLocaleString()
}

const loadVolunteers = async () => {
  loading.value = true
  try {
    const response = await api.get<ApiResponse<{ items: VolunteerItem[] }>>('/volunteers')
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '加载志愿者失败')
    }
    volunteers.value = (response.data.data.items || []).map((item) => ({
      ...item,
      updating: false,
      deleting: false,
    }))
  } catch (error) {
    const message = error instanceof Error ? error.message : '加载志愿者失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}

const toggleStatus = async (row: VolunteerItem) => {
  const targetStatus: VolunteerStatus = row.status === '已审核' ? '未审核' : '已审核'
  row.updating = true
  try {
    const response = await api.patch<ApiResponse<{ volunteer_id: number; status: VolunteerStatus }>>(
      `/volunteers/${row.volunteer_id}/status`,
      { status: targetStatus }
    )
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '状态更新失败')
    }
    row.status = targetStatus
    ElMessage.success('状态更新成功')
  } catch (error) {
    const message = error instanceof Error ? error.message : '状态更新失败'
    ElMessage.error(message)
  } finally {
    row.updating = false
  }
}

const handleDelete = async (row: VolunteerItem) => {
  try {
    await ElMessageBox.confirm(`确认删除志愿者「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
    })
    row.deleting = true
    const response = await api.delete<ApiResponse<{ volunteer_id: number }>>(`/volunteers/${row.volunteer_id}`)
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '删除失败')
    }
    volunteers.value = volunteers.value.filter((item) => item.volunteer_id !== row.volunteer_id)
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

const handleViewNote = (row: VolunteerItem) => {
  editingVolunteerId.value = row.volunteer_id
  noteDraft.value = row.note || ''
  noteDialogVisible.value = true
}

const handleSaveNote = async () => {
  const volunteerId = editingVolunteerId.value
  if (!volunteerId) {
    return
  }
  noteSaving.value = true
  try {
    const response = await api.patch<ApiResponse<{ volunteer_id: number; note: string | null }>>(
      `/volunteers/${volunteerId}/note`,
      { note: noteDraft.value.trim() || null }
    )
    if (response.data.code !== 0) {
      throw new Error(response.data.message || '备注保存失败')
    }
    volunteers.value = volunteers.value.map((item) =>
      item.volunteer_id === volunteerId ? { ...item, note: response.data.data.note } : item
    )
    ElMessage.success('备注保存成功')
    noteDialogVisible.value = false
  } catch (error) {
    const message = error instanceof Error ? error.message : '备注保存失败'
    ElMessage.error(message)
  } finally {
    noteSaving.value = false
  }
}

onMounted(() => {
  loadVolunteers()
})
</script>

<style scoped>
.volunteers-manage-page {
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
