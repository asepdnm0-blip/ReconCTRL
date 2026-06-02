import { useCallback, useEffect, useRef, useState } from 'react'
import { getStreamUrl } from '../api/client'
import { SSE_EVENT_TYPES } from '../constants/modules'
import { useAuth } from './useAuth'

const MAX_RETRIES = 3
const RETRY_DELAY_MS = 2000

const INITIAL_MODULE = {
  status: 'pending',
  progress: 0,
  error: null,
  message: null,
}

function parseEventData(raw) {
  try {
    return typeof raw === 'string' ? JSON.parse(raw) : raw
  } catch {
    return { raw }
  }
}

function applyEventToModules(prev, eventType, data) {
  const moduleName = data?.module
  if (!moduleName || moduleName === 'orchestrator') {
    return prev
  }

  const current = prev[moduleName] || { ...INITIAL_MODULE }

  switch (eventType) {
    case 'module_start':
      return {
        ...prev,
        [moduleName]: {
          ...current,
          status: 'running',
          progress: 0,
          error: null,
          message: data.message ?? null,
        },
      }
    case 'module_progress':
      return {
        ...prev,
        [moduleName]: {
          ...current,
          status: 'running',
          progress: data.progress ?? current.progress,
          message: data.message ?? current.message,
        },
      }
    case 'module_complete':
      return {
        ...prev,
        [moduleName]: {
          ...current,
          status: 'completed',
          progress: 100,
          error: null,
          message: data.message ?? null,
        },
      }
    case 'module_error':
      return {
        ...prev,
        [moduleName]: {
          ...current,
          status: 'failed',
          error: data.error ?? 'Module failed',
        },
      }
    default:
      return prev
  }
}

function computeOverallProgress(modules, isComplete) {
  if (isComplete) return 100
  const keys = Object.keys(modules)
  if (keys.length === 0) return 0
  const total = keys.reduce((sum, key) => sum + (modules[key].progress ?? 0), 0)
  return Math.round(total / keys.length)
}

/**
 * Subscribe to scan SSE stream.
 *
 * @param {string | undefined} scanId
 * @returns {{ modules: Record<string, object>, overallProgress: number, isComplete: boolean, error: string | null }}
 */
export function useSSE(scanId) {
  const { getToken, isAuthenticated } = useAuth()
  const [modules, setModules] = useState({})
  const [isComplete, setIsComplete] = useState(false)
  const [error, setError] = useState(null)

  const esRef = useRef(null)
  const retryCountRef = useRef(0)
  const retryTimerRef = useRef(null)
  const completedRef = useRef(false)

  const overallProgress = computeOverallProgress(modules, isComplete)

  const handleEvent = useCallback((eventType, rawData) => {
    const data = parseEventData(rawData)
    const type = eventType || data?.event || 'message'

    if (type === 'scan_complete') {
      completedRef.current = true
      setIsComplete(true)
      if (esRef.current) {
        esRef.current.close()
        esRef.current = null
      }
      return
    }

    setModules((prev) => applyEventToModules(prev, type, data))
  }, [])

  useEffect(() => {
    if (!scanId || !isAuthenticated) {
      return undefined
    }

    const token = getToken()
    if (!token) {
      setError('Not authenticated')
      return undefined
    }

    setModules({})
    setIsComplete(false)
    setError(null)
    completedRef.current = false
    retryCountRef.current = 0

    const url = getStreamUrl(scanId, token)

    const cleanup = () => {
      if (retryTimerRef.current) {
        clearTimeout(retryTimerRef.current)
        retryTimerRef.current = null
      }
      if (esRef.current) {
        esRef.current.close()
        esRef.current = null
      }
    }

    const connect = () => {
      if (completedRef.current) return

      cleanup()
      const es = new EventSource(url)
      esRef.current = es

      es.onopen = () => {
        retryCountRef.current = 0
        setError(null)
      }

      const onEvent = (e) => {
        const type = e.type === 'message' ? undefined : e.type
        handleEvent(type, e.data)
      }

      es.onmessage = onEvent
      SSE_EVENT_TYPES.forEach((evt) => {
        es.addEventListener(evt, onEvent)
      })

      es.onerror = () => {
        es.close()
        esRef.current = null

        if (completedRef.current) return

        if (retryCountRef.current >= MAX_RETRIES) {
          setError('SSE connection failed after 3 retries')
          return
        }

        retryCountRef.current += 1
        setError(`Connection lost. Reconnecting (${retryCountRef.current}/${MAX_RETRIES})…`)

        retryTimerRef.current = setTimeout(() => {
          if (!completedRef.current) {
            connect()
          }
        }, RETRY_DELAY_MS)
      }
    }

    connect()

    return () => {
      completedRef.current = true
      cleanup()
    }
  }, [scanId, isAuthenticated, getToken, handleEvent])

  return {
    modules,
    overallProgress,
    isComplete,
    error,
  }
}
