// 发布订单页面
const { orders } = require('../../utils/api')
const { showLoading, hideLoading, showSuccess } = require('../../utils/util')

Page({
  data: {
    types: ['快递代取', '外卖代送', '文件代送', '其他'],
    typeIndex: 0,
    details: '',
    pickup: '',
    dropoff: '',
    reward: '',
    note: '',
    loading: false
  },

  onInput(e) {
    const { field } = e.currentTarget.dataset
    this.setData({ [field]: e.detail.value })
  },

  onTypeChange(e) {
    this.setData({ typeIndex: parseInt(e.detail.value) })
  },

  async onSubmit() {
    const { types, typeIndex, details, pickup, dropoff, reward, note } = this.data

    if (!details || !pickup || !dropoff || !reward) {
      wx.showToast({ title: '请填写必要信息', icon: 'none' })
      return
    }

    if (parseFloat(reward) <= 0) {
      wx.showToast({ title: '配送费必须大于0', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    showLoading('发布中...')

    try {
      await orders.create({
        type: types[typeIndex],
        details,
        pickup,
        dropoff,
        reward: parseFloat(reward),
        note
      })
      showSuccess('发布成功')
      setTimeout(() => {
        // 重置表单
        this.setData({
          typeIndex: 0,
          details: '',
          pickup: '',
          dropoff: '',
          reward: '',
          note: ''
        })
        wx.navigateBack()
      }, 1500)
    } catch (err) {
      // 错误已在 api.js 处理
    } finally {
      this.setData({ loading: false })
      hideLoading()
    }
  }
})
