<template>
  <view class="container">
    <view class="header">
      <view class="title-main">谢晋故居</view>
      <view class="title-sub">上海谢晋电影艺术基金会</view>
    </view>

    <view class="banner-wrap">
      <swiper class="banner-swiper" circular autoplay :interval="3000" :duration="500">
        <swiper-item v-for="item in bannerImages" :key="item">
          <image class="banner-image" :src="item" mode="aspectFill"></image>
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
type NavAction = 'guide' | 'booking' | 'news' | 'volunteer'

const bannerImages = [
  '/static/museum_img/f9c3cb52f1859ff33b569b6024773334.jpg',
  '/static/museum_img/7f28e5732e1916bc8d48645ae3b33299.jpg',
  '/static/museum_img/eb9d69490f1ea168c46078c50544e1de.jpg',
  '/static/museum_img/b880576a8e57193e054f4abf4c94e7d8.jpg',
  '/static/museum_img/62ff29be24a9748931d6e4f1854338c8.jpg'
]

const toSvgDataUri = (svg: string) => `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`

const createIcon = (body: string) =>
  toSvgDataUri(
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" fill="none" stroke="#3a60a7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">${body}</svg>`
  )

const navItems: { action: NavAction; cn: string; en: string; icon: string }[] = [
  {
    action: 'guide',
    cn: '参观导览',
    en: 'Visitor Information',
    icon: createIcon('<path d="M10 8v32"/><path d="M10 10h14l4 4h10v14H24l-4-4H10"/><path d="M24 28h14v10H24"/>')
  },
  {
    action: 'booking',
    cn: '点击预约',
    en: 'Visit Booking',
    icon: createIcon('<path d="M8 16h32v18H8z"/><path d="M16 16v-4h16v4"/><path d="M16 25h16"/>')
  },
  {
    action: 'news',
    cn: '最新资讯',
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

const goToBooking = () => {
  uni.navigateTo({
    url: '/pages/booking/booking'
  })
}

const goToGuide = () => {
  uni.navigateTo({
    url: '/pages/guide/guide'
  })
}

const goToNews = () => {
  uni.navigateTo({
    url: '/pages/news/news'
  })
}

const goToVolunteer = () => {
  uni.navigateTo({
    url: '/pages/volunteer/volunteer'
  })
}

const handleNavClick = (action: NavAction) => {
  if (action === 'booking') {
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
  goToVolunteer()
}
</script>

<style lang="scss">
.container {
  min-height: 100vh;
  background: #2b3a6b;
  padding: 80rpx 40rpx 30rpx;
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
