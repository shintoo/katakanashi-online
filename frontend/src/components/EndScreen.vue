<script setup>
import { computed, onMounted, ref } from 'vue'
import { confetti } from '../lib/fx'
import Avatar from './Avatar.vue'
import SettingsForm from './SettingsForm.vue'

const props = defineProps({ state: Object, send: Function })
const isHost = computed(() => props.state.you === props.state.host)

// Tied players share a place.
const ranked = computed(() => {
  const list = [...props.state.players].sort((a, b) => b.score - a.score)
  return list.map((p) => ({ ...p, place: 1 + list.filter((q) => q.score > p.score).length }))
})
const STEP = [
  { height: 170, color: '#ffd23f' },
  { height: 125, color: '#d7dbe8' },
  { height: 90, color: '#ff9f5a' },
]
// Silver on the left, gold in the middle, bronze on the right. Nobody stands on it with 0 cards.
const onPodium = computed(() => ranked.value.slice(0, 3).filter((p) => p.score > 0))
const podium = computed(() => [1, 0, 2].map((k) => onPodium.value[k] && { ...onPodium.value[k], k }).filter(Boolean))
const rest = computed(() => ranked.value.slice(onPodium.value.length))

const choosing = ref(false)
const settings = ref({ ...props.state.settings })
const confirmClose = ref(false)
const cards = (n) => `${n} card${n === 1 ? '' : 's'}`

onMounted(confetti)
</script>

<template>
  <div class="ov endov">
    <div v-if="!choosing" class="endbox">
      <div class="endtitle">FINAL SCORES</div>
      <div class="podium">
        <div v-for="p in podium" :key="p.id" class="step">
          <span class="mini" :style="{ animationDelay: 0.9 - p.k * 0.3 + 's' }"><Avatar :icon="p.icon" /></span>
          <div class="who">{{ p.name }} <small>{{ cards(p.score) }}</small></div>
          <div class="block" :style="{ height: STEP[p.k].height + 'px', backgroundColor: STEP[p.place - 1]?.color || '#ff9f5a' }">{{ p.place }}</div>
        </div>
      </div>
      <div v-if="rest.length" class="rest">
        <div v-for="p in rest" :key="p.id">{{ p.place }}. {{ p.name }}, {{ cards(p.score) }}</div>
      </div>
      <template v-if="isHost">
        <div class="btns">
          <button class="big" @click="choosing = true">Play again</button>
          <button class="big alt" @click="confirmClose = true">Close room</button>
        </div>
      </template>
      <div v-else class="hostnote">Waiting for the host to start a new game</div>
    </div>

    <div v-else class="panel settings">
      <h3 class="disp">New game, same room</h3>
      <p>Pick your settings. Everyone stays in the room.</p>
      <SettingsForm v-model="settings" />
      <div class="btns">
        <button class="big" :disabled="state.players.length < 2" @click="send('start', { settings })">Start new game</button>
        <button class="big alt" @click="choosing = false">Back</button>
      </div>
    </div>

    <div v-if="confirmClose" class="ov" @click.self="confirmClose = false">
      <div class="panel" style="text-align: center">
        <h3 class="disp">Close the room?</h3>
        <p>This sends everyone back to the title screen.</p>
        <div class="btns">
          <button class="big red" @click="send('close')">Close room</button>
          <button class="big alt" @click="confirmClose = false">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
.endbox { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.endtitle { font-family: 'Lilita One'; font-size: 56px; transform: rotate(-2deg); color: #fff; -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; text-shadow: 0 5px 0 var(--ink); }
.podium { display: flex; align-items: flex-end; gap: 16px; justify-content: center; margin-top: 10px; }
.step { width: 150px; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.step .mini { width: 84px; height: 84px; animation: dropin 0.7s both; }
.step .who { font-weight: 900; font-size: 18px; background: #fff; border: 3px solid var(--ink); border-radius: 10px; padding: 0 10px; white-space: nowrap; }
.step .who small { font-weight: 800; opacity: 0.6; }
.step .block {
  width: 100%; border: 5px solid var(--ink); border-bottom: 0; border-radius: 16px 16px 0 0; display: grid; place-items: start center; padding-top: 8px;
  font-family: 'Lilita One'; font-size: 54px; color: #fff; -webkit-text-stroke: 3px var(--ink); paint-order: stroke fill; text-shadow: 0 4px 0 var(--ink);
  background-image: repeating-linear-gradient(-45deg, rgba(255, 255, 255, 0.25) 0 10px, transparent 10px 20px);
}
@keyframes dropin { from { transform: translateY(-240px); } 60% { transform: translateY(10px); } }
.rest { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.rest div { background: #fff; border: 3px solid var(--ink); border-radius: 12px; padding: 2px 12px; font-weight: 800; }
.hostnote { font-weight: 900; color: #fff; background: var(--ink); border-radius: 999px; padding: 6px 16px; }
.settings { min-width: 560px; }
</style>
