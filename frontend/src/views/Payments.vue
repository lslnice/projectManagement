<template>
  <div>
    <div class="page-header">
      <h2>汇款管理</h2>
      <div style="display: flex; gap: 10px;">
        <el-button @click="openBatchDialog">
          <el-icon><DocumentAdd /></el-icon> 批量导入
        </el-button>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon> 单条添加
        </el-button>
      </div>
    </div>

    <div class="filter-bar">
      <el-input v-model="filters.keyword" placeholder="搜索订单号" clearable style="width: 240px" @clear="loadData" @keyup.enter="loadData">
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filters.project_id" placeholder="全部项目" clearable filterable style="width: 220px" @change="loadData">
        <el-option v-for="p in projectList" :key="p.id" :label="p.name" :value="p.id" />
      </el-select>
      <el-button @click="loadData">
        <el-icon><RefreshRight /></el-icon> 刷新
      </el-button>
    </div>

    <div class="table-wrapper">
      <el-table :data="list" v-loading="loading" style="width: 100%" :header-cell-style="{ padding: '14px 16px' }" :cell-style="{ padding: '14px 16px' }">
        <el-table-column prop="project_name" label="所属项目" min-width="160">
          <template #default="{ row }">
            <span style="font-weight: 500;">{{ row.project_name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="order_no" label="订单号" min-width="200">
          <template #default="{ row }">
            <span class="mono-text">{{ row.order_no }}</span>
          </template>
        </el-table-column>
        <el-table-column label="汇款金额" width="150" align="right">
          <template #default="{ row }">
            <span class="money-text">+¥{{ formatMoney(row.amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="phase" label="期次" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.phase" size="small" effect="plain" style="border: none; background: #eef2ff; color: #6366f1;">{{ row.phase }}</el-tag>
            <span v-else style="color: #cbd5e1;">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <span style="color: var(--text-secondary);">{{ row.notes || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="时间" width="170">
          <template #default="{ row }">
            <span style="font-size: 13px; color: var(--text-muted);">{{ row.created_at }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" text type="danger" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 单条添加 -->
    <el-dialog v-model="dialogVisible" title="添加汇款" width="520px" destroy-on-close>
      <div class="payment-tip">
        <el-icon color="#6366f1" :size="16"><InfoFilled /></el-icon>
        <span>输入订单号后系统会自动匹配对应项目，也可以手动选择项目</span>
      </div>
      <el-form :model="form" label-width="100px" label-position="left" style="margin-top: 20px;">
        <el-form-item label="订单号" required>
          <el-input v-model="form.order_no" placeholder="输入支付订单号" />
        </el-form-item>
        <el-form-item label="指定项目">
          <el-select v-model="form.project_id" placeholder="自动匹配（可手动选择）" clearable filterable style="width: 100%">
            <el-option v-for="p in projectList" :key="p.id" :label="`${p.name}（${p.payment_order_no || '无订单号'}）`" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="汇款金额" required>
          <el-input-number v-model="form.amount" :min="0.01" :precision="2" :controls="false" style="width: 100%" placeholder="0.00" />
        </el-form-item>
        <el-form-item label="期次">
          <el-input v-model="form.phase" placeholder="如：一期、二期、尾款" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量导入 -->
    <el-dialog v-model="batchVisible" title="批量导入汇款" width="640px" destroy-on-close>
      <div class="payment-tip" style="margin-bottom: 16px;">
        <el-icon color="#6366f1" :size="16"><InfoFilled /></el-icon>
        <span>支持格式：每行 <code>订单号&nbsp;&nbsp;姓名（可省略）&nbsp;&nbsp;金额</code>，金额负数自动取绝对值，订单号自动匹配项目</span>
      </div>

      <el-input
        v-model="batchText"
        type="textarea"
        :rows="10"
        placeholder="粘贴流水记录，例如：&#10;4502041310031057745    李盛龙    -588&#10;3253320698642625970    李盛龙    -1715&#10;4502057546052011736    -245"
        class="batch-textarea"
      />

      <div style="display: flex; gap: 12px; margin-top: 16px;">
        <el-input v-model="batchPhase" placeholder="期次（可选，如：一期）" style="width: 160px;" />
        <el-input v-model="batchNotes" placeholder="备注（可选）" style="flex: 1;" />
      </div>

      <!-- 导入结果 -->
      <div v-if="batchResult" class="batch-result">
        <div class="result-summary">
          <div class="result-item success">
            <el-icon :size="18"><CircleCheckFilled /></el-icon>
            <span>成功 <strong>{{ batchResult.success_count }}</strong> 条</span>
          </div>
          <div class="result-item failed" v-if="batchResult.failed_count > 0">
            <el-icon :size="18"><CircleCloseFilled /></el-icon>
            <span>失败 <strong>{{ batchResult.failed_count }}</strong> 条</span>
          </div>
        </div>

        <div v-if="batchResult.success && batchResult.success.length" class="result-list">
          <div class="result-list-title success-title">导入成功</div>
          <div class="result-row success-row" v-for="item in batchResult.success" :key="item.order_no">
            <span class="mono-text">{{ item.order_no }}</span>
            <span class="project-tag">{{ item.project_name }}</span>
            <span class="money-text">+¥{{ formatMoney(item.amount) }}</span>
          </div>
        </div>

        <div v-if="batchResult.failed && batchResult.failed.length" class="result-list">
          <div class="result-list-title failed-title">导入失败</div>
          <div class="result-row failed-row" v-for="item in batchResult.failed" :key="item.line">
            <span class="mono-text">{{ item.line }}</span>
            <span class="fail-reason">{{ item.reason }}</span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="batchVisible = false">关闭</el-button>
          <el-button @click="batchText = ''; batchResult = null" :disabled="!batchText && !batchResult">清空</el-button>
          <el-button type="primary" :loading="batchSubmitting" @click="handleBatchSubmit">
            <el-icon><Upload /></el-icon> 开始导入
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, RefreshRight, Delete, InfoFilled, DocumentAdd, CircleCheckFilled, CircleCloseFilled, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPayments, createPayment, deletePayment, batchCreatePayments } from '../api/payments'
import { getProjects } from '../api/projects'

const loading = ref(false)
const submitting = ref(false)
const batchSubmitting = ref(false)
const dialogVisible = ref(false)
const batchVisible = ref(false)
const list = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const projectList = ref([])
const filters = reactive({ keyword: '', project_id: '' })

const form = reactive({ order_no: '', project_id: null, amount: 0, phase: '', notes: '' })

const batchText = ref('')
const batchPhase = ref('')
const batchNotes = ref('')
const batchResult = ref(null)

function formatMoney(val) {
  return (val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadProjects() {
  try {
    const res = await getProjects({ page: 1, page_size: 100 })
    projectList.value = res.data.items
  } catch (e) {}
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.project_id) params.project_id = filters.project_id
    const res = await getPayments(params)
    list.value = res.data.items
    total.value = res.data.total
  } catch (e) {} finally { loading.value = false }
}

function openDialog() {
  Object.assign(form, { order_no: '', project_id: null, amount: 0, phase: '', notes: '' })
  dialogVisible.value = true
}

function openBatchDialog() {
  batchText.value = ''
  batchPhase.value = ''
  batchNotes.value = ''
  batchResult.value = null
  batchVisible.value = true
}

async function handleSubmit() {
  if (!form.order_no) return ElMessage.warning('请输入订单号')
  if (!form.amount || form.amount <= 0) return ElMessage.warning('请输入汇款金额')
  submitting.value = true
  try {
    const data = { ...form }
    if (!data.project_id) delete data.project_id
    await createPayment(data)
    ElMessage.success('汇款记录添加成功')
    dialogVisible.value = false
    loadData()
  } catch (e) {} finally { submitting.value = false }
}

async function handleBatchSubmit() {
  if (!batchText.value.trim()) return ElMessage.warning('请粘贴汇款流水')
  batchSubmitting.value = true
  batchResult.value = null
  try {
    const res = await batchCreatePayments({
      text: batchText.value,
      phase: batchPhase.value,
      notes: batchNotes.value,
    })
    batchResult.value = res.data
    if (res.data.success_count > 0) {
      loadData()
    }
  } catch (e) {} finally { batchSubmitting.value = false }
}

async function handleDelete(row) {
  await ElMessageBox.confirm('确定删除此汇款记录？', '删除确认', {
    type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消',
  })
  try {
    await deletePayment(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {}
}

onMounted(() => { loadProjects(); loadData() })
</script>

<style scoped>
.mono-text {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
  color: var(--text-secondary);
}
.money-text {
  font-weight: 700;
  font-size: 14px;
  color: #10b981;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  white-space: nowrap;
}
.payment-tip {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: #eef2ff;
  border-radius: 10px;
  font-size: 13px;
  color: #6366f1;
  line-height: 1.6;
}
.payment-tip code {
  background: rgba(99,102,241,0.15);
  padding: 1px 5px;
  border-radius: 4px;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.batch-textarea :deep(textarea) {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.8;
}

.batch-result {
  margin-top: 20px;
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}

.result-summary {
  display: flex;
  gap: 16px;
  padding: 14px 16px;
  background: #f8fafc;
  border-bottom: 1px solid var(--border);
}

.result-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
}
.result-item.success { color: #10b981; }
.result-item.failed { color: #ef4444; }

.result-list {
  padding: 12px 16px;
}
.result-list + .result-list {
  border-top: 1px solid var(--border);
}

.result-list-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}
.success-title { color: #10b981; }
.failed-title { color: #ef4444; }

.result-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 7px 10px;
  border-radius: 8px;
  margin-bottom: 4px;
  font-size: 13px;
}
.success-row { background: #f0fdf4; }
.failed-row { background: #fef2f2; }

.project-tag {
  flex: 1;
  color: #6366f1;
  font-weight: 500;
  font-size: 12px;
}
.fail-reason {
  color: #ef4444;
  font-size: 12px;
  flex: 1;
}
</style>
