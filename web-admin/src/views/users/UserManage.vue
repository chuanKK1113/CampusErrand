<template>
  <div class="user-manage">
    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="mini-stat">
            <span class="mini-stat-label">总用户数</span>
            <span class="mini-stat-value">{{ users.length }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="mini-stat">
            <span class="mini-stat-label">需求方</span>
            <span class="mini-stat-value mini-stat-blue">{{ requesterCount }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="mini-stat">
            <span class="mini-stat-label">配送员</span>
            <span class="mini-stat-value mini-stat-green">{{ deliveryCount }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 用户表格 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>用户列表</span>
          <el-button type="primary" text @click="loadUsers">
            <el-icon><Refresh /></el-icon> 刷新
          </el-button>
        </div>
      </template>

      <el-table
        :data="users"
        stripe
        style="width: 100%"
        v-loading="loading"
        empty-text="暂无用户数据"
      >
        <el-table-column prop="username" label="用户名" width="130" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.role === 'admin' ? 'danger' : row.role === 'delivery' ? 'success' : 'primary'"
              size="small"
            >
              {{ row.role === 'requester' ? '需求方' : row.role === 'delivery' ? '配送员' : '管理员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="手机号" width="140" />
        <el-table-column prop="student_id" label="学号" width="130" />
        <el-table-column label="评分" width="80">
          <template #default="{ row }">
            {{ row.role === 'delivery' ? (row.rating || '-') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="完成数" width="80">
          <template #default="{ row }">
            {{ row.role === 'delivery' ? row.completed : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" min-width="160" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usersAPI } from '../../api'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const users = ref([])
const loading = ref(false)

const requesterCount = computed(() =>
  users.value.filter(u => u.role === 'requester').length
)

const deliveryCount = computed(() =>
  users.value.filter(u => u.role === 'delivery').length
)

async function loadUsers() {
  loading.value = true
  try {
    users.value = await usersAPI.list()
  } catch (err) {
    ElMessage.error('加载用户失败: ' + err.message)
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.stats-row {
  margin-bottom: 0;
}

.mini-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mini-stat-label {
  font-size: 14px;
  color: #999;
}

.mini-stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
}

.mini-stat-blue {
  color: #4A90D9;
}

.mini-stat-green {
  color: #67C23A;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
