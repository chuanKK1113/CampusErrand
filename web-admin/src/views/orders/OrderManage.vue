<template>
  <div class="order-manage">
    <!-- 搜索/筛选 -->
    <el-card shadow="hover" class="search-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            placeholder="搜索订单号..."
            clearable
            @input="onSearch"
          />
        </el-col>
        <el-col :span="4">
          <el-select
            v-model="statusFilter"
            placeholder="状态筛选"
            clearable
            style="width: 100%"
            @change="onSearch"
          >
            <el-option label="待接单" value="待接单" />
            <el-option label="配送中" value="配送中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-col>
        <el-col :span="2">
          <el-button type="primary" @click="loadOrders">
            <el-icon><Search /></el-icon> 查询
          </el-button>
        </el-col>
        <el-col :span="2">
          <el-button @click="onRefresh">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 订单表格 -->
    <el-card shadow="hover" style="margin-top: 16px">
      <el-table
        :data="filteredOrders"
        stripe
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无订单数据"
      >
        <el-table-column prop="id" label="订单号" width="100" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column label="发布人" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.requester }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="details" label="描述" min-width="160" show-overflow-tooltip />
        <el-table-column prop="pickup" label="取件地" width="130" show-overflow-tooltip />
        <el-table-column prop="dropoff" label="送达地" width="130" show-overflow-tooltip />
        <el-table-column label="配送员" width="120">
          <template #default="{ row }">
            {{ row.delivery_person || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="reward" label="配送费" width="90">
          <template #default="{ row }">¥{{ row.reward }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="dark">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="danger"
              text
              :disabled="row.status !== '待接单'"
              @click="onCancel(row)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ordersAPI } from '../../api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'

const orders = ref([])
const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')

function statusType(status) {
  const map = {
    '待接单': 'warning',
    '配送中': 'primary',
    '已完成': 'success',
    '已取消': 'info'
  }
  return map[status] || 'info'
}

const filteredOrders = computed(() => {
  let list = orders.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(o => o.id.toLowerCase().includes(q))
  }
  if (statusFilter.value) {
    list = list.filter(o => o.status === statusFilter.value)
  }
  return list
})

async function loadOrders() {
  loading.value = true
  try {
    orders.value = await ordersAPI.list()
  } catch (err) {
    ElMessage.error('加载订单失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

function onSearch() {
  // computed 会自动更新
}

function onRefresh() {
  loadOrders()
}

async function onCancel(row) {
  try {
    await ElMessageBox.confirm(
      `确定要取消订单「${row.id}」吗？`,
      '确认取消',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    await ordersAPI.cancel(row.id)
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(err.message || '取消失败')
    }
  }
}

onMounted(loadOrders)
</script>

<style scoped>
.search-card {
  border-radius: 12px;
}
</style>
