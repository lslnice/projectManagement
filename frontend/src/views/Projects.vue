<template>
  <div>
    <div class="page-header">
      <h2>项目管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增项目
      </el-button>
    </div>

    <!-- Tab 切换：进行中 / 已完成 -->
    <div class="tab-bar">
      <div class="tab-item" :class="{ active: activeTab === 0 }" @click="switchTab(0)">
        <el-icon><Odometer /></el-icon>
        进行中
        <span class="tab-count" v-if="activeTab === 0">{{ total }}</span>
      </div>
      <div class="tab-item" :class="{ active: activeTab === 1 }" @click="switchTab(1)">
        <el-icon><CircleCheckFilled /></el-icon>
        已完成
        <span class="tab-count completed" v-if="activeTab === 1">{{ total }}</span>
      </div>
    </div>

    <div class="filter-bar" style="border-radius: 0 0 12px 12px; margin-top: 0;">
      <el-input v-model="filters.keyword" placeholder="搜索项目名称 / 订单号" clearable style="width: 260px" @clear="loadData" @keyup.enter="loadData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filters.dev_status" placeholder="开发状态" clearable style="width: 140px" @change="loadData">
        <el-option v-for="s in DEV_STATUSES" :key="s.value" :label="s.label" :value="s.value" />
      </el-select>
      <el-button @click="loadData"><el-icon><RefreshRight /></el-icon> 刷新</el-button>
    </div>

    <div class="table-wrapper" style="margin-top: 12px;">
      <el-table :data="list" v-loading="loading" style="width: 100%"
        :header-cell-style="{ padding: '14px 16px' }" :cell-style="{ padding: '12px 16px' }">

        <el-table-column prop="name" label="项目名称" min-width="150">
          <template #default="{ row }">
            <div class="project-name">
              <div class="project-dot" :style="{ background: devStatusColor(row.dev_status) }"></div>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="开发状态" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" :style="devStatusStyle(row.dev_status)">
              {{ devStatusLabel(row.dev_status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="打款状态" width="200">
          <template #default="{ row }">
            <div class="payment-status-cell">
              <div class="payment-bar-wrap">
                <div class="payment-bar" :style="{ width: paymentPct(row) + '%', background: paymentBarColor(row) }"></div>
              </div>
              <div class="payment-text">
                <span :style="{ color: paymentBarColor(row), fontWeight: 600 }">
                  {{ paymentPctText(row) }}
                </span>
                <span style="color: #94a3b8; font-size: 11px;">¥{{ formatMoney(row.paid_amount) }} / ¥{{ formatMoney(row.total_amount) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="我的提成" width="130">
          <template #default="{ row }">
            <div class="amount-cell">
              <div class="amount-main" style="color: var(--primary);">¥{{ formatMoney(row.total_amount * row.commission_rate) }}</div>
              <div class="amount-sub">
                已到账 <span style="color: #10b981;">¥{{ formatMoney(row.paid_amount * row.commission_rate) }}</span>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="绑定订单号" min-width="180">
          <template #default="{ row }">
            <div class="order-tags" v-if="row.order_nos && row.order_nos.length">
              <el-tag v-for="no in row.order_nos" :key="no" size="small"
                style="font-family: monospace; font-size: 11px; border: none; background: #f1f5f9; color: #475569; margin: 2px;">
                {{ no }}
              </el-tag>
            </div>
            <span v-else style="color: #cbd5e1; font-size: 13px;">未绑定</span>
          </template>
        </el-table-column>

        <el-table-column label="远程接口" min-width="160" align="center">
          <template #default="{ row }">
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px;">
              <el-popover placement="left" :width="420" trigger="click">
                <template #reference>
                  <el-button size="small" plain style="font-size: 12px; border-color: #e0e7ff; color: #6366f1; background: #eef2ff;">
                    <el-icon :size="12"><Link /></el-icon> 查看接口
                  </el-button>
                </template>
                <div class="api-popover">
                  <div class="api-popover-title">远程控制接口地址</div>
                  <div class="api-url-box">
                    <span>{{ remoteUrl(row.id) }}</span>
                    <el-button size="small" text type="primary" @click="copyUrl(row.id)" style="flex-shrink:0;">
                      <el-icon><CopyDocument /></el-icon> 复制
                    </el-button>
                  </div>
                  <div class="api-popover-title" style="margin-top: 14px;">响应示例</div>
                  <div class="api-resp-box">
                    <div class="api-resp-item">
                      <el-tag size="small" style="background:#f0fdf4;color:#10b981;border:none;">开启时</el-tag>
                      <code>{"code": 1000, "data": true, "message": "success"}</code>
                    </div>
                    <div class="api-resp-item" style="margin-top: 8px;">
                      <el-tag size="small" style="background:#fef2f2;color:#ef4444;border:none;">关闭时</el-tag>
                      <code>{"code": 1000, "data": false, "message": "success"}</code>
                    </div>
                  </div>
                  <div class="api-popover-tip">客户端判断 <code>data === false</code> 时关闭系统功能</div>
                </div>
              </el-popover>
              <el-switch v-model="row.remote_status" :active-value="1" :inactive-value="0"
                @change="handleRemoteToggle(row)" size="small" style="--el-switch-on-color: #10b981" />
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="140" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions" style="justify-content: center;">
              <el-button size="small" text type="primary" @click="openDialog(row)">
                <el-icon><Edit /></el-icon> 编辑
              </el-button>
              <el-button size="small" text type="danger" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :total="total"
        :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
        @size-change="loadData" @current-change="loadData" />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑项目' : '新增项目'" width="580px" destroy-on-close>
      <el-form :model="form" label-width="110px" label-position="left">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="总金额" required>
          <el-input-number v-model="form.total_amount" :min="0" :precision="2" :controls="false" style="width: 100%" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="绑定订单号">
          <div class="order-no-input">
            <div class="order-tags-wrap">
              <el-tag v-for="(no, idx) in form.order_nos" :key="no" closable
                @close="form.order_nos.splice(idx, 1)"
                style="font-family: monospace; font-size: 12px; margin: 3px;">{{ no }}</el-tag>
              <span v-if="!form.order_nos.length" style="font-size: 12px; color: #c0c4cc; padding: 0 4px;">暂无绑定，输入后按回车添加</span>
            </div>
            <div style="display: flex; gap: 8px; margin-top: 8px;">
              <el-input v-model="orderNoInput" placeholder="输入订单号" size="small" @keyup.enter="addOrderNo" clearable />
              <el-button size="small" type="primary" plain @click="addOrderNo">添加</el-button>
            </div>
            <div style="font-size: 12px; color: #94a3b8; margin-top: 4px;">可绑定多个订单号，汇款时按订单号自动匹配到本项目</div>
          </div>
        </el-form-item>
        <el-form-item label="提成比例">
          <div style="display: flex; align-items: center; gap: 16px; width: 100%;">
            <el-slider v-model="commissionPct" :min="0" :max="100" style="flex: 1;" />
            <el-tag size="large" style="min-width: 56px; text-align: center; border: none; background: var(--primary-bg); color: var(--primary); font-weight: 600;">{{ commissionPct }}%</el-tag>
          </div>
        </el-form-item>

        <el-divider content-position="left" style="margin: 16px 0;">
          <span style="font-size: 13px; color: #94a3b8;">开发状态</span>
        </el-divider>

        <el-form-item label="开发阶段">
          <div class="dev-status-selector">
            <div v-for="s in DEV_STATUSES" :key="s.value"
              class="dev-status-option"
              :class="{ selected: form.dev_status === s.value }"
              :style="form.dev_status === s.value ? { borderColor: s.color, background: s.bg } : {}"
              @click="form.dev_status = s.value">
              <span class="status-dot" :style="{ background: s.color }"></span>
              <span>{{ s.label }}</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="开发进度">
          <div style="display: flex; align-items: center; gap: 16px; width: 100%;">
            <el-slider v-model="form.progress" :min="0" :max="100" style="flex: 1;"
              :marks="{ 0: '0', 25: '25', 50: '50', 75: '75', 100: '100' }" />
            <el-tag size="large" style="min-width: 56px; text-align: center; border: none; background: #f0fdf4; color: #10b981; font-weight: 600;">{{ form.progress }}%</el-tag>
          </div>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus, Search, RefreshRight, Edit, Delete, Link, CopyDocument, Odometer, CircleCheckFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjects, createProject, updateProject, deleteProject, toggleRemoteStatus } from '../api/projects'

const DEV_STATUSES = [
  { value: 'pending',    label: '待开发', color: '#94a3b8', bg: '#f8fafc' },
  { value: 'developing', label: '开发中', color: '#6366f1', bg: '#eef2ff' },
  { value: 'testing',    label: '测试中', color: '#f59e0b', bg: '#fffbeb' },
  { value: 'delivered',  label: '已交付', color: '#10b981', bg: '#f0fdf4' },
]

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const activeTab = ref(0)  // 0=进行中, 1=已完成
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const filters = reactive({ keyword: '', dev_status: '' })

const form = reactive({
  name: '', total_amount: 0, order_nos: [],
  commission_rate: 0.7, dev_status: 'developing', progress: 0, notes: ''
})
const orderNoInput = ref('')

const commissionPct = computed({
  get: () => Math.round(form.commission_rate * 100),
  set: (val) => { form.commission_rate = val / 100 }
})

function addOrderNo() {
  const val = orderNoInput.value.trim()
  if (!val) return
  if (!form.order_nos.includes(val)) form.order_nos.push(val)
  orderNoInput.value = ''
}

function formatMoney(val) {
  return (val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function paymentPct(row) {
  if (!row.total_amount) return 0
  return Math.min(100, Math.round((row.paid_amount / row.total_amount) * 100))
}
function paymentPctText(row) {
  const p = paymentPct(row)
  if (p === 0) return '未付款'
  if (p >= 100) return '已全款'
  return `已付 ${p}%`
}
function paymentBarColor(row) {
  const p = paymentPct(row)
  if (p >= 100) return '#10b981'
  if (p > 0) return '#f59e0b'
  return '#e2e8f0'
}

function devStatusLabel(v) { return DEV_STATUSES.find(s => s.value === v)?.label || v }
function devStatusColor(v) { return DEV_STATUSES.find(s => s.value === v)?.color || '#94a3b8' }
function devStatusStyle(v) {
  const s = DEV_STATUSES.find(s => s.value === v)
  if (!s) return {}
  return { border: 'none', background: s.bg, color: s.color, fontWeight: 500 }
}

function remoteUrl(id) { return `${location.origin}/api/v1/remote/check/${id}` }
function copyUrl(id) {
  const text = remoteUrl(id)
  // HTTPS 用 Clipboard API，HTTP 降级用 execCommand
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => {
      ElMessage.success('接口地址已复制')
    }).catch(() => fallbackCopy(text))
  } else {
    fallbackCopy(text)
  }
}

function fallbackCopy(text) {
  const el = document.createElement('textarea')
  el.value = text
  el.style.position = 'fixed'
  el.style.opacity = '0'
  document.body.appendChild(el)
  el.select()
  const ok = document.execCommand('copy')
  document.body.removeChild(el)
  ok ? ElMessage.success('接口地址已复制') : ElMessage.error('复制失败，请手动复制')
}

function switchTab(tab) {
  activeTab.value = tab
  page.value = 1
  loadData()
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: page.value, page_size: pageSize.value,
      completed: activeTab.value,
      ...filters
    }
    const res = await getProjects(params)
    list.value = res.data.items
    total.value = res.data.total
  } catch (e) {} finally { loading.value = false }
}

function openDialog(row) {
  orderNoInput.value = ''
  if (row) {
    editingId.value = row.id
    Object.assign(form, {
      name: row.name, total_amount: row.total_amount,
      order_nos: [...(row.order_nos || [])],
      commission_rate: row.commission_rate,
      dev_status: row.dev_status || 'developing',
      progress: row.progress, notes: row.notes || ''
    })
  } else {
    editingId.value = null
    Object.assign(form, {
      name: '', total_amount: 0, order_nos: [],
      commission_rate: 0.7, dev_status: 'developing', progress: 0, notes: ''
    })
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name) return ElMessage.warning('请输入项目名称')
  submitting.value = true
  try {
    if (editingId.value) {
      await updateProject(editingId.value, { ...form })
      ElMessage.success('更新成功')
    } else {
      await createProject({ ...form })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (e) {} finally { submitting.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm(`确定删除项目「${row.name}」？`, '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  })
  try {
    await deleteProject(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {}
}

async function handleRemoteToggle(row) {
  try {
    await toggleRemoteStatus(row.id, row.remote_status)
    ElMessage.success(row.remote_status ? '已开启' : '已关闭')
  } catch (e) { row.remote_status = row.remote_status ? 0 : 1 }
}

onMounted(loadData)
</script>

<style scoped>
.tab-bar {
  display: flex;
  background: #fff;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid var(--border);
  padding: 0 20px;
  box-shadow: var(--shadow-sm);
}
.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  transition: color 0.2s;
  user-select: none;
}
.tab-item:hover { color: var(--primary); }
.tab-item.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}
.tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: #eef2ff;
  color: var(--primary);
  font-size: 11px;
  font-weight: 700;
}
.tab-count.completed {
  background: #f0fdf4;
  color: #10b981;
}

.project-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}
.project-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.payment-status-cell { line-height: 1.5; }
.payment-bar-wrap {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 4px;
}
.payment-bar {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
  min-width: 4px;
}
.payment-text {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.amount-cell { line-height: 1.6; }
.amount-main { font-weight: 600; font-size: 14px; }
.amount-sub { font-size: 12px; color: var(--text-muted); }

.mono-text {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  color: var(--text-secondary);
}

.order-tags { display: flex; flex-wrap: wrap; gap: 3px; }

.order-no-input { width: 100%; }
.order-tags-wrap {
  min-height: 36px;
  padding: 4px 8px;
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.api-popover { font-size: 13px; }
.api-popover-title {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.api-url-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px 12px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #6366f1;
  word-break: break-all;
}
.api-resp-box {
  background: #0f172a;
  border-radius: 8px;
  padding: 12px 14px;
}
.api-resp-item {
  display: flex;
  align-items: center;
  gap: 10px;
}
.api-resp-item code {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #94a3b8;
}
.api-popover-tip {
  margin-top: 10px;
  font-size: 12px;
  color: #94a3b8;
  background: #fffbeb;
  border-radius: 6px;
  padding: 6px 10px;
}
.api-popover-tip code {
  background: rgba(245,158,11,0.15);
  color: #d97706;
  padding: 1px 5px;
  border-radius: 4px;
  font-family: monospace;
}

.dev-status-selector {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.dev-status-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1.5px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  color: var(--text-secondary);
  user-select: none;
}
.dev-status-option:hover { border-color: #94a3b8; }
.dev-status-option.selected { font-weight: 600; }
.status-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
