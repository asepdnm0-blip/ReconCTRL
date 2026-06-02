const OWASP_TOP_10 = [
  { id: 'A01', name: 'Broken Access Control', checks: ['access', 'authorization'] },
  { id: 'A02', name: 'Cryptographic Failures', checks: ['cookie_secure', 'hsts', 'strict-transport'] },
  { id: 'A03', name: 'Injection', checks: ['injection'] },
  { id: 'A04', name: 'Insecure Design', checks: ['design'] },
  { id: 'A05', name: 'Security Misconfiguration', checks: ['missing_', 'server_version', 'x_powered'] },
  { id: 'A06', name: 'Vulnerable Components', checks: ['component', 'version'] },
  { id: 'A07', name: 'Auth Failures', checks: ['auth', 'cookie'] },
  { id: 'A08', name: 'Software/Data Integrity', checks: ['integrity'] },
  { id: 'A09', name: 'Logging Failures', checks: ['logging'] },
  { id: 'A10', name: 'SSRF', checks: ['ssrf'] },
]

function riskClass(level) {
  if (level === 'high') return 'bg-rose-950 text-rose-300 border-rose-800'
  if (level === 'medium') return 'bg-amber-950 text-amber-300 border-amber-800'
  if (level === 'low') return 'bg-slate-800 text-slate-400 border-slate-600'
  return 'bg-emerald-950 text-emerald-400 border-emerald-800'
}

function mapFindingsToMatrix(findings = []) {
  return OWASP_TOP_10.map((item) => {
    const matched = findings.filter((f) =>
      item.checks.some((c) => (f.check || '').toLowerCase().includes(c)),
    )
    let level = 'pass'
    if (matched.some((f) => f.severity === 'high' || f.severity === 'critical')) {
      level = 'high'
    } else if (matched.some((f) => f.severity === 'medium')) {
      level = 'medium'
    } else if (matched.length) {
      level = 'low'
    }
    return { ...item, level, findings: matched }
  })
}

export default function OWASPMatrix({ data }) {
  const findings = data?.findings || []
  const matrix = mapFindingsToMatrix(findings)
  const score = data?.score

  return (
    <div className="space-y-4">
      {score != null && (
        <p className="text-sm text-slate-400">
          Security score:{' '}
          <span className="font-bold text-violet-300">{score}/100</span>
        </p>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {matrix.map((row) => (
          <div
            key={row.id}
            className="rounded-lg border border-slate-800 bg-slate-950 p-3 flex items-start justify-between gap-2"
          >
            <div>
              <span className="text-xs font-mono text-violet-400">{row.id}</span>
              <p className="text-sm font-medium text-slate-200">{row.name}</p>
              {row.findings.length > 0 && (
                <p className="text-xs text-slate-500 mt-1">{row.findings.length} finding(s)</p>
              )}
            </div>
            <span className={`shrink-0 rounded-full border px-2 py-0.5 text-xs font-semibold uppercase ${riskClass(row.level)}`}>
              {row.level === 'pass' ? 'ok' : row.level}
            </span>
          </div>
        ))}
      </div>
      {findings.length > 0 && (
        <ul className="mt-4 space-y-2 border-t border-slate-800 pt-4">
          {findings.map((f, i) => (
            <li key={i} className="text-sm text-slate-400">
              <span className={`font-semibold capitalize ${f.severity === 'medium' ? 'text-amber-400' : 'text-rose-400'}`}>
                [{f.severity}]
              </span>{' '}
              {f.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
