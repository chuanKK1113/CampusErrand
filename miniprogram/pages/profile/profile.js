// 个人中心页面
const { auth } = require('../../utils/api')
const app = getApp()

Page({
  data: {
    userInfo: {},
    roleText: ''
  },

  async onShow() {
    const userInfo = app.globalData.userInfo
    if (!userInfo) {
      wx.reLaunch({ url: '/pages/login/login' })
      return
    }
    // 从服务器刷新最新用户信息
    try {
      const fresh = await auth.getProfile()
      if (fresh) {
        app.globalData.userInfo = fresh
        wx.setStorageSync('userInfo', JSON.stringify(fresh))
        this.setData({ userInfo: fresh })
      } else {
        this.setData({ userInfo })
      }
    } catch {
      this.setData({ userInfo })
    }
    this.setData({
      roleText: userInfo.role === 'requester' ? '需求方' : userInfo.role === 'delivery' ? '配送员' : '管理员',
      avatarFullUrl: this.resolveAvatar(userInfo.avatar)
    })
  },

  resolveAvatar(avatar) {
    if (!avatar) return ''
    if (avatar.startsWith('http://') || avatar.startsWith('https://')) return avatar
    return app.globalData.baseUrl + avatar
  },

  onEditProfile() {
    wx.navigateTo({ url: '/pages/edit-profile/edit-profile' })
  },

  onIncome() {
    wx.navigateTo({ url: '/pages/income/income' })
  },

  onReviews() {
    wx.navigateTo({ url: '/pages/review-list/review-list' })
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
