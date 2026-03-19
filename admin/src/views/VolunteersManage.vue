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
      <el-table-column label="操作" width="430" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link :loading="row.updating" @click="toggleStatus(row)">
            切换为{{ row.status === '已审核' ? '未审核' : '已审核' }}
          </el-button>
          <el-button type="success" link :loading="row.exporting" @click="handleExportWord(row)">
            导出Word
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
  gender: string | null
  id_card: string | null
  age: number | null
  ethnicity: string | null
  phone: string
  service_time: string | null
  organization: string | null
  position: string | null
  email: string | null
  status: VolunteerStatus
  note: string | null
  created_at: string
  updated_at: string
  updating?: boolean
  deleting?: boolean
  exporting?: boolean
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
      exporting: false,
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

const escapeHtml = (value: string) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const normalizeText = (value: string | number | null | undefined) => {
  if (value === null || value === undefined) {
    return ''
  }
  return String(value).trim()
}

const isChecked = (serviceTime: string, key: string) => {
  return serviceTime.includes(key) ? '☑' : '☐'
}

const buildWordHtml = (row: VolunteerItem) => {
  const serviceTime = normalizeText(row.service_time)
  const note = normalizeText(row.note) || '无'
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>志愿者申请表</title>
  <style>
    body { font-family: "Microsoft YaHei", "SimSun", sans-serif; margin: 24px; color: #000; }
    .title { text-align: center; font-size: 20px; font-weight: 700; margin-bottom: 18px; }
    table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    td { border: 1px solid #000; padding: 8px 10px; font-size: 14px; vertical-align: middle; word-break: break-all; }
    .label { width: 18%; font-weight: 600; background: #fafafa; }
    .value { width: 32%; }
    .intro-label { width: 18%; font-weight: 600; background: #fafafa; vertical-align: top; }
    .intro { height: 180px; vertical-align: top; line-height: 1.8; white-space: pre-wrap; }
  </style>
</head>
<body>
  <div class="title">上海谢晋电影艺术基金会<br/>谢晋故居纪念馆志愿者申请表</div>
  <table>
    <tr>
      <td class="label">姓名</td>
      <td class="value">${escapeHtml(normalizeText(row.name))}</td>
      <td class="label">性别</td>
      <td class="value">${escapeHtml(normalizeText(row.gender))}</td>
    </tr>
    <tr>
      <td class="label">身份证</td>
      <td class="value">${escapeHtml(normalizeText(row.id_card))}</td>
      <td class="label">年龄</td>
      <td class="value">${escapeHtml(normalizeText(row.age))}</td>
    </tr>
    <tr>
      <td class="label">民族</td>
      <td class="value">${escapeHtml(normalizeText(row.ethnicity))}</td>
      <td class="label">联系电话</td>
      <td class="value">${escapeHtml(normalizeText(row.phone))}</td>
    </tr>
    <tr>
      <td class="label">邮箱</td>
      <td class="value">${escapeHtml(normalizeText(row.email))}</td>
      <td class="label">服务时段</td>
      <td class="value">${isChecked(serviceTime, '周三')} 周三　${isChecked(serviceTime, '周六')} 周六</td>
    </tr>
    <tr>
      <td class="label">学校 / 单位</td>
      <td class="value">${escapeHtml(normalizeText(row.organization))}</td>
      <td class="label">专业 / 职务</td>
      <td class="value">${escapeHtml(normalizeText(row.position))}</td>
    </tr>
    <tr>
      <td class="intro-label">个人简介</td>
      <td class="intro" colspan="3">${escapeHtml(note)}</td>
    </tr>
  </table>
</body>
</html>`
}

const handleExportWord = (row: VolunteerItem) => {
  row.exporting = true
  try {
    const html = buildWordHtml(row)
    const blob = new Blob(['\ufeff', html], {
      type: 'application/msword;charset=utf-8',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `志愿者申请表-${row.name}-${row.volunteer_id}.doc`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    row.exporting = false
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
