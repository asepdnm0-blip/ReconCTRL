export function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString()
}

export function statusBadgeClass(status) {
  const s = (status || '').toLowerCase()
  if (s === 'completed') return 'bg-emerald-950 text-emerald-400 border-emerald-800'
  if (s === 'running') return 'bg-amber-950 text-amber-400 border-amber-800 animate-pulse'
  if (s === 'failed') return 'bg-rose-950 text-rose-400 border-rose-800'
  if (s === 'cancelled') return 'bg-slate-800 text-slate-400 border-slate-600'
  return 'bg-slate-800 text-slate-400 border-slate-700'
}

export function moduleResult(scan, moduleName) {
  const mod = scan?.modules?.find((m) => m.module_name === moduleName)
  if (mod?.result_data) return mod.result_data
  return scan?.results_summary?.[moduleName] ?? scan?.results_summary?.[moduleName.replace('nmap', 'port_scan')]
}

export function resolveModuleKey(name) {
  const aliases = { nmap: 'port_scan', whois: 'osint', headers: 'header' }
  return aliases[name] || name
}
