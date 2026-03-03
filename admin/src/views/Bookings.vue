<template>
  <div>
    <h2>Bookings</h2>
    <el-table :data="bookings" style="width: 100%">
      <el-table-column prop="booking_id" label="Booking ID" />
      <el-table-column prop="visitor_name" label="Name" />
      <el-table-column prop="visit_date" label="Date" />
      <el-table-column prop="visit_time" label="Time" />
      <el-table-column prop="visitor_count" label="Count" />
      <el-table-column prop="status" label="Status">
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
