import { create } from 'zustand'
import api from '../api/client'

const ACCESS_KEY = 'reconctrl_access_token'
const REFRESH_KEY = 'reconctrl_refresh_token'

export const useAuthStore = create((set, get) => ({
  accessToken: localStorage.getItem(ACCESS_KEY),
  refreshToken: localStorage.getItem(REFRESH_KEY),
  user: null,
  loading: false,
  error: null,

  isAuthenticated: () => Boolean(get().accessToken),

  login: async (username, password) => {
    set({ loading: true, error: null })
    try {
      const { data } = await api.post('/api/v1/auth/login', { username, password })
      localStorage.setItem(ACCESS_KEY, data.access_token)
      localStorage.setItem(REFRESH_KEY, data.refresh_token)
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        loading: false,
      })
      return data
    } catch (err) {
      const detail = err.response?.data?.detail
      const message = Array.isArray(detail)
        ? detail[0]?.msg || 'Login failed'
        : detail || 'Login failed'
      set({ error: message, loading: false })
      throw err
    }
  },

  logout: () => {
    localStorage.removeItem(ACCESS_KEY)
    localStorage.removeItem(REFRESH_KEY)
    set({ accessToken: null, refreshToken: null, user: null })
  },

  getToken: () => get().accessToken,
}))
