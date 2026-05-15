// 个人中心页面
const app = getApp()

Page({
  data: {
    userInfo: {},
    roleText: ''
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
  },

  onIncome() {
    wx.navigateTo({ url: '/pages/income/income' })
  },

  onReviews() {
    wx.showToast({ title: '功能开发中', icon: 'none' })
  },

  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success(res) {
        if (res.confirm) {
          // 清除登录状态
          app.globalData.token = ''
          app.globalData.userInfo = null
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          wx.reLaunch({ url: '/pages/login/login' })
        }
      }
    })
  }
})
