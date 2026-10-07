import { onMounted, onUnmounted, reactive, ref } from 'vue'

// The game is laid out for a desktop screen. When the window is smaller than this, the whole game
// is drawn on a "stage" this big (or wider, to match the screen's shape) and shrunk to fit.
// We do the shrinking ourselves because phones ignore the viewport tag while in full screen.
const MIN_W = 1180
const MIN_H = 720

export const isTouch = window.matchMedia('(pointer: coarse)').matches
export const isPhone = isTouch && Math.min(screen.width, screen.height) < 600

const landscape = () => window.innerWidth > window.innerHeight

export const stage = reactive({ w: window.innerWidth, h: window.innerHeight, scale: 1 })

function fitStage() {
  const w = window.innerWidth
  const h = window.innerHeight
  // Portrait phones only see the "turn sideways" message, so they keep their normal size.
  const scale = isPhone && !landscape() ? 1 : Math.min(1, w / MIN_W, h / MIN_H)
  stage.scale = scale
  stage.w = w / scale
  stage.h = h / scale
  const root = document.documentElement.style
  root.setProperty('--sw', `${stage.w}px`)
  root.setProperty('--sh', `${stage.h}px`)
  root.setProperty('--scale', scale)
}

// A box on screen, measured in stage pixels.
export function stageRect(el) {
  const r = el?.getBoundingClientRect()
  if (!r) return
  const s = stage.scale
  return { left: r.left / s, top: r.top / s, width: r.width / s, height: r.height / s }
}

function goFullscreen() {
  if (document.fullscreenElement || !document.documentElement.requestFullscreen) return
  document.documentElement
    .requestFullscreen({ navigationUI: 'hide' })
    .then(() => screen.orientation?.lock?.('landscape'))
    .catch(() => {})
}

export function setupMobile() {
  fitStage()
  window.addEventListener('resize', fitStage)
  // Browsers only allow full screen right after a tap, so ask on every tap until we're in it.
  if (isPhone) window.addEventListener('click', goFullscreen)
}

export function usePortrait() {
  const portrait = ref(isPhone && !landscape())
  const update = () => (portrait.value = isPhone && !landscape())
  onMounted(() => window.addEventListener('resize', update))
  onUnmounted(() => window.removeEventListener('resize', update))
  return portrait
}
