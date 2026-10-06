<script setup>
import { INK } from '../lib/colors'

const squig = 'M10 30 Q 30 0 50 30 T 90 30 T 130 30 T 170 30'
const SHAPES = [
  ['star', '#ffd23f', 13, 28, 64, -10],
  ['squig', '#7b5cff', 13, 58, 150, 20],
  ['tri', '#5ee07a', 88, 32, 70, 15],
  ['bolt', '#ffd23f', 93, 58, 60, 10],
  ['star', '#fff', 80, 4, 40, 0],
  ['squig', '#ff5fa2', 38, 2, 130, -6],
  ['kana', '#ff5fa2', 4, 80, 70, -12, 'カ'],
  ['kana', '#3ec5ff', 55, 13, 56, 8, 'タ'],
  ['kana', '#5ee07a', 94, 80, 64, 10, 'ナ'],
  ['kana', '#ffd23f', 70, 70, 52, -8, 'シ'],
]
defineProps({ glow: Boolean })
</script>

<template>
  <div id="burst"></div>
  <div id="bg">
    <div
      v-for="([kind, color, x, y, w, r, char], i) in SHAPES"
      :key="i"
      class="shape"
      :style="{ left: x + '%', top: y + '%', width: w + 'px', height: w + 'px', '--r': r + 'deg', '--d': -i * 0.8 + 's' }"
    >
      <span v-if="kind === 'kana'" class="kana jp" :style="{ color, fontSize: w + 'px' }">{{ char }}</span>
      <svg v-else-if="kind === 'tri'" viewBox="0 0 100 100"><polygon points="50,8 94,90 6,90" :fill="color" :stroke="INK" stroke-width="6" stroke-linejoin="round" /></svg>
      <svg v-else-if="kind === 'star'" viewBox="0 0 100 100"><polygon points="50,6 61,38 95,38 67,58 78,92 50,72 22,92 33,58 5,38 39,38" :fill="color" :stroke="INK" stroke-width="6" stroke-linejoin="round" /></svg>
      <svg v-else-if="kind === 'bolt'" viewBox="0 0 60 100"><polygon points="36,4 6,56 28,56 20,96 54,40 32,40" :fill="color" :stroke="INK" stroke-width="5" stroke-linejoin="round" /></svg>
      <svg v-else viewBox="0 0 180 60">
        <path :d="squig" fill="none" :stroke="INK" stroke-width="18" stroke-linecap="round" />
        <path :d="squig" fill="none" :stroke="color" stroke-width="9" stroke-linecap="round" />
      </svg>
    </div>
  </div>
  <div id="edge" :class="{ on: glow }"></div>
</template>

<style>
#burst {
  position: fixed; inset: -50%; z-index: 0; pointer-events: none;
  background: repeating-conic-gradient(from 0deg at 50% 50%, color-mix(in srgb, var(--table) 88%, white) 0 10deg, var(--table) 10deg 20deg);
  animation: spin 80s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
#bg { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
#bg .shape { position: absolute; transform: rotate(var(--r)); animation: bob 5s ease-in-out infinite; animation-delay: var(--d); }
#bg svg { width: 100%; height: 100%; overflow: visible; }
#bg .kana { display: block; font-weight: 800; line-height: 1; -webkit-text-stroke: 6px var(--ink); paint-order: stroke fill; }
@keyframes bob { 50% { transform: rotate(calc(var(--r) + 12deg)) scale(1.08); } }
#edge {
  position: fixed; inset: 0; pointer-events: none; z-index: 45; opacity: 0; transition: opacity 0.3s;
  box-shadow: inset 0 0 90px 30px rgba(255, 77, 109, 0.9);
}
#edge.on { animation: edgepulse 0.5s ease-in-out infinite alternate; }
@keyframes edgepulse { from { opacity: 0.35; } to { opacity: 1; } }
</style>
