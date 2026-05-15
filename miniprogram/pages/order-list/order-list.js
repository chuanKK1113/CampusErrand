// 订单列表页
const { orders } = require('../../utils/api')
const { formatTime, statusClass, showLoading, hideLoading } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    userInfo: {},
    pageTitle: '订单',
    activeFilter: 'all',
    filters: [],
    orderList: [],
    formatTime,
    statusClass
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    if (!userInfo) return

    this.setData({ userInfo })

    if (userInfo.role === 'requester') {
      this.setData({
        pageTitle: '我的订单',
        filters: [
          { label: '待接单', value: '待接单' },
          { label: '配送中', value: '配送中' },
          { label: '已完成', value: '已完成' },
          { label: '已取消', value: '已取消' }
        ]
      })
    } else if (userInfo.role === 'delivery') {
      this.setData({
        pageTitle: '配送订单',
        filters: [
          { label: '可接单', value: 'available' },
          { label: '配送中', value: '配送中' },
          { label: '已完成', value: '已完成' }
        ]
      })
    } else {
      this.setData({ pageTitle: '全部订单' })
    }

    this.loadOrders()
  },

  onFilter(e) {
    const filter = e.currentTarget.dataset.filter
    this.setData({ activeFilter: filter })
    this.loadOrders()
  },

  async loadOrders() {
    showLoading()
    try {
      const { userInfo, activeFilter } = this.data
      let list = []

      if (userInfo.role === 'requester') {
        const status = activeFilter === 'all' ? null : activeFilter
        list = await orders.getMyOrders(status)
      } else if (userInfo.role === 'delivery') {
        if (activeFilter === 'available') {
          list = await orders.getAvailable()
        } else {
          const status = activeFilter === 'all' ? null : activeFilter
          list = await orders.getMyDeliveries(status)
        }
      }

      this.setData({ orderList: list || [] })
    } catch (err) {
      console.error('加载订单失败', err)
    } finally {
      hideLoading()
    }
  },

  onOrderTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` })
  }
})
