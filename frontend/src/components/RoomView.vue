<script setup>
import { computed, nextTick, onUnmounted, ref, shallowRef, watch } from 'vue'
import { forgetSeat, getSeat, joinRoom, markHowTo, roomInfo, saveProfile, saveSeat, seenHowTo } from '../lib/api'
import { burst, flipIn, flyCard, notice, rectOf, shout, wait } from '../lib/fx'
import { connectRoom } from '../lib/room'
import EndScreen from './EndScreen.vue'
import GameTable from './GameTable.vue'
import HostMenu from './HostMenu.vue'
import HowToPlay from './HowToPlay.vue'
import Lobby from './Lobby.vue'
import Marquee from './Marquee.vue'
import CornerButtons from './CornerButtons.vue'
import PlayerForm from './PlayerForm.vue'
import Wheel from './Wheel.vue'

const props = defineProps({ code: String })
const emit = defineEmits(['leave', 'glow'])

const conn = shallowRef(null)
const joinError = ref('')
const joining = ref(false)
const needsJoin = ref(false)
const howto = ref(false)

const state = computed(() => conn.value?.live.state)
const send = (type, data) => conn.value?.send(type, data)
const isHost = computed(() => state.value && state.value.you === state.value.host)
const nameOf = (id) => state.value?.players.find((p) => p.id === id)?.name ?? 'Someone'
const isMe = (id) => state.value?.you === id

async function start() {
  const seat = getSeat(props.code)
  if (seat) return connect(seat)
  try {
    await roomInfo(props.code)
    needsJoin.value = true
  } catch (e) {
    emit('leave', e.message)
  }
}

async function join(profile) {
  joinError.value = ''
  joining.value = true
  try {
    const seat = await joinRoom(props.code, profile.name, profile.icon)
    saveProfile(profile)
    saveSeat(props.code, seat)
    needsJoin.value = false
    connect(seat)
  } catch (e) {
    joinError.value = e.message
  } finally {
    joining.value = false
  }
}

function connect(seat) {
  conn.value = connectRoom(props.code, seat.token, { onEvent, onEnd })
  if (!seenHowTo()) howto.value = true
}

function onEnd(reason) {
  forgetSeat(props.code)
  conn.value = null
  if (reason === 'unknown') needsJoin.value = true
  else if (reason === 'removed') emit('leave', 'The host removed you from the room.')
  else emit('leave', 'This room is closed. Thanks for playing!')
}

function closeHowTo() {
  howto.value = false
  markHowTo()
}

// ---------- animations for things that happen at the table ----------

let drawFrom = null
const avRect = (id) => rectOf(`[data-pod="${id}"] .av`)
const leaving = (sel) => document.querySelector(sel)?.classList.add('leaving')

async function onEvent(e, s) {
  const handSel = s && isMe(s.describer) ? '#hand' : `[data-pod="${s?.describer}"] .held`
  switch (e.kind) {
    case 'drew':
      drawFrom = rectOf('#deckTop')
      break
    case 'gave': {
      const to = avRect(e.to)
      const from = rectOf(handSel)
      leaving(handSel)
      await flyCard(from, to, { num: s.hand?.number ?? '', rot: 360 })
      burst(to)
      const pod = document.querySelector(`[data-pod="${e.to}"]`)
      pod?.classList.remove('got')
      pod?.offsetWidth
      pod?.classList.add('got')
      shout(['正解!', '頭いいね!', 'thugoi'][Math.floor(Math.random() * 3)])
      break
    }
    case 'discarded': {
      const from = rectOf(handSel)
      leaving(handSel)
      await flyCard(from, rectOf('#discard'), { num: s.hand?.number ?? '', rot: 187, fit: true, ease: 'cubic-bezier(.4,0,.2,1)' })
      notice('Nobody got it. The card goes to the discard pile.')
      break
    }
    case 'shuffled': {
      shout('SHUFFLE!', '#3ec5ff')
      const from = rectOf('#discard')
      const to = rectOf('#deck')
      const n = Math.min(s?.discard_count || 3, 5)
      await Promise.all(
        Array.from({ length: n }, (_, k) => wait(k * 130).then(() => flyCard(from, to, { dur: 550, rot: -180, fit: true, ease: 'ease-in-out' }))),
      )
      document.querySelector('#deck')?.classList.add('shuffling')
      setTimeout(() => document.querySelector('#deck')?.classList.remove('shuffling'), 800)
      notice('The discard pile was shuffled back into the deck.')
      break
    }
    case 'moved':
      await flyCard(avRect(e.from), avRect(e.to), { dur: 800, rot: 20, ease: 'ease-in-out', fit: true })
      notice(`The host moved a card from ${nameOf(e.from)} to ${nameOf(e.to)}.`)
      break
    case 'first':
      // Let the wheel close before shouting.
      setTimeout(() => shout(isMe(e.id) ? 'YOU FIRST!' : `${nameOf(e.id).toUpperCase()} FIRST!`), 150)
      break
    case 'round':
      shout(`ROUND ${e.n}!`)
      break
    case 'joined':
      notice(`${e.name} joined the room.`)
      break
    case 'removed':
      notice(`${e.name} was removed from the room.`)
      break
    case 'skipped':
      notice(`${e.name} is away, so their turn was skipped.`)
      break
    case 'host':
      notice(isMe(e.id) ? 'The host left, so you are the host now.' : `The host left, so ${nameOf(e.id)} is the host now.`)
      break
  }
}

// Fly the drawn card in once it shows up on screen.
watch(
  () => state.value?.hand,
  async (hand, old) => {
    if (!hand || old || !drawFrom) return
    const from = drawFrom
    drawFrom = null
    await nextTick()
    if (isMe(state.value.describer)) flipIn(document.querySelector('#hand'), document.querySelector('#handInner'), from)
    else flipIn(document.querySelector(`[data-pod="${state.value.describer}"] .held`), null, from)
  },
)

// ---------- timer ----------

const remaining = ref(null)
let deadline = null
let lastSecs = null
const clock = setInterval(tickClock, 200)

watch(
  () => state.value?.time_left,
  (t) => {
    deadline = t == null ? null : performance.now() + t * 1000
    tickClock()
  },
)

function tickClock() {
  if (deadline == null || !state.value?.hand) {
    remaining.value = null
    lastSecs = null
    emit('glow', false)
    return
  }
  const left = Math.max(0, (deadline - performance.now()) / 1000)
  remaining.value = left
  const secs = Math.ceil(left)
  if (lastSecs != null && secs !== lastSecs) {
    if (lastSecs > 20 && secs <= 20 && secs > 10) shout('20 SECONDS!', '#ffd23f')
    if (lastSecs > 10 && secs <= 10 && secs > 0) shout('10 SECONDS!', '#ff4d6d')
    if (secs === 0) shout("TIME'S UP!", '#ff4d6d')
  }
  lastSecs = secs
  emit('glow', secs <= 5 && secs > 0)
}

// ---------- room-wide bits ----------

watch(
  () => state.value?.table_color,
  (c) => c && document.documentElement.style.setProperty('--table', c),
)
watch(
  () => conn.value?.live.error,
  (err) => err && notice(err.message, 'bad'),
)
const reconnecting = computed(() => conn.value?.live.status === 'reconnecting')

const roundTag = computed(() => {
  const r = state.value?.settings.rounds
  return r ? `/${r}` : '/∞'
})
const inGame = computed(() => state.value && state.value.phase !== 'lobby')

onUnmounted(() => {
  clearInterval(clock)
  conn.value?.close()
})
start()
</script>

<template>
  <div v-if="needsJoin" class="title">
    <CornerButtons class="corner" />
    <Marquee big />
    <PlayerForm :title="`Join room ${code}`" button="Join room" :busy="joining" :error="joinError" @submit="join" @back="emit('leave')" />
  </div>

  <div v-else-if="state" class="wrap">
    <header class="header">
      <Marquee />
      <div class="hright">
        <CornerButtons />
        <button class="helpbtn" title="How to play" @click="howto = true">?</button>
        <div class="badge"><small>ROOM</small><span class="disp">{{ state.code }}</span></div>
        <div v-if="inGame" class="badge">
          <small>ROUND</small>
          <div class="badge-row"><span class="disp">{{ state.round }}</span><span class="disp of">{{ roundTag }}</span></div>
        </div>
        <HostMenu v-if="isHost" :state="state" :send="send" />
      </div>
    </header>

    <Lobby v-if="state.phase === 'lobby'" :state="state" :send="send" @howto="howto = true" />
    <GameTable v-else :state="state" :remaining="remaining" :send="send" />

    <Wheel v-if="state.phase === 'picking'" :state="state" :send="send" />
    <EndScreen v-if="state.phase === 'ended'" :key="state.round" :state="state" :send="send" />
  </div>

  <div v-else class="loading disp">Connecting...</div>

  <div v-if="reconnecting" class="reconnect">Reconnecting...</div>
  <HowToPlay v-if="howto" @close="closeHowTo" />
</template>

<style>
.wrap { position: relative; z-index: 1; height: 100%; display: grid; grid-template-rows: auto 1fr; }
.header { display: flex; align-items: center; justify-content: space-between; padding: 16px 28px; position: relative; z-index: 10; }
.hright { display: flex; align-items: center; gap: 16px; }
.helpbtn { width: 48px; height: 48px; border-radius: 50%; border: 4px solid var(--ink); background: #fff; box-shadow: 0 4px 0 var(--ink); font-family: 'Lilita One'; font-size: 26px; padding: 0; }
.loading { position: relative; z-index: 1; height: 100%; display: grid; place-items: center; font-size: 40px; color: #fff; -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; }
.reconnect { position: fixed; bottom: 16px; left: 50%; transform: translateX(-50%); z-index: 90; background: var(--yellow); border: 4px solid var(--ink); border-radius: 999px; padding: 6px 18px; font-weight: 900; box-shadow: 0 4px 0 var(--ink); }
</style>
