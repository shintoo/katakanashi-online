<script setup>
import { computed } from 'vue'
import { INK } from '../lib/colors'

// Placeholder faces until the custom icons exist.
const SHAPES = [
  ['circle', { cx: 50, cy: 52, r: 42 }, 50],
  ['rect', { x: 9, y: 11, width: 82, height: 82, rx: 26 }, 50],
  ['polygon', { points: '50,7 91,30 91,76 50,97 9,76 9,30' }, 52],
  ['path', { d: 'M50 7 C80 7 95 30 91 57 C87 85 66 95 47 93 C22 91 7 74 9 50 C11 25 26 7 50 7Z' }, 50],
  ['path', { d: 'M50 8 Q55 8 58 13 L93 82 Q96 92 85 92 L15 92 Q4 92 7 82 L42 13 Q45 8 50 8Z' }, 66],
]

const props = defineProps({ icon: { type: Object, required: true } })
const shape = computed(() => SHAPES[props.icon.shape % SHAPES.length])
</script>

<template>
  <svg class="avatar" viewBox="0 0 100 100">
    <component :is="shape[0]" v-bind="shape[1]" :fill="icon.color" :stroke="INK" stroke-width="6" stroke-linejoin="round" />
    <circle cx="28" :cy="shape[2] + 12" r="6" fill="#fff" opacity=".45" />
    <circle cx="72" :cy="shape[2] + 12" r="6" fill="#fff" opacity=".45" />
    <circle cx="38" :cy="shape[2]" r="6.5" :fill="INK" />
    <circle cx="62" :cy="shape[2]" r="6.5" :fill="INK" />
    <circle cx="40" :cy="shape[2] - 2" r="2" fill="#fff" />
    <circle cx="64" :cy="shape[2] - 2" r="2" fill="#fff" />
    <path :d="`M43 ${shape[2] + 12} Q50 ${shape[2] + 19} 57 ${shape[2] + 12}`" fill="none" :stroke="INK" stroke-width="4.5" stroke-linecap="round" />
  </svg>
</template>

<style>
.avatar { width: 100%; height: 100%; overflow: visible; display: block; }
</style>
