// 编辑资料页面
const { auth, users } = require('../../utils/api')
const { showLoading, hideLoading, showSuccess } = require('../../utils/util')
const app = getApp()

Page({
  data: {
    nickname: '',
    username: '',
    phone: '',
    avatarUrl: '',
    defaultAvatar: '',
    loading: false
  },

  onShow() {
    const userInfo = app.globalData.userInfo
    if (!userInfo) {
      wx.reLaunch({ url: '/pages/login/login' })
      return
    }
    this.setData({
      nickname: userInfo.name || '',
      username: userInfo.username || '',
      phone: userInfo.phone || '',
      avatarUrl: userInfo.avatar ? app.globalData.baseUrl + userInfo.avatar : '',
      defaultAvatar: '/images/profile-active.png'
    })
  },

  onNicknameInput(e) {
    this.setData({ nickname: e.detail.value })
  },

  onChooseAvatar() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempPath = res.tempFilePaths[0]
        this.setData({ avatarUrl: tempPath })
        this.uploadAvatar(tempPath)
      }
    })
  },

  async uploadAvatar(filePath) {
    const token = app.globalData.token
    const baseUrl = app.globalData.baseUrl

    wx.showLoading({ title: '上传头像中...', mask: true })

    try {
      const res = await new Promise((resolve, reject) => {
        wx.uploadFile({
          url: `${baseUrl}/api/auth/avatar`,
          filePath: filePath,
          name: 'file',
          header: { Authorization: `Bearer ${token}` },
          success: (resp) => {
            try {
              resolve(JSON.parse(resp.data))
            } catch {
              reject(new Error('上传失败'))
            }
          },
          fail: reject
        })
      })

      if (res.success) {
        // 更新全局用户信息中的头像
        const userInfo = { ...app.globalData.userInfo, avatar: res.avatar }
        app.globalData.userInfo = userInfo
        wx.setStorageSync('userInfo', JSON.stringify(userInfo))
        this.setData({ avatarUrl: baseUrl + res.avatar })
        wx.showToast({ title: '头像已更新', icon: 'success' })
      } else {
        wx.showToast({ title: res.message || '上传失败', icon: 'none' })
      }
    } catch (err) {
      wx.showToast({ title: '上传失败，请重试', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  async onSave() {
    const { nickname } = this.data
    if (!nickname || !nickname.trim()) {
      wx.showToast({ title: '昵称不能为空', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    showLoading('保存中...')

    try {
      const res = await auth.updateProfile({ name: nickname.trim() })
      // 更新全局用户信息
      const userInfo = { ...app.globalData.userInfo, ...res.user }
      app.globalData.userInfo = userInfo
      wx.setStorageSync('userInfo', JSON.stringify(userInfo))
      showSuccess('保存成功')
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (err) {
      // 错误已在 api.js 中处理
    } finally {
      this.setData({ loading: false })
      hideLoading()
    }
  },

  onBack() {
    wx.navigateBack()
  }
})
