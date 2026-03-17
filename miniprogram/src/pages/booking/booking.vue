<template>
  <view class="container">
    <view class="page-header">
      <view class="page-title">参观预约</view>
      <view class="page-subtitle">Visit Booking</view>
    </view>
    <view class="form-card">
      <view class="form-title">填写预约信息</view>
      
      <view class="form-item">
        <text class="label">参观人/领队 姓名</text>
        <input class="input" v-model="form.visitor_name" placeholder="请输入姓名" />
      </view>
      
      <view class="form-item">
        <text class="label">手机号</text>
        <view class="phone-group">
          <input class="input" v-model="form.visitor_phone" placeholder="请输入手机号" type="number" />
        </view>
      </view>
      
      <view class="form-item">
        <text class="label">参观日期</text>
        <picker mode="date" :start="startDate" :end="endDate" @change="onDateChange">
          <view class="picker-value">{{ form.visit_date || '请选择日期' }}</view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="label">参观时间</text>
        <picker mode="selector" :range="timeSlots" @change="onTimeChange">
          <view class="picker-value">{{ form.visit_time || '请选择时间段' }}</view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="label">人数</text>
        <slider :value="form.visitor_count" @change="onCountChange" min="1" max="5" show-value />
      </view>
      
      <button class="submit-btn" type="button" @click="submitBooking">立即预约</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

const form = reactive({
  visitor_name: '',
  visitor_phone: '',
  visit_date: '',
  visit_time: '',
  visitor_count: 1
})

const countdown = ref(0)
const timeSlots = ['10:00-11:00', '11:00-12:00', '12:00-13:00', '13:00-14:00', '14:00-15:00']

const startDate = computed(() => {
  const d = new Date()
  return d.toISOString().split('T')[0]
})

const endDate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 30)
  return d.toISOString().split('T')[0]
})

const onDateChange = (e: any) => {
  form.visit_date = e.detail.value
}

const onTimeChange = (e: any) => {
  form.visit_time = timeSlots[e.detail.value]
}

const onCountChange = (e: any) => {
  form.visitor_count = e.detail.value
}


const submitBooking = () => {
  if (!form.visitor_name || !form.visitor_phone || !form.visit_date || !form.visit_time) {
    uni.showToast({ title: '请完善预约信息', icon: 'none' })
    return
  }
  
  const token = uni.getStorageSync('token')
  
  uni.showLoading({ title: '提交中...' })
  uni.request({
    url: 'http://localhost:8000/api/bookings/',
    method: 'POST',
    data: form,
    header: token ? {
      'Authorization': `Bearer ${token}`
    } : {},
    success: (res: any) => {
      uni.hideLoading()
      if (res.statusCode === 200) {
        uni.showToast({ title: '预约成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/my-bookings/my-bookings'
          })
        }, 1500)
      } else {
        uni.showToast({ title: '预约失败', icon: 'none' })
      }
    },
    fail: () => {
      uni.hideLoading()
      uni.showToast({ title: '网络请求失败', icon: 'none' })
    }
  })
}
</script>

<style>
.container {
  padding: 80rpx 40rpx 40rpx;
  background: #2b3a6b;
  min-height: 100vh;
  box-sizing: border-box;
}
.page-header {
  margin-bottom: 28rpx;
}
.page-title {
  font-size: 56rpx;
  font-weight: 700;
  color: #e3d90f;
  line-height: 1.25;
}
.page-subtitle {
  margin-top: 8rpx;
  font-size: 26rpx;
  font-weight: 500;
  color: #e3d90f;
  line-height: 1.3;
}
.form-card {
  background: #f6f8e1;
  border: 1rpx solid #e0e0e0;
  border-radius: 28rpx;
  padding: 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}
.form-title {
  font-size: 34rpx;
  font-weight: bold;
  text-align: center;
  margin-bottom: 34rpx;
  color: #1a1a1a;
}
.form-item {
  margin-bottom: 30rpx;
}
.label {
  display: block;
  font-size: 26rpx;
  color: #2c3f67;
  margin-bottom: 10rpx;
}
.input, .picker-value {
  background: #ffffff;
  height: 80rpx;
  line-height: 80rpx;
  padding: 0 24rpx;
  border-radius: 18rpx;
  font-size: 28rpx;
  color: #1a1a1a;
  border: 1rpx solid #d5dbe8;
}
.phone-group {
  display: flex;
  gap: 20rpx;
}
.phone-group .input {
  flex: 1;
}
.submit-btn {
  margin-top: 60rpx;
  background-color: #3a60a7;
  color: white;
  border-radius: 48rpx;
  font-size: 32rpx;
  font-weight: 700;
  border: none;
}
.submit-btn:active {
  background-color: #2f4f8f;
}
</style>
