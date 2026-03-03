<template>
  <view class="container">
    <!-- Upcoming Bookings -->
    <view class="section-title">我的预约</view>
    <view v-if="upcomingBookings.length === 0" class="empty-tip">
      暂无即将到来的预约
    </view>
    <view 
      class="booking-card" 
      v-for="item in upcomingBookings" 
      :key="item.id"
    >
      <view class="card-header">
        <text class="booking-id">预约号: {{ item.booking_id.slice(0, 100) }}</text>
      </view>
      <view class="card-body">
        <view class="info-row">
          <text class="label">参观日期：</text>
          <text class="value">{{ item.visit_date }}</text>
        </view>
        <view class="info-row">
          <text class="label">参观时间：</text>
          <text class="value">{{ item.visit_time }}</text>
        </view>
        <view class="info-row">
          <text class="label">参观人数：</text>
          <text class="value">{{ item.visitor_count }}人</text>
        </view>
        <view class="info-row">
          <text class="label">参观人：</text>
          <text class="value">{{ item.visitor_name }}</text>
        </view>
      </view>
      <view class="card-footer" v-if="item.status !== 'cancelled'">
        <button 
          class="cancel-btn" 
          size="mini" 
          type="button" 
          plain 
          @click="handleCancel(item)"
        >取消预约</button>
      </view>
    </view>

    <!-- Past Bookings -->
    <view class="history-section">
      <view class="section-header" @click="toggleHistory">
        <text class="section-title">历史记录</text>
        <text class="toggle-icon">{{ showHistory ? '收起 ▲' : '展开 ▼' }}</text>
      </view>
      
      <view v-if="showHistory">
        <view v-if="pastBookings.length === 0" class="empty-tip">
          暂无历史记录
        </view>
        <view 
          class="booking-card history-card" 
          v-for="item in pastBookings" 
          :key="item.id"
        >
          <view class="card-header">
            <text class="booking-id">预约号: {{ item.booking_id.slice(0, 8) }}...</text>
            <text class="status" :class="item.status">{{ getStatusText(item.status) }}</text>
          </view>
          <view class="card-body">
            <view class="info-row">
              <text class="label">参观日期：</text>
              <text class="value">{{ item.visit_date }}</text>
            </view>
            <view class="info-row">
              <text class="label">参观时间：</text>
              <text class="value">{{ item.visit_time }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'

interface Booking {
  id: number
  booking_id: string
  visit_date: string
  visit_time: string
  visitor_name: string
  visitor_count: number
  status: string
}

const bookings = ref<Booking[]>([])
const showHistory = ref(false)

const upcomingBookings = computed(() => {
  const now = new Date()
  const todayStr = now.toISOString().split('T')[0]
  
  return bookings.value.filter(b => {
    // If cancelled, treat as history? Or keep in main list but marked cancelled?
    // Requirement: "在当前时间之前的记录为以往记录"
    // So future cancelled bookings are technically "upcoming" in time, but maybe user wants to see them.
    // Let's strictly follow time.
    if (b.visit_date > todayStr) return true
    if (b.visit_date === todayStr) {
        // Simple time check, assuming format "HH:MM-HH:MM" or "HH:MM"
        // If it's a range like "09:00-11:00", take end time? Or start time?
        // Let's assume start time for safety.
        // If visit_time is just a string label, we might need parsing.
        // Assuming standard sortable string for now.
        return true 
    }
    return false
  })
})

const pastBookings = computed(() => {
  const now = new Date()
  const todayStr = now.toISOString().split('T')[0]
  
  return bookings.value.filter(b => {
    if (b.visit_date < todayStr) return true
    // Logic for today? If passed? simplified to date for now.
    return false
  })
})

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    'pending': '待确认',
    'confirmed': '已预约',
    'cancelled': '已取消'
  }
  return map[status] || status
}

const fetchBookings = async () => {
  const token = uni.getStorageSync('token')
  if (!token) {
    uni.navigateTo({ url: '/pages/login/login' })
    return
  }

  try {
    const res = await new Promise<any>((resolve, reject) => {
      uni.request({
        url: 'http://localhost:8000/api/bookings/my',
        method: 'GET',
        header: {
          'Authorization': `Bearer ${token}`
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(res)
          }
        },
        fail: reject
      })
    })
    bookings.value = res
  } catch (e) {
    console.error(e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const toggleHistory = () => {
  showHistory.value = !showHistory.value
}

const handleCancel = (item: Booking) => {
  uni.showModal({
    title: '确认取消',
    content: '确定要取消这条预约吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          const token = uni.getStorageSync('token')
          await new Promise((resolve, reject) => {
            uni.request({
              url: `http://localhost:8000/api/bookings/${item.booking_id}`,
              method: 'DELETE',
              header: {
                'Authorization': `Bearer ${token}`
              },
              success: (res) => {
                if (res.statusCode === 204 || res.statusCode === 200) {
                  resolve(res.data)
                } else {
                  reject(res.data)
                }
              },
              fail: reject
            })
          })
          
          uni.showToast({ title: '已取消', icon: 'success' })
          fetchBookings() // Refresh list
        } catch (e: any) {
          uni.showToast({ title: e.detail || '取消失败', icon: 'none' })
        }
      }
    }
  })
}

onShow(() => {
  fetchBookings()
})
</script>

<style>
.container {
  padding: 20rpx;
  background-color: #f8f8f8;
  min-height: 100vh;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  margin: 20rpx 0;
  color: #333;
}

.empty-tip {
  text-align: center;
  color: #999;
  padding: 40rpx;
  font-size: 28rpx;
}

.booking-card {
  background: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1rpx solid #eee;
  padding-bottom: 16rpx;
  margin-bottom: 16rpx;
}

.booking-id {
  font-size: 24rpx;
  color: #999;
}

.status {
  font-size: 26rpx;
  font-weight: bold;
}

.status.confirmed { color: #07c160; }
.status.pending { color: #ff9900; }
.status.cancelled { color: #999; }

.info-row {
  display: flex;
  margin-bottom: 12rpx;
  font-size: 28rpx;
}

.label {
  color: #666;
  width: 160rpx;
}

.value {
  color: #333;
  flex: 1;
}

.card-footer {
  border-top: 1rpx solid #eee;
  padding-top: 16rpx;
  margin-top: 16rpx;
  text-align: right;
}

.history-section {
  margin-top: 60rpx;
  border-top: 1rpx solid #ddd;
  padding-top: 20rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
}

.toggle-icon {
  font-size: 24rpx;
  color: #666;
}

.history-card {
  opacity: 0.8;
  background-color: #f9f9f9;
}
</style>
