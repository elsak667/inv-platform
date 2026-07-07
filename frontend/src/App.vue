<template>
  <el-container style="height: 100vh">
    <el-header class="app-header">
      <div class="logo-area" @click="$router.push('/')">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px">
            <path d="M3 3v18h18"/>
            <path d="M7 14l3-3 3 3 5-5"/>
            <circle cx="19" cy="9" r="1.5" fill="currentColor"/>
          </svg>
        </div>
        <div class="logo-text-wrap">
          <span class="logo-text">投资测算平台</span>
          <span class="logo-sub">Investment Calculator</span>
        </div>
      </div>
      <nav class="app-nav">
        <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
          <svg style="width:15px;height:15px;margin-right:6px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
          </svg>
          模板选择
        </router-link>
        <router-link to="/records" class="nav-item" :class="{ active: $route.path === '/records' }">
          <svg style="width:15px;height:15px;margin-right:6px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          历史方案
        </router-link>
      </nav>
      <div class="header-right">
        <span class="env-badge">v1.0</span>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #0f2b5c 0%, #1a56db 100%);
  padding: 0 32px;
  height: 64px;
  box-shadow: 0 2px 16px rgba(15,43,92,0.25);
  position: relative;
  z-index: 10;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 48px;
  cursor: pointer;
}

.logo-icon {
  width: 38px;
  height: 38px;
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  backdrop-filter: blur(4px);
}

.logo-text-wrap {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.logo-text {
  color: #fff;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.logo-sub {
  color: rgba(255,255,255,0.6);
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.app-nav {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  color: rgba(255,255,255,0.75);
  font-size: 14px;
  height: 64px;
  display: inline-flex;
  align-items: center;
  padding: 0 18px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255,255,255,0.08);
  border-bottom-color: rgba(255,255,255,0.3);
}

.nav-item.active {
  color: #fff;
  border-bottom-color: #fff;
  font-weight: 600;
}

.header-right {
  margin-left: 16px;
}

.env-badge {
  color: rgba(255,255,255,0.7);
  font-size: 11px;
  padding: 4px 10px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 12px;
  letter-spacing: 0.5px;
}

.app-main {
  background: var(--bg);
  padding: 0;
}
</style>
