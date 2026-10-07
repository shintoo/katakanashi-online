import { ref, watch } from 'vue'

// Calm mode: no spinning or wobbling, and simpler card moves.
// Starts on if the device asks for reduced motion and the player hasn't chosen yet.
let saved = null
try { saved = localStorage.getItem('calm') } catch {}
export const calm = ref(saved ? saved === '1' : matchMedia('(prefers-reduced-motion: reduce)').matches)

watch(
  calm,
  (c) => {
    try { localStorage.setItem('calm', c ? '1' : '0') } catch {}
    document.documentElement.classList.toggle('calm', c)
  },
  { immediate: true },
)
