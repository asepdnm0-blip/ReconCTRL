import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { useScans } from '../hooks/useScan'
import { formatDate, statusBadgeClass } from '../utils/scan'

export default function HistoryPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const { items, total, loading, error, refetch } = useScans({ limit: 100 })

  const filtered = useMemo(() => {
    return items.filter((scan) => {
      const matchSearch =
        !search ||
        scan.target.toLowerCase().includes(search.toLowerCase()) ||
        scan.scan_type.toLowerCase().includes(search.toLowerCase())
      const matchStatus = statusFilter === 'all' || scan.status === statusFilter
      return matchSearch && matchStatus
    })
  }, [items, search, statusFilter])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Scan history</h1>
        <p className="text-sm text-slate-500 mt-1">{total} total scans</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <input
          type="search"
          placeholder="Search target or type…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-200 focus:border-violet-500 focus:outline-none"
        >
          <option value="all">All statuses</option>
          <option value="queued">Queued</option>
          <option value="running">Running</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <button
          type="button"
          onClick={() => refetch()}
          className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm text-slate-300 hover:border-violet-600 hover:text-violet-300 transition"
        >
          Refresh
        </button>
      </div>

      {error && (
        <p className="text-rose-400 bg-rose-950 border border-rose-900 rounded-lg p-3 text-sm">{error}</p>
      )}

      <div className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden">
        {loading ? (
          <p className="p-6 text-slate-500 text-sm">Loading…</p>
        ) : filtered.length === 0 ? (
          <p className="p-6 text-slate-500 text-sm">No scans match your filters.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-6 py-3">Target</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Progress</th>
                  <th className="px-6 py-3">Created</th>
                  <th className="px-6 py-3">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map((scan) => (
                  <tr key={scan.id} className="hover:bg-slate-800/40">
                    <td className="px-6 py-4 font-mono text-violet-400">{scan.target}</td>
                    <td className="px-6 py-4 text-slate-500">{scan.scan_type}</td>
                    <td className="px-6 py-4">
                      <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold capitalize ${statusBadgeClass(scan.status)}`}>
                        {scan.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{scan.progress}%</td>
                    <td className="px-6 py-4 text-xs text-slate-500">{formatDate(scan.created_at)}</td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <Link
                          to={`/scan/${scan.id}`}
                          className="text-xs text-violet-400 hover:text-violet-300"
                        >
                          Live
                        </Link>
                        <Link
                          to={`/report/${scan.id}`}
                          className="text-xs text-slate-400 hover:text-slate-200"
                        >
                          Report
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
