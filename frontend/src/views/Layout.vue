<template>
  <el-container style="height: 100vh">
    <el-aside :width="collapsed ? '72px' : '230px'" class="sidebar">
      <div class="sidebar-header">
        <div class="sidebar-logo">
          <el-icon :size="24" color="#fff"><DataAnalysis /></el-icon>
        </div>
        <transition name="fade">
          <span v-if="!collapsed" class="sidebar-title">项目管理</span>
        </transition>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="collapsed"
        router
        background-color="transparent"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#ffffff"
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><FolderOpened /></el-icon>
          <template #title>项目管理</template>
        </el-menu-item>
        <el-menu-item index="/payments">
          <el-icon><Wallet /></el-icon>
          <template #title>汇款管理</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-toggle" @click="collapsed = !collapsed">
        <el-icon :size="16"><DArrowLeft v-if="!collapsed" /><DArrowRight v-else /></el-icon>
      </div>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <div class="topbar-left">
          <span class="topbar-breadcrumb">{{ currentTitle }}</span>
        </div>
        <div class="topbar-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-avatar">
              <div class="avatar-circle">{{ (authStore.user?.username || 'A')[0].toUpperCase() }}</div>
              <span class="user-name">{{ authStore.user?.username || '管理员' }}</span>
              <el-icon :size="12"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { DataAnalysis, Odometer, FolderOpened, Wallet, ArrowDown, SwitchButton, DArrowLeft, DArrowRight } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const collapsed = ref(false)

const titles = { '/dashboard': '仪表盘', '/projects': '项目管理', '/payments': '汇款管理' }
const currentTitle = computed(() => titles[route.path] || '')

function handleCommand(cmd) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.sidebar {
  background: linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  position: relative;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.sidebar-logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

.sidebar-menu {
  flex: 1;
  padding: 12px 8px;
  border: none !important;
}

.sidebar-menu .el-menu-item {
  height: 44px;
  line-height: 44px;
  border-radius: 10px !important;
  margin-bottom: 4px;
  padding-left: 16px !important;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.sidebar-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-menu .el-menu-item.is-active {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #fff !important;
  font-weight: 600;
}

.sidebar-toggle {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  transition: color 0.2s;
}
.sidebar-toggle:hover {
  color: rgba(255, 255, 255, 0.8);
}

.topbar {
  height: 64px !important;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: #fff;
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
}

.topbar-breadcrumb {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 10px;
  transition: background 0.2s;
}
.user-avatar:hover {
  background: #f1f5f9;
}

.avatar-circle {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.main-content {
  background: var(--bg-page);
  padding: 24px 28px;
  overflow-y: auto;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.page-enter-active { animation: pageIn 0.3s ease-out; }
.page-leave-active { animation: pageOut 0.15s ease-in; }

@keyframes pageIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pageOut {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>
