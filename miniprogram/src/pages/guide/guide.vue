<template>
  <view class="page">
    <view class="container">
      <view class="header-section">
        <view class="title-cn">谢晋故居纪念馆</view>
        <view class="title-en">XIE JIN FORMER RESIDENCE</view>
        <view class="header-line"></view>
      </view>

      <view class="intro-card">
        <view class="quote-box">
          <text class="quote-mark left">“</text>
          <text class="welcome-text">
            这里是他创作的大本营，也是他生活最久的家。从《女篮五号》到《芙蓉镇》，从《红色娘子军》到《鸦片战争》——60 年导演生涯，36 部电影作品。在这方天地里，谢晋完成了从青年导演到一代宗师的蜕变，用镜头记录了一个民族的奋进与沉思。推开这扇门，不只是走进一位导演，更是走进一个时代。
          </text>
          <text class="quote-mark right">”</text>
        </view>
        
        <view class="divider"></view>
        
        <view class="desc-text">
          谢晋故居位于上海市静安区江宁路 83 号江宁大楼 501 室，是谢晋导演在上海定居期间生活与工作的重要场所。在这里，他与无数创作者彻夜长谈，酝酿出一部部撼动时代的经典；在这里，他接待过海内外电影人，见证了中国电影的起承转合。这里，不仅是谢晋的家，更是中国电影的一个舞台。
        </view>
      </view>

      <view class="nav-section">
        <view class="nav-btn" hover-class="nav-btn-hover" @click="goToExhibition">
          <view class="nav-content">
            <text class="nav-title">展厅介绍</text>
            <text class="nav-sub">Exhibition Introduction</text>
          </view>
          <view class="nav-arrow">
            <text class="arrow-icon">➔</text>
          </view>
        </view>

        <view class="nav-btn" hover-class="nav-btn-hover" @click="goToNotice">
          <view class="nav-content">
            <text class="nav-title">参观须知</text>
            <text class="nav-sub">Visitor Notice</text>
          </view>
          <view class="nav-arrow">
            <text class="arrow-icon">➔</text>
          </view>
        </view>
      </view>
      
    </view>
  </view>
</template>

<script setup lang="ts">
const goToExhibition = () => {
  uni.navigateTo({
    url: '/pages/guide/exhibition_intro'
  })
}

const goToNotice = () => {
  uni.navigateTo({
    url: '/pages/guide/visitor_notice'
  })
}
</script>

<style lang="scss">
.page {
  min-height: 100vh;
  background: #0b1528;
  /* 增加一点顶部的背景光晕，提升质感 */
  background-image: radial-gradient(circle at 50% 0%, rgba(30, 60, 114, 0.4) 0%, transparent 60%);
  padding-bottom: 40rpx;
}

.container {
  padding: 40rpx 30rpx;
}

/* 头部样式优化 */
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 50rpx;
  margin-top: 20rpx;
}

.title-cn {
  font-size: 56rpx;
  line-height: 1.2;
  font-weight: bold;
  color: #e3d90f;
  letter-spacing: 4rpx;
  text-shadow: 0 4rpx 8rpx rgba(0, 0, 0, 0.5);
}

.title-en {
  margin-top: 12rpx;
  font-size: 22rpx;
  font-weight: 500;
  color: #c7a23f;
  letter-spacing: 6rpx;
  text-transform: uppercase;
}

.header-line {
  width: 60rpx;
  height: 4rpx;
  background: linear-gradient(90deg, transparent, #d4af37, transparent);
  margin-top: 24rpx;
}

/* 核心导览卡片 */
.intro-card {
  background: rgba(26, 42, 71, 0.45);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 24rpx;
  padding: 40rpx 36rpx;
  margin-bottom: 40rpx;
  box-shadow: 0 16rpx 40rpx rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(12px);
}

.quote-box {
  position: relative;
  padding: 20rpx 0;
}

.quote-mark {
  position: absolute;
  font-size: 80rpx;
  color: rgba(212, 175, 55, 0.2);
  font-family: serif;
  line-height: 1;
}

.quote-mark.left {
  top: -10rpx;
  left: -16rpx;
}

.quote-mark.right {
  bottom: -40rpx;
  right: -16rpx;
}

.welcome-text {
  font-size: 34rpx;
  line-height: 1.8;
  font-weight: 400;
  color: #d4af37;
  text-align: justify;
  letter-spacing: 2rpx;
  position: relative;
  z-index: 2;
}

.divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, rgba(212,175,55,0.05), rgba(212,175,55,0.3), rgba(212,175,55,0.05));
  margin: 40rpx 0;
}

.desc-text {
  font-size: 30rpx;
  line-height: 1.8;
  color: #a0aec0;
  text-align: justify;
  letter-spacing: 1rpx;
}

/* 导航按钮区 */
.nav-section {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}

.nav-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, rgba(30, 60, 114, 0.3) 0%, rgba(11, 21, 40, 0.5) 100%);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 20rpx;
  padding: 36rpx 40rpx;
  transition: all 0.3s ease;
}

.nav-btn-hover {
  background: rgba(212, 175, 55, 0.1);
  border-color: rgba(212, 175, 55, 0.4);
  transform: scale(0.98);
}

.nav-content {
  display: flex;
  flex-direction: column;
}

.nav-title {
  font-size: 38rpx;
  font-weight: 600;
  color: #f0f4f8;
  margin-bottom: 8rpx;
  letter-spacing: 2rpx;
}

.nav-sub {
  font-size: 22rpx;
  color: rgba(160, 174, 192, 0.7);
  letter-spacing: 1rpx;
  text-transform: uppercase;
}

.nav-arrow {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60rpx;
  height: 60rpx;
  border-radius: 50%;
  background: rgba(212, 175, 55, 0.1);
}

.arrow-icon {
  color: #d4af37;
  font-size: 32rpx;
}
</style>
