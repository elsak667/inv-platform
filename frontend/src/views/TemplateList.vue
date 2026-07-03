<template>
  <div>
    <h2>选择测算模板</h2>
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col v-for="t in templates" :key="t.id" :span="8">
        <el-card @click="$router.push(`/calc/${t.id}`)" style="cursor: pointer">
          <h3>{{ t.name }}</h3>
          <p style="color: #888; font-size: 13px">{{ t.description }}</p>
          <el-tag>v{{ t.version }}</el-tag>
        </el-card>
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