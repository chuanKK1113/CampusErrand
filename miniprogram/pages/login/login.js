// 登录页面
const { auth } = require('../../utils/api')
const app = getApp()

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  onUsernameInput(e) {
    this.setData({ username: e.detail.value })
  },

  onPasswordInput(e) {
    this.setData({ password: e.detail.value })
  },

  async onLogin() {
    const { username, password } = this.data
    if (!username || !password) {
      wx.showToast({ title: '请填写用户名和密码', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    try {
      const res = await auth.login(username, password)
      // 保存登录状态
      app.globalData.token = res.access_token
      app.globalData.userInfo = res.user
      wx.setStorageSync('token', res.access_token)
      wx.setStorageSync('userInfo', JSON.stringify(res.user))

      wx.showToast({ title: '登录成功', icon: 'success' })

      // 跳转到首页
      wx.switchTab({ url: '/pages/home/home' })
    } catch (err) {
      // 错误已在 api.js 中处理
    } finally {
      this.setData({ loading: false })
    }
  },

  onRegister() {
    wx.navigateTo({ url: '/pages/register/register' })
  }
})
