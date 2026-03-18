<template>
  <div v-loading="loading">
    <h2>参馆预约</h2>
    <el-table :data="bookings" style="width: 100%">
      <el-table-column prop="booking_id" label="预定号" />
      <el-table-column prop="visitor_name" label="访客名" />
      <el-table-column prop="visit_date" label="预定日期" />
      <el-table-column prop="visit_time" label="预定时间" />
      <el-table-column prop="visitor_count" label="访客人数" />
      <el-table-column prop="visitor_phone" label="手机号" />
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button type="danger" link @click="handleDelete(scope.row.booking_id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

type BookingItem = {
  booking_id: string
  visitor_name: string
  visitor_phone: string
  visit_date: string
  visit_time: string
  visitor_count: number
}

const bookings = ref<BookingItem[]>([])
const loading = ref(false)

const fetchBookings = async () => {
  loading.value = true
  try {
    const res = await api.get<BookingItem[]>('/bookings/')
    bookings.value = res.data
  } catch (error) {
    ElMessage.error('加载预约列表失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = async (bookingId: string) => {
  if (!bookingId) {
    return
  }
  try {
    await ElMessageBox.confirm(`确认删除预定号 ${bookingId} 吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消'
    })
    await api.delete(`/bookings/${bookingId}`)
    ElMessage.success('删除成功')
    await fetchBookings()
  } catch (error) {
    if (error === 'cancel') {
      return
    }
    ElMessage.error('删除预约失败')
  }
}

onMounted(fetchBookings)
</script>
