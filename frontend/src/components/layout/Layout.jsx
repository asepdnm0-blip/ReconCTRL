import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const navClass = ({ isActive }) =>
  `text-sm font-medium transition ${
    isActive ? 'text-violet-400' : 'text-slate-400 hover:text-slate-200'
  }`

export default function Layout() {
  const { logout } = useAuth()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50 print:hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
              RC
            </div>
            <div>
              <span className="font-extrabold text-xl bg-clip-text text-transparent bg-gradient-to-r from-violet-400 via-indigo-200 to-cyan-400">
                ReconCTRL
              </span>
              <span className="text-[10px] block text-slate-500 uppercase tracking-widest font-semibold">
                Dashboard
              </span>
            </div>
          </Link>
          <nav className="hidden md:flex items-center gap-8">
            <NavLink to="/" end className={navClass}>
              Dashboard
            </NavLink>
            <NavLink to="/history" className={navClass}>
              History
            </NavLink>
          </nav>
          <button
            type="button"
            onClick={logout}
            className="text-xs font-medium text-slate-500 hover:text-rose-400 transition"
          >
            Sign out
          </button>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
