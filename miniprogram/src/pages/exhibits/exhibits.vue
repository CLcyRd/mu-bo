<template>
  <view class="container">
    <view class="exhibit-list">
      <view class="exhibit-item" v-for="item in exhibits" :key="item.id">
        <image class="exhibit-image" :src="item.image_url || 'https://coresg-normal.trae.ai/api/ide/v1/text_to_image?prompt=Vintage%20movie%20poster%20or%20prop&image_size=square'" mode="aspectFill"></image>
        <view class="exhibit-info">
          <view class="exhibit-name">{{ item.name }}</view>
          <view class="exhibit-meta">{{ item.era }} | {{ item.category }}</view>
          <view class="exhibit-desc">{{ item.description }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'

interface Exhibit {
  id: number
  name: string
  description: string
  category: string
  era: string
  image_url: string
}

const exhibits = ref<Exhibit[]>([])

const fetchExhibits = () => {
  uni.request({
    url: 'http://localhost:8000/api/exhibits/',
    success: (res: any) => {
      if (res.data && res.data.exhibits) {
        exhibits.value = res.data.exhibits
      }
    },
    fail: (err) => {
      console.error('Failed to fetch exhibits', err)
    }
  })
}

onLoad(() => {
  fetchExhibits()
})
</script>

<style>
.container {
  padding: 10px;
  background-color: #f5f5f5;
}
.exhibit-item {
  background-color: #fff;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.exhibit-image {
  width: 100%;
  height: 200px;
}
.exhibit-info {
  padding: 12px;
}
.exhibit-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 4px;
}
.exhibit-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 8px;
}
.exhibit-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.4;
}
</style>
