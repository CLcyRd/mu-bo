<template>
  <view class="page">
    <scroll-view class="detail-main" scroll-y>
      <view class="image-stage">
        <scroll-view class="gallery" scroll-x :scroll-into-view="activeSlideId" scroll-with-animation>
          <view
            v-for="(color, index) in product.colors"
            :id="`slide-${index}`"
            :key="color.label"
            class="gallery-item"
          >
            <image
              v-if="color.imageUrl"
              class="gallery-image"
              :src="color.imageUrl"
              mode="aspectFill"
            ></image>
          </view>
        </scroll-view>
      </view>

      <view class="color-panel">
        <view class="panel-label">颜色选择</view>
        <view class="color-options">
          <view
            v-for="(color, index) in product.colors"
            :key="color.label"
            class="color-button"
            :class="{ 'is-active': index === activeColorIndex }"
            @click="selectColor(index)"
          >
            <view class="swatch" :style="{ background: color.value }"></view>
            <view>{{ color.label }}</view>
          </view>
        </view>
      </view>

      <view class="info-section">
        <view class="product-name">{{ product.name }}</view>
        <view class="product-summary">{{ product.summary }}</view>
        <view class="spec-list">
          <view v-for="spec in product.specs" :key="spec.label" class="spec-row">
            <view class="spec-label">{{ spec.label }}</view>
            <view class="spec-value">{{ spec.value }}</view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { buildApiUrl, normalizeApiAssetUrl } from '../../utils/api'

type ProductKey = 'tshirt' | 'vest' | 'cap' | 'cup'

type ProductDetail = {
  name: string
  summary: string
  colors: Array<{
    label: string
    value: string
    imageUrl: string
  }>
  specs: Array<{
    label: string
    value: string
  }>
}

type ApiResponse<T> = {
  code: number
  message: string
  data: T
}

type ProductApiItem = {
  id: string
  name?: string
  title?: string
  summary: string
  colors: Array<{
    label?: string
    name?: string
    value: string
    image_url?: string
  }>
  specs: Array<{
    label: string
    value: string
  }>
}

const products: Record<ProductKey, ProductDetail> = {
  tshirt: {
    name: 'T恤',
    summary: '纯棉宽松版型，适合日常穿着与文创展示。',
    colors: [
      { label: '黑色', value: '#1d1d1f', imageUrl: '' },
      { label: '深灰', value: '#4f5357', imageUrl: '' },
      { label: '浅灰', value: '#c8c9c7', imageUrl: '' }
    ],
    specs: [
      { label: '材质', value: '300g纯棉双纱紧密赛络纺' },
      { label: '颜色', value: '深灰、浅灰、黑色' },
      { label: '版型', value: 'OVERSIZE宽松版型' },
      { label: '尺码', value: 'M、L、XL、XXL' }
    ]
  },
  vest: {
    name: '马甲',
    summary: '多功能穿搭单品，后背可脱卸，适合户外和日常场景。',
    colors: [
      { label: '黑色', value: '#111214', imageUrl: '' },
      { label: '灰色', value: '#8c8f91', imageUrl: '' }
    ],
    specs: [
      { label: '材质', value: '100%锦纶面料 + 100%聚酯纤维网布' },
      { label: '特点', value: '多功能马甲，后背可脱卸，速干透气' },
      { label: '颜色', value: '黑色、灰色' },
      { label: '尺码', value: 'S、M、L、XL' }
    ]
  },
  cap: {
    name: '帽子',
    summary: '速干材质帽款，适合晴天出行与户外活动。',
    colors: [
      { label: '米紫', value: 'linear-gradient(135deg,#d7c9af 50%,#6d5aa7 50%)', imageUrl: '' },
      { label: '米黄', value: 'linear-gradient(135deg,#d7c9af 50%,#e6c94b 50%)', imageUrl: '' },
      { label: '黑绿', value: 'linear-gradient(135deg,#1b1d1e 50%,#4b8a54 50%)', imageUrl: '' },
      { label: '灰白', value: 'linear-gradient(135deg,#9c9fa3 50%,#f0f1ef 50%)', imageUrl: '' }
    ],
    specs: [
      { label: '材质', value: '速干材质' },
      { label: '特点', value: '吸湿快干、透气防晒' },
      { label: '颜色', value: '米紫、米黄、黑绿、灰白' },
      { label: '尺码', value: '头围56-58cm，帽深12cm' }
    ]
  },
  cup: {
    name: '水杯',
    summary: '双层不锈钢杯身，防烫隔冷，适合随身携带。',
    colors: [
      { label: '黑色', value: '#171819', imageUrl: '' },
      { label: '蓝色', value: '#2e6bb7', imageUrl: '' },
      { label: '绿色', value: '#49875a', imageUrl: '' },
      { label: '橙色', value: '#de7c2d', imageUrl: '' },
      { label: '紫色', value: '#7753a6', imageUrl: '' },
      { label: '红色', value: '#ba3931', imageUrl: '' },
      { label: '黄色', value: '#e6c542', imageUrl: '' }
    ],
    specs: [
      { label: '材质', value: '不锈钢原色内壁，双层不锈钢防烫隔冷' },
      { label: '颜色', value: '红色、蓝色、黄色、黑色、紫色、绿色、橙色' },
      { label: '容量', value: '255ML' },
      { label: '尺寸', value: '杯高8.5cm，杯宽7.5cm' }
    ]
  }
}

const productKey = ref<ProductKey>('tshirt')
const activeColorIndex = ref(0)
const remoteProduct = ref<ProductDetail | null>(null)

const product = computed(() => remoteProduct.value || products[productKey.value])
const activeSlideId = computed(() => `slide-${activeColorIndex.value}`)

const isProductKey = (value: string): value is ProductKey => {
  return Object.prototype.hasOwnProperty.call(products, value)
}

const selectColor = (index: number) => {
  activeColorIndex.value = index
}

const mapApiProduct = (item: ProductApiItem): ProductDetail => ({
  name: item.name || item.title || '',
  summary: item.summary,
  colors: item.colors.map((color) => ({
    label: color.label || color.name || '',
    value: color.value,
    imageUrl: normalizeApiAssetUrl(color.image_url || '')
  })),
  specs: item.specs
})

const fetchProductDetail = (id: string) => {
  uni.request({
    url: buildApiUrl(`/api/products/${id}`),
    method: 'GET',
    success: (res: any) => {
      if (res.statusCode >= 200 && res.statusCode < 300 && res.data?.code === 0) {
        const payload = res.data as ApiResponse<{ item: ProductApiItem }>
        remoteProduct.value = mapApiProduct(payload.data.item)
        activeColorIndex.value = 0
        uni.setNavigationBarTitle({ title: `${remoteProduct.value.name}详情` })
        return
      }
      uni.showToast({ title: res.data?.message || '产品加载失败', icon: 'none' })
    },
    fail: () => {
      uni.showToast({ title: '产品加载失败', icon: 'none' })
    }
  })
}

onLoad((options) => {
  const key = typeof options?.product === 'string' ? decodeURIComponent(options.product) : ''
  productKey.value = isProductKey(key) ? key : 'tshirt'
  uni.setNavigationBarTitle({ title: `${products[productKey.value].name}详情` })
  fetchProductDetail(productKey.value)
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

.detail-main {
  flex: 1;
  min-height: 0;
  background: #f7f8ee;
}

.image-stage {
  background: #eef2f5;
  border-bottom: 2rpx solid #dde3ea;
}

.gallery {
  width: 100%;
  white-space: nowrap;
}

.gallery-item {
  width: 100%;
  height: 600rpx;
  display: inline-block;
  background: #f1f4f6;
}

.gallery-image {
  width: 100%;
  height: 600rpx;
}

.color-panel {
  background: #ffffff;
  border-bottom: 2rpx solid #dde3ea;
  padding: 28rpx 32rpx 32rpx;
  box-sizing: border-box;
}

.panel-label {
  font-size: 24rpx;
  line-height: 1.2;
  color: #637083;
  margin-bottom: 20rpx;
}

.color-options {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.color-button {
  min-height: 68rpx;
  border: 2rpx solid #dde3ea;
  border-radius: 16rpx;
  background: #ffffff;
  color: #1f242d;
  padding: 14rpx 20rpx;
  font-size: 26rpx;
  font-weight: 650;
  display: flex;
  align-items: center;
  gap: 14rpx;
  box-sizing: border-box;
}

.color-button.is-active {
  border-color: #2d65b3;
  background: #e8f0fb;
  color: #2d65b3;
}

.swatch {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  border: 4rpx solid #ffffff;
  box-shadow: 0 0 0 2rpx rgba(31, 36, 45, 0.18);
  flex: 0 0 auto;
  box-sizing: border-box;
}

.info-section {
  padding: 36rpx 32rpx 60rpx;
  box-sizing: border-box;
}

.product-name {
  font-size: 50rpx;
  line-height: 1.2;
  font-weight: 780;
  letter-spacing: 0;
  margin-bottom: 16rpx;
}

.product-summary {
  font-size: 28rpx;
  line-height: 1.55;
  color: #637083;
  margin-bottom: 32rpx;
}

.spec-list {
  background: #ffffff;
  border: 2rpx solid #dde3ea;
  border-radius: 16rpx;
  overflow: hidden;
  box-shadow: 0 12rpx 36rpx rgba(25, 36, 58, 0.08);
}

.spec-row {
  display: grid;
  grid-template-columns: 144rpx minmax(0, 1fr);
  gap: 20rpx;
  padding: 26rpx 28rpx;
  border-bottom: 2rpx solid #dde3ea;
  font-size: 28rpx;
  line-height: 1.45;
  box-sizing: border-box;
}

.spec-row:last-child {
  border-bottom: 0;
}

.spec-label {
  color: #637083;
  font-weight: 650;
}

.spec-value {
  color: #1f242d;
  min-width: 0;
}
</style>
