<template>
  <VideoPlayer :src="videoSrc" :title="videoTitle" @close="goBack" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import VideoPlayer from '../../components/VideoPlayer.vue'

const videoSrc = ref('')
const videoTitle = ref('视频播放')

const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack()
    return
  }
  uni.switchTab({ url: '/pages/index/index' })
}

onLoad((options) => {
  videoSrc.value = typeof options?.src === 'string' ? decodeURIComponent(options.src) : ''
  videoTitle.value = typeof options?.title === 'string' ? decodeURIComponent(options.title) : '视频播放'
  if (!videoSrc.value) {
    uni.showToast({ title: '视频地址无效', icon: 'none' })
  }
})
</script>
