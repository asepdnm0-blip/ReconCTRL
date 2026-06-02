import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import ScanInput from '../components/ScanInput'
import { useScans } from '../hooks/useScan'
import { formatDate, statusBadgeClass } from '../utils/scan'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { items, loading, refetch } = useScans({ limit: 8 })
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState(null)

  const handleScan = async ({ target, modules, scan_type }) => {
    setSubmitting(true)
    setSubmitError(null)
    try {
      const { data } = await api.post('/api/v1/scans/', {
        target,
        modules,
        scan_type,
      })
      await refetch()
      navigate(`/scan/${data.id}`)
    } catch (err) {
      setSubmitError(err.response?.data?.detail || 'Failed to start scan')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-6 md:p-8 shadow-xl">
        <h1 className="text-2xl font-bold text-white mb-1">New reconnaissance</h1>
        <p className="text-slate-500 text-sm mb-6">
          Launch distributed scans via Celery workers. Results stream in real time.
        </p>
        {submitError && (
          <p className="mb-4 text-sm text-rose-400 bg-rose-950 border border-rose-900 rounded-lg px-3 py-2">
            {submitError}
          </p>
        )}
        <ScanInput onSubmit={handleScan} loading={submitting} />
      </section>

      <section className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-white">Recent scans</h2>
            <p className="text-xs text-slate-500">Your latest operations</p>
          </div>
          <Link
            to="/history"
            className="text-xs font-semibold text-violet-400 hover:text-violet-300 transition"
          >
            View all →
          </Link>
        </div>
        {loading ? (
          <p className="p-6 text-sm text-slate-500">Loading scans…</p>
        ) : items.length === 0 ? (
          <p className="p-6 text-sm text-slate-500">No scans yet. Start one above.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-500 text-xs uppercase">
                <tr>
                  <th className="px-6 py-3">Target</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Progress</th>
                  <th className="px-6 py-3">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {items.map((scan) => (
                  <tr key={scan.id} className="hover:bg-slate-800/40 group">
                    <td className="px-6 py-4">
                      <Link
                        to={`/scan/${scan.id}`}
                        className="font-mono text-violet-400 group-hover:text-violet-300"
                      >
                        {scan.target}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-slate-500">{scan.scan_type}</td>
                    <td className="px-6 py-4">
                      <span className={`rounded-full border px-2 py-0.5 text-xs font-semibold capitalize ${statusBadgeClass(scan.status)}`}>
                        {scan.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{scan.progress}%</td>
                    <td className="px-6 py-4 text-xs text-slate-500 font-mono">
                      {formatDate(scan.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  )
}
