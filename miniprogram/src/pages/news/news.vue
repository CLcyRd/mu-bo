<template>
  <view class="container">
    <view class="search-header">
      <view class="search-bar">
        <text class="search-icon">⌕</text>
        <input
          class="search-input"
          :value="keyword"
          placeholder="输入关键词搜索资讯..."
          placeholder-class="search-placeholder"
          @input="handleKeywordInput"
        />
      </view>
    </view>

    <scroll-view class="news-list" scroll-y>
      <view v-if="loading" class="status-text">加载中...</view>
      <view v-else-if="newsList.length === 0" class="status-text">暂无资讯</view>
      <view v-else>
        <view v-for="item in newsList" :key="item.id" class="news-card" @click="goToDetail(item.id)">
          <image
            class="news-cover"
            :src="getCoverSrc(item)"
            mode="aspectFill"
            :data-id="item.id"
            @error="handleCoverError"
          />
          <view class="news-info">
            <view class="news-title">{{ item.title }}</view>
            <view class="news-footer">
              <text class="news-time">{{ formatDisplayTime(item.updated_at || item.created_at) }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onUnload } from '@dcloudio/uni-app'
import { buildApiUrl, normalizeApiAssetUrl } from '../../utils/api'

type ConsultationItem = {
  id: string
  title: string
  cover: string
  created_at: string
  updated_at: string
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

const fallbackCover = '/static/museum_img/default_cover.png'
const keyword = ref('')
const loading = ref(false)
const newsList = ref<ConsultationItem[]>([])
const failedCoverMap = ref<Record<string, boolean>>({})
let searchTimer: ReturnType<typeof setTimeout> | null = null

const getCoverSrc = (item: ConsultationItem) => {
  if (failedCoverMap.value[item.id]) {
    return fallbackCover
  }
  return normalizeApiAssetUrl(item.cover) || fallbackCover
}

const handleCoverError = (event: any) => {
  const currentTarget = event && event.currentTarget ? event.currentTarget : null
  const dataset = currentTarget && currentTarget.dataset ? currentTarget.dataset : null
  const id = dataset && dataset.id ? String(dataset.id) : ''
  if (!id) return
  failedCoverMap.value[id] = true
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

const fetchNewsList = async () => {
  const token = uni.getStorageSync('token')
  loading.value = true
  try {
    const result = await new Promise<ApiResponse<{ items: ConsultationItem[] }>>((resolve, reject) => {
      const requestHeaders: Record<string, string> = {}
      if (token) {
        requestHeaders.Authorization = `Bearer ${token}`
      }
      uni.request({
        url: buildApiUrl('/api/consultations'),
        method: 'GET',
        data: {
          keyword: keyword.value.trim(),
          page: 1,
          page_size: 100
        },
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
    const responseData = result && result.data ? result.data : { items: [] }
    newsList.value = responseData.items || []
    failedCoverMap.value = {}
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

const handleKeywordInput = (event: any) => {
  keyword.value = event.detail.value || ''
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  searchTimer = setTimeout(() => {
    fetchNewsList()
  }, 300)
}

const goToDetail = (id: string) => {
  if (!id) return
  uni.navigateTo({
    url: `/pages/newsdetail/newsdetail?id=${encodeURIComponent(id)}`
  })
}

onLoad(() => {
  fetchNewsList()
})

onUnload(() => {
  if (searchTimer) {
    clearTimeout(searchTimer)
    searchTimer = null
  }
})
</script>

<style lang="scss">
.container {
  height: 100vh;
  background: #2b3a6b;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.search-header {
  padding: 40rpx 32rpx 24rpx;
  background: #2b3a6b;
}

.search-bar {
  height: 78rpx;
  background: #f0f2f5;
  border: 1rpx solid #e0e0e0;
  border-radius: 24rpx;
  padding: 0 26rpx;
  display: flex;
  align-items: center;
}

.search-icon {
  font-size: 28rpx;
  color: #3a60a7;
}

.search-input {
  flex: 1;
  margin-left: 16rpx;
  font-size: 28rpx;
  color: #1a1a1a;
}

.search-placeholder {
  color: #a0a7b8;
}

.news-list {
  flex: 1;
  min-height: 0;
  padding: 0 24rpx 28rpx;
  box-sizing: border-box;
}

.status-text {
  padding: 80rpx 0;
  text-align: center;
  color: #d8dfef;
  font-size: 28rpx;
}

.news-card {
  background: #f6f8e1;
  border-radius: 32rpx;
  overflow: hidden;
 
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
  margin-bottom: 28rpx;
}

.news-cover {
  width: 100%;
  height: 360rpx;
  background: rgba(143, 192, 9, 0.1);
}

.news-info {
  padding: 24rpx 30rpx 28rpx;
}

.news-title {
  font-size: 45rpx;
  font-weight: 700;
  color: #111111;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  margin-top: 14rpx;
  display: flex;
  align-items: center;
}

.news-time {
  font-size: 30rpx;
  color: #2b3a6b;
}
</style>
