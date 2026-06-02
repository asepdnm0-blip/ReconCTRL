import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export default function LoginPage() {
  const { login, isAuthenticated, loading, error } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')

  const from = location.state?.from?.pathname || '/'

  if (isAuthenticated) {
    return <Navigate to={from} replace />
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await login(username, password)
      navigate(from, { replace: true })
    } catch {
      /* error in store */
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-xl">
        <div className="text-center mb-8">
          <div className="mx-auto w-14 h-14 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center font-bold text-white text-lg mb-4">
            RC
          </div>
          <h1 className="text-2xl font-bold text-white">ReconCTRL</h1>
          <p className="text-sm text-slate-500 mt-1">Sign in to access the dashboard</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="block text-sm text-slate-400 mb-1">
              Username
            </label>
            <input
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-slate-100 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm text-slate-400 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-slate-100 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
              required
            />
          </div>
          {error && (
            <p className="text-sm text-rose-400 bg-rose-950 border border-rose-900 rounded-lg px-3 py-2">
              {typeof error === 'string' ? error : 'Login failed'}
            </p>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 py-2.5 text-sm font-semibold text-white hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 transition"
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
