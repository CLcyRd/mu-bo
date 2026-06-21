<template>
  <view class="container">
    <view class="header">
      <view class="title-main">谢晋故居</view>
      <view class="title-sub">上海谢晋电影艺术基金会</view>
    </view>

    <view class="banner-wrap">
      <swiper class="banner-swiper" circular autoplay :interval="3000" :duration="500">
        <swiper-item v-for="item in mediaItems" :key="item.id">
          <view v-if="item.type === 'video'" class="video-banner" @click="goToVideo(item)">
            <image class="banner-image" :src="item.coverUrl" mode="aspectFill"></image>
            <view class="video-mask"></view>
            <view class="play-button">
              <view class="play-triangle"></view>
            </view>
            <view class="video-copy">
              <view class="video-title">{{ item.title }}</view>
              <view class="video-subtitle">{{ item.subtitle }}</view>
            </view>
            <view class="video-badge">视频入口</view>
          </view>
          <image v-else class="banner-image" :src="item.url" mode="aspectFill"></image>
        </swiper-item>
      </swiper>
    </view>

    <view class="nav-grid">
      <view
        v-for="item in navItems"
        :key="item.action"
        class="nav-item"
        @click="handleNavClick(item.action)"
      >
        <view class="nav-icon">
          <image class="nav-icon-image" :src="item.icon" mode="aspectFit"></image>
        </view>
        <view class="nav-cn">{{ item.cn }}</view>
        <view class="nav-en">{{ item.en }}</view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { ensureLoginOrRedirect, syncTabBar } from '../../utils/auth'
import { buildApiUrl, normalizeApiAssetUrl } from '../../utils/api'

type NavAction = 'guide' | 'booking' | 'news' | 'volunteer'

type ImageMediaItem = {
  id: string
  type: 'image'
  url: string
}

type VideoMediaItem = {
  id: string
  type: 'video'
  title: string
  subtitle: string
  coverUrl: string
  videoUrl: string
}

type HomeMediaItem = ImageMediaItem | VideoMediaItem

type ApiMediaItem =
  | { type: 'image'; filename?: string; url: string }
  | { type: 'video'; title: string; subtitle: string; cover_url: string; video_url: string }

type ApiResponse<T> = { code: number; message: string; data: T | null }

const mediaItems = ref<HomeMediaItem[]>([])

const fetchHomepageMedia = () => {
  uni.request({
    url: buildApiUrl('/api/museum-info/homepage-media'),
    method: 'GET',
    success: (res: any) => {
      if (res.statusCode >= 200 && res.statusCode < 300 && res.data?.code === 0) {
        const payload = res.data as ApiResponse<{ items: ApiMediaItem[] }>
        mediaItems.value = (payload.data?.items || [])
          .map((item, index): HomeMediaItem | null => {
            if (item.type === 'video') {
              const coverUrl = normalizeApiAssetUrl(item.cover_url)
              const videoUrl = normalizeApiAssetUrl(item.video_url)
              if (!coverUrl || !videoUrl) {
                return null
              }
              return {
                id: `video-${index}`,
                type: 'video',
                title: item.title,
                subtitle: item.subtitle,
                coverUrl,
                videoUrl
              }
            }
            const url = normalizeApiAssetUrl(item.url)
            return url
              ? {
                  id: item.filename || `image-${index}`,
                  type: 'image',
                  url
                }
              : null
          })
          .filter((item): item is HomeMediaItem => Boolean(item))
        return
      }
      uni.showToast({ title: res.data?.message || '轮播图加载失败', icon: 'none' })
    },
    fail: () => {
      uni.showToast({ title: '轮播图加载失败', icon: 'none' })
    }
  })
}

const goToVideo = (item: VideoMediaItem) => {
  uni.navigateTo({
    url: `/pages/video-player/video-player?src=${encodeURIComponent(item.videoUrl)}&title=${encodeURIComponent(item.title)}`
  })
}

const toSvgDataUri = (svg: string) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`

const createIcon = (body: string) =>
  toSvgDataUri(
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" stroke="#3a60a7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`
  )

const navItems: { action: NavAction; cn: string; en: string; icon: string }[] = [
  {
    action: 'guide',
    cn: '展陈导览',
    en: 'Visitor Information',
    icon: createIcon('<path d="M10 8v32"/><path d="M10 10h14l4 4h10v14H24l-4-4H10"/><path d="M24 28h14v10H24"/>')
  },
  {
    action: 'booking',
    cn: '开放日预约',
    en: 'Visit Booking',
    icon: createIcon('<path d="M8 16h32v18H8z"/><path d="M16 16v-4h16v4"/><path d="M16 25h16"/>')
  },
  {
    action: 'news',
    cn: '活动资讯',
    en: 'Latest News',
    icon: createIcon('<rect x="8" y="10" width="32" height="28"/><path d="M15 18h18"/><path d="M15 24h18"/><path d="M15 30h12"/>')
  },
  {
    action: 'volunteer',
    cn: '加入志愿者',
    en: 'Be a volunteer',
    icon: createIcon('<path d="M8 20h32v18H8z"/><path d="M8 20h32"/><path d="M24 20v18"/><path d="M24 20c0-4 3-7 7-7 2 0 4 1 5 3-1 2-3 3-5 3h-7"/><path d="M24 20c0-4-3-7-7-7-2 0-4 1-5 3 1 2 3 3 5 3h7"/>')
  }
]

const navigateToPage = (url: string) => {
  uni.navigateTo({
    url,
    animationType: 'none',
    animationDuration: 0
  })
}

const goToBooking = () => {
  navigateToPage('/pages/booking/booking')
}

const goToGuide = () => {
  navigateToPage('/pages/guide/guide')
}

const goToNews = () => {
  navigateToPage('/pages/news/news')
}

const goToVolunteer = () => {
  navigateToPage('/pages/volunteer/volunteer')
}

const handleNavClick = async (action: NavAction) => {
  if (action === 'booking') {
    const ok = await ensureLoginOrRedirect('/pages/booking/booking')
    if (!ok) {
      return
    }
    goToBooking()
    return
  }
  if (action === 'guide') {
    goToGuide()
    return
  }
  if (action === 'news') {
    goToNews()
    return
  }
  const ok = await ensureLoginOrRedirect('/pages/volunteer/volunteer')
  if (!ok) {
    return
  }
  goToVolunteer()
}

onLoad(() => {
  fetchHomepageMedia()
})

onShow(() => {
  syncTabBar()
})
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #2b3a6b;
  padding: 50rpx 40rpx 30rpx;
  box-sizing: border-box;
}

.header {
  margin: 0 0 20rpx;
}

.title-main {
  font-size: 56rpx;
  font-weight: 700;
  color: #e3d90f;
  letter-spacing: 1rpx;
  line-height: 1.25;
}

.title-sub {
  margin-top: 8rpx;
  font-size: 26rpx;
  font-weight: 500;
  color: #e3d90f;
  line-height: 1.3;
}

.banner-wrap {
  width: 100%;
  height: 360rpx;
  border-radius: 32rpx;
  overflow: hidden;
  background: #d8d8d8;
}

.banner-swiper {
  width: 100%;
  height: 100%;
}

.banner-image {
  width: 100%;
  height: 100%;
}

.video-banner {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.video-mask {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(6, 10, 24, 0.08), rgba(6, 10, 24, 0.64));
}

.play-button {
  position: absolute;
  left: 50%;
  top: 45%;
  width: 112rpx;
  height: 112rpx;
  margin-left: -56rpx;
  margin-top: -56rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 18rpx 44rpx rgba(0, 0, 0, 0.26);
}

.play-triangle {
  width: 0;
  height: 0;
  margin-left: 8rpx;
  border-top: 22rpx solid transparent;
  border-bottom: 22rpx solid transparent;
  border-left: 34rpx solid #2b65ab;
}

.video-copy {
  position: absolute;
  left: 28rpx;
  bottom: 26rpx;
  right: 170rpx;
}

.video-title {
  color: #ffffff;
  font-size: 34rpx;
  line-height: 1.2;
  font-weight: 700;
  text-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.45);
}

.video-subtitle {
  margin-top: 6rpx;
  color: rgba(255, 255, 255, 0.82);
  font-size: 22rpx;
  line-height: 1.3;
}

.video-badge {
  position: absolute;
  right: 24rpx;
  bottom: 28rpx;
  padding: 10rpx 18rpx;
  border-radius: 999rpx;
  background: rgba(255, 255, 255, 0.18);
  color: #ffffff;
  font-size: 22rpx;
  line-height: 1.2;
  font-weight: 600;
}

.nav-grid {
  margin-top: 32rpx;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24rpx;
}

.nav-item {
  background: #f6f8e1;
  border-radius: 28rpx;
  border: 1rpx solid #e0e0e0;
  height: 284rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.12);
}

.nav-item:active {
  transform: scale(0.98);
}

.nav-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 24rpx;
  background: rgba(143, 192, 9, 0.1);
  color: #3563bd;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon-image {
  width: 58rpx;
  height: 58rpx;
}

.nav-cn {
  margin-top: 20rpx;
  font-size: 30rpx;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.2;
}

.nav-en {
  margin-top: 10rpx;
  font-size: 24rpx;
  color: #5f6368;
  line-height: 1.2;
}
</style>
