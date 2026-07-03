<template>
  <el-container style="height: 100vh">
    <el-header style="border-bottom: 1px solid #eee; display: flex; align-items: center">
      <h2 style="margin: 0; font-size: 18px">投资测算平台</h2>
      <el-menu mode="horizontal" style="flex: 1; border: none" :default-active="$route.path" router>
        <el-menu-item index="/">模板选择</el-menu-item>
        <el-menu-item index="/records">历史方案</el-menu-item>
      </el-menu>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>