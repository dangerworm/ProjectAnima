import { useEffect, useRef, useState, useCallback } from 'react'
import { fetchEnrollmentStatus, uploadEnrollmentWav } from '../api/client'

type Phase = 'idle' | 'countdown' | 'recording' | 'processing' | 'done' | 'error'

const RECORD_SECS = 10
const COUNTDOWN_SECS = 3

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
  'The quick brown fox jumps over the lazy dog.',
  'Good morning. I have been thinking about what it means to remember.',
  'Project Anima is learning to recognise the people it talks with.',
]

export function EnrollmentCard() {
  const [enrolledNames, setEnrolledNames] = useState<string[] | null>(null)
  const [name, setName] = useState('')
  const [phase, setPhase] = useState<Phase>('idle')
  const [countdown, setCountdown] = useState(COUNTDOWN_SECS)
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('')

  const mediaRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const checkStatus = useCallback(async () => {
    try {
      const { names } = await fetchEnrollmentStatus()
      setEnrolledNames(names)
    } catch {
      setEnrolledNames([])
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
    setPhase('recording')
    setProgress(0)

    let elapsed = 0
    timerRef.current = setInterval(() => {
      elapsed += 0.1
      setProgress(Math.min(elapsed / RECORD_SECS, 1))
      if (elapsed >= RECORD_SECS) {
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
      mediaRef.current.stop()
    }
    setPhase('idle')
    setProgress(0)
  }

  const reset = () => {
    setPhase('idle')
    setProgress(0)
    setMessage('')
  }

  const enrolled = enrolledNames !== null && enrolledNames.length > 0
  const statusDot = enrolledNames === null ? 'stopped' : enrolled ? 'running' : 'stopped'
  const statusText = enrolledNames === null
    ? 'Checking…'
    : enrolled
      ? enrolledNames.join(', ')
      : 'None enrolled'

  const nameValid = /^[a-zA-Z0-9_-]+$/.test(name.trim())

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
            {enrolledNames?.includes(name.trim()) ? 'Re-enroll' : 'Enroll voice'}
          </button>
        </div>
      )}

      {(phase === 'countdown' || phase === 'recording') && (
        <div className="enrollment-script">
          <div className="enrollment-script-label">Read aloud:</div>
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
            <div className="enrollment-progress-fill" style={{ width: `${progress * 100}%` }} />
          </div>
          <div className="enrollment-recording-label">
            Recording… {Math.ceil(RECORD_SECS - progress * RECORD_SECS)}s remaining
          </div>
          <button className="enrollment-btn-cancel" onClick={cancel}>Stop early</button>
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
