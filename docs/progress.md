# 投资测算平台 — 开发进度

## 项目概述

以旧换新收购存量房源转保租房投资测算工具。FastAPI 后端 + Vue3 前端，YAML 模板驱动，多方案对比，自动生成分析报告/PPT 大纲。

## 里程碑

### v0.1 — 初始版本（07-03）

- 保租房测算引擎，支持 4 种还款节奏
- 3 个贷款方案对比
- 模板渲染分析报告 + PPT 大纲
- AI 增强报告（NVIDIA GLM-5.2）
- SQLite 存档

### v0.2 — UI 大改 + CI/CD（07-04）

- 深蓝专业风全站 UI 美化
- ECharts 现金流走势图
- CI: GitHub Actions 自动构建前端并部署到 VPS
- 修复若干测算 bug（残值率、折旧、loan_ratio）

## 代码结构

| 目录 | 说明 |
|------|------|
| `backend/main.py` | FastAPI 入口，7 个 API 端点 |
| `engines/` | 引擎注册机制，@engine 装饰器 |
| `engines/baozufang.py` | 保租房测算引擎（442 行，核心逻辑） |
| `services/` | 报告生成、SQLite 存档、计算调度 |
| `templates/baozufang.yaml` | 测算模板（123 行） |
| `frontend/` | Vue3 + Element Plus + ECharts |
| `frontend/src/views/Calculator.vue` | 测算页面（966 行，含全部交互） |

## 已知问题

1. **模板加载失败** — 前端进入测算页时若后端 API 不可达则报错，需要用户确认后端已启动
2. 仅支持一种模板（baozufang），无模板管理功能

## 下一步

待定
