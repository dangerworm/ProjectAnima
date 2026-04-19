import { useEffect, useRef, useState, useCallback } from 'react'
import type { ServiceId, ServiceInfo } from '../types'
import { openLogStream } from '../api/client'

interface Props {
  services: ServiceInfo[]
}

type LogClass = 'default' | 'info' | 'warning' | 'error'

function classifyLine(line: string): LogClass {
  const l = line.toLowerCase()
  if (l.includes('[error]') || l.includes('error:') || l.includes('traceback') || l.includes('exception')) return 'error'
  if (l.includes('[warning]') || l.includes('[warn]') || l.includes('warning:')) return 'warning'
  if (l.includes('[info]') || l.includes('info:')) return 'info'
  return 'default'
}

const MAX_LINES = 500

export function LogPanel({ services }: Props) {
  const [selected, setSelected] = useState<ServiceId>('docker')
  const [lines, setLines] = useState<string[]>([])
  const [pinned, setPinned] = useState(true)
  const scrollRef = useRef<HTMLDivElement>(null)
  const esRef = useRef<EventSource | null>(null)

  const connect = useCallback((id: ServiceId) => {
    esRef.current?.close()
    setLines([])
    setPinned(true)

    const es = openLogStream(id)
    esRef.current = es

    es.onmessage = (e: MessageEvent) => {
      const line: string = JSON.parse(e.data)
      if (line === '') return
      setLines(prev => {
        const next = [...prev, line]
        return next.length > MAX_LINES ? next.slice(-MAX_LINES) : next
      })
    }

    es.onerror = () => {
      // EventSource auto-reconnects; no action needed
    }
  }, [])

  useEffect(() => {
    connect(selected)
    return () => { esRef.current?.close() }
  }, [selected, connect])

  // Auto-scroll when pinned
  useEffect(() => {
    if (pinned && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [lines, pinned])

  const handleScroll = () => {
    const el = scrollRef.current
    if (!el) return
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40
    setPinned(atBottom)
  }

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
    setPinned(true)
  }

  const statusFor = (id: ServiceId) =>
    services.find(s => s.id === id)?.status ?? 'stopped'

  return (
    <div className="log-panel">
      <div className="log-tabs">
        {services.map(svc => (
          <button
            key={svc.id}
            className={`log-tab ${svc.status} ${selected === svc.id ? 'active' : ''}`}
            onClick={() => setSelected(svc.id)}
          >
            <span className="log-tab-dot" />
            {svc.label}
          </button>
        ))}
      </div>

      <div
        className="log-body"
        ref={scrollRef}
        onScroll={handleScroll}
      >
        {lines.length === 0 ? (
          <div className="log-empty">No log output yet.</div>
        ) : (
          lines.map((line, i) => (
            <div key={i} className={`log-line ${classifyLine(line)}`}>
              {line}
            </div>
          ))
        )}

        {!pinned && (
          <button className="log-scroll-btn" onClick={scrollToBottom}>
            ↓ scroll to bottom
          </button>
        )}
      </div>
    </div>
  )
}
