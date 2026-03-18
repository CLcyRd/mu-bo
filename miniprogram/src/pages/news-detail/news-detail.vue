<template>
  <view class="page">
    <view class="detail-header">
      <view class="header-btn" @click="goBack">
        <text class="header-icon">←</text>
      </view>
      <view class="header-title"></view>
      <button class="header-share" open-type="share">
        <text class="header-icon">⤴</text>
      </button>
    </view>

    <scroll-view class="detail-scroll" scroll-y>
      <view v-if="loading" class="status-text">加载中...</view>
      <view v-else-if="!article.id" class="status-text">资讯不存在</view>
      <view v-else>
        <view class="article-cover-wrapper">
          <image class="article-cover" :src="getCoverSrc()" mode="aspectFill" />
          <view class="cover-gradient"></view>
        </view>

        <view class="article-content">
          <view class="article-title">{{ article.title }}</view>
          <view class="article-meta">
            <text>官方发布</text>
            <text class="meta-divider">|</text>
            <text>{{ formatDisplayTime(article.updated_at || article.created_at) }}</text>
          </view>
          <rich-text class="article-body" :nodes="richContent"></rich-text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShareAppMessage } from '@dcloudio/uni-app'
import { buildApiUrl, normalizeApiAssetUrl } from '../../utils/api'

type ConsultationDetail = {
  id: string
  title: string
  cover: string
  content: string
  created_at: string
  updated_at: string
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

const fallbackCover = '/static/museum_img/default_cover.png'
const loading = ref(false)
const article = ref<ConsultationDetail>({
  id: '',
  title: '',
  cover: '',
  content: '',
  created_at: '',
  updated_at: ''
})
const richContent = ref('')

const goBack = () => {
  uni.navigateBack()
}

const formatDisplayTime = (value: string) => {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return ''
  }
  const year = date.getFullYear()
  const month = `${date.getMonth() + 1}`.padStart(2, '0')
  const day = `${date.getDate()}`.padStart(2, '0')
  const hour = `${date.getHours()}`.padStart(2, '0')
  const minute = `${date.getMinutes()}`.padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}`
}

const withApiHost = (url: string) => {
  return normalizeApiAssetUrl(url)
}

const decorateRichText = (html: string) => {
  if (!html) return ''
  const normalized = html
    .replace(/(src|href)=["']([^"']+)["']/gi, (match, attr, value) => {
      const absolute = withApiHost(value)
      return `${attr}="${absolute || value}"`
    })
    .replace(/<img\b/gi, '<img style="max-width:100%;height:auto;border-radius:12rpx;margin:0 0 32rpx;display:block;"')
    .replace(/<h1\b/gi, '<h1 style="font-size:40rpx;color:#ffffff;line-height:1.45;margin:38rpx 0 20rpx;font-weight:700;"')
    .replace(/<h2\b/gi, '<h2 style="font-size:36rpx;color:#ffffff;line-height:1.45;margin:36rpx 0 20rpx;padding-left:16rpx;border-left:8rpx solid #1890ff;font-weight:700;"')
    .replace(/<h3\b/gi, '<h3 style="font-size:32rpx;color:#ffffff;line-height:1.45;margin:32rpx 0 18rpx;font-weight:700;"')
    .replace(/<p\b/gi, '<p style="font-size:36rpx;color:rgba(255,255,255,.9);line-height:1.85;margin:0 0 30rpx;text-align:justify;"')
    .replace(/<li\b/gi, '<li style="font-size:34rpx;color:rgba(255,255,255,.9);line-height:1.8;margin-bottom:14rpx;"')
    .replace(/<blockquote\b/gi, '<blockquote style="margin:0 0 28rpx;padding:20rpx 24rpx;background:rgba(255,255,255,.06);border-radius:14rpx;color:rgba(255,255,255,.85);"')
  return normalized
}

const getCoverSrc = () => {
  const cover = withApiHost(article.value.cover)
  return cover || fallbackCover
}

const fetchDetail = async (id: string) => {
  loading.value = true
  const token = uni.getStorageSync('token')
  try {
    const result = await new Promise<ApiResponse<ConsultationDetail>>((resolve, reject) => {
      const requestHeaders: Record<string, string> = {}
      if (token) {
        requestHeaders.Authorization = `Bearer ${token}`
      }
      uni.request({
        url: buildApiUrl(`/api/consultations/${id}`),
        method: 'GET',
        header: requestHeaders,
        success: (res: any) => {
          if (res.statusCode >= 200 && res.statusCode < 300 && res.data?.code === 0) {
            resolve(res.data)
            return
          }
          reject(res.data)
        },
        fail: reject
      })
    })
    const detail = result?.data
    article.value = detail || article.value
    richContent.value = decorateRichText((detail && detail.content) || '')
  } catch (error: any) {
    const errMessage = (error && error.message) || (error && error.data && error.data.message) || ''
    uni.showToast({
      title: errMessage || '资讯加载失败',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  const id = (options && options.id ? String(options.id) : '').trim()
  if (!id) {
    uni.showToast({ title: '资讯ID无效', icon: 'none' })
    setTimeout(() => {
      goBack()
    }, 500)
    return
  }
  fetchDetail(id)
})

onShareAppMessage(() => {
  return {
    title: article.value.title || '最新资讯',
    path: `/pages/news-detail/news-detail?id=${article.value.id}`,
    imageUrl: getCoverSrc()
  }
})
</script>

<style lang="scss">
.page {
  height: 100vh;
  background: #001b35;
  display: flex;
  flex-direction: column;
}

.detail-header {
  height: 92rpx;
  padding: 18rpx 28rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #001b35;
}

.header-btn,
.header-share {
  width: 56rpx;
  height: 56rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  background: transparent;
  border: none;
  padding: 0;
}

.header-title {
  flex: 1;
}

.header-share::after {
  border: none;
}

.header-icon {
  font-size: 42rpx;
  line-height: 1;
}

.detail-scroll {
  flex: 1;
  min-height: 0;
}

.status-text {
  padding: 200rpx 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 30rpx;
}

.article-cover-wrapper {
  width: 100%;
  height: 420rpx;
  position: relative;
}

.article-cover {
  width: 100%;
  height: 100%;
}

.cover-gradient {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 96rpx;
  background: linear-gradient(to bottom, rgba(0, 27, 53, 0), #001b35);
}

.article-content {
  background: #001b35;
  margin-top: -22rpx;
  border-radius: 24rpx 24rpx 0 0;
  padding: 24rpx 34rpx 60rpx;
}

.article-title {
  color: #ffffff;
  font-size: 56rpx;
  font-weight: 700;
  line-height: 1.35;
}

.article-meta {
  margin-top: 22rpx;
  margin-bottom: 30rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid rgba(255, 255, 255, 0.12);
  display: flex;
  align-items: center;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.55);
}

.meta-divider {
  margin: 0 14rpx;
}

.article-body {
  color: rgba(255, 255, 255, 0.9);
}
</style>
