import { useEffect, useState, useCallback } from 'react'
import { AnimatePresence } from 'framer-motion'
import type { ServiceId, ServiceInfo } from './types'
import { GROUP_ORDER, GROUP_LABELS } from './types'
import { fetchServices, startService, stopService } from './api/client'
import { ServiceCard } from './components/ServiceCard'
import { LogPanel } from './components/LogPanel'
import { EnrollmentCard } from './components/EnrollmentCard'

const POLL_MS = 2000

export default function App() {
  const [services, setServices] = useState<ServiceInfo[]>([])
  const [pending, setPending] = useState<Set<ServiceId>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [selectedLog, setSelectedLog] = useState<ServiceId>('docker')

  const poll = useCallback(async () => {
    try {
      const data = await fetchServices()
      setServices(data)
      setError(null)
    } catch {
      setError('Cannot reach admin server — is server.py running?')
    }
  }, [])

  useEffect(() => {
    poll()
    const id = setInterval(poll, POLL_MS)
    return () => clearInterval(id)
  }, [poll])

  const handleStart = async (id: ServiceId) => {
    setSelectedLog(id)
    setPending(p => new Set(p).add(id))
    try {
      await startService(id)
    } finally {
      setPending(p => { const n = new Set(p); n.delete(id); return n })
    }
    poll()
  }

  const handleStop = async (id: ServiceId) => {
    setPending(p => new Set(p).add(id))
    try {
      await stopService(id)
    } finally {
      setPending(p => { const n = new Set(p); n.delete(id); return n })
    }
    poll()
  }

  const runningCount = services.filter(s => s.status === 'running').length

  return (
    <div className="app">
      <header className="header">
        <div className="header-title">
          <h1>Anima</h1>
          <span>Control Panel</span>
        </div>
        <div className="header-status">
          <span className={`header-status-dot ${error ? 'offline' : ''}`} />
          {error ? 'Server offline' : `${runningCount} / ${services.length} running`}
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="main">
        <aside className="service-panel">
          <AnimatePresence>
            {GROUP_ORDER.map(group => {
              const groupServices = services.filter(s => s.group === group)
              if (groupServices.length === 0) return null
              return (
                <div key={group} className="service-group">
                  <div className="group-label">{GROUP_LABELS[group]}</div>
                  {groupServices.map((svc, i) => (
                    <ServiceCard
                      key={svc.id}
                      service={svc}
                      pending={pending.has(svc.id)}
                      onStart={() => handleStart(svc.id)}
                      onStop={() => handleStop(svc.id)}
                      onFocus={() => setSelectedLog(svc.id)}
                      index={i}
                    />
                  ))}
                </div>
              )
            })}
          </AnimatePresence>
        </aside>

        <div className="right-panel">
          <EnrollmentCard />
          <LogPanel services={services} selected={selectedLog} onSelect={setSelectedLog} />
        </div>
      </div>
    </div>
  )
}
