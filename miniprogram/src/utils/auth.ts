import { reactive } from 'vue'
import { buildApiUrl } from './api'

type UserInfo = {
  user_id: number
  username?: string | null
  phone_number?: string | null
  role?: string
}

type AuthState = {
  loggedIn: boolean
  checking: boolean
  user: UserInfo | null
}

type AuthChangeListener = (state: AuthState) => void

const pendingRedirectKey = 'pending_redirect_url'
const listeners = new Set<AuthChangeListener>()

const state = reactive<AuthState>({
  loggedIn: false,
  checking: false,
  user: null
})

const cloneState = (): AuthState => ({
  loggedIn: state.loggedIn,
  checking: state.checking,
  user: state.user ? { ...state.user } : null
})

const emitChange = () => {
  const snapshot = cloneState()
  listeners.forEach((listener) => listener(snapshot))
}

const tabBarRoutes = new Set(['pages/index/index', 'pages/my-bookings/my-bookings'])

const isTabBarRoute = () => {
  const pages = getCurrentPages()
  const current = pages[pages.length - 1]
  const route = current?.route || ''
  return tabBarRoutes.has(route)
}

const applyTabBar = () => {
  if (!isTabBarRoute()) {
    return
  }
  uni.setTabBarStyle({
    color: '#A9B7D8',
    selectedColor: '#E3D90F',
    backgroundColor: '#2B3A6B',
    borderStyle: 'white'
  })
  uni.setTabBarItem({
    index: 1,
    text: state.loggedIn ? '我的' : '登录'
  })
  uni.setTabBarItem({
    index: 0,
    text: '首页'
  })
}

const setAuthState = (next: Partial<AuthState>) => {
  if (typeof next.loggedIn === 'boolean') {
    state.loggedIn = next.loggedIn
  }
  if (typeof next.checking === 'boolean') {
    state.checking = next.checking
  }
  if (Object.prototype.hasOwnProperty.call(next, 'user')) {
    state.user = next.user ?? null
  }
  applyTabBar()
  emitChange()
}

const fetchMe = () =>
  new Promise<UserInfo>((resolve, reject) => {
    const token = uni.getStorageSync('token')
    if (!token) {
      reject(new Error('未登录'))
      return
    }
    uni.request({
      url: buildApiUrl('/api/users/me'),
      method: 'GET',
      timeout: 5000,
      header: {
        Authorization: `Bearer ${token}`
      },
      success: (res: any) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as UserInfo)
          return
        }
        reject(res.data || res)
      },
      fail: reject
    })
  })

const refreshAuthState = async () => {
  const token = uni.getStorageSync('token')
  if (!token) {
    setAuthState({ loggedIn: false, checking: false, user: null })
    return false
  }
  setAuthState({ checking: true })
  try {
    const user = await fetchMe()
    setAuthState({ loggedIn: true, checking: false, user })
    return true
  } catch (error) {
    setAuthState({ loggedIn: false, checking: false, user: null })
    return false
  }
}

const setTokenAndRefresh = async (token: string) => {
  uni.setStorageSync('token', token)
  return refreshAuthState()
}

const clearAuth = () => {
  uni.removeStorageSync('token')
  setAuthState({ loggedIn: false, checking: false, user: null })
}

const setPendingRedirect = (url: string) => {
  uni.setStorageSync(pendingRedirectKey, url)
}

const consumePendingRedirect = () => {
  const url = uni.getStorageSync(pendingRedirectKey)
  if (url) {
    uni.removeStorageSync(pendingRedirectKey)
  }
  return (url as string) || ''
}

const goLoginWithRedirect = (targetUrl: string) => {
  setPendingRedirect(targetUrl)
  uni.reLaunch({
    url: `/pages/login/login?redirect=${encodeURIComponent(targetUrl)}`
  })
}

const promptLoginAndRedirect = (targetUrl: string) => {
  let handled = false
  const timer = setTimeout(() => {
    if (handled) {
      return
    }
    handled = true
    goLoginWithRedirect(targetUrl)
  }, 2000)
  uni.showModal({
    title: '温馨提示',
    content: '请先登录，即将为您跳转…',
    confirmText: '去登录',
    cancelText: '取消',
    success: (res) => {
      if (handled) {
        return
      }
      handled = true
      clearTimeout(timer)
      if (!res.confirm) {
        return
      }
      goLoginWithRedirect(targetUrl)
    },
    fail: () => {
      if (handled) {
        return
      }
      handled = true
      clearTimeout(timer)
    }
  })
}

const ensureLoginOrRedirect = async (targetUrl: string) => {
  const ok = await refreshAuthState()
  if (ok) {
    return true
  }
  promptLoginAndRedirect(targetUrl)
  return false
}

const subscribeAuthChange = (listener: AuthChangeListener) => {
  listeners.add(listener)
  listener(cloneState())
  return () => listeners.delete(listener)
}

const getAuthState = () => cloneState()
const syncTabBar = () => applyTabBar()

export {
  state as authState,
  getAuthState,
  syncTabBar,
  subscribeAuthChange,
  refreshAuthState,
  setTokenAndRefresh,
  clearAuth,
  setPendingRedirect,
  consumePendingRedirect,
  goLoginWithRedirect,
  promptLoginAndRedirect,
  ensureLoginOrRedirect
}
