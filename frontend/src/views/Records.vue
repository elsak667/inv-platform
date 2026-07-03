<template>
  <div>
    <el-page-header @back="$router.push('/')" content="历史方案" style="margin-bottom: 20px" />
    <el-table :data="records" border>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="方案名称" />
      <el-table-column prop="template_id" label="模板" width="120" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column prop="updated_at" label="更新时间" width="180" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button type="primary" link @click="load(row)">加载</el-button>
          <el-button type="danger" link @click="del(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
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
      // 存 sessionStorage 让 Calculator 页读取
      sessionStorage.setItem('loadRecord', JSON.stringify(r))
      this.$router.push(`/calc/${row.template_id}`)
    },
    async del(row) {
      await api.deleteRecord(row.id)
      await this.refresh()
    }
  }
}
</script>