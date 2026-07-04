<template>
  <div class="page-container">
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:24px">
      <el-button @click="$router.push('/')" text size="small">
        <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        返回
      </el-button>
      <h2 style="font-size:18px;font-weight:600;color:#1e293b;margin:0">历史方案</h2>
    </div>

    <div class="section-card">
      <el-table :data="records" border stripe style="width:100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="方案名称" header-align="center">
          <template #default="{ row }">
            <span style="font-weight:500;color:#1e293b">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="template_id" label="模板" width="180" align="center" />
        <el-table-column prop="created_at" label="创建时间" width="180" align="center" />
        <el-table-column prop="updated_at" label="更新时间" width="180" align="center" />
        <el-table-column label="操作" width="160" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="load(row)">加载</el-button>
            <el-button type="danger" size="small" plain @click="del(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="records.length === 0" style="text-align:center;padding:40px 0;color:#94a3b8;font-size:14px">
        暂无历史方案
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  data() { return { records: [] } },
  async mounted() { await this.refresh() },
  methods: {
    async refresh() { this.records = await api.listRecords() },
    async load(row) {
      const r = await api.getRecord(row.id)
      sessionStorage.setItem('loadRecord', JSON.stringify(r))
      this.$router.push(`/calc/${row.template_id}`)
    },
    async del(row) {
      await api.deleteRecord(row.id)
      this.$message.success('已删除')
      await this.refresh()
    }
  }
}
</script>
