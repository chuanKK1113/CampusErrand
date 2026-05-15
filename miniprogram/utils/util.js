// 工具函数

/**
 * 格式化订单状态显示
 */
function formatStatus(status) {
  const map = {
    '待接单': '待接单',
    '配送中': '配送中',
    '已完成': '已完成',
    '已取消': '已取消'
  }
  return map[status] || status
}

/**
 * 获取状态对应的 CSS class
 */
function statusClass(status) {
  const map = {
    '待接单': 'status-pending',
    '配送中': 'status-delivering',
    '已完成': 'status-completed',
    '已取消': 'status-cancelled'
  }
  return map[status] || ''
}

/**
 * 格式化金额
 */
function formatPrice(price) {
  return `¥${parseFloat(price || 0).toFixed(2)}`
}

/**
 * 格式化时间
 */
function formatTime(timeStr) {
  if (!timeStr) return ''
  return timeStr.substring(0, 16)
}

/**
 * 显示加载提示
 */
function showLoading(title = '加载中...') {
  wx.showLoading({ title, mask: true })
}

/**
 * 隐藏加载提示
 */
function hideLoading() {
  wx.hideLoading()
}

/**
 * 显示成功提示
 */
function showSuccess(msg = '操作成功') {
  wx.showToast({ title: msg, icon: 'success' })
}

module.exports = {
  formatStatus,
  statusClass,
  formatPrice,
  formatTime,
  showLoading,
  hideLoading,
  showSuccess
}
