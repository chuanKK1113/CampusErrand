// 评价页面
const { reviews } = require('../../utils/api')
const { showLoading, hideLoading, showSuccess } = require('../../utils/util')

Page({
  data: {
    orderId: '',
    deliveryName: '',
    rating: 5,
    comment: '',
    loading: false
  },

  onLoad(options) {
    if (options.order_id) {
      this.setData({ orderId: options.order_id })
    }
    if (options.delivery) {
      this.setData({ deliveryName: options.delivery })
    }
  },

  setRating(e) {
    const rating = parseInt(e.currentTarget.dataset.rating)
    this.setData({ rating })
  },

  onCommentInput(e) {
    this.setData({ comment: e.detail.value })
  },

  async onSubmit() {
    const { orderId, rating, comment } = this.data

    showLoading('提交中...')
    this.setData({ loading: true })

    try {
      await reviews.add({ order_id: orderId, rating, comment })
      showSuccess('评价成功')
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (err) {
      // 错误已在 api.js 处理
    } finally {
      this.setData({ loading: false })
      hideLoading()
    }
  }
})
