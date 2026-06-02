import { useState } from 'react'
import { MODULE_OPTIONS, SCAN_PROFILES } from '../constants/modules'

export default function ScanInput({ onSubmit, loading = false }) {
  const [target, setTarget] = useState('')
  const [profile, setProfile] = useState('standard')
  const [modules, setModules] = useState(
    () => SCAN_PROFILES.find((p) => p.id === 'standard')?.modules ?? [],
  )

  const applyProfile = (profileId) => {
    setProfile(profileId)
    const p = SCAN_PROFILES.find((x) => x.id === profileId)
    if (p) setModules([...p.modules])
  }

  const toggleModule = (id) => {
    setProfile('custom')
    setModules((prev) =>
      prev.includes(id) ? prev.filter((m) => m !== id) : [...prev, id],
    )
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!target.trim() || modules.length === 0) return
    onSubmit({ target: target.trim(), modules, scan_type: profile === 'custom' ? 'full' : profile })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="target" className="block text-sm font-medium text-slate-300 mb-2">
          Target URL / domain / IP
        </label>
        <input
          id="target"
          type="text"
          value={target}
          onChange={(e) => setTarget(e.target.value)}
          placeholder="example.com or https://target.app"
          className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 placeholder-slate-500 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
          required
        />
      </div>

      <div>
        <span className="block text-sm font-medium text-slate-300 mb-2">Scan profile</span>
        <div className="flex flex-wrap gap-2">
          {SCAN_PROFILES.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => applyProfile(p.id)}
              className={`rounded-lg border px-4 py-2 text-sm font-medium transition ${
                profile === p.id
                  ? 'border-violet-500 bg-violet-950 text-violet-300'
                  : 'border-slate-700 bg-slate-900 text-slate-400 hover:border-slate-600 hover:text-slate-200'
              }`}
            >
              {p.label}
            </button>
          ))}
          {profile === 'custom' && (
            <span className="rounded-lg border border-slate-600 bg-slate-800 px-4 py-2 text-sm text-slate-300">
              Custom
            </span>
          )}
        </div>
        <p className="mt-2 text-xs text-slate-500">
          {SCAN_PROFILES.find((p) => p.id === profile)?.description || 'Select modules below'}
        </p>
      </div>

      <div>
        <span className="block text-sm font-medium text-slate-300 mb-2">Modules</span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {MODULE_OPTIONS.map((mod) => (
            <label
              key={mod.id}
              className={`flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition ${
                modules.includes(mod.id)
                  ? 'border-violet-600 bg-violet-950/50'
                  : 'border-slate-800 bg-slate-900/50 hover:border-slate-700'
              }`}
            >
              <input
                type="checkbox"
                checked={modules.includes(mod.id)}
                onChange={() => toggleModule(mod.id)}
                className="mt-1 rounded border-slate-600 bg-slate-950 text-violet-600 focus:ring-violet-500"
              />
              <span>
                <span className="block text-sm font-medium text-slate-200">{mod.label}</span>
                <span className="block text-xs text-slate-500">{mod.description}</span>
              </span>
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !target.trim() || modules.length === 0}
        className="w-full rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 py-3 text-sm font-semibold text-white shadow-lg transition hover:from-violet-500 hover:to-indigo-500 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto sm:px-8"
      >
        {loading ? 'Starting scan…' : 'Start reconnaissance'}
      </button>
    </form>
  )
}
