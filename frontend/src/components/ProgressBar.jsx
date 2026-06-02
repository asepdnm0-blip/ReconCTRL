import { MODULE_OPTIONS } from '../constants/modules'
import { statusBadgeClass } from '../utils/scan'

function labelFor(moduleId) {
  return MODULE_OPTIONS.find((m) => m.id === moduleId)?.label || moduleId
}

export default function ProgressBar({ modules = [], moduleProgress = {}, scanStatus }) {
  const list = modules.length
    ? modules
    : MODULE_OPTIONS.map((m) => ({ module_name: m.id, status: 'pending', progress: 0 }))

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-300">Module progress</span>
        {scanStatus && (
          <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${statusBadgeClass(scanStatus)}`}>
            {scanStatus}
          </span>
        )}
      </div>
      {list.map((mod) => {
        const name = mod.module_name || mod
        const live = moduleProgress[name] || {}
        const progress = live.progress ?? mod.progress ?? 0
        const status = live.status || mod.status || 'pending'
        const isFailed = status === 'failed'

        return (
          <div key={name} className="rounded-lg border border-slate-800 bg-slate-950 p-3">
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-slate-200">{labelFor(name)}</span>
              <span className={`text-xs font-semibold capitalize ${isFailed ? 'text-rose-400' : 'text-slate-400'}`}>
                {status}
                {progress > 0 && status === 'running' ? ` · ${progress}%` : ''}
              </span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-800">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  isFailed
                    ? 'bg-rose-600'
                    : status === 'completed'
                      ? 'bg-emerald-500'
                      : 'bg-violet-500'
                }`}
                style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
              />
            </div>
            {live.error && (
              <p className="mt-2 text-xs text-rose-400">{live.error}</p>
            )}
            {mod.error_message && (
              <p className="mt-2 text-xs text-rose-400">{mod.error_message}</p>
            )}
          </div>
        )
      })}
    </div>
  )
}
