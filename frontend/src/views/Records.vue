<template>
  <div class="page-container">
    <div class="page-header">
      <el-button @click="$router.push('/')" text size="small">
        <svg style="width:14px;height:14px;margin-right:4px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        返回首页
      </el-button>
      <h2>历史方案</h2>
    </div>

    <div v-if="records.length === 0" class="empty-state">
      <svg style="width:64px;height:64px;color:#cbd5e1;margin-bottom:16px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M8 13h8"/><path d="M8 17h8"/><path d="M10 9h4"/></svg>
      <p>暂无历史方案</p>
      <el-button type="primary" @click="$router.push('/')">去创建方案</el-button>
    </div>

    <div v-else class="records-section">
      <div class="records-header">
        <div class="records-title">
          <svg style="width:18px;height:18px;color:#1a56db;margin-right:8px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          已保存 {{ records.length }} 个方案
        </div>
      </div>
      <div style="padding:4px">
        <el-table :data="records" stripe size="small"
          :header-cell-style="{ background:'#f8fafc', color:'#334155', fontWeight:600 }"
          :cell-style="{ padding:'12px 4px' }"
          style="width:100%">
          <el-table-column prop="id" label="ID" width="60" align="center">
            <template #default="{ row }">
              <span style="font-family:monospace;font-size:12px;color:#64748b">#{{ row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="name" label="方案名称">
            <template #default="{ row }">
              <span style="font-weight:500;color:#1e293b">{{ row.name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="template_id" label="模板" width="200" align="center">
            <template #default="{ row }">
              <span style="font-size:12px;color:#64748b">{{ row.template_name || row.template_id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180" align="center">
            <template #default="{ row }">
              <span style="font-size:12px;color:#64748b">{{ fmtDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180" align="center">
            <template #default="{ row }">
              <span style="font-size:12px;color:#64748b">{{ fmtDate(row.updated_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" align="center">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="load(row)">加载</el-button>
              <el-button type="danger" size="small" plain @click="del(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
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
    fmtDate(s) {
      if (!s) return '-'
      try { return new Date(s).toLocaleString('zh-CN', { hour12: false }) } catch { return s }
    },
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

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 28px;
}

.page-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: #fff;
  border-radius: 14px;
  border: 1px solid #f1f5f9;
  box-shadow: 0 1px 3px rgba(15,43,92,0.06);
}

.empty-state p {
  color: #94a3b8;
  font-size: 14px;
  margin: 0 0 24px;
}

.records-section {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(15,43,92,0.06);
  border: 1px solid #f1f5f9;
  overflow: hidden;
}

.records-header {
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}

.records-title {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}
</style>
