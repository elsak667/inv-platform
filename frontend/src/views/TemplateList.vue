<template>
  <div class="page-container">
    <div class="hero">
      <h1>投资测算平台</h1>
      <p>模板驱动的投资分析——快速测算、多方案对比、自动生成汇报材料</p>
    </div>

    <div style="font-size:15px;font-weight:600;color:#1e293b;margin-bottom:16px">选择测算模板</div>

    <el-row :gutter="20">
      <el-col v-for="t in templates" :key="t.id" :xs="24" :sm="12" :md="8">
        <div class="template-card" @click="$router.push(`/calc/${t.id}`)">
          <div class="icon">📋</div>
          <h3>{{ t.name }}</h3>
          <p>{{ t.description }}</p>
          <div style="display:flex;gap:8px;align-items:center">
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
