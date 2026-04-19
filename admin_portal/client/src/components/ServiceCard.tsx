import { motion } from 'framer-motion'
import type { ServiceInfo } from '../types'

interface Props {
  service: ServiceInfo
  pending: boolean
  onStart: () => void
  onStop: () => void
  index: number
}

export function ServiceCard({ service, pending, onStart, onStop, index }: Props) {
  const effectiveStatus = pending
    ? service.status === 'stopped' ? 'starting' : 'stopping'
    : service.status

  const isRunning = effectiveStatus === 'running'

  return (
    <motion.div
      className={`service-card ${effectiveStatus}`}
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.04 }}
    >
      <div className="status-dot" />

      <div className="card-body">
        <div className="card-label">{service.label}</div>
        <div className="card-desc">{service.description}</div>
        {service.pid != null && (
          <div className="card-pid">PID {service.pid}</div>
        )}
      </div>

      <motion.button
        className={`card-btn ${pending ? 'pending' : isRunning ? 'stop' : 'start'}`}
        disabled={pending}
        onClick={isRunning ? onStop : onStart}
        whileTap={{ scale: 0.95 }}
      >
        {pending
          ? effectiveStatus === 'starting' ? 'Starting…' : 'Stopping…'
          : isRunning ? 'Stop' : 'Start'}
      </motion.button>
    </motion.div>
  )
}
