import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

// 基础防爬: 有 VITE_API_KEY 则自动附带
const key = import.meta.env.VITE_API_KEY
if (key) {
  api.interceptors.request.use(config => {
    config.headers['X-API-Key'] = key
    return config
  })
}

export default {
  listTemplates: () => api.get('/templates').then(r => r.data),
  getTemplate: (id) => api.get(`/templates/${id}`).then(r => r.data),
  calculate: (templateId, params, planId) =>
    api.post('/calculate', { template_id: templateId, params, plan_id: planId }).then(r => r.data),
  saveRecord: (name, templateId, params, results) =>
    api.post('/records', { name, template_id: templateId, params, results }).then(r => r.data),
  listRecords: (templateId) =>
    api.get('/records', { params: { template_id: templateId } }).then(r => r.data),
  getRecord: (id) => api.get(`/records/${id}`).then(r => r.data),
  deleteRecord: (id) => api.delete(`/records/${id}`).then(r => r.data),
  generateReport: (templateId, params, mode) =>
    api.post(`/report/${templateId}`, { params, mode }).then(r => r.data),
  exportXlsx: (templateId, params, recordId) =>
    api.post(`/export/${templateId}`, { params, record_id: recordId }, { responseType: 'blob' }).then(r => r.data),
}
