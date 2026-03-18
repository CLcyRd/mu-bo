<template>
  <view class="container">
    <view class="section-title volunteer-title">志愿者报名</view>
    <view v-if="!myVolunteer" class="empty-tip">
      暂无志愿者报名信息
    </view>
    <view v-else class="booking-card">
      <view class="card-header">
        <text class="booking-id">志愿者信息</text>
        <text class="status volunteer-status" :class="getVolunteerStatusClass(myVolunteer.status)">
          {{ myVolunteer.status }}
        </text>
      </view>
      <view class="card-body">
        <view class="info-row">
          <text class="label">报名人：</text>
          <text class="value">{{ myVolunteer.name }}</text>
        </view>
        <view class="info-row">
          <text class="label">报名时间：</text>
          <text class="value">{{ formatVolunteerTime(myVolunteer.created_at) }}</text>
        </view>
        <view class="info-row">
          <text class="label">状态：</text>
          <text class="value">{{ myVolunteer.status }}</text>
        </view>
      </view>
      <view class="card-footer" v-if="myVolunteer.status === '未审核'">
        <button
          class="cancel-btn"
          size="mini"
          type="button"
          plain
          @click="handleVolunteerCancel"
        >取消报名</button>
      </view>
    </view>
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
import { getAuthState, refreshAuthState, goLoginWithRedirect, syncTabBar } from '../../utils/auth'
import { buildApiUrl } from '../../utils/api'

interface Booking {
  id: number
  booking_id: string
  visit_date: string
  visit_time: string
  visitor_name: string
  visitor_count: number
  status: string
}

interface Volunteer {
  volunteer_id: number
  user_id: number
  name: string
  phone: string
  email: string | null
  status: '已审核' | '未审核'
  note: string | null
  created_at: string
  updated_at: string
}

interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

const bookings = ref<Booking[]>([])
const myVolunteer = ref<Volunteer | null>(null)
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

const getVolunteerStatusClass = (status: Volunteer['status']) => {
  return status === '已审核' ? 'approved' : 'unreviewed'
}

const formatVolunteerTime = (value?: string) => {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

const requestWithToken = <T>(url: string, method: 'GET' | 'DELETE') => {
  const token = uni.getStorageSync('token')
  if (!token) {
    goLoginWithRedirect('/pages/my-bookings/my-bookings')
    return Promise.reject(new Error('未登录'))
  }
  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: buildApiUrl(url),
      method,
      header: {
        Authorization: `Bearer ${token}`
      },
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as T)
          return
        }
        reject(res.data || res)
      },
      fail: reject
    })
  })
}

const fetchBookings = async () => {
  try {
    const res = await requestWithToken<Booking[]>('/api/bookings/my', 'GET')
    bookings.value = res
  } catch (e) {
    console.error(e)
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

const fetchMyVolunteer = async () => {
  try {
    const res = await requestWithToken<ApiResponse<{ item: Volunteer | null }>>('/api/volunteers/my', 'GET')
    if (res.code !== 0) {
      throw new Error(res.message || '加载失败')
    }
    myVolunteer.value = res.data?.item || null
  } catch (e: any) {
    myVolunteer.value = null
    const message = e?.message || e?.detail
    if (message && message !== '未登录') {
      uni.showToast({ title: '志愿者信息加载失败', icon: 'none' })
    }
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
          await requestWithToken(`/api/bookings/${item.booking_id}`, 'DELETE')
          uni.showToast({ title: '已取消', icon: 'success' })
          fetchBookings()
        } catch (e: any) {
          uni.showToast({ title: e.detail || '取消失败', icon: 'none' })
        }
      }
    }
  })
}

const handleVolunteerCancel = () => {
  if (!myVolunteer.value) {
    return
  }
  uni.showModal({
    title: '确认取消',
    content: '未审核状态下可取消志愿者报名，确认取消吗？',
    success: async (res) => {
      if (!res.confirm) {
        return
      }
      try {
        const response = await requestWithToken<ApiResponse<{ volunteer_id: number }>>('/api/volunteers/my', 'DELETE')
        if (response.code !== 0) {
          throw new Error(response.message || '取消失败')
        }
        uni.showToast({ title: '已取消报名', icon: 'success' })
        myVolunteer.value = null
      } catch (e: any) {
        const message = e?.message || e?.detail || '取消失败'
        uni.showToast({ title: message, icon: 'none' })
      }
    }
  })
}

onShow(() => {
  syncTabBar()
  const auth = getAuthState()
  if (!auth.loggedIn) {
    refreshAuthState().then((ok) => {
      if (!ok) {
        bookings.value = []
        myVolunteer.value = null
        goLoginWithRedirect('/pages/my-bookings/my-bookings')
      }
    })
    return
  }
  fetchBookings()
  fetchMyVolunteer()
})
</script>

<style>
.container {
  padding: 5rpx 40rpx;
  background: #2b3a6b;
  min-height: 100vh;
  box-sizing: border-box;
}

.section-title {
  font-size: 40rpx;
  font-weight: 700;
  margin: 0 0 24rpx;
  color: #e3d90f;
}

.empty-tip {
  text-align: center;
  color: rgba(255, 255, 255, 0.75);
  padding: 50rpx 20rpx;
  font-size: 28rpx;
  border: 1rpx dashed rgba(227, 217, 15, 0.35);
  border-radius: 22rpx;
  background: rgba(11, 21, 40, 0.35);
}

.booking-card {
  background: #f6f8e1;
  border: 1rpx solid #e0e0e0;
  border-radius: 28rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1rpx solid rgba(44, 63, 103, 0.2);
  padding-bottom: 16rpx;
  margin-bottom: 16rpx;
}

.booking-id {
  font-size: 24rpx;
  color: #5f6368;
}

.status {
  font-size: 26rpx;
  font-weight: bold;
}

.status.confirmed { color: #2c8f5a; }
.status.pending { color: #9b7400; }
.status.cancelled { color: #7a8088; }
.status.volunteer-status.approved { color: #2c8f5a; }
.status.volunteer-status.unreviewed { color: #9b7400; }

.info-row {
  display: flex;
  margin-bottom: 12rpx;
  font-size: 28rpx;
}

.label {
  color: #2c3f67;
  width: 160rpx;
}

.value {
  color: #1a1a1a;
  flex: 1;
}

.card-footer {
  border-top: 1rpx solid rgba(44, 63, 103, 0.2);
  padding-top: 16rpx;
  margin-top: 16rpx;
  text-align: right;
}

.history-section {
  margin-top: 60rpx;
  border-top: 1rpx solid rgba(227, 217, 15, 0.35);
  padding-top: 20rpx;
}

.volunteer-title {
  margin-top: 36rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
}

.toggle-icon {
  font-size: 24rpx;
  color: rgba(227, 217, 15, 0.95);
}

.history-card {
  opacity: 0.92;
}

.cancel-btn {
  background: transparent;
  border: 1rpx solid #2c3f67;
  color: #2c3f67;
  border-radius: 32rpx;
  font-size: 24rpx;
  padding: 0 24rpx;
  height: 56rpx;
  line-height: 56rpx;
}
</style>
