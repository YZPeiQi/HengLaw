<template>
  <div class="home-page">
    <TopNavBar />

    <main>
      <section class="hero">
        <div class="hero-content">
          <p class="eyebrow">AI DRIVEN LEGAL OPERATIONS</p>
          <h2>让法律服务进入<br />高可信、可追溯、可量化的新时代</h2>
          <p class="hero-description">
            面向律所、法务团队与企业经营者，LawIntelEmpower 提供从咨询、检索到审查与文书生成的一体化法律智能工作台。
          </p>
          <div class="hero-cta">
            <router-link to="/consultation" class="action-btn">立即开始咨询</router-link>
            <router-link to="/case-search" class="action-btn secondary">查看案例库</router-link>
          </div>
        </div>
        <aside class="hero-panel">
          <p class="panel-title">案件推进看板</p>
          <div class="panel-row">
            <span>合同风险扫描</span>
            <strong>97%</strong>
          </div>
          <div class="panel-row">
            <span>类案命中效率</span>
            <strong>2.1x</strong>
          </div>
          <div class="panel-row">
            <span>文书草拟耗时</span>
            <strong>-65%</strong>
          </div>
          <p class="panel-note">* 数据示意，指标可按团队流程自定义。</p>
        </aside>
      </section>

      <section class="feature-ribbon">
        <article v-for="item in highlightItems" :key="item.title" class="ribbon-card">
          <p class="ribbon-title">{{ item.title }}</p>
          <p class="ribbon-value">{{ item.value }}</p>
          <p class="ribbon-desc">{{ item.desc }}</p>
        </article>
      </section>

      <section class="services fullbleed-slider">
        <div class="section-heading">
          <p>核心能力</p>
          <h3>覆盖法律业务主路径</h3>
        </div>
        <div class="slider-wrapper">
          <button class="slider-arrow prev-arrow" @click="prevSlide">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>

          <div class="slider-window">
            <div 
              class="service-slider-track"
              :style="{
                transform: `translateX(calc(-${virtualIndex} * (80vw + 24px)))`,
                transition: isTransitioning ? 'transform 0.4s ease-in-out' : 'none'
              }"
              @transitionend="handleTransitionEnd"
            >
              <template v-for="group in [0, 1, 2]" :key="group">
                <article
                  v-for="(service, index) in services"
                  :key="`${group}-${service.title}`"
                  class="full-slide"
                  :class="`slide-bg-${index}`"
                >
                  <div class="slide-content">
                    <p class="service-index">{{ service.index }}</p>
                    <h4>{{ service.title }}</h4>
                    <p>{{ service.desc }}</p>
                    <button class="slide-jump-btn" @click="$router.push(service.path)">进入模块</button>
                  </div>
                </article>
              </template>
            </div>
          </div>

          <button class="slider-arrow next-arrow" @click="nextSlide">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>

        <div class="slider-indicators">
          <div
            v-for="(_, index) in services"
            :key="index"
            class="indicator-dot"
            :class="{ active: activeSlide === index }"
            @click="scrollToSlide(index)"
          ></div>
        </div>
      </section>

      <section class="workflow">
        <div class="section-heading">
          <p>工作流</p>
          <h3>从问题输入到行动闭环</h3>
        </div>
        <div class="workflow-steps">
          <div v-for="step in workflow" :key="step.title" class="step-item">
            <span class="step-no">{{ step.no }}</span>
            <h4>{{ step.title }}</h4>
            <p>{{ step.desc }}</p>
          </div>
        </div>
      </section>

      <section class="domains">
        <div class="section-heading">
          <p>服务领域</p>
          <h3>面向多类型法律场景</h3>
        </div>
        <div class="domain-tags">
          <span v-for="tag in domainTags" :key="tag" class="glass-tag">{{ tag }}</span>
        </div>
      </section>

      <section class="trust-metrics dashboard-layout">
        <!-- 顶部 4个 Kpi 卡片 -->
        <div class="dashboard-kpi-row">
          <div class="kpi-card glass-panel">
            <div class="kpi-header" style="position: relative;">
              <span class="kpi-title">总分析案件</span>
              <span class="kpi-icon" @click.stop="activeInfo = activeInfo === 'total' ? null : 'total'" :class="{ 'icon-active': activeInfo === 'total' }">ℹ</span>
              <transition name="fade-down">
                <div v-if="activeInfo === 'total'" class="info-tooltip">
                  累计所有处理完毕及正在处理的案件总数。记录历史总处理承载量。
                </div>
              </transition>
            </div>
            <div class="kpi-num">12,560</div>
            <div class="kpi-compare">
              <span>周同比 <strong>12% ▲</strong></span>
              <span>日同比 <strong>11% ▼</strong></span>
            </div>
            <div class="kpi-footer">日均分析量 234</div>
          </div>
          <div class="kpi-card glass-panel">
            <div class="kpi-header" style="position: relative;">
              <span class="kpi-title">系统日访问量</span>
              <span class="kpi-icon" @click.stop="activeInfo = activeInfo === 'visits' ? null : 'visits'" :class="{ 'icon-active': activeInfo === 'visits' }">ℹ</span>
              <transition name="fade-down">
                <div v-if="activeInfo === 'visits'" class="info-tooltip">
                  今日访问各个法律服务功能入口的独立用户访问量（UV）统计。
                </div>
              </transition>
            </div>
            <div class="kpi-num">8,846</div>
            <div class="kpi-chart">
              <svg viewBox="0 0 100 30" class="mini-chart">
                <path d="M0,30 L0,20 Q10,25 20,15 T40,25 T60,5 T80,15 T100,5 L100,30 Z" fill="#8d72df" opacity="0.8"/>
              </svg>
            </div>
            <div class="kpi-footer">日访问量 1,234</div>
          </div>
          <div class="kpi-card glass-panel">
            <div class="kpi-header" style="position: relative;">
              <span class="kpi-title">生成文书数</span>
              <span class="kpi-icon" @click.stop="activeInfo = activeInfo === 'docs' ? null : 'docs'" :class="{ 'icon-active': activeInfo === 'docs' }">ℹ</span>
              <transition name="fade-down">
                <div v-if="activeInfo === 'docs'" class="info-tooltip">
                  智能体本周已自动生成的起诉状、答辩状、合同协议等结构化文书数量。
                </div>
              </transition>
            </div>
            <div class="kpi-num">6,560</div>
            <div class="kpi-chart bar-chart">
              <div class="bar" style="height: 40%"></div>
              <div class="bar" style="height: 70%"></div>
              <div class="bar" style="height: 30%"></div>
              <div class="bar" style="height: 90%"></div>
              <div class="bar" style="height: 60%"></div>
              <div class="bar" style="height: 80%"></div>
              <div class="bar" style="height: 100%"></div>
              <div class="bar" style="height: 50%"></div>
            </div>
            <div class="kpi-footer">转化率 60%</div>
          </div>
          <div class="kpi-card glass-panel">
            <div class="kpi-header" style="position: relative;">
              <span class="kpi-title">成功合规率</span>
              <span class="kpi-icon" @click.stop="activeInfo = activeInfo === 'compliance' ? null : 'compliance'" :class="{ 'icon-active': activeInfo === 'compliance' }">ℹ</span>
              <transition name="fade-down">
                <div v-if="activeInfo === 'compliance'" class="info-tooltip">
                  完成初步合规审查并且未发现重大致命风险阻断点的案例占比率。
                </div>
              </transition>
            </div>
            <div class="kpi-num">98%</div>
            <div class="kpi-chart progress-chart">
              <div class="progress-track">
                <div class="progress-fill" style="width: 98%"></div>
              </div>
            </div>
            <div class="kpi-compare">
              <span>周同比 <strong>1% ▲</strong></span>
              <span>日同比 <strong>0% -</strong></span>
            </div>
          </div>
        </div>

        <!-- 底部大面板：趋势与排名 -->
        <div class="dashboard-main glass-panel">
          <div class="main-header">
            <div class="main-tabs">
              <span :class="{ active: activeMainTab === '案源趋势' }" @click="activeMainTab = '案源趋势'">案源趋势</span>
              <span :class="{ active: activeMainTab === '访问量' }" @click="activeMainTab = '访问量'">访问量</span>
            </div>
            <div class="main-filters">
              <span :class="{ active: activeMainFilter === '今日' }" @click="activeMainFilter = '今日'">今日</span>
              <span :class="{ active: activeMainFilter === '本周' }" @click="activeMainFilter = '本周'">本周</span>
              <span :class="{ active: activeMainFilter === '本月' }" @click="activeMainFilter = '本月'">本月</span>
              <span :class="{ active: activeMainFilter === '全年' }" @click="activeMainFilter = '全年'">全年</span>
            </div>
          </div>
          <div class="main-body">
            <div class="chart-section">
              <h4 class="section-title">{{ activeMainTab }}评测</h4>
              <div class="css-bar-chart">
                <div class="chart-col" v-for="(item, idx) in chartData" :key="idx">
                  <div class="chart-bar" :style="{ height: item.percent + '%' }"></div>
                  <span>{{ item.label }}</span>
                </div>
              </div>
            </div>
            <div class="rank-section">
              <h4 class="section-title">分所/团队 {{ activeMainTab }}排名</h4>
              <div class="rank-list">
                <div class="rank-item" v-for="(item, idx) in rankData" :key="idx">
                  <span class="rank-badge" :class="{ top3: idx < 3 }">{{ idx + 1 }}</span>
                  <span class="rank-name">{{ item.name }}</span>
                  <span class="rank-val">{{ item.value.toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <footer class="footer glass-footer">
      <p>法研智谱 · 法律智能体平台</p>
      <p>© 2026 All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import TopNavBar from '@/components/TopNavBar.vue'
import { ref, computed } from 'vue'

const virtualIndex = ref(4) // 开始时设在中间组（对应 services.length: 4）
const isTransitioning = ref(false)
let isLocked = false

// Dashboard 交互状态
const activeInfo = ref<string | null>(null)
const activeMainTab = ref('案源趋势')
const activeMainFilter = ref('今日')

const chartData = computed(() => {
  const isTraffic = activeMainTab.value === '访问量';
  const multiplier = activeMainFilter.value === '今日' ? 1 
                   : activeMainFilter.value === '本周' ? 7 
                   : activeMainFilter.value === '本月' ? 30 
                   : 365;

  return [
    { label: '1月', percent: isTraffic ? 30 + (multiplier % 10) : 60 + (multiplier % 25) },
    { label: '2月', percent: isTraffic ? 45 + (multiplier % 15) : 50 + (multiplier % 20) },
    { label: '3月', percent: isTraffic ? 60 + (multiplier % 10) : 20 + (multiplier % 15) },
    { label: '4月', percent: isTraffic ? 80 + (multiplier % 5) : 50 + (multiplier % 10) },
    { label: '5月', percent: isTraffic ? 90 + (multiplier % 3) : 10 + (multiplier % 20) },
    { label: '6月', percent: isTraffic ? 75 + (multiplier % 12) : 30 + (multiplier % 15) },
    { label: '7月', percent: isTraffic ? 55 + (multiplier % 15) : 65 + (multiplier % 10) },
    { label: '8月', percent: isTraffic ? 40 + (multiplier % 20) : 40 + (multiplier % 25) },
    { label: '9月', percent: isTraffic ? 65 + (multiplier % 8) : 50 + (multiplier % 15) },
    { label: '10月', percent: isTraffic ? 85 + (multiplier % 5) : 75 + (multiplier % 10) },
    { label: '11月', percent: isTraffic ? 50 + (multiplier % 10) : 25 + (multiplier % 20) },
    { label: '12月', percent: isTraffic ? 70 + (multiplier % 5) : 45 + (multiplier % 20) },
  ];
})

const rankData = computed(() => {
  const isTraffic = activeMainTab.value === '访问量';
  const multiplier = activeMainFilter.value === '今日' ? 1 
                   : activeMainFilter.value === '本周' ? 7 
                   : activeMainFilter.value === '本月' ? 30 
                   : 365;
  const baseData = isTraffic ? [
    { name: '网页端入口', value: 87654 },
    { name: '移动端App', value: 65432 },
    { name: '微信小程序', value: 43210 },
    { name: '第三方引流', value: 32109 },
    { name: '搜索引擎', value: 21098 },
    { name: '线下推广', value: 10987 },
    { name: '其他渠道', value: 9876 },
  ] : [
    { name: '北京总所', value: 323234 },
    { name: '上海分所', value: 312345 },
    { name: '深圳分所', value: 298765 },
    { name: '广州分所', value: 287654 },
    { name: '杭州分所', value: 276543 },
    { name: '成都分所', value: 265432 },
    { name: '重庆合伙团队', value: 254321 },
  ];
  return baseData.map(item => ({ ...item, value: Math.floor(item.value * multiplier * (0.9 + Math.random() * 0.2)) }));
})

// 每次操作后，动态计算真实高亮的圆点
const activeSlide = computed(() => {
  const N = services.length
  return ((virtualIndex.value % N) + N) % N
})

const handleTransitionEnd = () => {
  const N = services.length
  if (virtualIndex.value < N) {
    isTransitioning.value = false
    virtualIndex.value += N
  } else if (virtualIndex.value >= N * 2) {
    isTransitioning.value = false
    virtualIndex.value -= N
  }
  
  // 延迟解锁以允许在无动画状态下完成重绘
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      isLocked = false
    })
  })
}

const prevSlide = () => {
  if (isLocked) return
  isLocked = true
  isTransitioning.value = true
  virtualIndex.value--
}

const nextSlide = () => {
  if (isLocked) return
  isLocked = true
  isTransitioning.value = true
  virtualIndex.value++
}

const scrollToSlide = (index: number) => {
  if (isLocked || index === activeSlide.value) return
  isLocked = true
  const diff = index - activeSlide.value
  isTransitioning.value = true
  virtualIndex.value += diff
}

const highlightItems = [
  {
    title: '响应时效',
    value: '24/7',
    desc: '全天候法律问答接入'
  },
  {
    title: '审查深度',
    value: 'Clause-Level',
    desc: '逐条款风险标注与建议'
  },
  {
    title: '检索覆盖',
    value: '多维类案',
    desc: '结合争议焦点与裁判逻辑'
  }
]

const services = [
  {
    index: '01',
    title: '法律咨询',
    desc: '输入事实与诉求，快速获得结构化应对建议与法规依据。',
    path: '/consultation'
  },
  {
    index: '02',
    title: '案例检索',
    desc: '按争议点、法院层级与案由筛选，定位高相关裁判参考。',
    path: '/case-search'
  },
  {
    index: '03',
    title: '合同审查',
    desc: '自动识别关键风险条款，输出可落地的修订建议。',
    path: '/contract-review'
  },
  {
    index: '04',
    title: '文书生成',
    desc: '基于案情与主张一键生成诉讼文书，提高交付效率。',
    path: '/document-generate'
  },
]

const workflow = [
  {
    no: 'STEP 1',
    title: '事实输入',
    desc: '上传材料并明确目标，系统自动提炼争议焦点。'
  },
  {
    no: 'STEP 2',
    title: '智能推演',
    desc: '匹配法律规则与类案路径，形成可解释分析链。'
  },
  {
    no: 'STEP 3',
    title: '结果交付',
    desc: '输出咨询建议、审查意见与文书草案，支持团队协同。'
  }
]

const domainTags = [
  '公司治理',
  '劳动人事',
  '建设工程',
  '知识产权',
  '跨境合规',
  '数据与隐私',
  '争议解决',
  '投融资法律',
  '婚姻家事',
  '侵权责任'
]
</script>

<style scoped>
.home-page {
  position: relative;
  min-height: 100vh;
  color: #eef4fc;
  background:
    linear-gradient(120deg, rgba(181, 141, 69, 0.14), rgba(181, 141, 69, 0) 38%),
    radial-gradient(circle at 80% 0, rgba(255, 255, 255, 0.08), transparent 42%),
    linear-gradient(145deg, #061526 0%, #0e263d 48%, #183654 100%);
  overflow-x: hidden;
}

.glow-effect {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 1;
}

/* 统一的毛玻璃特效 */
.glass-panel {
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
}

main {
  position: relative;
  z-index: 2;
  width: min(1200px, calc(100% - 2.5rem));
  margin: 0 auto;
  padding: clamp(2rem, 4vw, 4rem) 0 3rem;
}

.hero {
  display: grid;
  grid-template-columns: 1.35fr 0.9fr;
  gap: 1.2rem;
  margin-bottom: 1.4rem;
}

.hero-content,
.hero-panel {
  border-radius: 1.4rem;
  /* 加上毛玻璃特效 */
  background: rgba(20, 25, 38, 0.4);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.16);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.26);
  transition: transform 0.3s ease, border-color 0.3s ease;
}

.hero-content:hover,
.hero-panel:hover {
  border-color: rgba(214, 185, 121, 0.4);
}

.hero-content {
  padding: clamp(1.6rem, 3vw, 3rem);
  animation: rise-in 0.9s ease both;
}

.eyebrow {
  font-size: 0.82rem;
  letter-spacing: 0.26rem;
  color: #d6b979;
  margin-bottom: 1rem;
}

.hero-content h2 {
  margin: 0;
  font-family: 'Cormorant Garamond', Georgia, serif;
  line-height: 1.1;
  font-size: clamp(2.1rem, 4.6vw, 4rem);
  text-wrap: balance;
}

.hero-description {
  margin-top: 1.1rem;
  max-width: 46ch;
  color: rgba(238, 244, 252, 0.82);
  font-size: 1.08rem;
}

.hero-cta {
  margin-top: 1.8rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.85rem;
}

.action-btn {
  border-radius: 999px;
  padding: 0.8rem 1.4rem;
  background: linear-gradient(90deg, #ba9654, #d7bc86);
  border: 1px solid rgba(255, 255, 255, 0.24);
  color: #1a1f29;
  font-weight: 700;
}

.action-btn.secondary {
  background: transparent;
  color: #ecf3fc;
}

.action-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.hero-panel {
  padding: 1.4rem 1.4rem 1rem;
  animation: rise-in 1.1s ease both;
}

.panel-title {
  margin: 0 0 0.8rem;
  font-weight: 700;
  color: #f4e2bb;
}

.panel-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}

.panel-row span {
  color: rgba(238, 244, 252, 0.8);
}

.panel-row strong {
  color: #f5dfaf;
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 1.2rem;
}

.panel-note {
  margin: 0.9rem 0 0;
  color: rgba(238, 244, 252, 0.56);
  font-size: 0.82rem;
}

.feature-ribbon {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.2rem;
}

.ribbon-card {
  border-radius: 1rem;
  padding: 1.5rem;
  background: rgba(25, 32, 45, 0.4);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  animation: rise-in 1s ease both;
}

.ribbon-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  border-color: rgba(214, 185, 121, 0.4);
}

.ribbon-title {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(238, 244, 252, 0.7);
}

.ribbon-value {
  margin: 0.4rem 0;
  font-size: clamp(1.45rem, 2.8vw, 2rem);
  font-family: 'Cormorant Garamond', Georgia, serif;
  color: #f5e3bb;
}

.ribbon-desc {
  margin: 0;
  font-size: 0.92rem;
  color: rgba(238, 244, 252, 0.78);
}

.services,
.workflow,
.domains {
  margin-top: 2rem;
}

.section-heading p {
  margin: 0;
  color: #d3b67a;
  letter-spacing: 0.2rem;
  font-size: 0.8rem;
  text-transform: uppercase;
}

.section-heading h3 {
  margin: 0.3rem 0 1rem;
  font-size: clamp(1.55rem, 3vw, 2.4rem);
  font-family: 'Cormorant Garamond', Georgia, serif;
}

.fullbleed-slider {
  width: 100vw;
  position: relative;
  left: 50%;
  right: 50%;
  margin-left: -50vw;
  margin-right: -50vw;
  overflow: hidden;
  padding: 0 0 5rem 0; /* 底部留空间给指示器 */
}

.fullbleed-slider .section-heading {
  position: relative;
  z-index: 10;
  text-align: center;
  margin-top: 2rem;
  margin-bottom: 3rem;
}

.slider-wrapper {
  position: relative;
  width: 100vw;
  display: flex;
  align-items: center;
  margin-top: 0;
}

.slider-window {
  width: 100vw;
  overflow: hidden;
}

.service-slider-track {
  display: flex;
  width: max-content;
  gap: 24px;
  padding: 0 10vw; /* 保证第一个和最后一个居中 */
}

/* Arrows */
.slider-arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 20;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  width: 54px;
  height: 54px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(8px);
}

.slider-arrow:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-50%) scale(1.05);
}

.prev-arrow { left: 2vw; }
.next-arrow { right: 2vw; }

/* Indicators */
.slider-indicators {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 12px;
  z-index: 20;
}

.indicator-dot {
  width: 32px;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  cursor: pointer;
  transition: background 0.3s, width 0.3s;
}

.indicator-dot:hover {
  background: rgba(255, 255, 255, 0.6);
}

.indicator-dot.active {
  background: #d6b979;
  width: 56px;
}

.full-slide {
  flex: 0 0 80vw;
  width: 80vw;
  height: min(85vh, 650px);
  border-radius: 1.5rem;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: transform 0.4s ease, opacity 0.4s ease;
}

.slide-content {
  max-width: 600px;
  text-align: center;
  padding: 2rem;
  background: rgba(10, 15, 26, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  transform: translateY(20px);
  opacity: 0;
  animation: slide-up-fade 0.8s ease forwards 0.2s;
}

@keyframes slide-up-fade {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-bg-0 { background: linear-gradient(135deg, #1a2a40, #0d1624); }
.slide-bg-1 { background: linear-gradient(135deg, #2c3a50, #162436); }
.slide-bg-2 { background: linear-gradient(135deg, #382c40, #1f162a); }
.slide-bg-3 { background: linear-gradient(135deg, #2c423f, #152422); }
.slide-bg-4 { background: linear-gradient(135deg, #403225, #241a12); }

.service-index {
  margin: 0;
  color: rgba(214, 185, 121, 0.92);
  font-size: 1.2rem;
  letter-spacing: 0.15rem;
  margin-bottom: 0.5rem;
}

.full-slide h4 {
  margin: 0 0 1rem;
  font-size: 2.2rem;
  color: #fff;
}

.full-slide p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 2rem;
}

.slide-jump-btn {
  background: #d6b979;
  color: #0d1624;
  border: none;
  padding: 12px 30px;
  border-radius: 999px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.slide-jump-btn:hover {
  background: #f1cf89;
  transform: scale(1.05);
  box-shadow: 0 0 15px rgba(214, 185, 121, 0.4);
}

.workflow-steps {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.step-item {
  border-radius: 1rem;
  padding: 1.1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: linear-gradient(140deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.03));
}

.step-no {
  font-size: 0.8rem;
  color: #d7bc86;
  letter-spacing: 0.1rem;
}

.step-item h4 {
  margin: 0.4rem 0;
  font-size: 1.1rem;
}

.step-item p {
  margin: 0;
  color: rgba(238, 244, 252, 0.8);
}

.domain-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
}

.domain-tags span {
  border-radius: 999px;
  padding: 0.48rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #eff4fb;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.domain-tags span:hover {
  background: rgba(214, 185, 121, 0.15);
  border-color: rgba(214, 185, 121, 0.6);
  color: #fff;
  transform: translateY(-2px);
}

/* Dashboard 样式 */
.dashboard-layout {
  margin-top: 5rem;
  margin-bottom: 5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 顶栏 KPI 的 4 张小卡片 */
.dashboard-kpi-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
}

.kpi-card {
  padding: 1.5rem;
  border-radius: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: rgba(20, 25, 38, 0.4);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.16);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.26);
}

.kpi-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: rgba(238, 244, 252, 0.6);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.kpi-icon {
  width: 18px;
  height: 18px;
  border: 1px solid rgba(238, 244, 252, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.kpi-icon:hover, .kpi-icon.icon-active {
  background: rgba(238, 244, 252, 0.15);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.6);
}

.info-tooltip {
  position: absolute;
  top: 30px;
  right: -5px;
  width: max-content;
  max-width: 250px;
  background: rgba(18, 24, 38, 0.95);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 0.8rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  line-height: 1.5;
  color: rgba(238, 244, 252, 0.9);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
  z-index: 50;
  text-align: left;
}

.fade-down-enter-active,
.fade-down-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-down-enter-from,
.fade-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.kpi-num {
  font-size: 2.2rem;
  font-weight: 500;
  color: #fff;
  margin-bottom: 1rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

.kpi-compare, .kpi-chart {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: rgba(238, 244, 252, 0.7);
  height: 40px; /* 固定高度给微缩图表 */
  align-items: end;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 1rem;
}

.kpi-compare span {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.kpi-compare strong {
  font-weight: normal;
}
.kpi-compare strong:first-child { color: #f5222d; }
.kpi-compare strong:last-child { color: #52c41a; }

.kpi-footer {
  font-size: 0.9rem;
  color: rgba(238, 244, 252, 0.8);
}

.mini-chart {
  width: 100%;
  height: 100%;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
}
.bar-chart .bar {
  flex: 1;
  background-color: #5b8ff9;
  border-radius: 2px 2px 0 0;
}

.progress-chart {
  width: 100%;
  display: flex;
  align-items: center;
  border-bottom: none; /* 特殊点没有底线 */
  margin-bottom: 0;
  padding-bottom: 0;
}
.progress-track {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #13c2c2;
  border-radius: 4px;
}

/* 底栏主面板 */
.dashboard-main {
  border-radius: 1rem;
  padding: 1.5rem;
  background: rgba(20, 25, 38, 0.4);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.16);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.26);
}

.main-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 1rem;
  margin-bottom: 2rem;
}

.main-tabs { display: flex; gap: 2rem; font-size: 1.1rem; }
.main-tabs span {
  cursor: pointer;
  padding-bottom: 1.15rem;
  margin-bottom: -1rem;
  color: rgba(238,244,252,0.6);
}
.main-tabs span.active {
  color: #fff;
  border-bottom: 3px solid #5b8ff9;
}

.main-filters {
  display: flex;
  gap: 1.2rem;
  font-size: 0.95rem;
}
.main-filters span { color: rgba(238,244,252,0.6); cursor: pointer; }
.main-filters span.active { color: #5b8ff9; }

.main-body {
  display: flex;
  gap: 3rem;
  flex-wrap: wrap; /* 处理小屏设备 */
}

.chart-section {
  flex: 2;
  min-width: 400px;
}

.section-title {
  margin: 0 0 1.5rem 0;
  font-size: 1rem;
  font-weight: 500;
  color: rgba(238,244,252,0.9);
}

/* 模拟 CSS 大柱状图 */
.css-bar-chart {
  display: flex;
  align-items: flex-end;
  height: 250px;
  gap: min(2rem, 3vw);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  padding-bottom: 0.5rem;
}

.chart-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
}

.chart-col .chart-bar {
  width: 32px;
  background-color: #5b8ff9;
  border-radius: 4px 4px 0 0;
  transition: height 0.4s ease;
}

.chart-col span {
  margin-top: 0.8rem;
  font-size: 0.85rem;
  color: rgba(238, 244, 252, 0.6);
}

.rank-section {
  flex: 1;
  min-width: 300px;
}

.rank-list {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.rank-badge {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: bold;
}

.rank-badge.top3 {
  background: #314659;
}

.rank-name {
  flex: 1;
  color: rgba(238,244,252,0.9);
  font-size: 0.95rem;
}

.rank-val {
  color: rgba(238,244,252,0.9);
  font-size: 0.95rem;
}

.glass-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(6, 15, 28, 0.6);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  padding: 2.5rem 0;
  text-align: center;
  position: relative;
  z-index: 2;
}

.footer {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.14);
  margin-top: 3rem;
  padding: 1rem clamp(1rem, 3vw, 3rem) 1.3rem;
  color: rgba(238, 244, 252, 0.72);
  font-size: 0.9rem;
}

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1080px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .feature-ribbon {
    grid-template-columns: 1fr;
  }

  .service-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .workflow-steps {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  main {
    width: min(1200px, calc(100% - 1.3rem));
  }

  .hero-content,
  .hero-panel {
    border-radius: 1rem;
  }

  .hero-content h2 {
    font-size: 2rem;
  }

  .service-grid {
    grid-template-columns: 1fr;
  }

  .footer {
    flex-direction: column;
  }
}
</style>
