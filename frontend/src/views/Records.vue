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
        <div class="plain-table-wrap">
          <table class="plain-table">
            <thead><tr>
              <th style="width:60px">ID</th><th>方案名称</th><th style="width:200px">模板</th><th style="width:180px">创建时间</th><th style="width:180px">更新时间</th><th style="width:200px">操作</th>
            </tr></thead>
            <tbody>
              <tr v-for="r in records" :key="r.id">
                <td><span style="font-family:monospace;color:#64748b">#{{ r.id }}</span></td>
                <td style="font-weight:500;color:#1e293b;text-align:left;padding-left:14px">{{ r.name }}</td>
                <td>{{ r.template_name || r.template_id }}</td>
                <td>{{ fmtDate(r.created_at) }}</td>
                <td>{{ fmtDate(r.updated_at) }}</td>
                <td>
                  <el-button type="primary" size="small" @click="load(r)">加载</el-button>
                  <el-button type="success" size="small" plain @click="exportXlsx(r)" :loading="exportingId === r.id" :disabled="r.template_id !== 'zulin'">导出</el-button>
                  <el-button type="danger" size="small" plain @click="del(r)">删除</el-button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index.js'

export default {
  data() { return { records: [], exportingId: null } },
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
    },
    async exportXlsx(row) {
      this.exportingId = row.id
      try {
        const blob = await api.exportXlsx(row.template_id, null, row.id)
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `${row.name}_测算表.xlsx`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        this.$message.success('导出成功')
      } catch (e) {
        console.error('[export]', e)
        this.$message.error('导出失败: ' + (e.message || String(e)))
      }
      this.exportingId = null
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
.plain-table-wrap { overflow-x:auto; }
.plain-table { width:100%; border-collapse:collapse; font-size:13px; }
.plain-table th { background:#f8fafc; color:#64748b; font-weight:600; padding:12px 8px; text-align:center; border-bottom:1px solid #e2e8f0; }
.plain-table td { padding:10px 8px; text-align:center; border-bottom:1px solid #f1f5f9; }
.plain-table tbody tr:hover { background:#f8fafc; }
</style>
