<template>
  <view class="device-container">
    <!-- 顶部导航栏 -->
    <view class="nav-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
      <view class="icon-btn" @click="goBack">
        <text class="back-icon">‹</text>
      </view>
      <text class="nav-title">讲解ID: {{ audioId ? audioId : '' }}</text>
      <view class="icon-btn"></view>    
    </view>

    <!-- 动态视觉区 -->
    <view class="visualizer-container">
      <view class="circle-pulse" :class="{ 'is-playing': isPlaying }">
        <view class="circle-inner">
          <image src="data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2024%2024%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M12%203v10.55c-.59-.34-1.27-.55-2-.55-2.21%200-4%201.79-4%204s1.79%204%204%204%204-1.79%204-4V7h4V3h-6z%22%20fill%3D%22%23FFD700%22%2F%3E%3C%2Fsvg%3E" class="note-svg" mode="aspectFit" />
        </view>
      </view>
    </view>

    <!-- 标题信息 -->
    <view class="info-section">
      <text class="title">{{ audioInfo.title || '加载中...' }}</text>
    </view>

    <!-- 播放器组件 -->
    <view class="player-section">
      <view class="progress-bar">
        <text class="time">{{ formatTime(currentTime) }}</text>
        <slider 
          class="slider" 
          :value="currentTime" 
          :max="duration || 100" 
          activeColor="#FFD700" 
          backgroundColor="rgba(255,255,255,0.2)" 
          block-size="14" 
          block-color="#FFD700" 
          @change="onSliderChange"
          @changing="onSliderChanging"
        />
        <text class="time">{{ formatTime(duration) }}</text>
      </view>
      <view class="controls">
        <view class="side-btn" @click="seekBy(-15)">
          <image src="data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2024%2024%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M11%2018V6l-8.5%206%208.5%206zm.5-6l8.5%206V6l-8.5%206z%22%20fill%3D%22%23ccd6f6%22%2F%3E%3C%2Fsvg%3E" class="side-svg" mode="aspectFit" />
        </view>
        <view class="play-btn" @click="togglePlay">
          <image v-if="!isPlaying" src="data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2024%2024%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M8%205v14l11-7z%22%20fill%3D%22%230A192F%22%2F%3E%3C%2Fsvg%3E" class="play-svg" mode="aspectFit" />
          <image v-else src="data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2024%2024%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M6%2019h4V5H6v14zm8-14v14h4V5h-4z%22%20fill%3D%22%230A192F%22%2F%3E%3C%2Fsvg%3E" class="pause-svg" mode="aspectFit" />
        </view>
        <view class="side-btn" @click="seekBy(15)">
          <image src="data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2024%2024%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cpath%20d%3D%22M4%2018l8.5-6L4%206v12zm9-12v12l8.5-6L13%206z%22%20fill%3D%22%23ccd6f6%22%2F%3E%3C%2Fsvg%3E" class="side-svg" mode="aspectFit" />
        </view>
      </view>
    </view>

    <view v-if="!audioInfo.description" class="bottom-spacer"></view>

    <!-- 简介卡片：如果有简介则显示 -->
    <view v-if="audioInfo.description" class="desc-section">
      <view class="desc-header">
        <text class="desc-title">简介</text>
      </view>
      <text class="desc-preview">{{ audioInfo.description }}</text>
      <view class="read-more-btn" @click="openSheet">查看全部详情</view>
    </view>

    <!-- 底部半屏弹窗(Bottom Sheet) -->
    <template v-if="audioInfo.description">
      <view class="modal-overlay" :class="{ 'active': bottomSheetVisible }" @click="closeSheet"></view>
      <view class="bottom-sheet" :class="{ 'active': bottomSheetVisible }">
        <view class="sheet-handle"></view>
        <view class="sheet-header">
          <text class="sheet-title">完整简介</text>
          <view class="close-btn" @click="closeSheet">
            <text class="close-icon">×</text>
          </view>
        </view>
        <scroll-view scroll-y class="sheet-content">
          <text class="desc-full-text">{{ audioInfo.description }}</text>
        </scroll-view>
      </view>
    </template>
  </view>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { API_BASE_URL } from '@/utils/api'

const audioId = ref<number | null>(null)
const audioInfo = ref({
  title: '',
  audio_url: '',
  description: ''
})

const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const isDragging = ref(false)
const bottomSheetVisible = ref(false)

const statusBarHeight = ref(44) // Default value

let audioContext: UniApp.InnerAudioContext | null = null

onMounted(() => {
  const systemInfo = uni.getSystemInfoSync()
  if (systemInfo.statusBarHeight) {
    // Add some padding to avoid being exactly at the edge
    statusBarHeight.value = systemInfo.statusBarHeight + 10
  }
})

onLoad((options) => {
  // 解析场景值 (小程序码扫描进入)
  if (options && options.scene) {
    const scene = decodeURIComponent(options.scene)
    // 假设 scene 格式为 id=123
    const match = scene.match(/id=(\d+)/)
    if (match) {
      audioId.value = parseInt(match[1], 10)
    }
  } else if (options && options.id) {
    audioId.value = parseInt(options.id, 10)
  }
  
  if (audioId.value) {
    fetchAudioDetail(audioId.value)
  } else {
    uni.showToast({ title: '未找到音频参数', icon: 'none' })
  }
})

const fetchAudioDetail = async (id: number) => {
  try {
    const res = await uni.request({
      url: `${API_BASE_URL}/api/audio-explanations/public/${id}`,
      method: 'GET'
    })
    
    const data = res.data as any
    if (data && data.code === 0) {
      audioInfo.value = data.data.item
      initAudioPlayer(data.data.item.audio_url)
    } else {
      uni.showToast({ title: data.message || '获取讲解失败', icon: 'none' })
    }
  } catch (error) {
    uni.showToast({ title: '网络请求失败', icon: 'none' })
  }
}

const resolveAudioUrl = (url: string) => {
  if (!url) return ''
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url
  }
  return API_BASE_URL + url
}

const initAudioPlayer = (url: string) => {
  if (audioContext) {
    audioContext.destroy()
  }
  
  audioContext = uni.createInnerAudioContext()
  audioContext.src = resolveAudioUrl(url)
  
  audioContext.onPlay(() => {
    isPlaying.value = true
  })
  
  audioContext.onPause(() => {
    isPlaying.value = false
  })
  
  audioContext.onStop(() => {
    isPlaying.value = false
    currentTime.value = 0
  })
  
  audioContext.onEnded(() => {
    isPlaying.value = false
    currentTime.value = 0
  })
  
  audioContext.onTimeUpdate(() => {
    if (!isDragging.value && audioContext) {
      currentTime.value = audioContext.currentTime
      if (audioContext.duration && duration.value === 0) {
        duration.value = audioContext.duration
      }
    }
  })
  
  audioContext.onCanplay(() => {
    if (audioContext && audioContext.duration) {
      duration.value = audioContext.duration
    }
  })
  
  audioContext.onError((res) => {
    console.error('音频播放错误', res.errMsg)
    uni.showToast({ title: '音频加载失败', icon: 'none' })
    isPlaying.value = false
  })
}

const togglePlay = () => {
  if (!audioContext) return
  
  if (isPlaying.value) {
    audioContext.pause()
  } else {
    audioContext.play()
  }
}

const seekBy = (seconds: number) => {
  if (!audioContext) return
  let newTime = currentTime.value + seconds
  if (newTime < 0) newTime = 0
  if (newTime > duration.value) newTime = duration.value
  
  currentTime.value = newTime
  audioContext.seek(newTime)
}

const onSliderChanging = (e: any) => {
  isDragging.value = true
  currentTime.value = e.detail.value
}

const onSliderChange = (e: any) => {
  if (!audioContext) return
  currentTime.value = e.detail.value
  audioContext.seek(e.detail.value)
  isDragging.value = false
}

const formatTime = (time: number) => {
  if (!time || isNaN(time)) return '00:00'
  const min = Math.floor(time / 60)
  const sec = Math.floor(time % 60)
  return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
}

const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
}

const openSheet = () => {
  bottomSheetVisible.value = true
}

const closeSheet = () => {
  bottomSheetVisible.value = false
}

onUnmounted(() => {
  if (audioContext) {
    audioContext.destroy()
    audioContext = null
  }
})
</script>

<style lang="scss" scoped>
.device-container {
  min-height: 100vh;
  background: linear-gradient(160deg, #0A192F 0%, #112240 100%);
  display: flex;
  flex-direction: column;
  color: #ffffff;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
}

/* 顶部导航栏 */
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px 20px;
  font-size: 16px;
  font-weight: 500;
  
  .nav-title {
    color: #fff;
    font-size: 16px;
  }
}

.icon-btn {
  background: none;
  border: none;
  color: #ffffff;
  width: 32px;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: background 0.2s;
  
  &:active {
    background: rgba(255, 255, 255, 0.1);
  }
}

.back-icon {
  font-size: 24px;
  font-weight: 600;
  line-height: 1;
}

/* 动态视觉区 */
.visualizer-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
  min-height: 160px;
}

.circle-pulse {
  width: 184px;
  height: 184px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FFD700 0%, #FF9800 100%);
  box-shadow: 0 0 40px rgba(255, 215, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  animation: pulse 3s infinite ease-in-out;
  animation-play-state: paused;
  
  &.is-playing {
    animation-play-state: running;
  }
}

.circle-inner {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background-color: #0A192F;
  display: flex;
  justify-content: center;
  align-items: center;
}

.note-svg {
  width: 80px;
  height: 80px;
  fill: #FFD700;
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4); }
  70% { transform: scale(1); box-shadow: 0 0 0 30px rgba(255, 215, 0, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 215, 0, 0); }
}

/* 标题信息 */
.info-section {
  padding: 0 24px;
  text-align: center;
  margin-bottom: 20px;
  
  .title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 8px;
    letter-spacing: 1px;
    color: #fff;
    display: block;
  }
}

/* 播放器组件 */
.player-section {
  padding: 0 24px;
  margin-bottom: 25px;
}

.bottom-spacer {
  height: 16vh;
  width: 100%;
}

.progress-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  
  .time {
    font-size: 14px;
    color: #8892b0;
    font-variant-numeric: tabular-nums;
    width: 40px;
    text-align: center;
  }
  
  .slider {
    flex: 1;
    margin: 0;
  }
}

.controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 30px;
}

.play-btn {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  background: #FFD700;
  color: #0A192F;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 10px 20px rgba(255, 215, 0, 0.2);
  transition: all 0.2s;
  
  &:active {
    transform: scale(0.95);
  }
}

.play-svg {
  width: 32px;
  height: 32px;
}

.pause-svg {
  width: 32px;
  height: 32px;
}

.side-btn {
  background: none;
  border: none;
  color: #ccd6f6;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: color 0.2s;
  padding: 10px;
  
  &:active {
    color: #FFD700;
  }
  
.side-svg {
  width: 28px;
  height: 28px;
}
}

/* 简介卡片：摘要版 */
.desc-section {
  margin: 0 20px 30px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.desc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.desc-title {
  font-size: 16px;
  font-weight: 600;
  color: #ccd6f6;
}

.desc-preview {
  font-size: 13px;
  color: #8892b0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.read-more-btn {
  display: block;
  width: 100%;
  text-align: center;
  background: none;
  color: #FFD700;
  font-size: 13px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  font-weight: 500;
}

/* ========== 底部半屏弹窗样式 ========== */
.modal-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(3px);
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s ease;
  
  &.active {
    opacity: 1;
    visibility: visible;
  }
}

.bottom-sheet {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 65%;
  background: #112240;
  border-top-left-radius: 30px;
  border-top-right-radius: 30px;
  z-index: 101;
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.1, 0.88, 0.3, 1);
  display: flex;
  flex-direction: column;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.5);
  box-sizing: border-box;
  
  &.active {
    transform: translateY(0);
  }
}

.sheet-handle {
  width: 40px;
  height: 5px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  margin: 15px auto;
}

.sheet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px 15px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.sheet-title {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.close-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  
}

.close-icon {
  font-size: 18px;
  font-weight: 600;
  line-height: 1;
}

.sheet-content {
  padding: 24px;
  flex: 1;
  height: 0;
  box-sizing: border-box;
  
  .desc-full-text {
    font-size: 14px;
    color: #8892b0;
    line-height: 1.8;
    text-align: justify;
    white-space: pre-wrap;
  }

}
</style>
