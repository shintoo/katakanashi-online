<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { calm } from '../lib/motion'
import Avatar from './Avatar.vue'

const props = defineProps({ state: Object, send: Function })
const SPIN_MS = 4600

const players = computed(() => props.state.players)
const seg = computed(() => 360 / players.value.length)
const isHost = computed(() => props.state.you === props.state.host)
const wheel = computed(() => props.state.wheel)
const winner = computed(() => players.value.find((p) => p.id === wheel.value?.winner))
const background = computed(
  () => `conic-gradient(${players.value.map((p, i) => `${p.icon.color} ${i * seg.value}deg ${(i + 1) * seg.value}deg`).join(',')})`,
)

const angle = ref(0)
const animate = ref(true)
const done = ref(false)

function aim(instant) {
  const i = players.value.findIndex((p) => p.id === wheel.value.winner)
  animate.value = !instant
  angle.value = 360 * (calm.value ? 0 : 6) + 360 - (i + 0.5) * seg.value + (wheel.value.spin * 0.6 - 0.3) * seg.value
  if (instant) done.value = true
  else setTimeout(() => (done.value = true), SPIN_MS)
}

// If the wheel already spun before this page loaded, jump straight to the result.
onMounted(() => wheel.value?.winner && aim(true))
watch(() => wheel.value?.winner, (w, old) => w && !old && aim(false))

const result = computed(() => {
  if (!wheel.value?.winner) return isHost.value ? '' : 'Waiting for the host to spin...'
  if (!done.value) return 'spinning...'
  return winner.value?.id === props.state.you ? 'You draw first!' : `${winner.value?.name} draws first!`
})
</script>

<template>
  <div class="ov wheelov">
    <div class="wheelbox">
      <h2>Who goes first?</h2>
      <div class="wheelarea">
        <div class="pointer"></div>
        <div class="wheel" :class="{ still: !animate }" :style="{ background, transform: `rotate(${angle}deg)` }">
          <div v-for="(p, i) in players" :key="p.id" class="lab" :style="{ transform: `rotate(${(i + 0.5) * seg}deg)` }">
            <span><span class="mini"><Avatar :icon="p.icon" /></span>{{ p.name }}</span>
          </div>
        </div>
        <div class="hub">GO</div>
      </div>
      <div class="result">{{ result || '\u00a0' }}</div>
      <div v-if="isHost" class="btns">
        <button v-if="!wheel?.winner" class="big" @click="send('spin')">SPIN!</button>
        <button v-else class="big" :disabled="!done" @click="send('begin')">START!</button>
      </div>
    </div>
  </div>
</template>

<style>
.wheelov { background: rgba(42, 31, 61, 0.45); }
.wheelbox { display: flex; flex-direction: column; align-items: center; gap: 18px; }
.wheelbox h2 { margin: 0; font-family: 'Lilita One'; font-weight: 400; font-size: 46px; color: #fff; -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; text-shadow: 0 5px 0 var(--ink); }
.wheelarea { position: relative; width: 400px; height: 400px; }
.pointer { position: absolute; top: -24px; left: 50%; margin-left: -22px; width: 0; height: 0; border-left: 22px solid transparent; border-right: 22px solid transparent; border-top: 44px solid var(--ink); z-index: 3; }
.pointer::after { content: ''; position: absolute; left: -14px; top: -40px; border-left: 14px solid transparent; border-right: 14px solid transparent; border-top: 28px solid var(--yellow); }
.wheel { position: absolute; inset: 0; border-radius: 50%; border: 8px solid var(--ink); box-shadow: 0 10px 0 var(--ink); transition: transform 4.5s cubic-bezier(0.12, 0.7, 0.15, 1); }
.wheel.still { transition: none; }
.wheel .lab { position: absolute; left: 50%; top: 50%; width: 0; height: 0; }
.wheel .lab > span { position: absolute; top: -128px; transform: translate(-50%, -50%); display: flex; flex-direction: column; align-items: center; font-weight: 900; font-size: 18px; white-space: nowrap; }
.wheel .lab .mini { width: 54px; height: 54px; }
.hub { position: absolute; left: 50%; top: 50%; width: 70px; height: 70px; margin: -35px; border-radius: 50%; background: var(--yellow); border: 6px solid var(--ink); z-index: 2; display: grid; place-items: center; font-family: 'Lilita One'; font-size: 20px; }
.result { font-family: 'Lilita One'; font-size: 30px; color: #fff; -webkit-text-stroke: 1.5px var(--ink); paint-order: stroke fill; min-height: 40px; }
</style>
