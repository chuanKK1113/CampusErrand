import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

// 请求拦截器 - 添加认证令牌
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('admin_token')
        localStorage.removeItem('admin_user')
        window.location.href = '/login'
      }
      return Promise.reject(new Error(data?.detail || '请求失败'))
    }
    return Promise.reject(new Error('网络错误，请检查连接'))
  }
)

// ==================== 认证 ====================
export const authAPI = {
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },
  getProfile() {
    return api.get('/auth/me')
  }
}

// ==================== 用户管理 ====================
export const usersAPI = {
  list() {
    return api.get('/users')
  },
  get(username) {
    return api.get(`/users/${username}`)
  }
}

// ==================== 订单管理 ====================
export const ordersAPI = {
  list() {
    return api.get('/admin/orders')
  },
  get(id) {
    return api.get(`/orders/${id}`)
  },
  cancel(id) {
    return api.put(`/orders/${id}/cancel`)
  }
}

// ==================== 统计 ====================
export const statsAPI = {
  get() {
    return api.get('/stats')
  }
}

export default api
