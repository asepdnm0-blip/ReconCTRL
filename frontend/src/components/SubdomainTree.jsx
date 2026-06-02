export default function SubdomainTree({ data }) {
  const items = data?.subdomains || []

  if (!items.length) {
    return <p className="text-sm text-slate-500">No subdomains discovered.</p>
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-4 text-xs text-slate-500 mb-3">
        <span>Found: <strong className="text-slate-300">{data.total_found ?? items.length}</strong></span>
        <span>Live: <strong className="text-emerald-400">{data.total_live ?? items.filter((s) => s.live).length}</strong></span>
      </div>
      <ul className="max-h-80 overflow-y-auto rounded-lg border border-slate-800 divide-y divide-slate-800">
        {items.map((sub) => (
          <li
            key={sub.fqdn}
            className="flex items-center justify-between gap-4 px-4 py-2.5 text-sm hover:bg-slate-800/50"
          >
            <span className="font-mono text-slate-200 truncate">{sub.fqdn}</span>
            <div className="flex items-center gap-2 shrink-0">
              {sub.ip && (
                <span className="font-mono text-xs text-slate-500">{sub.ip}</span>
              )}
              <span
                className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${
                  sub.live
                    ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
                    : 'bg-slate-800 text-slate-500 border-slate-700'
                }`}
              >
                {sub.live ? 'live' : 'dead'}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
