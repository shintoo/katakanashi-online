export const INK = '#2a1f3d'

export const TABLE_COLORS = [
  '#b49cff', '#3ecfb2', '#ff8a7a', '#6cc4ff', '#8ee3a5',
  '#ffd35c', '#ff9ccf', '#ffad5c', '#8fa5ff', '#c6e86b',
]
export const PLAYER_COLORS = [
  '#ffd23f', '#ff5fa2', '#3ec5ff', '#5ee07a', '#ff8c42',
  '#7b5cff', '#ff4d6d', '#2ee6d6', '#c08bff', '#a3e635',
]
export const ICON_SHAPES = 5

export function mix(hex, amt, to = INK) {
  const a = hex.match(/\w\w/g).map((h) => parseInt(h, 16))
  const b = to.match(/\w\w/g).map((h) => parseInt(h, 16))
  return '#' + a.map((v, i) => Math.round(v + (b[i] - v) * amt).toString(16).padStart(2, '0')).join('')
}
