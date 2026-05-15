<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.label">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <p class="stat-label">{{ stat.label }}</p>
              <p class="stat-value">{{ stat.value }}</p>
            </div>
            <el-icon :size="48" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 最近订单 -->
    <el-card class="recent-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>最近订单</span>
          <el-button type="primary" text @click="$router.push('/orders')">
            查看全部
          </el-button>
        </div>
      </template>

      <el-table :data="recentOrders" stripe style="width: 100%">
        <el-table-column prop="id" label="订单号" width="100" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="requester" label="发布人" width="120" />
        <el-table-column prop="delivery_person" label="配送员" width="120">
          <template #default="{ row }">
            {{ row.delivery_person || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="reward" label="配送费" width="100">
          <template #default="{ row }">
            ¥{{ row.reward }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statsAPI, ordersAPI } from '../../api'
import { DataAnalysis, List, CircleCheck, Clock } from '@element-plus/icons-vue'

const stats = ref([
  { label: '总用户数', value: 0, icon: 'UserFilled', color: '#4A90D9' },
  { label: '总订单数', value: 0, icon: 'List', color: '#67C23A' },
  { label: '进行中', value: 0, icon: 'Clock', color: '#E6A23C' },
  { label: '已完成', value: 0, icon: 'CircleCheck', color: '#409EFF' }
])

const recentOrders = ref([])

function statusType(status) {
  const map = {
    '待接单': 'warning',
    '配送中': 'primary',
    '已完成': 'success',
    '已取消': 'info'
  }
  return map[status] || 'info'
}

async function loadData() {
  try {
    const [statsData, ordersData] = await Promise.all([
      statsAPI.get(),
      ordersAPI.list()
    ])
    stats.value = [
      { label: '总用户数', value: statsData.total_users || 0, icon: 'UserFilled', color: '#4A90D9' },
      { label: '总订单数', value: statsData.total_orders || 0, icon: 'List', color: '#67C23A' },
      { label: '进行中', value: statsData.active_orders || 0, icon: 'Clock', color: '#E6A23C' },
      { label: '已完成', value: statsData.completed_orders || 0, icon: 'CircleCheck', color: '#409EFF' }
    ]
    recentOrders.value = (ordersData || []).slice(0, 10)
  } catch (err) {
    console.error('加载数据失败', err)
  }
}

onMounted(loadData)
</script>

<style scoped>
.dashboard {
  max-width: 1400px;
}

.stats-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-card {
  border-radius: 12px;
}
</style>
