<template>
  <view class="page">
    <view class="container">
      <view class="hero-section">
        <view class="title-wrapper">
          <view class="title-line">寻找</view>
          <view class="main-title">爱电影的你</view>
        </view>
        <view class="poetic-text">
          <view class="poetic-paragraph">作为谢晋故居的一位志愿者，<text class="line-break" />您是“工作人员”，也是故居当天的“临时主人”。</view>
          <view class="poetic-paragraph">您会看见清晨的阳光照进玄关的<text class="highlight">金句墙</text>，<text class="line-break" />听见下午的脚步声在老地板上轻轻响起，<text class="line-break" />遇见来自不同地方的观众——</view>
          <view class="poetic-paragraph">有人是看了他的电影后来的，<text class="line-break" />有人是陪父母或孩子来的，<text class="line-break" />有人只是想来看看，<text class="line-break" />一位导演曾经住过的地方是什么样子。</view>
          <view class="poetic-end">您的一天，将成为光影故事的一页。</view>
        </view>
      </view>

      <view class="content-section">
        <view class="info-card">
          <view class="section-subtitle">志愿者的日常</view>
          <view class="info-list">
            <view v-for="item in dailyInfo" :key="item.label" class="info-item">
              <view class="info-label">{{ item.label }}</view>
              <view class="info-value">{{ item.value }}</view>
            </view>
          </view>
        </view>
      </view>

      <view class="form-card">
        <view class="section-subtitle">加入我们</view>
        <view class="form-group">
          <view class="form-label">您的姓名</view>
          <input v-model="form.name" class="form-control input-control" type="text" placeholder="请输入真实姓名" />
        </view>
        <view class="form-group">
          <view class="form-label">联系电话</view>
          <input v-model="form.phone" class="form-control input-control" type="number" placeholder="请输入手机号码" />
        </view>
        <view class="form-group">
          <view class="form-label">邮箱（选填）</view>
          <input v-model="form.email" class="form-control input-control" type="text" placeholder="请输入邮箱地址" />
        </view>
        <view class="form-group">
          <view class="form-label">最喜欢的谢晋导演作品 / 报名初衷</view>
          <textarea v-model="form.reason" class="form-control textarea-control" maxlength="300" placeholder="聊聊您为什么想来这里，或者您与电影的故事..."></textarea>
        </view>
        <button class="submit-btn" type="button" :loading="submitting" :disabled="submitting" @click="submitForm">提交报名</button>
      </view>

      <view class="footer-decor">🎬</view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { ensureLoginOrRedirect } from '../../utils/auth'

const dailyInfo = [
  {
    label: '工作时间',
    value: '每周三、周六 10:00 - 16:00'
  },
  {
    label: '工作地点',
    value: '谢晋故居纪念馆内'
  },
  {
    label: '工作内容',
    value: '配合游客参观，做好引导与秩序维护，闭馆前整理工作台账。在需要的时候，为来访者指一指路、聊一聊谢晋、聊一聊电影。'
  }
]

const form = reactive({
  name: '',
  phone: '',
  email: '',
  reason: ''
})
const submitting = ref(false)
const apiHost = 'http://localhost:8000'

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type CurrentUser = {
  user_id: number
}

const isValidPhone = (value: string) => /^1\d{10}$/.test(value)
const isValidEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)

const requestWithToken = <T>(url: string, method: 'GET' | 'POST', data?: Record<string, unknown>) => {
  const token = uni.getStorageSync('token')
  if (!token) {
    return Promise.reject(new Error('未登录'))
  }
  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: `${apiHost}${url}`,
      method,
      data,
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

const createVolunteerRedirectUrl = () => {
  const query: string[] = []
  if (form.name) query.push(`name=${encodeURIComponent(form.name)}`)
  if (form.phone) query.push(`phone=${encodeURIComponent(form.phone)}`)
  if (form.email) query.push(`email=${encodeURIComponent(form.email)}`)
  if (form.reason) query.push(`reason=${encodeURIComponent(form.reason)}`)
  if (query.length === 0) {
    return '/pages/volunteer/volunteer'
  }
  return `/pages/volunteer/volunteer?${query.join('&')}`
}

onLoad((options) => {
  if (!options) {
    return
  }
  form.name = typeof options.name === 'string' ? decodeURIComponent(options.name) : ''
  form.phone = typeof options.phone === 'string' ? decodeURIComponent(options.phone) : ''
  form.email = typeof options.email === 'string' ? decodeURIComponent(options.email) : ''
  form.reason = typeof options.reason === 'string' ? decodeURIComponent(options.reason) : ''
})

const submitForm = async () => {
  const loggedIn = await ensureLoginOrRedirect(createVolunteerRedirectUrl())
  if (!loggedIn) {
    return
  }
  if (!form.name.trim()) {
    uni.showToast({ title: '请输入姓名', icon: 'none' })
    return
  }
  if (!isValidPhone(form.phone.trim())) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }
  if (form.email.trim() && !isValidEmail(form.email.trim())) {
    uni.showToast({ title: '请输入正确邮箱', icon: 'none' })
    return
  }

  if (submitting.value) {
    return
  }

  submitting.value = true
  try {
    const me = await requestWithToken<CurrentUser>('/api/users/me', 'GET')
    const payload = {
      user_id: me.user_id,
      name: form.name.trim(),
      phone: form.phone.trim(),
      email: form.email.trim() || null,
      note: form.reason.trim() || null,
      reason: form.reason.trim() || null
    }
    const response = await requestWithToken<ApiResponse<{ volunteer_id: number; existed: boolean }>>(
      '/api/volunteers/register',
      'POST',
      payload
    )
    if (response.code !== 0) {
      throw new Error(response.message || '提交失败')
    }
    uni.showToast({
      title: response.data?.existed ? '您已报名过' : '报名成功',
      icon: 'success'
    })
    if (!response.data?.existed) {
      form.name = ''
      form.phone = ''
      form.email = ''
      form.reason = ''
    }
  } catch (error: any) {
    const message = error?.message || error?.detail || error?.data?.message || '提交失败，请稍后重试'
    uni.showToast({ title: message, icon: 'none' })
  } finally {
    submitting.value = false
  }
}
</script>

<style lang="scss">
.page {
  min-height: 100vh;
  background: #0b1528;
}

.container {
  padding: 0 0 60rpx;
}

.hero-section {
  padding: 60rpx 20rpx 40rpx;
  text-align: center;
  background: linear-gradient(to bottom, rgba(212, 175, 55, 0.05) 0%, transparent 100%);
}

.title-wrapper {
  margin-bottom: 30rpx;
}

.title-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  color: #d4af37;
  font-size: 28rpx;
  letter-spacing: 4rpx;
  margin-bottom: 12rpx;
}

.title-line::before,
.title-line::after {
  content: '';
  height: 2rpx;
  width: 60rpx;
  background: #d4af37;
  opacity: 0.5;
}

.main-title {
  font-size: 56rpx;
  font-weight: 300;
  letter-spacing: 6rpx;
  color: #ffffff;
}

.poetic-text {
  margin: 0 10rpx;
}

.poetic-paragraph {
  margin-bottom: 16rpx;
  font-size: 30rpx;
  color: rgba(255, 255, 255, 0.85);
  line-height: 2;
  text-align: center;
}

.line-break {
  display: block;
}

.highlight {
  color: #d4af37;
  font-style: italic;
}

.poetic-end {
  margin-top: 24rpx;
  font-size: 30rpx;
  line-height: 1.8;
  color: #d4af37;
  font-weight: 500;
}

.content-section {
  padding: 0 20rpx;
  margin-top: 20rpx;
}

.info-card {
  background: rgba(26, 42, 71, 0.4);
  border: 1rpx solid rgba(212, 175, 55, 0.15);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 30rpx;
}

.section-subtitle {
  text-align: center;
  font-size: 32rpx;
  color: #d4af37;
  letter-spacing: 4rpx;
  margin-bottom: 24rpx;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 26rpx;
  color: #d4af37;
  margin-bottom: 6rpx;
  opacity: 0.9;
}

.info-value {
  font-size: 28rpx;
  color: #f0f4f8;
  line-height: 1.7;
}

.form-card {
  padding: 0 20rpx;
}

.form-group {
  margin-bottom: 20rpx;
}

.form-label {
  font-size: 28rpx;
  color: #a0aec0;
  margin-bottom: 8rpx;
  padding-left: 4rpx;
}

.form-control {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1rpx solid rgba(255, 255, 255, 0.15);
  border-radius: 12rpx;
  padding: 0 24rpx;
  color: #fff;
  font-size: 30rpx;
  box-sizing: border-box;
}

.input-control {
  height: 80rpx;
  line-height: 80rpx;
}

.textarea-control {
  height: 220rpx;
  padding: 20rpx 24rpx;
  line-height: 1.6;
}

.submit-btn {
  width: 100%;
  background: #d4af37;
  color: #0b1528;
  border: none;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 32rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
  margin-top: 10rpx;
}

.footer-decor {
  text-align: center;
  margin-top: 40rpx;
  opacity: 0.3;
  font-size: 44rpx;
}
</style>
