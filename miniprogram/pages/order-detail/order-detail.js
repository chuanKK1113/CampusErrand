// 订单详情页
const { orders, reviews } = require('../../utils/api')
const { formatTime, statusClass, showLoading, hideLoading, showSuccess } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    order: {},
    userInfo: {},
    loading: true,
    reviewed: false,
    formatTime,
    statusClass
  },

  onLoad(options) {
    this.setData({ userInfo: app.globalData.userInfo })
    if (options.id) {
      this.loadOrder(options.id)
    }
  },

  async loadOrder(id) {
    showLoading()
    try {
      const order = await orders.getDetail(id)
      this.setData({ order })

      // 检查是否已评价
      if (order.status === '已完成') {
        const res = await reviews.check(id)
        this.setData({ reviewed: res.exists })
      }
    } catch (err) {
      console.error('加载订单失败', err)
    } finally {
      this.setData({ loading: false })
      hideLoading()
    }
  },

  statusBgClass(status) {
    const map = {
      '待接单': 'status-bg-pending',
      '配送中': 'status-bg-delivering',
      '已完成': 'status-bg-completed',
      '已取消': 'status-bg-cancelled'
    }
    return map[status] || ''
  },

  async onAccept() {
    wx.showModal({
      title: '确认接单',
      content: '确定要接取此订单吗？',
      success: async (res) => {
        if (res.confirm) {
          showLoading()
          try {
            await orders.accept(this.data.order.id)
            showSuccess('接单成功')
            this.loadOrder(this.data.order.id)
          } catch (err) {}
          hideLoading()
        }
      }
    })
  },

  async onComplete() {
    wx.showModal({
      title: '确认送达',
      content: '确认已送达并完成此订单？',
      success: async (res) => {
        if (res.confirm) {
          showLoading()
          try {
            await orders.complete(this.data.order.id)
            showSuccess('已确认送达')
            this.loadOrder(this.data.order.id)
          } catch (err) {}
          hideLoading()
        }
      }
    })
  },

  async onCancel() {
    wx.showModal({
      title: '取消订单',
      content: '确定要取消此订单吗？',
      success: async (res) => {
        if (res.confirm) {
          showLoading()
          try {
            await orders.cancel(this.data.order.id)
            showSuccess('订单已取消')
            this.loadOrder(this.data.order.id)
          } catch (err) {}
          hideLoading()
        }
      }
    })
  },

  onReview() {
    wx.navigateTo({
      url: `/pages/review/review?order_id=${this.data.order.id}&delivery=${this.data.order.delivery_person}`
    })
  }
})
