<template>
  <view class="page">
    <view class="page-header">
      <view class="page-kicker">MUSEUM STORE</view>
      <view class="page-title">文创产品展示</view>
      <view class="page-subtitle">选择产品种类，查看对应颜色与产品信息。</view>
    </view>

    <scroll-view class="product-list" scroll-y>
      <view
        v-for="product in products"
        :key="product.id"
        class="product-card"
        hover-class="product-card-active"
        @click="goToDetail(product.id)"
      >
        <view class="product-image-placeholder">
          <image
            v-if="product.primaryImageUrl"
            class="product-image"
            :src="product.primaryImageUrl"
            mode="aspectFill"
          ></image>
        </view>
        <view class="product-copy">
          <view>
            <view class="product-title-row">
              <view class="product-title">{{ product.title }}</view>
              <view class="product-count">{{ product.colorCount }}色</view>
            </view>
            <view class="product-desc">{{ product.desc }}</view>
          </view>

          <view class="color-row">
            <view
              v-for="color in product.colors"
              :key="color.name"
              class="swatch"
              :style="{ background: color.value }"
            ></view>
          </view>

          <view class="action-row">
            <view class="product-meta">{{ product.meta }}</view>
            <view class="detail-button">查看详情</view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad, onShow } from '@dcloudio/uni-app'
import { syncTabBar } from '../../utils/auth'
import { buildApiUrl, normalizeApiAssetUrl } from '../../utils/api'

type ProductColor = {
  name: string
  value: string
}

type ProductItem = {
  id: string
  title: string
  colorCount: number
  desc: string
  meta: string
  primaryImageUrl: string
  colors: ProductColor[]
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type ProductApiItem = {
  id: string
  title?: string
  name?: string
  desc: string
  meta: string
  color_count?: number
  primary_image_url?: string
  colors: Array<{
    name?: string
    label?: string
    value: string
  }>
}

const fallbackProducts: ProductItem[] = [
  {
    id: 'tshirt',
    title: 'T恤',
    colorCount: 3,
    desc: '300g纯棉双纱紧密赛络纺，OVERSIZE宽松版型。',
    meta: 'M-L-XL-XXL',
    primaryImageUrl: '',
    colors: [
      { name: '黑色', value: '#1d1d1f' },
      { name: '深灰', value: '#4f5357' },
      { name: '浅灰', value: '#c8c9c7' }
    ]
  },
  {
    id: 'vest',
    title: '马甲',
    colorCount: 2,
    desc: '多功能马甲，后背可脱卸，速干透气。',
    meta: 'S-M-L-XL',
    primaryImageUrl: '',
    colors: [
      { name: '黑色', value: '#111214' },
      { name: '灰色', value: '#8c8f91' }
    ]
  },
  {
    id: 'cap',
    title: '帽子',
    colorCount: 4,
    desc: '速干材质，吸湿快干、透气防晒。',
    meta: '头围56-58cm',
    primaryImageUrl: '',
    colors: [
      { name: '米紫', value: 'linear-gradient(135deg,#d7c9af 50%,#6d5aa7 50%)' },
      { name: '米黄', value: 'linear-gradient(135deg,#d7c9af 50%,#e6c94b 50%)' },
      { name: '黑绿', value: 'linear-gradient(135deg,#1b1d1e 50%,#4b8a54 50%)' },
      { name: '灰白', value: 'linear-gradient(135deg,#9c9fa3 50%,#f0f1ef 50%)' }
    ]
  },
  {
    id: 'cup',
    title: '水杯',
    colorCount: 7,
    desc: '双层不锈钢防烫隔冷，255ML容量。',
    meta: '255ML',
    primaryImageUrl: '',
    colors: [
      { name: '黑色', value: '#171819' },
      { name: '蓝色', value: '#2e6bb7' },
      { name: '绿色', value: '#49875a' },
      { name: '橙色', value: '#de7c2d' },
      { name: '紫色', value: '#7753a6' },
      { name: '红色', value: '#ba3931' },
      { name: '黄色', value: '#e6c542' }
    ]
  }
]

const products = ref<ProductItem[]>(fallbackProducts)

const mapApiProduct = (item: ProductApiItem): ProductItem => ({
  id: item.id,
  title: item.title || item.name || '',
  colorCount: item.color_count ?? item.colors.length,
  desc: item.desc,
  meta: item.meta,
  primaryImageUrl: normalizeApiAssetUrl(item.primary_image_url || ''),
  colors: item.colors.map((color) => ({
    name: color.name || color.label || '',
    value: color.value
  }))
})

const fetchProducts = () => {
  uni.request({
    url: buildApiUrl('/api/products'),
    method: 'GET',
    success: (res: any) => {
      if (res.statusCode >= 200 && res.statusCode < 300 && res.data?.code === 0) {
        const payload = res.data as ApiResponse<{ items: ProductApiItem[] }>
        products.value = (payload.data?.items || []).map(mapApiProduct)
        return
      }
      uni.showToast({ title: res.data?.message || '文创加载失败', icon: 'none' })
    },
    fail: () => {
      uni.showToast({ title: '文创加载失败', icon: 'none' })
    }
  })
}

const goToDetail = (id: string) => {
  uni.navigateTo({
    url: `/pages/cultural/detail?product=${encodeURIComponent(id)}`
  })
}

onLoad(() => {
  fetchProducts()
})

onShow(() => {
  syncTabBar()
})
</script>

<style>
.page {
  height: 100vh;
  background: #f7f8ee;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  color: #1f242d;
}

.page-header {
  padding: 68rpx 40rpx 36rpx;
  background: #26365f;
  color: #ffffff;
  flex: 0 0 auto;
}

.page-kicker {
  font-size: 24rpx;
  line-height: 1.2;
  color: rgba(255, 255, 255, 0.72);
  margin-bottom: 16rpx;
}

.page-title {
  font-size: 50rpx;
  line-height: 1.25;
  font-weight: 750;
  letter-spacing: 0;
}

.page-subtitle {
  margin-top: 16rpx;
  font-size: 26rpx;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.78);
}

.product-list {
  flex: 1;
  min-height: 0;
  padding: 32rpx 28rpx 60rpx;
  box-sizing: border-box;
  background: #f7f8ee;
}

.product-card {
  width: 100%;
  min-height: 320rpx;
  margin-bottom: 28rpx;
  background: #ffffff;
  border: 2rpx solid #dde3ea;
  border-radius: 16rpx;
  box-shadow: 0 12rpx 36rpx rgba(25, 36, 58, 0.08);
  overflow: hidden;
  display: grid;
  grid-template-columns: 236rpx minmax(0, 1fr);
  color: inherit;
}

.product-card-active {
  transform: scale(0.985);
}

.product-image-placeholder {
  width: 236rpx;
  min-height: 320rpx;
  background: #f1f4f6;
}

.product-image {
  width: 100%;
  height: 320rpx;
}

.product-copy {
  min-width: 0;
  padding: 28rpx 26rpx 26rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 20rpx;
  box-sizing: border-box;
}

.product-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16rpx;
}

.product-title {
  font-size: 36rpx;
  line-height: 1.25;
  font-weight: 760;
  color: #1f242d;
}

.product-count {
  flex: 0 0 auto;
  color: #2d65b3;
  font-size: 24rpx;
  line-height: 1.25;
  font-weight: 650;
}

.product-desc {
  margin-top: 6rpx;
  font-size: 26rpx;
  line-height: 1.45;
  color: #637083;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.color-row {
  display: flex;
  align-items: center;
  gap: 14rpx;
  min-height: 44rpx;
  flex-wrap: wrap;
}

.swatch {
  width: 36rpx;
  height: 36rpx;
  border-radius: 50%;
  border: 4rpx solid #ffffff;
  box-shadow: 0 0 0 2rpx rgba(31, 36, 45, 0.16);
  flex: 0 0 auto;
  box-sizing: border-box;
}

.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16rpx;
}

.product-meta {
  min-width: 0;
  color: #637083;
  font-size: 24rpx;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.detail-button {
  flex: 0 0 auto;
  height: 68rpx;
  line-height: 68rpx;
  padding: 0 24rpx;
  border-radius: 16rpx;
  background: #2d65b3;
  color: #ffffff;
  font-size: 26rpx;
  font-weight: 680;
  white-space: nowrap;
}
</style>
