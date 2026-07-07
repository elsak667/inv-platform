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

// 显式声明 passive:false 消除 Chrome wheel/mousewheel 合规警告
const _orig = EventTarget.prototype.addEventListener
EventTarget.prototype.addEventListener = function (t, h, o) {
  if ((t === 'wheel' || t === 'mousewheel') && (!o || o.passive === undefined))
    return _orig.call(this, t, h, typeof o === 'object' ? { ...o, passive: false } : { passive: false, capture: !!o })
  return _orig.call(this, t, h, o)
}

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
