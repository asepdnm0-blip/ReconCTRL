import { useCallback, useEffect, useState } from 'react'
import api from '../api/client'
import { useAuth } from './useAuth'

const ACTIVE_STATUSES = ['queued', 'running']

export function useScan(scanId, { pollInterval = 3000, enabled = true } = {}) {
  const { isAuthenticated } = useAuth()
  const [scan, setScan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchScan = useCallback(async () => {
    if (!scanId) return null
    const { data } = await api.get(`/api/v1/scans/${scanId}`)
    setScan(data)
    setError(null)
    return data
  }, [scanId])

  useEffect(() => {
    if (!enabled || !scanId || !isAuthenticated) {
      setLoading(false)
      return undefined
    }

    let cancelled = false
    setLoading(true)

    fetchScan()
      .catch((err) => {
        if (!cancelled) {
          setError(err.response?.data?.detail || 'Failed to load scan')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [scanId, enabled, isAuthenticated, fetchScan])

  useEffect(() => {
    if (!scan || !ACTIVE_STATUSES.includes(scan.status)) return undefined

    const timer = setInterval(() => {
      fetchScan().catch(() => {})
    }, pollInterval)

    return () => clearInterval(timer)
  }, [scan?.status, scan?.id, pollInterval, fetchScan])

  return { scan, loading, error, refetch: fetchScan, setScan }
}

export function useScans({ skip = 0, limit = 20 } = {}) {
  const { isAuthenticated } = useAuth()
  const [items, setItems] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchScans = useCallback(async () => {
    const { data } = await api.get('/api/v1/scans/', { params: { skip, limit } })
    setItems(data.items)
    setTotal(data.total)
    setError(null)
    return data
  }, [skip, limit])

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false)
      return undefined
    }
    setLoading(true)
    fetchScans()
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load scans'))
      .finally(() => setLoading(false))
  }, [isAuthenticated, fetchScans])

  return { items, total, loading, error, refetch: fetchScans }
}
