<template>
  <view class="page">
    <view class="container">
      <view class="header-section">
        <view class="title-cn">谢晋故居纪念馆</view>
        <view class="title-en">XIE JIN FORMER RESIDENCE</view>
      </view>

      <view class="card">
        <view class="section-title">参观导览</view>
        <view class="welcome-text">这里是他创作的大本营，也是他生活最久的家。<br>
            从《女篮五号》到《芙蓉镇》，从《红色娘子军》到《鸦片战争》
            ——60 年导演生涯，36 部电影作品。在这方天地里，谢晋完成了从
            青年导演到一代宗师的蜕变，用镜头记录了一个民族的奋进与沉思。
            推开这扇门，不只是走进一位导演，更是走进一个时代。
        </view>
        <view class="desc-text">
          谢晋故居位于上海市静安区江宁路 83 号江宁大楼 501 室，是谢晋导演在上海定居期间生活与工作的重要场所。在这里，他与无数创作者彻夜长谈，酝酿出一部部撼动时代的经典；在这里，他接待过海内外电影人，见证了中国电影的起承转合。这里，不仅是谢晋的家，更是中国电影的一个舞台。
        </view>
      </view>

      <view class="card">
        <view class="section-title">展厅介绍</view>
        <view class="preface">
          这里，辑录的是谢晋广为流传的部分名言。<br>
            他说：“金杯银杯，不如老百姓的口碑。”<br>
            他说：“我的每一次创作，都是一次生命的燃烧。”<br>
            他说：“艺术家要有赤子之心，要有历史的忧患感。”<br>
            请您在此停留，感受谢晋的温度与厚度
        </view>

        <scroll-view class="zone-list" scroll-x enhanced show-scrollbar="false">
          <view class="zone-item" v-for="zone in zones" :key="zone.name">
            <view class="zone-img-placeholder">{{ zone.placeholder }}</view>
            <view class="zone-info">
              <view class="zone-name">{{ zone.name }}</view>
              <view class="zone-desc">{{ zone.desc }}</view>
              <view class="zone-name">{{ zone.name2 }}</view>
              <view class="zone-desc">{{ zone.desc2 }}</view>
            </view>
          </view>
        </scroll-view>
      </view>

      <view class="card">
        <view class="section-title">参观须知</view>
        <view class="notice-section" v-for="section in noticeList" :key="section.title">
          <view class="notice-title">{{ section.title }}</view>
          <view class="notice-item" v-for="item in section.items" :key="item">
            <text class="notice-dot">•</text>
            <text class="notice-text">{{ item }}</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
const zones = [
  {
    placeholder: '展区一 家庭 | 朋友',
    name: '点位 · 家庭',
    desc: '这里，展现的是谢晋的生活日常。\n他说：“故乡的人民哺育我，我吃故乡的水长大。我是上虞的儿子，我是谢塘的儿子。”\n他说：“我是一只飘扬在天空的风筝，无论飞得多高多远，下面总有一根线牵着，这牵线的地方就是故乡。”\n他说：“每次我拍片回来，阿四总要守候在门口，时间再长，夜再深，他也要等我回来。”\n他说：“我是个严厉而不称职的父亲。”\n请您在此停留，感受谢晋的深情与柔情。\n\n',
    name2: '点位 · 朋友圈',
    desc2: '这里，陈列的是谢晋的师友群——海内外的编剧、演员、作家、艺术家。谢晋和他的朋友们，彼此激发，创造了中国电影的一个黄金时代。\n请您在此停留，感受谢晋时代的高原与高峰。'
  },
  {
    placeholder: '展区二 场景 | 创作',
    name: '点位 · 创作现场',
    desc: '书桌前的那副眼镜，仿佛在等主人归来。\n谢晋说：“我们拍一部影片，好像双手捧一碗水，每一步都要聚精会神，严谨认真。”\n从分镜头手稿到导演工作本，从案头笔记到现场调度——这里，还原的是一位伟大的导演如何将故事变成光影，涓涓细流如何汇聚成滚滚江河。\n\n',
    name2: '点位 · 壮志未酬',
    desc2: '戛然而止，有些电影终究没有拍成。\n《大人家》《拉贝日记》《牧马人续集》……\n晚年，他的创作步履从未停歇。一份长长的片单，是他未完成的念想，也是我们永远的遗憾。它们未曾出现在银幕上，却留下了一串串的印迹。'
  },
  {
    placeholder: '展区三 作品与荣誉',
    name: '点位 · 作品',
    desc: '1948 年-2008 年，60 年的创作足迹。\n成名：《女篮五号》《红色娘子军》《大李小李和老李》《舞台姐妹》\n代表：《天云山传奇》《牧马人》《高山下的花环》《芙蓉镇》\n转型：《最后的贵族》《清凉寺的钟声》《鸦片战争》\n每一部作品，都是生命的燃烧；每一个故事，都是时代的回响。\n\n',
    name2: '点位 · 荣誉',
    desc2: '奖杯与证书，是一个导演创造的艺术高度，也是中国电影走向世界的见证。\n但他最珍视的荣誉，永远是观众坐在影院里，为他的电影落泪或沉思的那一刻。'
  }
]

const noticeList = [
  {
    title: '1. 开放时间',
    items: ['每周三、周六 10:00 - 16:00（15:00 前入场）']
  },
  {
    title: '2. 预约入馆',
    items: [
      '个人参观，请通过“个人预约”，实名、分时段提前预约。',
      '现场凭预约码或有效身份证件核验入馆。',
      '团队参观（含 10 人及以上），请通过“团队预约”，提前 5 个工作日预约。'
    ]
  },
  {
    title: '3. 文明公约',
    items: [
      '轻声细语：故居是安静的，请将手机调至静音，勿大声喧哗',
      '尊重展品：请勿触摸或损伤馆内一切展品、展柜',
      '摄影须知：允许非商业用途的拍摄，禁用闪光灯、三脚架及自拍杆',
      '爱护环境：请勿携带宠物（导盲犬除外）、禁烟、禁食、禁携危险品',
      '儿童看护：请家长照看好随行儿童，勿攀爬展台展柜'
    ]
  }
]
</script>

<style lang="scss">
.page {
  min-height: 100vh;
  background: #0b1528;
}

.container {
  padding: 34rpx 22rpx 44rpx;
}

.header-section {
  text-align: center;
  margin-bottom: 28rpx;
}

.title-cn {
  font-size: 54rpx;
  line-height: 1.25;
  font-weight: 700;
  color: #e3d90f;
  letter-spacing: 2rpx;
}

.title-en {
  margin-top: 8rpx;
  font-size: 24rpx;
  line-height: 1.35;
  font-weight: 600;
  color: #c7a23f;
  letter-spacing: 2rpx;
}

.card {
  background: rgba(26, 42, 71, 0.6);
  border: 1rpx solid rgba(212, 175, 55, 0.22);
  border-radius: 24rpx;
  padding: 24rpx 24rpx 26rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10rpx);
}

.section-title {
  position: relative;
  padding-left: 20rpx;
  font-size: 48rpx;
  line-height: 1.25;
  font-weight: 700;
  color: #f0f4f8;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8rpx;
  width: 6rpx;
  height: 36rpx;
  border-radius: 4rpx;
  background: #d4af37;
}

.welcome-text {
  margin-top: 18rpx;
  font-size: 38rpx;
  line-height: 1.45;
  font-weight: 500;
  color: #d4af37;
}

.desc-text {
  margin-top: 12rpx;
  font-size: 38rpx;
  line-height: 1.7;
  color: #a0aec0;
  text-align: justify;
}

.preface {
  margin-top: 18rpx;
  padding: 18rpx;
  border-radius: 14rpx;
  background: rgba(0, 0, 0, 0.2);
  font-size: 34rpx;
  line-height: 1.65;
  color: #a0aec0;
  font-style: italic;
}

.zone-list {
  margin-top: 18rpx;
  white-space: nowrap;
}

.zone-item {
  display: inline-flex;
  vertical-align: top;
  flex-direction: column;
  width: 580rpx;
  margin-right: 18rpx;
  padding: 16rpx;
  border-radius: 18rpx;
  background: rgba(255, 255, 255, 0.03);
  border: 1rpx solid rgba(255, 255, 255, 0.06);
  box-sizing: border-box;
}

.zone-item:last-child {
  margin-right: 0;
}

.zone-img-placeholder {
  width: 300rpx;
  height: 92rpx;
  border-radius: 12rpx;
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 28rpx;
  line-height: 1;
  margin-bottom: 14rpx;
}

.zone-info {
  margin-top: 14rpx;
}

.zone-name {
  font-size: 42rpx;
  line-height: 1.35;
  color: #f0f4f8;
  font-weight: 700;
}

.zone-desc {
  margin-top: 8rpx;
  font-size: 34rpx;
  line-height: 1.6;
  color: #a0aec0;
  white-space: pre-line;
}

.notice-item {
  margin-top: 16rpx;
  display: flex;
  align-items: flex-start;
}

.notice-section {
  margin-top: 16rpx;
}

.notice-title {
  font-size: 38rpx;
  line-height: 1.5;
  color: #f0f4f8;
  font-weight: 600;
}

.notice-dot {
  color: #d4af37;
  font-size: 42rpx;
  line-height: 1.3;
  margin-right: 10rpx;
}

.notice-text {
  flex: 1;
  font-size: 36rpx;
  line-height: 1.7;
  color: #a0aec0;
}
</style>
