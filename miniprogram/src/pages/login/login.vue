<template>
  <view class="login-container">
    <view class="logo-area">
      <image class="logo" src="/static/logo.png" mode="aspectFit"></image>
      <text class="app-name">谢晋故居</text>
    </view>
    
    <view class="action-area">
      <button 
        class="login-btn" 
        type="button" 
        @click="onWeChatLogin"
        :loading="loading"
      >
        微信一键登录
      </button>
      <text class="tips">登录即代表您同意《用户服务协议》和《隐私政策》</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { consumePendingRedirect, setTokenAndRefresh } from '../../utils/auth'

const loading = ref(false)
const redirectUrl = ref('/pages/index/index')

type WechatLoginResponse = {
  access_token: string
  token_type: string
}

const parseRoute = (url: string) => {
  const [path] = url.split('?')
  return path
}

const navigateAfterLogin = (url: string) => {
  const routePath = parseRoute(url)
  if (routePath === '/pages/index/index' || routePath === '/pages/my-bookings/my-bookings') {
    uni.switchTab({ url: routePath })
    return
  }
  uni.redirectTo({ url })
}

const showRetryModal = (content: string) => {
  uni.showModal({
    title: '登录失败',
    content,
    confirmText: '重试',
    cancelText: '取消',
    success: (res) => {
      if (res.confirm) {
        onWeChatLogin()
      }
    }
  })
}

const requestWeChatLogin = (code: string) =>
  new Promise<WechatLoginResponse>((resolve, reject) => {
    uni.request({
      url: 'http://localhost:8000/api/auth/wechat/login',
      method: 'POST',
      timeout: 10000,
      data: { code },
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as WechatLoginResponse)
          return
        }
        reject({
          type: 'http',
          statusCode: res.statusCode,
          data: res.data
        })
      },
      fail: (err) => reject({ type: 'network', error: err })
    })
  })

const resolveTargetUrl = () => {
  const pending = consumePendingRedirect()
  if (pending) {
    return pending
  }
  return redirectUrl.value
}

const onWeChatLogin = async () => {
  if (loading.value) {
    return
  }
  loading.value = true
  try {
    const loginRes = await new Promise<UniApp.LoginRes>((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: resolve,
        fail: reject
      })
    })
    const response = await requestWeChatLogin(loginRes.code)
    const refreshed = await setTokenAndRefresh(response.access_token)
    if (!refreshed) {
      showRetryModal('网络波动导致登录状态校验失败，请重试')
      return
    }
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => {
      navigateAfterLogin(resolveTargetUrl())
    }, 800)
  } catch (error: any) {
    const statusCode = error?.statusCode
    const detail = error?.data?.detail || error?.error?.errMsg || error?.message || '登录失败，请重试'
    if (statusCode === 500 || `${detail}`.includes('timeout') || `${detail}`.includes('超时')) {
      showRetryModal('服务暂时不可用，请重试')
      return
    }
    uni.showToast({ title: detail, icon: 'none' })
  } finally {
    loading.value = false
  }
}

onLoad((options) => {
  if (options?.redirect) {
    redirectUrl.value = decodeURIComponent(options.redirect)
  }
})
</script>

<style lang="scss">
.login-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  height: 100vh;
  padding: 100rpx 40rpx;
  box-sizing: border-box;
  background-color: #2b3a6b;
}

.logo-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 100rpx;
  
  .logo {
    width: 160rpx;
    height: 160rpx;
    border-radius: 20rpx;
    margin-bottom: 30rpx;
  }
  
  .app-name {
    font-size: 36rpx;
    font-weight: bold;
    color: #ffffff;
  }
}

.action-area {
  width: 100%;
  margin-bottom: 100rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  
  .login-btn {
    width: 100%;
    height: 90rpx;
    line-height: 90rpx;
    border-radius: 45rpx;
    font-size: 32rpx;
    background-color: #d4af37;
    margin-bottom: 30rpx;
    
    &::after {
      border: none;
    }
  }
  
  .tips {
    font-size: 24rpx;
    color: #999;
  }
}
</style>
