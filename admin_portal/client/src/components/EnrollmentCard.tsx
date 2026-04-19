import { useEffect, useRef, useState, useCallback } from 'react'
import { fetchEnrollmentStatus, uploadEnrollmentWav, type Speaker } from '../api/client'

type Phase = 'idle' | 'countdown' | 'recording' | 'processing' | 'done' | 'error'

const MAX_RECORD_SECS = 60
const COUNTDOWN_SECS = 3

function playTone(startHz: number, endHz: number, durationMs: number, volume = 0.18) {
  const ctx = new AudioContext()
  const osc = ctx.createOscillator()
  const gain = ctx.createGain()
  osc.connect(gain)
  gain.connect(ctx.destination)
  osc.type = 'sine'
  osc.frequency.setValueAtTime(startHz, ctx.currentTime)
  osc.frequency.linearRampToValueAtTime(endHz, ctx.currentTime + durationMs / 1000)
  gain.gain.setValueAtTime(volume, ctx.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + durationMs / 1000)
  osc.start(ctx.currentTime)
  osc.stop(ctx.currentTime + durationMs / 1000)
  osc.onended = () => ctx.close()
}

// Decode browser audio (WebM/Opus) via AudioContext and re-encode as 16-bit
// PCM WAV at 16 kHz so soundfile can read it without needing ffmpeg.
async function decodeToWav(blob: Blob): Promise<Blob> {
  const arrayBuffer = await blob.arrayBuffer()
  const ctx = new AudioContext({ sampleRate: 16_000 })
  const audioBuffer = await ctx.decodeAudioData(arrayBuffer)
  await ctx.close()

  const pcm = audioBuffer.getChannelData(0) // mono
  const wavBuffer = new ArrayBuffer(44 + pcm.length * 2)
  const view = new DataView(wavBuffer)
  const write = (off: number, str: string) => {
    for (let i = 0; i < str.length; i++) view.setUint8(off + i, str.charCodeAt(i))
  }
  write(0, 'RIFF')
  view.setUint32(4, 36 + pcm.length * 2, true)
  write(8, 'WAVE')
  write(12, 'fmt ')
  view.setUint32(16, 16, true)    // chunk size
  view.setUint16(20, 1, true)     // PCM
  view.setUint16(22, 1, true)     // mono
  view.setUint32(24, 16_000, true)
  view.setUint32(28, 32_000, true) // byte rate
  view.setUint16(32, 2, true)     // block align
  view.setUint16(34, 16, true)    // bits/sample
  write(36, 'data')
  view.setUint32(40, pcm.length * 2, true)
  let off = 44
  for (let i = 0; i < pcm.length; i++) {
    const s = Math.max(-1, Math.min(1, pcm[i]))
    view.setInt16(off, s < 0 ? s * 0x8000 : s * 0x7fff, true)
    off += 2
  }
  return new Blob([wavBuffer], { type: 'audio/wav' })
}

const PROMPTS = [
  'What did you do last weekend?',
  'Describe somewhere you\'ve visited that you\'d recommend to a friend.',
  'What\'s something you\'ve been thinking about recently?',
]

export function EnrollmentCard() {
  const [speakers, setSpeakers] = useState<Speaker[] | null>(null)
  const [name, setName] = useState('')
  const [phase, setPhase] = useState<Phase>('idle')
  const [countdown, setCountdown] = useState(COUNTDOWN_SECS)
  const [elapsed, setElapsed] = useState(0)
  const [message, setMessage] = useState('')

  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const checkStatus = useCallback(async () => {
    try {
      const { speakers: s } = await fetchEnrollmentStatus()
      setSpeakers(s)
    } catch {
      setSpeakers([])
    }
  }, [])

  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  const clearTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current)
      timerRef.current = null
    }
  }

  const startRecording = async () => {
    setPhase('countdown')
    setCountdown(COUNTDOWN_SECS)
    setMessage('')

    let count = COUNTDOWN_SECS
    timerRef.current = setInterval(() => {
      count -= 1
      setCountdown(count)
      if (count <= 0) {
        clearTimer()
        beginCapture()
      }
    }, 1000)
  }

  const beginCapture = async () => {
    chunksRef.current = []
    let stream: MediaStream
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
    } catch {
      setPhase('error')
      setMessage('Microphone access denied.')
      return
    }

    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    mediaRef.current = recorder
    recorder.ondataavailable = e => { if (e.data.size > 0) chunksRef.current.push(e.data) }
    recorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop())
      handleUpload()
    }

    recorder.start()
    playTone(880, 1320, 120)
    setPhase('recording')
    setElapsed(0)

    let secs = 0
    timerRef.current = setInterval(() => {
      secs += 0.1
      setElapsed(secs)
      if (secs >= MAX_RECORD_SECS) {
        clearTimer()
        recorder.stop()
      }
    }, 100)
  }

  const handleUpload = async () => {
    setPhase('processing')
    try {
      const webmBlob = new Blob(chunksRef.current, { type: 'audio/webm' })
      const wavBlob = await decodeToWav(webmBlob)
      const result = await uploadEnrollmentWav(wavBlob, name.trim())
      setMessage(result.detail)
      setPhase('done')
      await checkStatus()
    } catch (err: unknown) {
      setMessage(err instanceof Error ? err.message : 'Unknown error')
      setPhase('error')
    }
  }

  const cancel = () => {
    clearTimer()
    if (mediaRef.current?.state === 'recording') {
      mediaRef.current.stream.getTracks().forEach(t => t.stop())
      mediaRef.current.ondataavailable = null
      mediaRef.current.onstop = null
      mediaRef.current.stop()
    }
    setPhase('idle')
    setElapsed(0)
  }

  const stopRecording = () => {
    clearTimer()
    if (mediaRef.current?.state === 'recording') {
      playTone(880, 660, 200)
      mediaRef.current.stop()
    }
  }

  const reset = () => {
    setPhase('idle')
    setElapsed(0)
    setMessage('')
  }

  const enrolled = speakers !== null && speakers.length > 0
  const statusDot = speakers === null ? 'stopped' : enrolled ? 'running' : 'stopped'
  const statusText = speakers === null
    ? 'Checking…'
    : enrolled
      ? speakers.map(s => `${s.name} (${s.sessions})`).join(', ')
      : 'None enrolled'

  const nameValid = /^[a-zA-Z0-9_-]+$/.test(name.trim())
  const existingSpeaker = speakers?.find(s => s.name === name.trim())

  return (
    <div className="enrollment-card">
      <div className="enrollment-header">
        <div className="enrollment-title">
          <span className={`log-tab-dot ${statusDot}`} style={{ marginRight: 6 }} />
          Voice Enrollment
        </div>
        <div className="enrollment-status">{statusText}</div>
      </div>

      <div className="enrollment-desc">
        Record ~10 s of speech so Anima can identify who is speaking.
      </div>

      {phase === 'idle' && (
        <div className="enrollment-idle">
          <input
            className="enrollment-name-input"
            type="text"
            placeholder="Name (e.g. drew)"
            value={name}
            onChange={e => setName(e.target.value)}
            maxLength={32}
          />
          <button
            className="enrollment-btn"
            onClick={startRecording}
            disabled={!nameValid}
          >
            {existingSpeaker ? `Add session (${existingSpeaker.sessions} recorded)` : 'Enroll voice'}
          </button>
        </div>
      )}

      {(phase === 'countdown' || phase === 'recording') && (
        <div className="enrollment-script">
          <div className="enrollment-script-label">Answer out loud:</div>
          {PROMPTS.map((p, i) => (
            <div key={i} className="enrollment-script-line">{p}</div>
          ))}
        </div>
      )}

      {phase === 'countdown' && (
        <div className="enrollment-countdown">
          Starting in {countdown}…
          <button className="enrollment-btn-cancel" onClick={cancel}>Cancel</button>
        </div>
      )}

      {phase === 'recording' && (
        <div className="enrollment-recording">
          <div className="enrollment-progress-bar">
            <div className="enrollment-progress-fill" style={{ width: `${Math.min(elapsed / MAX_RECORD_SECS, 1) * 100}%` }} />
          </div>
          <div className="enrollment-recording-label">
            <span>Recording… {Math.floor(elapsed)}s</span>
            {elapsed >= MAX_RECORD_SECS - 5 && <span>Max {MAX_RECORD_SECS}s</span>}
          </div>
          <button className="enrollment-btn" onClick={stopRecording}>Stop recording</button>
        </div>
      )}

      {phase === 'processing' && (
        <div className="enrollment-processing">Processing…</div>
      )}

      {(phase === 'done' || phase === 'error') && (
        <div className={`enrollment-result ${phase}`}>
          <span>{message || (phase === 'done' ? 'Enrolled successfully.' : 'Enrollment failed.')}</span>
          <button className="enrollment-btn-cancel" onClick={reset}>Dismiss</button>
        </div>
      )}
    </div>
  )
}
