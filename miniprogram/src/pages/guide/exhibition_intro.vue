<template>
  <view class="page">
    <view class="container">
      <view class="header-section">
        <view class="title-cn">展厅介绍</view>
        <view class="title-en">EXHIBITION INTRODUCTION</view>
        <view class="header-line"></view>
      </view>

      <view class="preface-section">
        <view class="preface-intro">这里，辑录的是谢晋广为流传的部分名言。</view>
        <view class="quote-list">
          <view class="quote-item">
            <text class="quote-icon">❝</text>
            <text class="quote-text">金杯银杯，不如老百姓的口碑。</text>
          </view>
          <view class="quote-item">
            <text class="quote-icon">❝</text>
            <text class="quote-text">我的每一次创作，都是一次生命的燃烧。</text>
          </view>
          <view class="quote-item">
            <text class="quote-icon">❝</text>
            <text class="quote-text">艺术家要有赤子之心，要有历史的忧患感。</text>
          </view>
        </view>
        <view class="preface-outro">请您在此停留，感受谢晋的温度与厚度。</view>
      </view>

      <view class="zone-list">
        <view class="zone-card" v-for="(zone, index) in formattedZones" :key="index">
          <view class="zone-header">
            <view class="zone-index">ZONE {{ index + 1 }}</view>
            <view class="zone-title">{{ zone.title }}</view>
          </view>

          <view class="image-placeholder">
            <image class="zone-image" :src="zone.imageUrl" mode="aspectFill" />
          </view>

          <view class="zone-points">
            <view class="point-item" v-for="(point, pIndex) in zone.points" :key="pIndex">
              <view class="point-name">
                <text class="point-dot"></text>
                {{ point.name }}
              </view>
              <view class="point-desc">{{ point.desc }}</view>
            </view>
          </view>
        </view>
      </view>

    </view>
  </view>
</template>

<script setup lang="ts">
// 将原有扁平的数据结构重构为嵌套结构，更利于页面渲染和未来扩展
const formattedZones = [
  {
    title: '家庭 | 朋友',
    imageUrl: '/static/museum_img/f9c3cb52f1859ff33b569b6024773334.jpg',
    points: [
      {
        name: '点位 · 家庭',
        desc: '这里，展现的是谢晋的生活日常。\n他说：“故乡的人民哺育我，我吃故乡的水长大。我是上虞的儿子，我是谢塘的儿子。”\n他说：“我是一只飘扬在天空的风筝，无论飞得多高多远，下面总有一根线牵着，这牵线的地方就是故乡。”\n他说：“每次我拍片回来，阿四总要守候在门口，时间再长，夜再深，他也要等我回来。”\n他说：“我是个严厉而不称职的父亲。”\n请您在此停留，感受谢晋的深情与柔情。'
      },
      {
        name: '点位 · 朋友圈',
        desc: '这里，陈列的是谢晋的师友群——海内外的编剧、演员、作家、艺术家。谢晋和他的朋友们，彼此激发，创造了中国电影的一个黄金时代。\n请您在此停留，感受谢晋时代的高原与高峰。'
      }
    ]
  },
  {
    title: '场景 | 创作',
    imageUrl: '/static/museum_img/a794f1ec2977772d115f3bfceee23717.jpg',
    points: [
      {
        name: '点位 · 创作现场',
        desc: '书桌前的那副眼镜，仿佛在等主人归来。\n谢晋说：“我们拍一部影片，好像双手捧一碗水，每一步都要聚精会神，严谨认真。”\n从分镜头手稿到导演工作本，从案头笔记到现场调度——这里，还原的是一位伟大的导演如何将故事变成光影，涓涓细流如何汇聚成滚滚江河。'
      },
      {
        name: '点位 · 壮志未酬',
        desc: '戛然而止，有些电影终究没有拍成。\n《大人家》《拉贝日记》《牧马人续集》……\n晚年，他的创作步履从未停歇。一份长长的片单，是他未完成的念想，也是我们永远的遗憾。它们未曾出现在银幕上，却留下了一串串的印迹。'
      }
    ]
  },
  {
    title: '作品与荣誉',
    imageUrl: '/static/museum_img/20260303215335_541_22.jpg',
    points: [
      {
        name: '点位 · 作品',
        desc: '1948 年-2008 年，60 年的创作足迹。\n成名：《女篮五号》《红色娘子军》《大李小李和老李》《舞台姐妹》\n代表：《天云山传奇》《牧马人》《高山下的花环》《芙蓉镇》\n转型：《最后的贵族》《清凉寺的钟声》《鸦片战争》\n每一部作品，都是生命的燃烧；每一个故事，都是时代的回响。'
      },
      {
        name: '点位 · 荣誉',
        desc: '奖杯与证书，是一个导演创造的艺术高度，也是中国电影走向世界的见证。\n但他最珍视的荣誉，永远是观众坐在影院里，为他的电影落泪或沉思的那一刻。'
      }
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
  margin-bottom: 40rpx;
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

/* 前言名言区 */
.preface-section {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 20rpx;
  padding: 36rpx;
  margin-bottom: 50rpx;
}

.preface-intro {
  font-size: 30rpx;
  color: #a0aec0;
  margin-bottom: 24rpx;
  text-align: center;
}

.quote-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.quote-item {
  display: flex;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.03);
  padding: 20rpx 24rpx;
  border-radius: 12rpx;
}

.quote-icon {
  font-size: 36rpx;
  color: #d4af37;
  margin-right: 12rpx;
  line-height: 1;
  font-family: serif;
}

.quote-text {
  font-size: 32rpx;
  line-height: 1.5;
  color: #f0f4f8;
  font-style: italic;
  letter-spacing: 1rpx;
}

.preface-outro {
  font-size: 28rpx;
  color: #d4af37;
  text-align: center;
  margin-top: 30rpx;
  letter-spacing: 2rpx;
  opacity: 0.8;
}

/* 展区卡片列表 */
.zone-list {
  display: flex;
  flex-direction: column;
  gap: 40rpx;
}

.zone-card {
  background: rgba(26, 42, 71, 0.45);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 24rpx;
  padding: 36rpx 30rpx;
  backdrop-filter: blur(12px);
  box-shadow: 0 12rpx 30rpx rgba(0, 0, 0, 0.25);
}

.zone-header {
  display: flex;
  align-items: flex-end;
  margin-bottom: 24rpx;
}

.zone-index {
  font-size: 24rpx;
  color: rgba(212, 175, 55, 0.8);
  font-weight: bold;
  letter-spacing: 2rpx;
  margin-right: 16rpx;
  padding-bottom: 6rpx;
}

.zone-title {
  font-size: 42rpx;
  font-weight: 700;
  color: #f0f4f8;
  letter-spacing: 2rpx;
}

/* 图片预留占位符 (16:9比例) */
.image-placeholder {
  width: 100%;
  aspect-ratio: 16 / 9;
  background: linear-gradient(135deg, rgba(30, 60, 114, 0.5) 0%, rgba(11, 21, 40, 0.8) 100%);
  border: 2rpx dashed rgba(212, 175, 55, 0.3);
  border-radius: 16rpx;
  margin-bottom: 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.zone-image {
  width: 100%;
  height: 100%;
}

.placeholder-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: 0.6;
}

.icon-camera {
  font-size: 60rpx;
  margin-bottom: 12rpx;
}

.placeholder-text {
  font-size: 26rpx;
  color: #a0aec0;
  letter-spacing: 1rpx;
}

/* 点位详情 */
.zone-points {
  display: flex;
  flex-direction: column;
  gap: 28rpx;
}

.point-item {
  background: rgba(0, 0, 0, 0.15);
  padding: 24rpx;
  border-radius: 16rpx;
}

.point-name {
  font-size: 34rpx;
  font-weight: 600;
  color: #d4af37;
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.point-dot {
  width: 8rpx;
  height: 24rpx;
  background: #d4af37;
  border-radius: 4rpx;
  margin-right: 16rpx;
}

.point-desc {
  font-size: 30rpx;
  line-height: 1.7;
  color: #a0aec0;
  white-space: pre-line; /* 保留文本中的换行符 */
  text-align: justify;
}
</style>
