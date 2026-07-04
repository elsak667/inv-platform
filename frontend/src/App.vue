<template>
  <el-container style="height: 100vh">
    <el-header class="app-header">
      <div class="logo-area">
        <div class="logo-icon">投</div>
        <span class="logo-text">投资测算平台</span>
      </div>
      <el-menu mode="horizontal" :default-active="$route.path" router class="app-nav">
        <el-menu-item index="/">
          <svg style="width:14px;height:14px;margin-right:6px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          模板选择
        </el-menu-item>
        <el-menu-item index="/records">
          <svg style="width:14px;height:14px;margin-right:6px" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          历史方案
        </el-menu-item>
      </el-menu>
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
  background: linear-gradient(135deg, #0f2b5c, #1a56db);
  padding: 0 32px;
  height: 60px;
  box-shadow: 0 2px 12px rgba(15,43,92,0.3);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 40px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-weight: 700;
  font-size: 16px;
}

.logo-text {
  color: #fff;
  font-size: 17px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.app-nav {
  flex: 1;
  background: transparent;
  border-bottom: none;
}

.app-nav .el-menu-item {
  color: rgba(255,255,255,0.75) !important;
  font-size: 14px;
  height: 60px;
  line-height: 60px;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.app-nav .el-menu-item:hover {
  color: #fff !important;
  background: rgba(255,255,255,0.1) !important;
  border-bottom-color: rgba(255,255,255,0.3) !important;
}

.app-nav .el-menu-item.is-active {
  color: #fff !important;
  border-bottom-color: #fff !important;
  font-weight: 600;
}

.app-main {
  background: #f1f5f9;
  padding: 0;
}
</style>
