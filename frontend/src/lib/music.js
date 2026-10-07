import { ref, watch } from 'vue'
import bgmUrl from '../assets/bgm.mp3'

// Background music. Web Audio loops with no gap, unlike <audio loop>.
// Browsers block sound until the first tap or key press, so we start then.
const VOLUME = 0.35
const LOOP_SECONDS = 814154 / 44100 // exact length of the original wav

let saved = null
try { saved = localStorage.getItem('muted') } catch {}
export const muted = ref(saved === '1')

let ctx, gain, started = false

async function start() {
  if (started) return
  started = true
  ctx = new AudioContext()
  gain = ctx.createGain()
  gain.gain.value = muted.value ? 0 : VOLUME
  gain.connect(ctx.destination)
  const data = await (await fetch(bgmUrl)).arrayBuffer()
  const buffer = await ctx.decodeAudioData(data)
  const src = ctx.createBufferSource()
  src.buffer = buffer
  src.loop = true
  src.loopEnd = Math.min(LOOP_SECONDS, buffer.duration)
  src.connect(gain)
  src.start()
}

watch(muted, (m) => {
  try { localStorage.setItem('muted', m ? '1' : '0') } catch {}
  if (gain) gain.gain.setTargetAtTime(m ? 0 : VOLUME, ctx.currentTime, 0.05)
})

export function setupMusic() {
  const kick = () => {
    start().catch(() => (started = false))
    if (ctx?.state === 'suspended' && !document.hidden) ctx.resume()
  }
  window.addEventListener('pointerdown', kick)
  window.addEventListener('keydown', kick)
  document.addEventListener('visibilitychange', () => {
    if (!ctx) return
    if (document.hidden) ctx.suspend()
    else ctx.resume()
  })
}
