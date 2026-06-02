function severityClass(severity) {
  const s = (severity || '').toLowerCase()
  if (s.includes('critical')) return 'bg-rose-950 text-rose-300 border-rose-800'
  if (s.includes('high')) return 'bg-orange-950 text-orange-300 border-orange-800'
  if (s.includes('medium')) return 'bg-amber-950 text-amber-300 border-amber-800'
  return 'bg-slate-800 text-slate-400 border-slate-700'
}

export default function PortTable({ data }) {
  const ports = data?.ports || []

  if (!ports.length) {
    return <p className="text-sm text-slate-500">No open ports detected.</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm text-slate-300">
        <thead className="border-b border-slate-800 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-3 py-2">Port</th>
            <th className="px-3 py-2">State</th>
            <th className="px-3 py-2">Service</th>
            <th className="px-3 py-2">Version</th>
            <th className="px-3 py-2">CVEs</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800">
          {ports.map((p) => (
            <tr key={p.port} className="hover:bg-slate-800/40">
              <td className="px-3 py-3 font-mono font-medium text-violet-300">{p.port}</td>
              <td className="px-3 py-3 capitalize">{p.state}</td>
              <td className="px-3 py-3">{p.service || '—'}</td>
              <td className="px-3 py-3 text-slate-400">{p.version || '—'}</td>
              <td className="px-3 py-3">
                <div className="flex flex-wrap gap-1">
                  {(p.cves || []).length === 0 ? (
                    <span className="text-xs text-slate-600">None</span>
                  ) : (
                    p.cves.map((cve) => (
                      <span
                        key={cve.id}
                        title={cve.description}
                        className={`rounded border px-1.5 py-0.5 text-xs font-mono ${severityClass(cve.severity)}`}
                      >
                        {cve.id}
                        {cve.cvss_score != null ? ` (${cve.cvss_score})` : ''}
                      </span>
                    ))
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data?.os_guess && (
        <p className="mt-3 text-xs text-slate-500">
          OS guess: <span className="text-slate-300">{data.os_guess}</span>
          {data.duration_s != null && ` · ${data.duration_s}s`}
        </p>
      )}
    </div>
  )
}
