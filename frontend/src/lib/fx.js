// Screen effects that live outside Vue: shouts, notices, sparks, confetti, flying cards.
import { calm } from './motion'

const wait = (ms) => new Promise((r) => setTimeout(r, ms))
const FUN = ['#ffd23f', '#ff5fa2', '#3ec5ff', '#5ee07a', '#7b5cff']

function el(cls, parent = document.body) {
  const d = document.createElement('div')
  d.className = cls
  parent.appendChild(d)
  return d
}

let shoutEl, shoutTimer
export function shout(text, color = '#fff') {
  shoutEl ??= el('shout')
  shoutEl.textContent = text
  shoutEl.style.setProperty('--sc', color)
  shoutEl.classList.add('on')
  clearTimeout(shoutTimer)
  shoutTimer = setTimeout(() => shoutEl.classList.remove('on'), 1100)
}

let noticeEl, noticeTimer
export function notice(text, kind = '') {
  noticeEl ??= el('notice')
  noticeEl.textContent = text
  noticeEl.className = `notice on ${kind}`
  clearTimeout(noticeTimer)
  noticeTimer = setTimeout(() => noticeEl.classList.remove('on'), 2800)
}

export function burst(rect) {
  if (calm.value) return
  const x = rect.left + rect.width / 2
  const y = rect.top + rect.height / 2
  for (let i = 0; i < 24; i++) {
    const s = el('spark')
    const a = Math.random() * Math.PI * 2
    const r = 60 + Math.random() * 90
    s.style.cssText = `left:${x}px;top:${y}px;background:${[...FUN, '#fff'][i % 6]};--x:${Math.cos(a) * r}px;--y:${Math.sin(a) * r - 40}px`
    setTimeout(() => s.remove(), 900)
  }
}

export function confetti() {
  if (calm.value) return
  for (let i = 0; i < 80; i++) {
    const c = el('confetti')
    c.style.cssText = `left:${Math.random() * 100}vw;background:${FUN[i % 5]};animation-duration:${2 + Math.random() * 2}s;animation-delay:${0.6 + Math.random()}s;border-radius:${i % 3 ? 2 : 50}px`
    setTimeout(() => c.remove(), 5000)
  }
}

// A small card back that flies from one box on screen to another.
export function flyCard(from, to, { num = '', dur = 650, rot = 0, ease = 'cubic-bezier(.6,-0.4,.6,1)', fit = false } = {}) {
  if (!from || !to) return Promise.resolve()
  if (calm.value) {
    rot = 0
    ease = 'ease-in-out'
  }
  const c = el('cb small flying')
  c.innerHTML = `<div class="num">${num}</div>`
  Object.assign(c.style, {
    left: from.left + 'px', top: from.top + 'px', width: from.width + 'px', height: from.height + 'px',
  })
  const sx = fit ? to.width / from.width : (to.width / from.width) * 0.6
  const sy = fit ? to.height / from.height : sx
  const dx = to.left + to.width / 2 - (from.left + from.width / 2)
  const dy = to.top + to.height / 2 - (from.top + from.height / 2)
  c.offsetWidth
  c.style.transition = `transform ${dur}ms ${ease}`
  c.style.transform = `translate(${dx}px,${dy}px) scale(${sx},${sy}) rotate(${rot}deg)`
  return wait(dur).then(() => c.remove())
}

// Animate an element from where `from` was to where it is now, optionally spinning a 3D inner part.
export function flipIn(target, inner, from) {
  if (!target || !from) return
  if (calm.value) {
    target.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 400, easing: 'ease-out' })
    return
  }
  target.style.transformOrigin = '0 0'
  target.style.transition = 'none'
  const to = target.getBoundingClientRect()
  target.style.transform = `translate(${from.left - to.left}px,${from.top - to.top}px) scale(${from.width / to.width})`
  if (inner) {
    inner.style.transition = 'none'
    inner.style.transform = 'rotateY(540deg) rotateX(20deg)'
  }
  target.offsetWidth
  target.style.transition = 'transform .9s cubic-bezier(.2,1.2,.4,1)'
  target.style.transform = ''
  if (inner) {
    inner.style.transition = 'transform 1.1s cubic-bezier(.3,0,.2,1)'
    inner.style.transform = ''
  }
}

export const rectOf = (sel) => document.querySelector(sel)?.getBoundingClientRect()
export { wait }
