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

const loading = ref(false)

const onWeChatLogin = async () => {
  loading.value = true
  
  try {
    // 1. Get Login Code
    const loginRes = await new Promise<UniApp.LoginRes>((resolve, reject) => {
      uni.login({
        provider: 'weixin',
        success: resolve,
        fail: reject
      })
    })
    
    const loginCode = loginRes.code

    // 2. Call Backend
    const response = await new Promise<any>((resolve, reject) => {
      uni.request({
        url: 'http://localhost:8000/api/auth/wechat/login', // Update with real server IP in prod
        method: 'POST',
        data: {
          code: loginCode
          // phone_code is optional now
        },
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else {
            reject(res.data)
          }
        },
        fail: reject
      })
    })

    // 3. Handle Success
    console.log('Login success', response)
    uni.setStorageSync('token', response.access_token)
    
    uni.showToast({
      title: '登录成功',
      icon: 'success'
    })
    
    setTimeout(() => {
      uni.switchTab({
        url: '/pages/index/index'
      })
    }, 1500)

  } catch (error: any) {
    console.error('Login failed', error)
    uni.showToast({
      title: error.detail || '登录失败，请重试',
      icon: 'none'
    })
  } finally {
    loading.value = false
  }
}

// Keep old handler commented out or remove it? Let's remove it to clean up.
/*
const onGetPhoneNumber = async (e: any) => {
   // ... (old code)
}
*/
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
  background-color: #ffffff;
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
    color: #333;
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
    background-color: #07c160;
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
