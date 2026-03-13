<template>
  <div>
    <h2>参馆预约</h2>
    <el-table :data="bookings" style="width: 100%">
      <el-table-column prop="booking_id" label="预定号" />
      <el-table-column prop="visitor_name" label="访客名" />
      <el-table-column prop="visit_date" label="预定日期" />
      <el-table-column prop="visit_time" label="预定时间" />
      <el-table-column prop="visitor_count" label="访客人数" />
      <el-table-column prop="status" label="状态">
        <template #default="scope">
          <el-tag>{{ scope.row.status }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '../api'
import { ElMessage } from 'element-plus'

const bookings = ref([])

const fetchBookings = async () => {
  try {
    const res = await api.get('/bookings/')
    bookings.value = res.data
  } catch (error) {
    ElMessage.error('Failed to fetch bookings')
  }
}

onMounted(fetchBookings)
</script>
