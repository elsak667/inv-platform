import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/global.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import TemplateList from './views/TemplateList.vue'
import Calculator from './views/Calculator.vue'
import KaifaCalculator from './views/KaifaCalculator.vue'
import ZulinCalculator from './views/ZulinCalculator.vue'
import Records from './views/Records.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TemplateList },
    { path: '/calc/kaifa', component: KaifaCalculator },
    { path: '/calc/zulin', component: ZulinCalculator },
    { path: '/calc/:templateId', component: Calculator },
    { path: '/records', component: Records },
  ]
})

const app = createApp(App)
for (const [key, comp] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, comp)
}
app.config.errorHandler = (err, vm, info) => {
  console.error('[Vue-global]', err, info, vm?.$options?.name || vm?.type?.name || '?')
}
window.addEventListener('error', e => {
  if (e.message?.startsWith('ResizeObserver loop')) return
  console.error('[window-error]', e.error?.stack || e.error || e.message)
  // Mark the event as handled so the default handler still shows it
})
window.addEventListener('unhandledrejection', e => {
  console.error('[unhandled]', e.reason?.stack || e.reason)
})
app.use(router)
app.use(ElementPlus)
try {
  app.mount('#app')
} catch (e) {
  console.error('[mount-error]', e)
}
