import { useEffect, useState } from 'react'

export default function AIReport({ text = '', streaming = false, speed = 12 }) {
  const [displayed, setDisplayed] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    if (!streaming) {
      setDisplayed(text)
      setDone(true)
      return undefined
    }

    setDisplayed('')
    setDone(false)
    let i = 0
    const id = setInterval(() => {
      i += 1
      setDisplayed(text.slice(0, i))
      if (i >= text.length) {
        clearInterval(id)
        setDone(true)
      }
    }, speed)

    return () => clearInterval(id)
  }, [text, streaming, speed])

  if (!text) {
    return (
      <p className="text-sm text-slate-500 italic">
        AI summary will appear when the ai_summary module completes.
      </p>
    )
  }

  return (
    <div className="relative">
      <div className="prose prose-invert prose-sm max-w-none">
        <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-slate-300 bg-transparent p-0 border-0">
          {displayed}
          {streaming && !done && (
            <span className="inline-block w-2 h-4 ml-0.5 bg-violet-400 animate-pulse align-middle" />
          )}
        </pre>
      </div>
    </div>
  )
}
