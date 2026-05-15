// 校园跑腿系统 - 小程序入口
App({
  globalData: {
    userInfo: null,
    token: '',
    baseUrl: 'http://127.0.0.1:8000'
  },

  onLaunch() {
    // 从缓存恢复登录状态
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = JSON.parse(userInfo)
    }
  }
})
