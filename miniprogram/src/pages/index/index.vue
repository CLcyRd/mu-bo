<template>
  <view class="container">
    <image class="hero-image" src="https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt=A%20vintage%20movie%20artist%20museum%20exterior%2C%20historical%20building%2C%20cinematic%20lighting&image_size=landscape_16_9" mode="aspectFill"></image>
    
    <view class="content">
      <view class="title">电影艺术家故居</view>
      <view class="description">
        这里是著名电影艺术家的故居，记录了中国电影百年的发展历程。馆内珍藏了大量珍贵的电影剧本、海报、道具以及艺术家的生活用品，带您穿越时空，感受光影艺术的魅力。
      </view>
      
      <view class="section-title">参观须知</view>
      <view class="info-item">
        <text class="label">开放时间：</text>
        <text>周二至周日 9:00 - 17:00</text>
      </view>
      <view class="info-item">
        <text class="label">地址：</text>
        <text>上海市徐汇区安福路201号</text>
      </view>

      <view class="action-area">
        <button class="book-now-btn" @click="goToBooking">立即预约</button>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
const goToBooking = () => {
  uni.navigateTo({
    url: '/pages/booking/booking'
  })
}
</script>

<style>
.container {
  padding-bottom: 20px;
}
.hero-image {
  width: 100%;
  height: 240px;
}
.content {
  padding: 20px;
}
.title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 16px;
}
.description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-bottom: 24px;
}
.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
  border-left: 4px solid #3cc51f;
  padding-left: 10px;
}
.info-item {
  margin-bottom: 8px;
  font-size: 14px;
}
.label {
  color: #333;
  font-weight: bold;
}
.action-area {
  margin-top: 30px;
  padding: 0 20px;
}
.book-now-btn {
  background-color: #07c160;
  color: white;
  font-size: 16px;
  font-weight: bold;
  border-radius: 8px;
  padding: 10px 0;
  box-shadow: 0 4px 6px rgba(7, 193, 96, 0.3);
}
.book-now-btn:active {
  background-color: #06ad56;
  transform: translateY(1px);
}
</style>
