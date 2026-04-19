export type ServiceId = 'docker' | 'webui' | 'tts' | 'stt' | 'discord'
export type ServiceGroup = 'infrastructure' | 'audio' | 'channels'
export type ServiceStatus = 'running' | 'stopped' | 'starting' | 'stopping'

export interface ServiceInfo {
  id: ServiceId
  label: string
  description: string
  group: ServiceGroup
  status: ServiceStatus
  pid: number | null
}

export const GROUP_LABELS: Record<ServiceGroup, string> = {
  infrastructure: 'Infrastructure',
  audio: 'Audio',
  channels: 'Channels',
}

export const GROUP_ORDER: ServiceGroup[] = ['infrastructure', 'audio', 'channels']
