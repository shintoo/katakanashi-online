<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { TABLE_COLORS } from '../lib/colors'
import Avatar from './Avatar.vue'

const props = defineProps({ state: Object, send: Function })
const open = ref(false)
const dialog = ref(null) // 'fix', 'remove', 'close'
const fixFrom = ref(null)
const fixTo = ref(null)

const others = computed(() => props.state.players.filter((p) => p.id !== props.state.host))
const inGame = computed(() => ['playing', 'round_end'].includes(props.state.phase))
const anyCards = computed(() => props.state.players.some((p) => p.score > 0))
const canEnd = computed(() => props.state.can_end && inGame.value)

function show(name) {
  open.value = false
  fixFrom.value = fixTo.value = null
  dialog.value = name
}
function act(type, data) {
  props.send(type, data)
  dialog.value = null
}

const closeMenu = () => (open.value = false)
onMounted(() => document.addEventListener('click', closeMenu))
onUnmounted(() => document.removeEventListener('click', closeMenu))
</script>

<template>
  <div class="hostwrap" @click.stop>
    <button class="hostbtn" @click="open = !open">
      <svg viewBox="0 0 24 24"><path d="M3 6h18M3 12h18M3 18h18" stroke="#2a1f3d" stroke-width="3.5" stroke-linecap="round" /></svg>HOST
    </button>
    <div class="menu" :class="{ on: open }">
      <div class="mlabel">TABLE COLOR</div>
      <div class="sw">
        <button v-for="c in TABLE_COLORS" :key="c" :class="{ on: c === state.table_color }" :style="{ background: c }" @click="send('color', { color: c })" />
      </div>
      <hr />
      <button class="item" :disabled="!anyCards" @click="show('fix')">Fix a mistake<small>Move a card that went to the wrong player</small></button>
      <button class="item" :disabled="!others.length" @click="show('remove')">Remove a player<small>For someone who left for good</small></button>
      <button class="item" :disabled="!canEnd" @click="act('end_game')">
        End game<small>{{ canEnd ? 'Show the final scores now' : 'Available between rounds' }}</small>
      </button>
      <hr />
      <button class="item danger" @click="show('close')">Close room<small>Ends the game for everyone</small></button>
    </div>

    <Teleport to="body">
      <div v-if="dialog === 'fix'" class="ov" @click.self="dialog = null">
        <div class="panel">
          <h3 class="disp">Fix a mistake</h3>
          <p>Move one card from one player to another. Everyone will see a note that the host moved a card.</p>
          <div class="pickrow">
            <b>Take a card from</b>
            <div class="picks">
              <button v-for="p in state.players" :key="p.id" class="pick" :class="{ on: fixFrom === p.id }" :disabled="!p.score" @click="(fixFrom = p.id), fixTo === p.id && (fixTo = null)">
                <span class="mini"><Avatar :icon="p.icon" /></span>{{ p.name }} ({{ p.score }})
              </button>
            </div>
          </div>
          <div class="pickrow">
            <b>Give it to</b>
            <div class="picks">
              <button v-for="p in state.players" :key="p.id" class="pick" :class="{ on: fixTo === p.id }" :disabled="!fixFrom || fixFrom === p.id" @click="fixTo = p.id">
                <span class="mini"><Avatar :icon="p.icon" /></span>{{ p.name }}
              </button>
            </div>
          </div>
          <div class="btns">
            <button class="big" :disabled="!fixFrom || !fixTo" @click="act('move_card', { from: fixFrom, to: fixTo })">Move card</button>
            <button class="big alt" @click="dialog = null">Cancel</button>
          </div>
        </div>
      </div>

      <div v-if="dialog === 'remove'" class="ov" @click.self="dialog = null">
        <div class="panel">
          <h3 class="disp">Remove a player</h3>
          <p>Their cards go to the discard pile. They can join again with the room code.</p>
          <div class="pickrow">
            <div class="picks">
              <button v-for="p in others" :key="p.id" class="pick" :class="{ on: fixFrom === p.id }" @click="fixFrom = p.id">
                <span class="mini"><Avatar :icon="p.icon" /></span>{{ p.name }}{{ p.connected ? '' : ' (away)' }}
              </button>
            </div>
          </div>
          <div class="btns">
            <button class="big red" :disabled="!fixFrom" @click="act('remove', { id: fixFrom })">Remove</button>
            <button class="big alt" @click="dialog = null">Cancel</button>
          </div>
        </div>
      </div>

      <div v-if="dialog === 'close'" class="ov" @click.self="dialog = null">
        <div class="panel" style="text-align: center">
          <h3 class="disp">Close the room?</h3>
          <p>This ends the game for everyone and sends them back to the title screen.</p>
          <div class="btns">
            <button class="big red" @click="act('close')">Close room</button>
            <button class="big alt" @click="dialog = null">Keep playing</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<style>
.hostwrap { position: relative; }
.hostbtn { display: flex; align-items: center; gap: 8px; height: 56px; padding: 0 16px; border-radius: 16px; border: 4px solid var(--ink); background: #fff; box-shadow: 0 5px 0 var(--ink); font-weight: 900; letter-spacing: 0.1em; }
.hostbtn svg { width: 24px; height: 24px; }
.hostbtn:active { transform: translateY(4px); box-shadow: 0 1px 0 var(--ink); }
.menu { position: absolute; right: 0; top: calc(100% + 10px); width: 260px; background: #fff; border: 4px solid var(--ink); border-radius: 18px; box-shadow: 0 6px 0 var(--ink); padding: 10px; display: none; flex-direction: column; gap: 6px; z-index: 50; }
.menu.on { display: flex; }
.menu .mlabel { font-size: 11px; font-weight: 900; letter-spacing: 0.18em; opacity: 0.55; padding: 4px 6px 0; }
.menu .sw { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; padding: 4px 6px 8px; }
.menu .sw button { aspect-ratio: 1; border-radius: 50%; border: 3px solid var(--ink); padding: 0; }
.menu .sw button.on { box-shadow: 0 0 0 3px #fff, 0 0 0 6px var(--ink); }
.menu .item { text-align: left; border: 3px solid transparent; background: none; border-radius: 12px; padding: 8px 10px; font-weight: 800; font-size: 15px; }
.menu .item:hover:not(:disabled) { background: #f3eeff; border-color: var(--ink); }
.menu .item small { display: block; font-weight: 700; font-size: 12px; opacity: 0.65; }
.menu .item.danger { color: #c9184a; }
.menu hr { border: 0; border-top: 3px dashed #ddd; margin: 2px 0; }
.pickrow { margin-bottom: 14px; }
.pickrow b { display: block; margin-bottom: 6px; }
.picks { display: flex; gap: 8px; flex-wrap: wrap; }
.pick { display: flex; align-items: center; gap: 6px; border: 3px solid var(--ink); border-radius: 14px; background: #fff; padding: 4px 10px 4px 4px; font-weight: 900; }
.pick .mini { width: 34px; height: 34px; }
.pick.on { background: var(--yellow); box-shadow: 0 3px 0 var(--ink); transform: translateY(-2px); }
</style>
