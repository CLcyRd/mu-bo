<template>
  <view class="page">
    <view class="container">
      <view class="form-card">
        <view class="section-subtitle">加入我们</view>
        <view class="form-group">
          <view class="form-label">您的姓名</view>
          <input v-model="form.name" class="form-control input-control" type="text" placeholder="请输入真实姓名" />
        </view>
        <view class="form-group">
          <view class="form-label">性别</view>
          <picker class="picker-control" mode="selector" :range="genderOptions" :value="genderIndex" @change="onGenderChange">
            <view class="picker-value">{{ form.gender || '请选择性别' }}</view>
          </picker>
        </view>
        <view class="form-group">
          <view class="form-label">身份证</view>
          <input v-model="form.id_card" class="form-control input-control" type="text" maxlength="18" placeholder="请输入身份证号" />
        </view>
        <view class="form-group">
          <view class="form-label">年龄</view>
          <input v-model="form.age" class="form-control input-control" type="number" placeholder="请输入年龄" />
        </view>
        <view class="form-group">
          <view class="form-label">民族</view>
          <input v-model="form.ethnicity" class="form-control input-control" type="text" placeholder="请输入民族" />
        </view>
        <view class="form-group">
          <view class="form-label">联系电话</view>
          <input v-model="form.phone" class="form-control input-control" type="number" placeholder="请输入手机号码" />
        </view>
        <view class="form-group">
          <view class="form-label">服务时段</view>
          <view class="service-time-group">
            <view
              v-for="slot in serviceTimeOptions"
              :key="slot"
              class="service-time-chip"
              :class="{ active: form.service_times.includes(slot) }"
              @click="toggleServiceTime(slot)"
            >
              {{ slot }}
            </view>
          </view>
        </view>
        <view class="form-group">
          <view class="form-label">学校 / 单位</view>
          <input v-model="form.organization" class="form-control input-control" type="text" placeholder="请输入学校或单位" />
        </view>
        <view class="form-group">
          <view class="form-label">专业 / 职务</view>
          <input v-model="form.position" class="form-control input-control" type="text" placeholder="请输入专业或职务" />
        </view>
        <view class="form-group">
          <view class="form-label">邮箱（选填）</view>
          <input v-model="form.email" class="form-control input-control" type="text" placeholder="请输入邮箱地址" />
        </view>
        <view class="form-group">
          <view class="form-label">最喜欢的谢晋导演作品 / 报名初衷</view>
          <textarea v-model="form.note" class="form-control textarea-control" maxlength="500" placeholder="聊聊您为什么想来这里，或者您与电影的故事..."></textarea>
        </view>
        <button class="submit-btn" type="button" :loading="submitting" :disabled="submitting" @click="submitForm">提交报名</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { ensureLoginOrRedirect } from '../../utils/auth'
import { buildApiUrl } from '../../utils/api'

const form = reactive({
  name: '',
  gender: '',
  id_card: '',
  age: '',
  ethnicity: '',
  phone: '',
  service_times: [] as string[],
  organization: '',
  position: '',
  email: '',
  note: ''
})
const submitting = ref(false)
const genderOptions = ['女', '男']
const serviceTimeOptions = ['周三', '周六']

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
const isValidIdCard = (value: string) => /^(\d{15}|\d{17}[\dXx])$/.test(value)

const getGenderIndex = () => {
  const index = genderOptions.indexOf(form.gender)
  return index >= 0 ? index : 0
}

const onGenderChange = (event: any) => {
  const selected = genderOptions[event?.detail?.value || 0]
  form.gender = selected || ''
}

const toggleServiceTime = (slot: string) => {
  const index = form.service_times.indexOf(slot)
  if (index >= 0) {
    form.service_times.splice(index, 1)
    return
  }
  form.service_times.push(slot)
}

const normalizeServiceTime = () => {
  const unique = Array.from(new Set(form.service_times))
  const ordered = serviceTimeOptions.filter((item) => unique.includes(item))
  form.service_times = ordered
}

const requestWithToken = <T>(url: string, method: 'GET' | 'POST', data?: Record<string, unknown>) => {
  const token = uni.getStorageSync('token')
  if (!token) {
    return Promise.reject(new Error('未登录'))
  }
  return new Promise<T>((resolve, reject) => {
    uni.request({
      url: buildApiUrl(url),
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
  if (form.gender) query.push(`gender=${encodeURIComponent(form.gender)}`)
  if (form.id_card) query.push(`id_card=${encodeURIComponent(form.id_card)}`)
  if (form.age) query.push(`age=${encodeURIComponent(form.age)}`)
  if (form.ethnicity) query.push(`ethnicity=${encodeURIComponent(form.ethnicity)}`)
  if (form.phone) query.push(`phone=${encodeURIComponent(form.phone)}`)
  if (form.service_times.length) query.push(`service_times=${encodeURIComponent(form.service_times.join(','))}`)
  if (form.organization) query.push(`organization=${encodeURIComponent(form.organization)}`)
  if (form.position) query.push(`position=${encodeURIComponent(form.position)}`)
  if (form.email) query.push(`email=${encodeURIComponent(form.email)}`)
  if (form.note) query.push(`note=${encodeURIComponent(form.note)}`)
  if (query.length === 0) {
    return '/pages/volunteer/volunteer_form'
  }
  return `/pages/volunteer/volunteer_form?${query.join('&')}`
}

onLoad((options) => {
  if (!options) {
    return
  }
  form.name = typeof options.name === 'string' ? decodeURIComponent(options.name) : ''
  form.gender = typeof options.gender === 'string' ? decodeURIComponent(options.gender) : ''
  form.id_card = typeof options.id_card === 'string' ? decodeURIComponent(options.id_card) : ''
  form.age = typeof options.age === 'string' ? decodeURIComponent(options.age) : ''
  form.ethnicity = typeof options.ethnicity === 'string' ? decodeURIComponent(options.ethnicity) : ''
  form.phone = typeof options.phone === 'string' ? decodeURIComponent(options.phone) : ''
  form.service_times = typeof options.service_times === 'string' && options.service_times
    ? decodeURIComponent(options.service_times).split(',').map((item) => item.trim()).filter(Boolean)
    : []
  normalizeServiceTime()
  form.organization = typeof options.organization === 'string' ? decodeURIComponent(options.organization) : ''
  form.position = typeof options.position === 'string' ? decodeURIComponent(options.position) : ''
  form.email = typeof options.email === 'string' ? decodeURIComponent(options.email) : ''
  form.note = typeof options.note === 'string' ? decodeURIComponent(options.note) : ''
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
  if (!form.gender.trim()) {
    uni.showToast({ title: '请选择性别', icon: 'none' })
    return
  }
  if (!isValidIdCard(form.id_card.trim())) {
    uni.showToast({ title: '请输入正确身份证号', icon: 'none' })
    return
  }
  const ageValue = Number(form.age)
  if (!Number.isInteger(ageValue) || ageValue < 1 || ageValue > 120) {
    uni.showToast({ title: '请输入正确年龄', icon: 'none' })
    return
  }
  if (!form.ethnicity.trim()) {
    uni.showToast({ title: '请输入民族', icon: 'none' })
    return
  }
  if (!isValidPhone(form.phone.trim())) {
    uni.showToast({ title: '请输入正确手机号', icon: 'none' })
    return
  }
  normalizeServiceTime()
  if (!form.service_times.length) {
    uni.showToast({ title: '请选择服务时段', icon: 'none' })
    return
  }
  if (!form.organization.trim()) {
    uni.showToast({ title: '请输入学校或单位', icon: 'none' })
    return
  }
  if (!form.position.trim()) {
    uni.showToast({ title: '请输入专业或职务', icon: 'none' })
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
      gender: form.gender.trim(),
      id_card: form.id_card.trim().toUpperCase(),
      age: ageValue,
      ethnicity: form.ethnicity.trim(),
      phone: form.phone.trim(),
      service_time: form.service_times.join('、'),
      organization: form.organization.trim(),
      position: form.position.trim(),
      email: form.email.trim() || null,
      note: form.note.trim() || null,
      personal_intro: form.note.trim() || null
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
      form.gender = ''
      form.id_card = ''
      form.age = ''
      form.ethnicity = ''
      form.phone = ''
      form.service_times = []
      form.organization = ''
      form.position = ''
      form.email = ''
      form.note = ''
    }
  } catch (error: any) {
    const message = error?.message || error?.detail || error?.data?.message || '提交失败，请稍后重试'
    uni.showToast({ title: message, icon: 'none' })
  } finally {
    submitting.value = false
  }
}

const genderIndex = computed(() => getGenderIndex())
</script>

<style lang="scss">
.page {
  min-height: 100vh;
  background: #0b1528;
}

.container {
  padding: 24rpx 0 60rpx;
}

.form-card {
  padding: 0 30rpx;
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

.picker-control {
  width: 100%;
}

.picker-value {
  height: 80rpx;
  line-height: 80rpx;
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1rpx solid rgba(255, 255, 255, 0.15);
  border-radius: 12rpx;
  padding: 0 24rpx;
  color: #fff;
  font-size: 30rpx;
  box-sizing: border-box;
}

.service-time-group {
  display: flex;
  gap: 16rpx;
}

.service-time-chip {
  flex: 1;
  height: 72rpx;
  border-radius: 36rpx;
  border: 1rpx solid rgba(212, 175, 55, 0.45);
  color: #d4af37;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.service-time-chip.active {
  background: rgba(212, 175, 55, 0.18);
  border-color: #d4af37;
  color: #f0f4f8;
}

.section-subtitle {
  text-align: center;
  font-size: 32rpx;
  color: #d4af37;
  letter-spacing: 4rpx;
  margin-bottom: 24rpx;
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
</style>
