// API 请求封装
const app = getApp()

const BASE_URL = () => app.globalData.baseUrl

/**
 * 发起 HTTP 请求
 */
function request(method, url, data = {}) {
  return new Promise((resolve, reject) => {
    const token = app.globalData.token
    const header = { 'Content-Type': 'application/json' }
    if (token) header['Authorization'] = `Bearer ${token}`

    wx.request({
      url: `${BASE_URL()}${url}`,
      method,
      header,
      data,
      timeout: 15000,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const msg = res.data?.detail || '请求失败'
          wx.showToast({ title: msg, icon: 'none' })
          reject({ code: res.statusCode, msg })
        }
      },
      fail(err) {
        wx.showToast({ title: '网络错误，请检查连接', icon: 'none' })
        reject(err)
      }
    })
  })
}

// ==================== 认证 ====================
const auth = {
  login(username, password) {
    return request('POST', '/api/auth/login', { username, password })
  },
  register(data) {
    return request('POST', '/api/auth/register', data)
  },
  getProfile() {
    return request('GET', '/api/auth/me')
  }
}

// ==================== 订单 ====================
const orders = {
  create(data) {
    return request('POST', '/api/orders', data)
  },
  getMyOrders(status) {
    const params = status ? `?status=${status}` : ''
    return request('GET', `/api/orders/mine${params}`)
  },
  getAvailable() {
    return request('GET', '/api/orders/available')
  },
  getMyDeliveries(status) {
    const params = status ? `?status=${status}` : ''
    return request('GET', `/api/orders/delivery${params}`)
  },
  getDetail(id) {
    return request('GET', `/api/orders/${id}`)
  },
  accept(id) {
    return request('PUT', `/api/orders/${id}/accept`)
  },
  complete(id) {
    return request('PUT', `/api/orders/${id}/complete`)
  },
  cancel(id) {
    return request('PUT', `/api/orders/${id}/cancel`)
  }
}

// ==================== 评价 ====================
const reviews = {
  add(data) {
    return request('POST', '/api/reviews', data)
  },
  check(orderId) {
    return request('GET', `/api/reviews/check/${orderId}`)
  },
  getMine() {
    return request('GET', '/api/reviews/mine')
  },
  getDelivery(username) {
    return request('GET', `/api/reviews/delivery/${username}`)
  }
}

// ==================== 用户 ====================
const users = {
  getInfo(username) {
    return request('GET', `/api/users/${username}`)
  }
}

module.exports = { auth, orders, reviews, users }
