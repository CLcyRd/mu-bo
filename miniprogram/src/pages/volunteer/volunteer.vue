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

      <view class="cta-section">
        <button class="join-btn" type="button" @click="goToVolunteerForm">加入我们</button>
      </view>

      <view class="footer-decor">🎬</view>
    </view>
  </view>
</template>

<script setup lang="ts">

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
const goToVolunteerForm = () => {
  uni.navigateTo({
    url: '/pages/volunteer/volunteer_form'
  })
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

.cta-section {
  padding: 0 20rpx;
}

.join-btn {
  width: 100%;
  height: 92rpx;
  border-radius: 16rpx;
  border: 1rpx solid rgba(212, 175, 55, 0.55);
  background: linear-gradient(135deg, #d4af37 0%, #f0d87d 100%);
  color: #0b1528;
  font-size: 34rpx;
  font-weight: 600;
  letter-spacing: 2rpx;
}

.join-btn::after {
  border: none;
}

.footer-decor {
  text-align: center;
  margin-top: 40rpx;
  opacity: 0.3;
  font-size: 44rpx;
}
</style>
