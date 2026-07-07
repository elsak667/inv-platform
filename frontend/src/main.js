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
})
window.addEventListener('unhandledrejection', e => {
  console.error('[unhandled]', e.reason?.stack || e.reason)
})

const origWarn = console.warn
console.warn = (...args) => {
  if (args[0]?.includes?.('non-passive event listener')) return
  origWarn.call(console, ...args)
}

app.use(router)
app.use(ElementPlus)

// Trace component creation to catch which component fails
let compDepth = 0
app.mixin({
  beforeCreate() {
    compDepth++
    const name = this.$options.name || this.$options.__name || '?'
    if (name.startsWith('El')) console.log('[trace]', '  '.repeat(Math.min(compDepth, 10)), name)
  },
  created() {
    compDepth--
    const name = this.$options.name || this.$options.__name || '?'
    if (name === 'ElMenuItem') {
      let p = this.$parent
      const chain = []
      while (p) { chain.push(p.$options.name || '?'); p = p.$parent }
      console.log('[ElMenuItem] parentChain:', chain)
    }
  }
})
try {
  app.mount('#app')
} catch (e) {
  console.error('[mount-error]', e)
}
