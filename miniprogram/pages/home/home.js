// 首页
const { orders } = require('../../utils/api')
const { showLoading, hideLoading } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    userInfo: {},
    roleText: '',
    recentOrders: [],
    activeDeliveries: [],
    stats: { completed_count: 0, total_income: 0 }
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    if (!userInfo) {
      wx.reLaunch({ url: '/pages/login/login' })
      return
    }

    this.setData({
      userInfo,
      roleText: userInfo.role === 'requester' ? '需求方' : userInfo.role === 'delivery' ? '配送员' : '管理员'
    })

    this.loadData()
  },

  async loadData() {
    const userInfo = this.data.userInfo
    if (!userInfo) return

    showLoading()
    try {
      if (userInfo.role === 'requester') {
        const orders_data = await orders.getMyOrders()
        this.setData({ recentOrders: (orders_data || []).slice(0, 5) })
      } else if (userInfo.role === 'delivery') {
        const deliveries = await orders.getMyDeliveries('配送中')
        this.setData({ activeDeliveries: deliveries || [] })
        // 获取收入统计
        try {
          const { formatPrice } = require('../../utils/util')
          const res = await wx.request({
            url: app.globalData.baseUrl + `/api/orders/delivery`,
            header: { Authorization: `Bearer ${app.globalData.token}` },
          })
          if (res.data) {
            const all_deliveries = res.data || []
            const completed = all_deliveries.filter(o => o.status === '已完成')
            const total = completed.reduce((sum, o) => sum + parseFloat(o.reward || 0), 0)
            this.setData({ stats: { completed_count: completed.length, total_income: total } })
          }
        } catch(e) {}
      }
    } catch (err) {
      console.error('加载首页数据失败', err)
    } finally {
      hideLoading()
    }
  },

  onCreateOrder() {
    wx.navigateTo({ url: '/pages/create-order/create-order' })
  },

  onMyOrders() {
    wx.switchTab({ url: '/pages/order-list/order-list' })
  },

  onMyReviews() {
    // TODO: 跳转到评价列表
  },

  onBrowseOrders() {
    wx.switchTab({ url: '/pages/order-list/order-list' })
  },

  onMyDeliveries() {
    wx.switchTab({ url: '/pages/order-list/order-list' })
  },

  onIncome() {
    wx.navigateTo({ url: '/pages/income/income' })
  },

  onOrderDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` })
  }
})
