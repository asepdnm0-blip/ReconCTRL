import { useAuthStore } from '../store/authStore'

export function useAuth() {
  const accessToken = useAuthStore((s) => s.accessToken)
  const refreshToken = useAuthStore((s) => s.refreshToken)
  const loading = useAuthStore((s) => s.loading)
  const error = useAuthStore((s) => s.error)
  const login = useAuthStore((s) => s.login)
  const logout = useAuthStore((s) => s.logout)
  const getToken = useAuthStore((s) => s.getToken)

  return {
    accessToken,
    refreshToken,
    isAuthenticated: Boolean(accessToken),
    loading,
    error,
    login,
    logout,
    getToken,
  }
}
