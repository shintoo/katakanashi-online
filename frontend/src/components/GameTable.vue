<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import Desk from './Desk.vue'

const props = defineProps({ state: Object, remaining: Number, send: Function })

const players = computed(() => props.state.players)
const byId = (id) => players.value.find((p) => p.id === id)
const me = computed(() => byId(props.state.you))
const describer = computed(() => byId(props.state.describer))
const isDescriber = computed(() => props.state.you === props.state.describer && props.state.phase === 'playing')
const isHost = computed(() => props.state.you === props.state.host)
const hand = computed(() => props.state.hand)
const playing = computed(() => props.state.phase === 'playing')

// The highlight waits for the card to finish flipping in.
const revealed = ref(!!hand.value?.words)
let revealTimer
watch(
  () => hand.value?.words,
  (words, old) => {
    clearTimeout(revealTimer)
    if (!words) revealed.value = false
    else if (!old) revealTimer = setTimeout(() => (revealed.value = true), 1100)
  },
)
const targetWord = computed(() => hand.value?.words?.[hand.value.target - 1])
const peek = ref(false)
watch(hand, (h) => !h && (peek.value = false))

const limit = computed(() => props.state.settings.time_limit)
const secs = computed(() => (props.remaining == null ? limit.value : Math.ceil(props.remaining)))
const pct = computed(() => (props.remaining == null || !limit.value ? 100 : (props.remaining / limit.value) * 100))
const timerClass = computed(() => {
  if (props.remaining == null) return ''
  return secs.value <= 10 ? 't-low' : secs.value <= 20 ? 't-warn' : ''
})

const name = (p) => (p ? p.name.toUpperCase() : '')
const watchTitle = computed(() => {
  const d = describer.value
  if (props.state.phase === 'round_end') return 'ROUND OVER'
  if (hand.value) return `${name(d)} IS DESCRIBING`
  return `${name(d)} IS ABOUT TO DRAW`
})
const watchSub = computed(() => {
  if (props.state.phase === 'round_end') return isHost.value ? 'Next round, or end game?' : 'Waiting for the host'
  if (hand.value) return '推測して！'
  if (!describer.value || describer.value.connected) return 'Get ready to guess'
  return `Waiting for ${describer.value.name} to come back...`
})
const drawLabel = computed(() => (isDescriber.value ? 'Your turn: draw!' : `${describer.value?.name} draws next`))

// Keep the desks in a gentle arc and shrink the row when there are lots of players.
const width = ref(window.innerWidth)
const onResize = () => (width.value = window.innerWidth)
onMounted(() => window.addEventListener('resize', onResize))
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  clearTimeout(revealTimer)
})
const podZoom = computed(() => Math.min(1, (width.value - 40) / (players.value.length * 206)))
function offset(i) {
  const half = (players.value.length - 1) / 2
  return half ? ((i - half) / half) * Math.min(half, 2) : 0
}

function draw() {
  if (isDescriber.value && !hand.value) props.send('draw')
}
</script>

<template>
  <div class="table" :class="[timerClass, { ended: state.phase === 'ended' }]">
    <section class="stage" :class="{ lit: hand }">
      <div class="spot"></div>

      <div v-if="state.phase === 'round_end'" class="roundover">
        <div class="ro-title disp">ROUND {{ state.round }} COMPLETE!</div>
        <template v-if="isHost">
          <div class="ro-sub">You're the host. Keep going, or wrap it up?</div>
          <div class="btns">
            <button class="big" @click="send('next_round')">Next round</button>
            <button class="big alt" @click="send('end_game')">End game</button>
          </div>
        </template>
        <div v-else class="ro-sub">Waiting for the host to start the next round</div>
      </div>

      <div class="piles">
        <div class="pilecol">
          <div id="deck" class="deck" :class="{ locked: !isDescriber || hand, empty: !state.deck_count }" @click="draw">
            <div v-if="playing && !hand" class="drawme">{{ drawLabel }}</div>
            <div v-if="state.deck_count > 2" class="cb l1"><div class="num"></div></div>
            <div v-if="state.deck_count > 1" class="cb l2"><div class="num"></div></div>
            <div v-if="state.deck_count" id="deckTop" class="cb" :class="{ reveal: isDescriber && hand && revealed }">
              <div class="num">{{ state.top_number }}</div>
            </div>
          </div>
          <div class="decktag">{{ state.deck_count }} LEFT</div>
        </div>
        <div class="pilecol">
          <div id="discard" class="discard" :class="{ empty: !state.discard_count }">
            <div v-if="state.discard_count > 1" class="cb small under"><div class="num"></div></div>
            <div v-if="state.discard_count" class="cb small"><div class="num">{{ state.discard_number }}</div></div>
          </div>
          <div class="decktag light">DISCARD {{ state.discard_count }}</div>
        </div>
      </div>

      <template v-if="isDescriber">
        <div class="cardcol">
          <div class="slot">
            your card goes here
            <div v-if="hand" id="hand" class="hand">
              <div id="handInner" class="inner">
                <div class="f front">
                  <div class="head"><span class="jp">カタカナシ</span></div>
                  <ol class="words jp">
                    <li
                      v-for="(w, i) in hand.words"
                      :key="i"
                      :class="revealed && { hl: i + 1 === hand.target, dim: i + 1 !== hand.target }"
                    >
                      <span class="n">{{ i + 1 }}</span>{{ w[0] }}
                    </li>
                  </ol>
                </div>
                <div class="f back cb"><div class="num">{{ hand.number }}</div></div>
              </div>
            </div>
          </div>
          <div class="tbar" :class="{ on: hand && state.time_left != null }">
            <div class="fill" :style="{ width: pct + '%' }"></div>
            <span class="tnum">{{ secs }}</span>
          </div>
        </div>

        <div class="sticky" :class="{ on: hand && revealed }">
          <div class="tape"></div>
          <div class="note" :class="{ flip: peek }" @click="peek = !peek">
            <div class="side s1"><div class="q">?</div><b>Don't know it?</b><span>Tap to peek at the meaning</span></div>
            <div v-if="targetWord" class="side s2">
              <div class="kw jp">{{ targetWord[0] }}</div>
              <div class="rom">{{ targetWord[1] }}</div>
              <div class="def">{{ targetWord[2] }}</div>
            </div>
          </div>
          <div class="rule">NO KATAKANA ALLOWED!</div>
          <button class="pass" @click="send('give', { to: null })">Nobody got it</button>
        </div>
      </template>

      <div v-else-if="playing || state.phase === 'round_end'" class="watch">
        <div v-if="limit" class="bigclock" :class="{ idle: !hand || state.time_left == null }" :style="{ '--p': pct }">
          <span>{{ secs }}</span>
        </div>
        <div class="wtitle disp">{{ watchTitle }}</div>
        <div class="wsub">{{ watchSub }}</div>
      </div>
    </section>

    <section class="podiums" :style="{ '--pz': podZoom }">
      <Desk
        v-for="(p, i) in players"
        :key="p.id"
        :player="p"
        :offset="offset(i)"
        :describer="p.id === state.describer && state.phase === 'playing'"
        :holding="!!hand && p.id === state.describer && !isDescriber"
        :held-number="hand?.number"
        :target="isDescriber && !!hand && p.id !== state.you"
        :host="p.id === state.host"
        :me="p.id === state.you"
        @give="send('give', { to: $event })"
      />
    </section>
  </div>
</template>

<style>
.table { position: relative; display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.stage { position: relative; display: flex; align-items: center; justify-content: center; gap: 50px; min-height: 0; }
.spot {
  position: absolute; left: 50%; top: 50%; width: 760px; height: 540px; transform: translate(-50%, -50%); border-radius: 50%;
  background: radial-gradient(closest-side, rgba(255, 255, 255, 0.75), rgba(255, 255, 255, 0)); opacity: 0.35; transition: opacity 0.6s; pointer-events: none;
}
.stage.lit .spot { opacity: 1; }
.table.ended .stage { visibility: hidden; }

.piles { position: relative; display: flex; align-items: flex-end; gap: 22px; }
.pilecol { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.deck { position: relative; width: 170px; height: 238px; cursor: pointer; }
.deck .l1 { transform: translate(0, 12px); }
.deck .l2 { transform: translate(0, 6px); }
#deckTop { transition: transform 0.2s; }
.deck:hover #deckTop { transform: translateY(-10px) rotate(3deg); }
.deck.locked { cursor: default; }
.deck.locked:hover #deckTop { transform: none; }
.deck.empty { border: 5px dashed rgba(42, 31, 61, 0.35); border-radius: 20px; }
.deck.shuffling .l1 { animation: shufL 0.25s 3; }
.deck.shuffling .l2 { animation: shufR 0.25s 3; }
@keyframes shufL { 50% { transform: translate(-40px, 12px) rotate(-8deg); } }
@keyframes shufR { 50% { transform: translate(40px, 6px) rotate(8deg); } }
#deckTop.reveal { background-color: var(--yellow); }
#deckTop.reveal .num { color: #fff; transform: scale(1.35) rotate(-8deg); }
#deckTop.reveal::after { content: ''; position: absolute; inset: -5px; border-radius: 20px; border: 6px solid #fff; animation: ping 1s infinite; }
@keyframes ping { to { transform: scale(1.25); opacity: 0; } }
.decktag { font-family: 'Lilita One'; font-size: 17px; background: var(--ink); color: #fff; border-radius: 12px; padding: 2px 14px; white-space: nowrap; }
.decktag.light { background: #fff; color: var(--ink); border: 3px solid var(--ink); }
.drawme {
  position: absolute; top: -58px; left: 50%; transform: translateX(-50%); font-family: 'Lilita One'; font-size: 21px;
  background: var(--green); border: 4px solid var(--ink); border-radius: 14px; padding: 2px 14px; box-shadow: 0 4px 0 var(--ink);
  animation: hop 1s ease-in-out infinite; white-space: nowrap; z-index: 3;
}
.deck.locked .drawme { background: #fff; }
@keyframes hop { 50% { margin-top: -8px; } }
.discard { position: relative; width: 120px; height: 168px; transform: rotate(7deg); }
.discard.empty { border: 4px dashed rgba(42, 31, 61, 0.35); border-radius: 14px; }
.discard .under { transform: rotate(-9deg); }

.cardcol { display: flex; flex-direction: column; align-items: center; gap: 16px; }
.slot {
  position: relative; width: 260px; height: 364px; border-radius: 22px; border: 5px dashed rgba(42, 31, 61, 0.3); display: grid; place-items: center;
  font-family: 'Lilita One'; font-size: 20px; color: rgba(42, 31, 61, 0.4); text-align: center; padding: 30px;
}
.hand { position: absolute; inset: -5px; perspective: 1400px; z-index: 5; }
.inner { position: relative; width: 100%; height: 100%; transform-style: preserve-3d; }
.f { position: absolute; inset: 0; backface-visibility: hidden; border-radius: 22px; }
.f.back { transform: rotateY(180deg); }
.front { background: var(--paper); border: 5px solid var(--ink); box-shadow: 0 8px 0 var(--ink); padding: 12px; display: flex; flex-direction: column; gap: 6px; color: var(--ink); }
.front .head { display: flex; justify-content: flex-end; align-items: center; gap: 8px; font-family: 'Lilita One'; font-size: 15px; }
.front .head .jp { background: var(--blue); border: 3px solid var(--ink); border-radius: 10px; padding: 0 8px; font-size: 12px; white-space: nowrap; }
.words { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 5px; flex: 1; text-align: left; }
.words li { flex: 1; display: flex; align-items: center; gap: 10px; border: 3px solid var(--ink); border-radius: 12px; padding: 0 10px; font-size: 19px; font-weight: 800; background: #fff; transition: all 0.4s; }
.words .n { font-family: 'Lilita One'; font-size: 20px; width: 22px; color: var(--purple); }
.words li.hl { background: var(--yellow); transform: scale(1.1); box-shadow: 0 4px 0 var(--ink); z-index: 2; }
.words li.hl::after {
  content: ''; margin-left: auto; width: 16px; height: 16px; background: var(--pink);
  clip-path: polygon(50% 0, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%); animation: spin 3s linear infinite;
}
.words li.dim { opacity: 0.4; transform: scale(0.95); }

.tbar { position: relative; width: 280px; height: 34px; border: 4px solid var(--ink); border-radius: 999px; background: #fff; box-shadow: 0 5px 0 var(--ink); overflow: hidden; visibility: hidden; }
.tbar.on { visibility: visible; }
.tbar .fill {
  position: absolute; inset: 0 auto 0 0; background-color: var(--green); transition: width 0.25s linear, background 0.3s;
  background-image: repeating-linear-gradient(-45deg, rgba(255, 255, 255, 0.3) 0 10px, transparent 10px 20px);
}
.tbar .tnum { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-family: 'Lilita One'; font-size: 20px; }
.t-warn .tbar .fill { background-color: var(--yellow); }
.t-low .tbar .fill { background-color: var(--red); }
.t-low .tbar { animation: shake 0.3s infinite; }
@keyframes shake { 25% { transform: rotate(-2deg); } 75% { transform: rotate(2deg); } }

.watch { display: flex; flex-direction: column; align-items: center; gap: 14px; text-align: center; width: 380px; }
.bigclock {
  width: 200px; height: 200px; border-radius: 50%; border: 6px solid var(--ink); box-shadow: 0 8px 0 var(--ink);
  background: conic-gradient(var(--green) calc(var(--p) * 1%), #fff 0); display: grid; place-items: center; transition: background 0.3s;
}
.bigclock span { width: 130px; height: 130px; border-radius: 50%; background: #fff; border: 5px solid var(--ink); display: grid; place-items: center; font-family: 'Lilita One'; font-size: 60px; }
.bigclock.idle { background: #fff; }
.t-warn .bigclock { background: conic-gradient(var(--yellow) calc(var(--p) * 1%), #fff 0); }
.t-low .bigclock { background: conic-gradient(var(--red) calc(var(--p) * 1%), #fff 0); animation: shake 0.3s infinite; }
.wtitle { font-size: 32px; color: #fff; -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; text-shadow: 0 4px 0 var(--ink); line-height: 1.1; }
.wsub { font-weight: 800; background: #fff; border: 3px solid var(--ink); border-radius: 12px; padding: 4px 12px; }

.sticky { position: relative; width: 240px; opacity: 0; transform: translateX(-30px) rotate(10deg); transition: all 0.5s cubic-bezier(0.3, 1.5, 0.5, 1); perspective: 900px; pointer-events: none; }
.sticky.on { opacity: 1; transform: rotate(4deg); pointer-events: auto; }
.note { position: relative; height: 220px; transform-style: preserve-3d; transition: transform 0.6s; cursor: pointer; }
.note.flip { transform: rotateY(180deg); }
.note .side { position: absolute; inset: 0; backface-visibility: hidden; border: 4px solid var(--ink); padding: 18px 16px; box-shadow: 0 6px 0 var(--ink); }
.note .s1 { background: #fff59d; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; text-align: center; }
.note .s1 .q { font-family: 'Lilita One'; font-size: 64px; line-height: 1; color: var(--purple); -webkit-text-stroke: 3px var(--ink); paint-order: stroke fill; }
.note .s1 b { font-family: 'Lilita One'; font-size: 22px; font-weight: 400; }
.note .s2 { background: #c8f7ff; transform: rotateY(180deg); }
.note .kw { font-size: 28px; font-weight: 800; }
.note .rom { color: var(--purple); font-weight: 900; }
.note .def { font-size: 17px; font-weight: 700; line-height: 1.3; margin-top: 6px; }
.tape { position: absolute; top: -14px; left: 50%; width: 90px; height: 26px; margin-left: -45px; background: rgba(255, 255, 255, 0.7); border: 2px solid rgba(42, 31, 61, 0.3); transform: rotate(-4deg); z-index: 3; }
.rule { margin-top: 16px; font-family: 'Lilita One'; font-size: 17px; background: var(--pink); color: #fff; border: 4px solid var(--ink); border-radius: 14px; padding: 6px 10px; text-align: center; box-shadow: 0 4px 0 var(--ink); transform: rotate(-2deg); }
.pass { margin-top: 12px; width: 100%; font-weight: 900; background: #fff; border: 4px solid var(--ink); border-radius: 14px; padding: 6px; box-shadow: 0 4px 0 var(--ink); }

.roundover {
  position: absolute; top: 8px; left: 0; right: 0; margin: 0 auto; width: fit-content; z-index: 8; animation: pop 0.45s cubic-bezier(0.3, 1.6, 0.5, 1);
  background: #fff; border: 5px solid var(--ink); border-radius: 22px; box-shadow: 0 8px 0 var(--ink); padding: 14px 26px; text-align: center;
}
.ro-title { font-size: 34px; color: var(--purple); }
.ro-sub { font-weight: 800; margin: 2px 0 10px; }
.leaving { visibility: hidden !important; }
</style>
