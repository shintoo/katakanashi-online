<script setup>
import { computed } from 'vue'
import { mix } from '../lib/colors'
import Avatar from './Avatar.vue'

const props = defineProps({
  player: Object,
  offset: Number,
  describer: Boolean,
  holding: Boolean,
  heldNumber: Number,
  target: Boolean,
  host: Boolean,
  me: Boolean,
})
const emit = defineEmits(['give'])

const c = computed(() => props.player.icon.color)
const dark = computed(() => mix(c.value, 0.3))
const light = computed(() => mix(c.value, 0.45, '#ffffff'))
const fan = computed(() => Math.min(props.player.score, 5))
</script>

<template>
  <div
    class="pod"
    :data-pod="player.id"
    :class="{ describer, holding, target, away: !player.connected, me }"
    :style="{ '--o': offset, '--o2': offset * offset }"
    @click="target && emit('give', player.id)"
  >
    <div class="lift">
      <div v-if="holding" class="held"><div class="cb small"><div class="num">{{ heldNumber }}</div></div></div>
      <div class="give">与える</div>
      <svg class="sh-desk" viewBox="0 0 180 112">
        <ellipse cx="90" cy="108" rx="78" ry="6" fill="#2a1f3d" opacity=".25" />
        <path d="M16 24 L164 24 L152 106 L28 106 Z" :fill="c" stroke="#2a1f3d" stroke-width="4" stroke-linejoin="round" />
        <path d="M25 33 L155 33 L154 40 L26 40 Z" :fill="light" />
        <path d="M34 96 L146 96" :stroke="dark" stroke-width="5" stroke-linecap="round" />
        <rect x="4" y="4" width="172" height="24" rx="12" :fill="dark" stroke="#2a1f3d" stroke-width="4" />
        <circle v-for="k in 8" :key="k" class="bulb" :cx="20 + (k - 1) * 20" cy="16" r="3.5" />
      </svg>
      <div class="won">
        <i v-for="k in fan" :key="k" class="wc" :style="{ '--k': k - 1, '--m': (fan - 1) / 2 }"></i>
      </div>
      <div class="av"><Avatar :icon="player.icon" /></div>
      <div class="plate">{{ player.name }}</div>
      <div class="score">{{ player.score }}</div>
      <div v-if="!player.connected" class="podtag grey">AWAY</div>
      <div v-else-if="host" class="podtag">HOST</div>
    </div>
  </div>
</template>

<style>
.podiums { zoom: var(--pz, 1); display: flex; justify-content: center; align-items: flex-end; gap: 26px; padding: 0 20px 14px; position: relative; z-index: 3; }
.pod { position: relative; transition: transform 0.3s; transform: translateY(calc(var(--o2) * -9px)) rotate(calc(var(--o) * -4deg)); }
.lift { position: relative; width: 180px; height: 190px; }
.lift > * { position: absolute; }
.pod.target { cursor: pointer; }
.pod.target .lift { animation: podhop 1.2s ease-in-out infinite; }
.pod.target:hover .lift { animation: none; transform: translateY(-14px); }
@keyframes podhop { 50% { transform: translateY(-6px); } }
.pod.away .lift { opacity: 0.5; filter: grayscale(0.6); }
.sh-desk { left: 0; bottom: 0; width: 180px; height: 112px; z-index: 2; overflow: visible; }
.av { width: 76px; height: 76px; left: 52px; bottom: 92px; z-index: 1; }
.pod.describer .av { filter: drop-shadow(0 0 8px #fff) drop-shadow(0 0 16px #fff); }
.plate { left: 50%; transform: translateX(-50%); bottom: 58px; z-index: 3; background: #fff; border: 3px solid var(--ink); border-radius: 10px; padding: 0 12px; font-weight: 900; font-size: 17px; white-space: nowrap; }
.pod.describer .plate { background: var(--yellow); }
.pod.me .plate { outline: 3px dashed #fff; outline-offset: 2px; }
.score {
  font-family: 'Lilita One', 'M PLUS Rounded 1c'; text-align: center; left: 50%; transform: translateX(-50%); bottom: 10px; z-index: 3;
  font-size: 34px; line-height: 1.15; color: #ffea7a; background: var(--ink); border-radius: 12px; min-width: 64px; padding: 0 14px;
  text-shadow: 0 0 10px #ffd23f;
}
.pod.got .score { animation: bump 0.6s; }
@keyframes bump { 40% { transform: translateX(-50%) scale(1.4) rotate(-6deg); } }
.won { right: 30px; bottom: 100px; z-index: 3; width: 24px; height: 34px; }
.won .wc {
  position: absolute; bottom: 0; left: 0; width: 20px; height: 28px; border: 2.5px solid var(--ink); border-radius: 5px;
  background: var(--orange); transform-origin: bottom center; transform: rotate(calc((var(--k) - var(--m)) * 14deg));
}
.held { width: 64px; height: 90px; left: 50%; margin-left: -32px; bottom: 166px; z-index: 6; }
.held .cb { animation: hold 2.4s ease-in-out infinite; }
@keyframes hold { 0%, 100% { transform: rotate(-6deg); } 50% { transform: rotate(5deg) translateY(-5px); } }
.give {
  display: none; left: 50%; transform: translateX(-50%); bottom: 174px; background: var(--green); border: 3px solid var(--ink);
  border-radius: 10px; font-family: 'Lilita One', 'M PLUS Rounded 1c'; font-size: 16px; padding: 1px 10px; z-index: 7; white-space: nowrap; box-shadow: 0 3px 0 var(--ink);
}
.pod.target:hover .give { display: block; }
@media (hover: none) { .pod.target .give { display: block; bottom: 84px; } }
.bulb { fill: #fff6c2; animation: blinkf 1s infinite; }
.bulb:nth-of-type(even) { animation-delay: 0.5s; }
.pod.describer .bulb { animation-duration: 0.35s; }
@keyframes blinkf { 50% { fill: rgba(255, 255, 255, 0.25); } }
.podtag { left: 14px; bottom: 112px; z-index: 3; font-size: 10px; font-weight: 900; letter-spacing: 0.15em; background: var(--purple); color: #fff; border: 2px solid var(--ink); border-radius: 6px; padding: 0 5px; }
.podtag.grey { background: #8a8299; }
</style>
