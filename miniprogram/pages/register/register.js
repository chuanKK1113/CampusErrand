// 注册页面
const { auth } = require('../../utils/api')

Page({
  data: {
    username: '',
    password: '',
    name: '',
    phone: '',
    student_id: '',
    roles: ['发布需求（需求方）', '接单配送（配送员）'],
    roleIndex: 0,
    loading: false
  },

  onInput(e) {
    const { field } = e.currentTarget.dataset
    this.setData({ [field]: e.detail.value })
  },

  onRoleChange(e) {
    this.setData({ roleIndex: parseInt(e.detail.value) })
  },

  async onRegister() {
    const { username, password, name, phone, student_id, roleIndex } = this.data
    if (!username || !password || !name || !phone) {
      wx.showToast({ title: '请填写必要信息', icon: 'none' })
      return
    }

    this.setData({ loading: true })
    try {
      await auth.register({
        username,
        password,
        name,
        phone,
        student_id,
        role: roleIndex === 0 ? 'requester' : 'delivery'
      })
      wx.showToast({ title: '注册成功', icon: 'success' })
      setTimeout(() => wx.navigateBack(), 1500)
    } catch (err) {
      // 错误已在 api.js 处理
    } finally {
      this.setData({ loading: false })
    }
  },

  onBack() {
    wx.navigateBack()
  }
})
