// 收入统计页面
const { orders } = require('../../utils/api')
const { formatTime, showLoading, hideLoading } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    userInfo: {},
    stats: { completed_count: 0, total_income: 0 },
    completedOrders: [],
    formatTime
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    this.setData({ userInfo })
    this.loadIncome()
  },

  async loadIncome() {
    showLoading()
    try {
      const list = await orders.getMyDeliveries('已完成')
      this.setData({ completedOrders: list || [] })

      const total = (list || []).reduce((sum, o) => sum + parseFloat(o.reward || 0), 0)
      this.setData({
        stats: {
          completed_count: (list || []).length,
          total_income: total
        }
      })
    } catch (err) {
      console.error('加载收入数据失败', err)
    } finally {
      hideLoading()
    }
  },

  onOrderDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: `/pages/order-detail/order-detail?id=${id}` })
  }
})
