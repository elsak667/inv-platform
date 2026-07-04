<template>
  <div class="page-container">
    <div class="hero">
      <h1>投资测算平台</h1>
      <p>模板驱动的投资分析 · 快速测算 · 多方案对比 · 自动生成汇报材料</p>
      <div class="hero-stats">
        <div class="hero-stat">
          <div class="hero-stat-num">{{ templates.length }}</div>
          <div class="hero-stat-label">测算模板</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-num">4+</div>
          <div class="hero-stat-label">还款方式</div>
        </div>
        <div class="hero-stat">
          <div class="hero-stat-num">AI</div>
          <div class="hero-stat-label">报告生成</div>
        </div>
      </div>
    </div>

    <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px">
      <span style="width:4px;height:16px;background:linear-gradient(180deg,#1a56db,#3b82f6);border-radius:2px"></span>
      <span style="font-size:16px;font-weight:600;color:#1e293b">选择测算模板</span>
    </div>

    <el-row :gutter="20">
      <el-col v-for="t in templates" :key="t.id" :xs="24" :sm="12" :md="8">
        <div class="template-card" @click="$router.push(`/calc/${t.id}`)">
          <div class="icon-wrap">📋</div>
          <h3>{{ t.name }}</h3>
          <p>{{ t.description }}</p>
          <div style="display:flex;gap:8px;align-items:center;justify-content:space-between">
            <span class="cta">开始测算 →</span>
            <el-tag size="small" type="info" effect="plain">v{{ t.version }}</el-tag>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  data() {
    return { templates: [] }
  },
  async mounted() {
    this.templates = await api.listTemplates()
  }
}
</script>
