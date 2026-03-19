<template>
  <view class="page">
    <view class="container">
      <view class="header-section">
        <view class="title-cn">参观须知</view>
        <view class="title-en">VISITOR NOTICE</view>
        <view class="header-line"></view>
      </view>

      <view class="notice-list">
        <view class="notice-card" v-for="(section, index) in formattedNoticeList" :key="index">
          <view class="card-header">
            <text class="section-num">{{ section.num }}</text>
            <text class="section-title">{{ section.title }}</text>
          </view>
          
          <view class="card-divider"></view>
          
          <view class="card-body">
            <view class="list-item" v-for="(item, itemIdx) in section.items" :key="itemIdx">
              <view class="bullet-point"></view>
              <view class="item-content">
                <text class="item-label" v-if="item.label">{{ item.label }}：</text>
                <text class="item-text">{{ item.text }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>

      <view class="footer-tip">
        推开这扇门，走进一个时代<br>感谢您的配合与守候
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
// 对原有的须知数据进行了结构化升级，拆分出强调标签，方便UI排版
const formattedNoticeList = [
  {
    num: '01',
    title: '开放时间',
    items: [
      { label: '', text: '每周三、周六 10:00 - 16:00' },
      { label: '温馨提示', text: '15:00 前停止入场，请合理安排您的行程。' }
    ]
  },
  {
    num: '02',
    title: '预约入馆',
    items: [
      { label: '个人参观', text: '请通过“个人预约”实名、分时段提前预约。现场凭预约码或有效身份证件核验入馆。' },
      { label: '团队参观', text: '（含 10 人及以上）请通过“团队预约”，提前 5 个工作日进行预约。' }
    ]
  },
  {
    num: '03',
    title: '文明公约',
    items: [
      { label: '轻声细语', text: '故居是安静的，请将手机调至静音，勿大声喧哗。' },
      { label: '尊重展品', text: '请勿触摸或损伤馆内一切展品、展柜。' },
      { label: '摄影须知', text: '允许非商业用途的拍摄，禁用闪光灯、三脚架及自拍杆。' },
      { label: '爱护环境', text: '请勿携带宠物（导盲犬除外）、禁烟、禁食、禁携危险品。' },
      { label: '儿童看护', text: '请家长照看好随行儿童，勿攀爬展台展柜。' }
    ]
  }
]
</script>

<style lang="scss">
.page {
  min-height: 100vh;
  background: #0b1528;
  background-image: radial-gradient(circle at 50% 0%, rgba(30, 60, 114, 0.4) 0%, transparent 60%);
  padding-bottom: 60rpx;
}

.container {
  padding: 40rpx 30rpx;
}

/* 头部样式 */
.header-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 50rpx;
  margin-top: 20rpx;
}

.title-cn {
  font-size: 52rpx;
  font-weight: bold;
  color: #e3d90f;
  letter-spacing: 4rpx;
}

.title-en {
  margin-top: 10rpx;
  font-size: 22rpx;
  font-weight: 500;
  color: #c7a23f;
  letter-spacing: 6rpx;
}

.header-line {
  width: 60rpx;
  height: 4rpx;
  background: linear-gradient(90deg, transparent, #d4af37, transparent);
  margin-top: 24rpx;
}

/* 须知卡片列表 */
.notice-list {
  display: flex;
  flex-direction: column;
  gap: 36rpx;
}

.notice-card {
  background: rgba(26, 42, 71, 0.45);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 20rpx;
  padding: 40rpx 36rpx;
  backdrop-filter: blur(12px);
  box-shadow: 0 12rpx 30rpx rgba(0, 0, 0, 0.2);
}

/* 卡片头部：序号 + 标题 */
.card-header {
  display: flex;
  align-items: baseline;
}

.section-num {
  font-size: 44rpx;
  font-weight: bold;
  font-style: italic;
  color: rgba(212, 175, 55, 0.6);
  margin-right: 16rpx;
  font-family: 'Times New Roman', serif;
}

.section-title {
  font-size: 38rpx;
  font-weight: 600;
  color: #f0f4f8;
  letter-spacing: 2rpx;
}

/* 精致的分割线 */
.card-divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, rgba(212,175,55,0.3) 0%, transparent 100%);
  margin: 24rpx 0 32rpx;
}

/* 列表内容区 */
.list-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 24rpx;
}

.list-item:last-child {
  margin-bottom: 0;
}

.bullet-point {
  width: 8rpx;
  height: 8rpx;
  border-radius: 50%;
  background: #d4af37;
  margin-top: 18rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
  box-shadow: 0 0 8rpx rgba(212, 175, 55, 0.8);
}

.item-content {
  flex: 1;
  font-size: 32rpx;
  line-height: 1.6;
}

.item-label {
  font-weight: 600;
  color: #d4af37;
}

.item-text {
  color: #a0aec0;
  text-align: justify;
}

/* 底部结语 */
.footer-tip {
  margin-top: 60rpx;
  text-align: center;
  font-size: 26rpx;
  line-height: 1.8;
  color: rgba(160, 174, 192, 0.5);
  letter-spacing: 2rpx;
}
</style>