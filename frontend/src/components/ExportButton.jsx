export default function ExportButton({ scan, className = '' }) {
  const downloadJson = () => {
    if (!scan) return
    const blob = new Blob([JSON.stringify(scan, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `reconctrl-${scan.target}-${scan.id}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  const downloadPdf = () => {
    window.print()
  }

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      <button
        type="button"
        onClick={downloadJson}
        disabled={!scan}
        className="rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-medium text-slate-200 hover:border-violet-600 hover:bg-violet-950 hover:text-violet-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        Export JSON
      </button>
      <button
        type="button"
        onClick={downloadPdf}
        disabled={!scan}
        className="rounded-lg border border-violet-700 bg-violet-950 px-4 py-2 text-sm font-medium text-violet-200 hover:bg-violet-900 disabled:opacity-50 disabled:cursor-not-allowed transition print:hidden"
      >
        Export PDF (Print)
      </button>
    </div>
  )
}
