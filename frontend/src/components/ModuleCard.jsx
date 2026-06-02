export default function ModuleCard({
  title,
  subtitle,
  status,
  children,
  defaultOpen = true,
}) {
  const statusClass =
    status === 'completed'
      ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
      : status === 'running'
        ? 'bg-amber-950 text-amber-400 border-amber-800'
        : status === 'failed'
          ? 'bg-rose-950 text-rose-400 border-rose-800'
          : 'bg-slate-800 text-slate-400 border-slate-700'

  return (
    <details
      open={defaultOpen}
      className="group rounded-xl border border-slate-800 bg-slate-900 overflow-hidden"
    >
      <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 hover:bg-slate-800/50">
        <div>
          <h3 className="text-base font-semibold text-slate-100">{title}</h3>
          {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-2">
          {status && (
            <span className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${statusClass}`}>
              {status}
            </span>
          )}
          <span className="text-slate-500 group-open:rotate-180 transition-transform">▼</span>
        </div>
      </summary>
      <div className="border-t border-slate-800 px-5 py-4">{children}</div>
    </details>
  )
}
