<template>
  <div>
    <div class="page-header">
      <h2>数据概览</h2>
    </div>

    <div class="stat-cards">
      <div class="stat-card" v-for="item in statItems" :key="item.label">
        <div class="stat-card-inner" :style="{ background: item.bg }">
          <div class="stat-icon" :style="{ background: item.iconBg }">
            <el-icon :size="22" color="#fff"><component :is="item.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">{{ item.label }}</div>
            <div class="stat-value">{{ item.prefix }}{{ item.value }}</div>
          </div>
        </div>
      </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
      <el-card>
        <template #header>
          <div style="font-weight: 600; font-size: 15px;">收款进度</div>
        </template>
        <div class="progress-item">
          <div class="progress-label">
            <span>已收款</span>
            <span style="color: var(--success); font-weight: 600;">¥{{ formatMoney(stats.paid_amount) }}</span>
          </div>
          <el-progress :percentage="paidPercent" :stroke-width="10" :color="'#10b981'" :show-text="false" style="margin-bottom: 4px;" />
        </div>
        <div class="progress-item" style="margin-top: 20px;">
          <div class="progress-label">
            <span>待收款</span>
            <span style="color: var(--danger); font-weight: 600;">¥{{ formatMoney(stats.unpaid_amount) }}</span>
          </div>
          <el-progress :percentage="100 - paidPercent" :stroke-width="10" :color="'#ef4444'" :show-text="false" style="margin-bottom: 4px;" />
        </div>
        <div class="progress-item" style="margin-top: 20px;">
          <div class="progress-label">
            <span>已到账提成</span>
            <span style="color: var(--primary); font-weight: 600;">¥{{ formatMoney(stats.paid_commission) }}</span>
          </div>
          <el-progress :percentage="commissionPercent" :stroke-width="10" :color="'#6366f1'" :show-text="false" style="margin-bottom: 4px;" />
        </div>
      </el-card>

      <el-card>
        <template #header>
          <div style="font-weight: 600; font-size: 15px;">项目状态</div>
        </template>
        <div class="status-list">
          <div class="status-item">
            <div class="status-dot" style="background: #6366f1;"></div>
            <span class="status-name">进行中</span>
            <span class="status-count">{{ stats.active_projects }}</span>
          </div>
          <div class="status-item">
            <div class="status-dot" style="background: #10b981;"></div>
            <span class="status-name">已完成</span>
            <span class="status-count">{{ stats.completed_projects }}</span>
          </div>
          <div class="status-item">
            <div class="status-dot" style="background: #94a3b8;"></div>
            <span class="status-name">总项目</span>
            <span class="status-count">{{ stats.total_projects }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Folder, Money, TrendCharts, Coin, Wallet, DocumentChecked, DataLine, PriceTag } from '@element-plus/icons-vue'
import { getProjectStats } from '../api/projects'

const stats = ref({
  total_projects: 0, active_projects: 0, completed_projects: 0,
  total_amount: 0, paid_amount: 0, unpaid_amount: 0,
  total_commission: 0, paid_commission: 0,
})

const paidPercent = computed(() => {
  if (!stats.value.total_amount) return 0
  return Math.round((stats.value.paid_amount / stats.value.total_amount) * 100)
})

const commissionPercent = computed(() => {
  if (!stats.value.total_commission) return 0
  return Math.round((stats.value.paid_commission / stats.value.total_commission) * 100)
})

const statItems = computed(() => [
  { label: '项目总数', value: stats.value.total_projects, prefix: '', icon: Folder,
    bg: 'linear-gradient(135deg, #eff6ff, #dbeafe)', iconBg: 'linear-gradient(135deg, #3b82f6, #6366f1)' },
  { label: '进行中', value: stats.value.active_projects, prefix: '', icon: TrendCharts,
    bg: 'linear-gradient(135deg, #f0fdf4, #dcfce7)', iconBg: 'linear-gradient(135deg, #10b981, #059669)' },
  { label: '总金额', value: formatMoney(stats.value.total_amount), prefix: '¥', icon: Coin,
    bg: 'linear-gradient(135deg, #fffbeb, #fef3c7)', iconBg: 'linear-gradient(135deg, #f59e0b, #d97706)' },
  { label: '已收款', value: formatMoney(stats.value.paid_amount), prefix: '¥', icon: Wallet,
    bg: 'linear-gradient(135deg, #ecfdf5, #d1fae5)', iconBg: 'linear-gradient(135deg, #10b981, #34d399)' },
  { label: '待收款', value: formatMoney(stats.value.unpaid_amount), prefix: '¥', icon: Money,
    bg: 'linear-gradient(135deg, #fef2f2, #fecaca)', iconBg: 'linear-gradient(135deg, #ef4444, #f87171)' },
  { label: '总提成', value: formatMoney(stats.value.total_commission), prefix: '¥', icon: PriceTag,
    bg: 'linear-gradient(135deg, #eef2ff, #e0e7ff)', iconBg: 'linear-gradient(135deg, #6366f1, #818cf8)' },
  { label: '已到账提成', value: formatMoney(stats.value.paid_commission), prefix: '¥', icon: DocumentChecked,
    bg: 'linear-gradient(135deg, #f0fdf4, #bbf7d0)', iconBg: 'linear-gradient(135deg, #22c55e, #16a34a)' },
  { label: '已完成', value: stats.value.completed_projects, prefix: '', icon: DataLine,
    bg: 'linear-gradient(135deg, #f5f3ff, #ede9fe)', iconBg: 'linear-gradient(135deg, #8b5cf6, #a78bfa)' },
])

function formatMoney(val) {
  return (val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadStats() {
  try {
    const res = await getProjectStats()
    stats.value = res.data
  } catch (e) {}
}

onMounted(loadStats)
</script>

<style scoped>
.stat-card {
  border-radius: var(--radius);
  overflow: hidden;
  transition: var(--transition);
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.stat-card-inner {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-radius: var(--radius);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
  font-weight: 500;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.status-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 8px 0;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 10px;
  transition: background 0.2s;
}
.status-item:hover {
  background: #f1f5f9;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-name {
  flex: 1;
  font-size: 14px;
  color: var(--text-secondary);
}

.status-count {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}
</style>
