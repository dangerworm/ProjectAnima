import type { ServiceId, ServiceInfo } from '../types'

const BASE = 'http://localhost:8765'

export async function fetchServices(): Promise<ServiceInfo[]> {
  const res = await fetch(`${BASE}/api/services`)
  if (!res.ok) throw new Error('Failed to fetch services')
  return res.json()
}

export async function startService(id: ServiceId): Promise<void> {
  const res = await fetch(`${BASE}/api/services/${id}/start`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to start ${id}`)
}

export async function stopService(id: ServiceId): Promise<void> {
  const res = await fetch(`${BASE}/api/services/${id}/stop`, { method: 'POST' })
  if (!res.ok) throw new Error(`Failed to stop ${id}`)
}

export function openLogStream(id: ServiceId): EventSource {
  return new EventSource(`${BASE}/api/services/${id}/logs`)
}
