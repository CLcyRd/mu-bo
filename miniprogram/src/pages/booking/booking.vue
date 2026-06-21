<template>
  <view class="container">
    <view class="page-header">
      <view class="page-title">开放日预约</view>
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
        <picker mode="selector" :range="saturdayDateOptions" @change="onDateChange">
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
import { reactive } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { ensureLoginOrRedirect } from '../../utils/auth'
import { buildApiUrl } from '../../utils/api'

const form = reactive({
  visitor_name: '',
  visitor_phone: '',
  visit_date: '',
  visit_time: '',
  visitor_count: 1
})

const bookingWindowDays = 60
const timeSlots = ['13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00']

const formatDate = (date: Date) => {
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  return `${year}-${month}-${day}`
}

const createSaturdayDateOptions = () => {
  const options: string[] = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  for (let offset = 0; offset <= bookingWindowDays; offset += 1) {
    const current = new Date(today)
    current.setDate(today.getDate() + offset)
    if (current.getDay() === 6) {
      options.push(formatDate(current))
    }
  }
  return options
}

const saturdayDateOptions = createSaturdayDateOptions()

const onDateChange = (e: any) => {
  const selected = saturdayDateOptions[Number(e.detail.value)]
  form.visit_date = selected || ''
}

const onTimeChange = (e: any) => {
  form.visit_time = timeSlots[Number(e.detail.value)] || ''
}

const onCountChange = (e: any) => {
  form.visitor_count = e.detail.value
}

const createBookingRedirectUrl = () => {
  const query: string[] = []
  if (form.visitor_name) query.push(`visitor_name=${encodeURIComponent(form.visitor_name)}`)
  if (form.visitor_phone) query.push(`visitor_phone=${encodeURIComponent(form.visitor_phone)}`)
  if (form.visit_date) query.push(`visit_date=${encodeURIComponent(form.visit_date)}`)
  if (form.visit_time) query.push(`visit_time=${encodeURIComponent(form.visit_time)}`)
  query.push(`visitor_count=${encodeURIComponent(String(form.visitor_count))}`)
  return `/pages/booking/booking?${query.join('&')}`
}

const toNumber = (value: unknown, defaultValue: number) => {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : defaultValue
}

onLoad((options) => {
  if (!options) {
    return
  }
  form.visitor_name = typeof options.visitor_name === 'string' ? decodeURIComponent(options.visitor_name) : ''
  form.visitor_phone = typeof options.visitor_phone === 'string' ? decodeURIComponent(options.visitor_phone) : ''
  form.visit_date = typeof options.visit_date === 'string' ? decodeURIComponent(options.visit_date) : ''
  form.visit_time = typeof options.visit_time === 'string' ? decodeURIComponent(options.visit_time) : ''
  form.visitor_count = toNumber(options.visitor_count, 1)
  if (form.visit_date && !saturdayDateOptions.includes(form.visit_date)) {
    form.visit_date = ''
  }
  if (form.visit_time && !timeSlots.includes(form.visit_time)) {
    form.visit_time = ''
  }
})


const submitBooking = async () => {
  const loggedIn = await ensureLoginOrRedirect(createBookingRedirectUrl())
  if (!loggedIn) {
    return
  }
  if (!form.visitor_name || !form.visitor_phone || !form.visit_date || !form.visit_time) {
    uni.showToast({ title: '请完善预约信息', icon: 'none' })
    return
  }
  if (!saturdayDateOptions.includes(form.visit_date)) {
    uni.showToast({ title: '请选择周六参观日期', icon: 'none' })
    return
  }
  if (!timeSlots.includes(form.visit_time)) {
    uni.showToast({ title: '请选择13:00-17:00内时间段', icon: 'none' })
    return
  }
  
  const token = uni.getStorageSync('token')
  
  uni.showLoading({ title: '提交中...' })
  uni.request({
    url: buildApiUrl('/api/bookings/'),
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
