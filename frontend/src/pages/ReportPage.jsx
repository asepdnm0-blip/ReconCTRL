import { Link, useParams } from 'react-router-dom'
import AIReport from '../components/AIReport'
import ExportButton from '../components/ExportButton'
import ModuleCard from '../components/ModuleCard'
import OWASPMatrix from '../components/OWASPMatrix'
import PortTable from '../components/PortTable'
import SubdomainTree from '../components/SubdomainTree'
import { useScan } from '../hooks/useScan'
import { formatDate, moduleResult, statusBadgeClass } from '../utils/scan'

export default function ReportPage() {
  const { id } = useParams()
  const { scan, loading, error } = useScan(id)

  if (loading) return <p className="text-slate-500">Loading report…</p>
  if (error) return <p className="text-rose-400">{error}</p>
  if (!scan) return null

  const portData = moduleResult(scan, 'port_scan')
  const subdomainData = moduleResult(scan, 'subdomain')
  const headerData = moduleResult(scan, 'header')
  const owaspData = moduleResult(scan, 'owasp')
  const osintData = moduleResult(scan, 'osint')
  const aiData = moduleResult(scan, 'ai_summary')

  return (
    <div className="space-y-8 print:space-y-6">
      <div className="print:hidden flex items-center justify-between gap-4">
        <Link to={`/scan/${id}`} className="text-sm text-slate-500 hover:text-violet-400">
          ← Back to live scan
        </Link>
        <ExportButton scan={scan} />
      </div>

      <header className="border-b border-slate-800 pb-6 print:border-slate-400">
        <p className="text-xs uppercase tracking-widest text-violet-400 font-semibold mb-2">
          ReconCTRL Security Report
        </p>
        <h1 className="text-3xl font-bold text-white print:text-black">{scan.target}</h1>
        <div className="mt-3 flex flex-wrap gap-4 text-sm text-slate-400 print:text-slate-700">
          <span>ID: <span className="font-mono text-slate-300">{scan.id}</span></span>
          <span>Type: {scan.scan_type}</span>
          <span className={`capitalize rounded border px-2 py-0.5 text-xs ${statusBadgeClass(scan.status)}`}>
            {scan.status}
          </span>
          <span>Created: {formatDate(scan.created_at)}</span>
          {scan.completed_at && <span>Completed: {formatDate(scan.completed_at)}</span>}
        </div>
      </header>

      {aiData?.summary && (
        <section>
          <h2 className="text-lg font-bold text-white mb-4 print:text-black">Executive summary</h2>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 print:border-slate-300 print:bg-white">
            <AIReport text={aiData.summary} streaming={false} />
          </div>
        </section>
      )}

      {portData && (
        <ModuleCard title="Port scan results" status="completed" defaultOpen>
          <PortTable data={portData} />
        </ModuleCard>
      )}

      {subdomainData && (
        <ModuleCard title="Subdomain enumeration" status="completed" defaultOpen>
          <SubdomainTree data={subdomainData} />
        </ModuleCard>
      )}

      {headerData && (
        <ModuleCard title="HTTP security headers" status="completed">
          <pre className="text-xs text-slate-400 whitespace-pre-wrap print:text-slate-800">
            {JSON.stringify(headerData.headers, null, 2)}
          </pre>
        </ModuleCard>
      )}

      {owaspData && (
        <ModuleCard title="OWASP Top 10 matrix" status="completed">
          <OWASPMatrix data={owaspData} />
        </ModuleCard>
      )}

      {osintData && (
        <ModuleCard title="OSINT" status="completed">
          <pre className="text-xs text-slate-400 whitespace-pre-wrap print:text-slate-800">
            {JSON.stringify(osintData, null, 2)}
          </pre>
        </ModuleCard>
      )}

      <section className="print:hidden rounded-xl border border-slate-800 bg-slate-950 p-4">
        <h3 className="text-sm font-semibold text-slate-400 mb-2">Raw results summary</h3>
        <pre className="text-xs text-slate-500 overflow-x-auto max-h-64">
          {JSON.stringify(scan.results_summary, null, 2)}
        </pre>
      </section>
    </div>
  )
}
