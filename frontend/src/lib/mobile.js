import { onMounted, onUnmounted, ref } from 'vue'

// The game is laid out for a desktop screen. On touch screens smaller than that, we tell the
// browser to pretend the screen is at least this big, and it shrinks the whole page to fit.
const MIN_W = 1180
const MIN_H = 720

export const isTouch = window.matchMedia('(pointer: coarse)').matches
export const isPhone = isTouch && Math.min(screen.width, screen.height) < 600

const meta = document.querySelector('meta[name=viewport]')
const landscape = () => window.innerWidth > window.innerHeight

function fitViewport() {
  // Portrait phones only see the "turn sideways" message, so they keep their normal size.
  let content = 'width=device-width, initial-scale=1'
  if (!(isPhone && !landscape())) {
    const aspect = window.innerWidth / window.innerHeight
    const deviceW = landscape() ? Math.max(screen.width, screen.height) : Math.min(screen.width, screen.height)
    const w = Math.ceil(Math.max(MIN_W, MIN_H * aspect))
    if (w > deviceW) content = `width=${w}`
  }
  content += ', interactive-widget=resizes-visual'
  if (meta.content !== content) meta.content = content
}

function goFullscreen() {
  if (document.fullscreenElement || !document.documentElement.requestFullscreen) return
  document.documentElement
    .requestFullscreen({ navigationUI: 'hide' })
    .then(() => screen.orientation?.lock?.('landscape'))
    .catch(() => {})
}

export function setupMobile() {
  if (!isTouch) return
  fitViewport()
  window.addEventListener('resize', fitViewport)
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
