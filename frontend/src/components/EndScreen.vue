<script setup>
import { computed, onMounted, ref } from 'vue'
import { confetti } from '../lib/fx'
import Avatar from './Avatar.vue'
import SettingsForm from './SettingsForm.vue'

const props = defineProps({ state: Object, send: Function })
const isHost = computed(() => props.state.you === props.state.host)

// Players with the same score share a place, like sports rankings: 1st, 1st, 3rd.
const groups = computed(() => {
  const out = []
  for (const p of [...props.state.players].sort((a, b) => b.score - a.score)) {
    const last = out.at(-1)
    if (last && last.score === p.score) last.players.push(p)
    else out.push({ score: p.score, place: 1 + out.reduce((n, g) => n + g.players.length, 0), players: [p] })
  }
  return out
})
const allTied = computed(() => groups.value.length === 1 && props.state.players.length > 1)
const STEP = {
  1: { height: 170, color: '#ffd23f' },
  2: { height: 125, color: '#d7dbe8' },
  3: { height: 90, color: '#ff9f5a' },
}
// Silver on the left, gold in the middle, bronze on the right. Nobody stands on it with 0 cards.
const onPodium = computed(() =>
  allTied.value ? groups.value : groups.value.filter((g) => g.place <= 3 && g.score > 0),
)
const podium = computed(() => [1, 0, 2].map((k) => onPodium.value[k]).filter(Boolean))
const rest = computed(() => groups.value.slice(onPodium.value.length))

const ORD = ['', '1st', '2nd', '3rd']
const ordinal = (n) => ORD[n] || `${n}th`
const tieLine = computed(() => {
  const score = groups.value[0]?.score
  return score ? `${cards(score)} each. Everybody wins!` : 'Nobody got a single card. Wow. Everybody wins anyway!'
})
const dropDelay = (g, i) => `${0.3 * (4 - g.place) + i * 0.12}s`
const hopDelay = (i) => `${1.6 + i * 0.15}s`

const choosing = ref(false)
const settings = ref({ ...props.state.settings })
const confirmClose = ref(false)
const cards = (n) => `${n} card${n === 1 ? '' : 's'}`
const groupCards = (g) => cards(g.score) + (g.players.length > 1 ? ' each' : '')

onMounted(confetti)
</script>

<template>
  <div class="ov endov">
    <div v-if="!choosing" class="endbox">
      <div class="endtitle">{{ allTied ? "IT'S A TIE!" : 'FINAL SCORES' }}</div>
      <div v-if="allTied" class="tieline">{{ tieLine }}</div>
      <div class="podium" :class="{ everyone: allTied }">
        <div v-for="g in podium" :key="g.place" class="step" :class="{ tied: g.players.length > 1, crowd: g.players.length > 3 }">
          <div class="folks">
            <div v-for="(p, i) in g.players" :key="p.id" class="person">
              <span class="mini" :style="{ animationDelay: dropDelay(g, i) }">
                <Avatar :icon="p.icon" :style="{ animationDelay: hopDelay(i) }" />
              </span>
              <div class="who">{{ p.name }}</div>
            </div>
          </div>
          <div class="block" :style="{ height: STEP[g.place].height + 'px', backgroundColor: STEP[g.place].color }">
            <span v-if="g.players.length > 1" class="tietag">{{ allTied ? 'ALL TIED!' : 'TIE!' }}</span>
            <span>{{ g.place }}</span>
            <small>{{ groupCards(g) }}</small>
          </div>
        </div>
      </div>
      <div v-if="rest.length" class="rest">
        <div v-for="g in rest" :key="g.place">
          {{ ordinal(g.place) }}{{ g.players.length > 1 ? ' (tie)' : '' }}: {{ g.players.map((p) => p.name).join(', ') }}, {{ groupCards(g) }}
        </div>
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
      <h3 class="disp">New game</h3>
      <SettingsForm v-model="settings" />
      <div class="btns">
        <button class="big" :disabled="state.players.length < 2" @click="send('start', { settings })">レッツゴー！</button>
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
.endtitle { font-family: 'Lilita One', 'M PLUS Rounded 1c'; font-size: 56px; transform: rotate(-2deg); color: #fff; -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; text-shadow: 0 5px 0 var(--ink); }
.podium { display: flex; align-items: flex-end; gap: 16px; justify-content: center; margin-top: 10px; }
.step { display: flex; flex-direction: column; align-items: center; gap: 6px; }
.folks { display: flex; gap: 8px; justify-content: center; }
.person { width: 150px; display: flex; flex-direction: column; align-items: center; gap: 6px; }
.step.tied .person { width: 120px; }
.step.crowd .person { width: 92px; }
.step .mini { width: 84px; height: 84px; animation: dropin 0.7s both; }
.step.crowd .mini { width: 62px; height: 62px; }
.step .who { font-weight: 900; font-size: 18px; background: #fff; border: 3px solid var(--ink); border-radius: 10px; padding: 0 10px; white-space: nowrap; max-width: 100%; overflow: hidden; text-overflow: ellipsis; }
.step.crowd .who { font-size: 14px; padding: 0 6px; }
.step .block {
  position: relative; width: 100%; border: 5px solid var(--ink); border-bottom: 0; border-radius: 16px 16px 0 0; display: flex; flex-direction: column; align-items: center; padding-top: 8px;
  font-family: 'Lilita One', 'M PLUS Rounded 1c'; font-size: 54px; line-height: 1; color: #fff; -webkit-text-stroke: 3px var(--ink); paint-order: stroke fill; text-shadow: 0 4px 0 var(--ink);
  background-image: repeating-linear-gradient(-45deg, rgba(255, 255, 255, 0.25) 0 10px, transparent 10px 20px);
}
.step .block small { margin-top: 6px; font-family: inherit; font-size: 14px; letter-spacing: 0.03em; color: var(--ink); -webkit-text-stroke: 0; text-shadow: none; background: rgba(255, 255, 255, 0.85); border-radius: 999px; padding: 2px 10px; }
.tietag {
  position: absolute; bottom: 14px; right: -16px; transform: rotate(8deg); font-size: 20px; -webkit-text-stroke: 0; text-shadow: none;
  background: #ff5fa2; color: #fff; border: 3px solid var(--ink); border-radius: 10px; padding: 3px 10px; box-shadow: 0 3px 0 var(--ink); z-index: 1;
}
.tieline { margin-top: -8px; font-weight: 900; font-size: 20px; color: #fff; background: var(--ink); border-radius: 999px; padding: 6px 18px; }
.podium.everyone .avatar { animation: hop 1.4s ease-in-out infinite both; }
@keyframes dropin { from { transform: translateY(-240px); } 60% { transform: translateY(10px); } }
@keyframes hop { 0%, 40%, 100% { transform: translateY(0); } 20% { transform: translateY(-22px) rotate(-6deg); } }
.rest { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
.rest div { background: #fff; border: 3px solid var(--ink); border-radius: 12px; padding: 2px 12px; font-weight: 800; }
.hostnote { font-weight: 900; color: #fff; background: var(--ink); border-radius: 999px; padding: 6px 16px; }
.settings { min-width: 560px; }
</style>
