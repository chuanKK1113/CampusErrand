// 评价列表页面
const { reviews } = require('../../utils/api')
const { showLoading, hideLoading } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    reviews: [],
    isDelivery: false
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    this.setData({ isDelivery: userInfo?.role === 'delivery' })
    this.loadReviews(userInfo)
  },

  async loadReviews(userInfo) {
    showLoading()
    try {
      let list
      if (userInfo.role === 'delivery') {
        // 配送员查看别人给自己的评价
        list = await reviews.getDelivery(userInfo.username)
      } else {
        // 需求方查看自己给出的评价
        list = await reviews.getMine()
      }
      this.setData({ reviews: list || [] })
    } catch (err) {
      console.error('加载评价失败', err)
    } finally {
      hideLoading()
    }
  }
})
