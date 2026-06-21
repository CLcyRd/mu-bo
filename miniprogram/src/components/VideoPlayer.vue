<template>
  <view class="video-page">
    <view class="top-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="close-button" @click="emitClose">‹</view>
      <view class="title">{{ title || '视频播放' }}</view>
      <view class="top-spacer"></view>
    </view>

    <view class="video-stage">
      <video
        id="sharedVideoPlayer"
        class="video"
        :src="src"
        :title="title"
        controls
        autoplay
        object-fit="contain"
        :show-fullscreen-btn="false"
        show-play-btn
        enable-progress-gesture
        @fullscreenchange="handleFullscreenChange"
        @error="handleError"
      ></video>
      <cover-view v-if="!isFullscreen" class="fullscreen-button" @click="requestFullscreen">
        <cover-view class="fullscreen-icon">⛶</cover-view>
      </cover-view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { getCurrentInstance, nextTick, onMounted, ref } from 'vue'

defineProps<{
  src: string
  title?: string
}>()

const emit = defineEmits<{
  (event: 'close'): void
}>()

const statusBarHeight = ref(30)
const isFullscreen = ref(false)
const instance = getCurrentInstance()
let videoContext: any = null

const emitClose = () => {
  emit('close')
}

const requestFullscreen = () => {
  if (!videoContext) {
    videoContext = uni.createVideoContext('sharedVideoPlayer', instance?.proxy as any)
  }
  try {
    videoContext.requestFullScreen({ direction: 90 })
  } catch (error) {
    uni.showToast({ title: '无法进入全屏', icon: 'none' })
  }
}

const handleFullscreenChange = (event: any) => {
  isFullscreen.value = Boolean(event?.detail?.fullScreen)
}

const handleError = () => {
  uni.showToast({ title: '视频加载失败', icon: 'none' })
}

onMounted(() => {
  const systemInfo = uni.getSystemInfoSync()
  statusBarHeight.value = systemInfo.statusBarHeight || 30
  nextTick(() => {
    videoContext = uni.createVideoContext('sharedVideoPlayer', instance?.proxy as any)
  })
})
</script>

<style>
.video-page {
  height: 100vh;
  background: #000000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.top-bar {
  flex: 0 0 auto;
  min-height: 96rpx;
  padding-left: 24rpx;
  padding-right: 24rpx;
  padding-bottom: 18rpx;
  box-sizing: border-box;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  color: #ffffff;
  background: rgba(0, 0, 0, 0.72);
}

.close-button {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.14);
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 46rpx;
  line-height: 1;
  flex: 0 0 auto;
}

.title {
  min-width: 0;
  flex: 1;
  padding: 0 20rpx;
  text-align: center;
  font-size: 32rpx;
  line-height: 64rpx;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.top-spacer {
  width: 64rpx;
  height: 64rpx;
  flex: 0 0 auto;
}

.video-stage {
  flex: 1;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000000;
  position: relative;
}

.video {
  width: 100%;
  height: 100%;
  background: #000000;
}

.fullscreen-button {
  position: absolute;
  right: 28rpx;
  bottom: 34rpx;
  width: 72rpx;
  height: 72rpx;
  border-radius: 36rpx;
  background: rgba(0, 0, 0, 0.46);
  border: 1rpx solid rgba(255, 255, 255, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
}

.fullscreen-icon {
  color: #ffffff;
  font-size: 42rpx;
  line-height: 72rpx;
  text-align: center;
}
</style>
