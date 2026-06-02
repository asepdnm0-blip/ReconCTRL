import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import AIReport from '../components/AIReport'
import ExportButton from '../components/ExportButton'
import ModuleCard from '../components/ModuleCard'
import OWASPMatrix from '../components/OWASPMatrix'
import PortTable from '../components/PortTable'
import ProgressBar from '../components/ProgressBar'
import SubdomainTree from '../components/SubdomainTree'
import { useSSE } from '../hooks/useSSE'
import { useScan } from '../hooks/useScan'
import { formatDate, moduleResult, statusBadgeClass } from '../utils/scan'

export default function ScanPage() {
  const { id } = useParams()
  const { scan, loading, error, refetch } = useScan(id)
  const { modules, overallProgress, isComplete, error: sseError } = useSSE(id)

  const isActive = scan && ['queued', 'running'].includes(scan.status)

  useEffect(() => {
    if (isComplete) {
      refetch()
    }
  }, [isComplete, refetch])

  if (loading && !scan) {
    return <p className="text-slate-500">Loading scan…</p>
  }

  if (error) {
    return (
      <p className="text-rose-400 bg-rose-950 border border-rose-900 rounded-lg p-4">{error}</p>
    )
  }

  if (!scan) return null

  const portData = moduleResult(scan, 'port_scan') || moduleResult(scan, 'nmap')
  const subdomainData = moduleResult(scan, 'subdomain')
  const headerData = moduleResult(scan, 'header')
  const owaspData = moduleResult(scan, 'owasp')
  const osintData = moduleResult(scan, 'osint')
  const aiData = moduleResult(scan, 'ai_summary')

  const modStatus = (name) =>
    scan.modules?.find((m) => m.module_name === name)?.status || 'pending'

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <Link to="/" className="text-xs text-slate-500 hover:text-violet-400 mb-2 inline-block">
            ← Dashboard
          </Link>
          <h1 className="text-2xl font-bold text-white font-mono">{scan.target}</h1>
          <p className="text-sm text-slate-500 mt-1">
            {scan.scan_type} · {formatDate(scan.created_at)}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className={`rounded-full border px-3 py-1 text-sm font-semibold capitalize ${statusBadgeClass(scan.status)}`}>
            {scan.status}
          </span>
          <span className="text-xs text-slate-500 font-mono">
            Progress: <span className="text-violet-300">{overallProgress}%</span>
          </span>
          <Link
            to={`/report/${id}`}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 hover:border-violet-600 hover:text-violet-300 transition"
          >
            Full report
          </Link>
          <ExportButton scan={scan} />
        </div>
      </div>

      {sseError && (
        <p className="text-sm text-amber-400 bg-amber-950 border border-amber-800 rounded-lg px-4 py-2">
          {sseError}
        </p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <ProgressBar
            modules={scan.modules}
            moduleProgress={modules}
            scanStatus={scan.status}
          />
        </div>
        <div className="lg:col-span-2 space-y-4">
          {(portData || scan.modules?.some((m) => m.module_name === 'port_scan' || m.module_name === 'nmap')) && (
            <ModuleCard title="Port scan" subtitle="nmap + NVD CVE enrichment" status={modStatus('port_scan')}>
              <PortTable data={portData} />
            </ModuleCard>
          )}

          {(subdomainData || scan.modules?.some((m) => m.module_name === 'subdomain')) && (
            <ModuleCard title="Subdomains" subtitle="crt.sh + DNS" status={modStatus('subdomain')}>
              <SubdomainTree data={subdomainData} />
            </ModuleCard>
          )}

          {(headerData || scan.modules?.some((m) => m.module_name === 'header')) && (
            <ModuleCard title="HTTP headers" status={modStatus('header')}>
              {headerData ? (
                <div className="space-y-2 max-h-48 overflow-y-auto font-mono text-xs">
                  {Object.entries(headerData.headers || {}).map(([k, v]) => (
                    <div key={k} className="flex gap-2">
                      <span className="text-violet-400 shrink-0">{k}:</span>
                      <span className="text-slate-400 break-all">{v}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">{isActive ? 'Waiting for results…' : 'No data'}</p>
              )}
            </ModuleCard>
          )}

          {(owaspData || scan.modules?.some((m) => m.module_name === 'owasp')) && (
            <ModuleCard title="OWASP analysis" status={modStatus('owasp')}>
              <OWASPMatrix data={owaspData} />
            </ModuleCard>
          )}

          {(osintData || scan.modules?.some((m) => m.module_name === 'osint')) && (
            <ModuleCard title="OSINT" status={modStatus('osint')}>
              {osintData ? (
                <pre className="text-xs text-slate-400 overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(osintData, null, 2)}
                </pre>
              ) : (
                <p className="text-sm text-slate-500">{isActive ? 'Running…' : 'No data'}</p>
              )}
            </ModuleCard>
          )}

          {(aiData || scan.modules?.some((m) => m.module_name === 'ai_summary')) && (
            <ModuleCard title="AI summary" status={modStatus('ai_summary')}>
              <AIReport
                text={aiData?.summary || ''}
                streaming={isActive && !aiData?.summary}
              />
            </ModuleCard>
          )}
        </div>
      </div>
    </div>
  )
}
