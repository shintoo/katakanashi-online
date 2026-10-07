<script setup>
import { computed, ref, watch } from 'vue'
import Avatar from './Avatar.vue'
import SettingsForm from './SettingsForm.vue'

const props = defineProps({ state: Object, send: Function })
const emit = defineEmits(['howto'])

const isHost = computed(() => props.state.you === props.state.host)
const host = computed(() => props.state.players.find((p) => p.id === props.state.host))
const settings = ref({ ...props.state.settings })
watch(() => props.state.settings, (s) => (settings.value = { ...s }))

const link = computed(() => `${location.origin}/r/${props.state.code}`)
const copied = ref(false)
async function copy() {
  try {
    await navigator.clipboard.writeText(link.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 1600)
  } catch {
    // Clipboard can be blocked; the link is still visible to copy by hand.
  }
}

function change(s) {
  settings.value = s
  props.send('settings', { settings: s })
}
</script>

<template>
  <section class="lobby">
    <div class="panel lob-room">
      <small>ROOM CODE</small>
      <div class="lob-code disp">{{ state.code }}</div>
      <div class="lob-link">
        <span>{{ link }}</span>
        <button class="chip" @click="copy">{{ copied ? 'Copied!' : 'Copy link' }}</button>
      </div>
      <button class="lob-how" @click="emit('howto')">How to play</button>
    </div>

    <div class="panel lob-players">
      <h3 class="disp">Players <span class="lob-count">{{ state.players.length }}/10</span></h3>
      <div class="lob-grid">
        <div v-for="p in state.players" :key="p.id" class="lob-p" :class="{ away: !p.connected, me: p.id === state.you }">
          <div class="lob-av"><Avatar :icon="p.icon" /></div>
          <div class="lob-name">{{ p.name }}</div>
          <span v-if="p.id === state.host" class="lob-tag">HOST</span>
          <span v-else-if="!p.connected" class="lob-tag grey">AWAY</span>
          <button v-if="isHost && p.id !== state.host" class="lob-x" title="Remove player" @click="send('remove', { id: p.id })">
            <svg viewBox="0 0 20 20"><path d="M5 5 L15 15 M15 5 L5 15" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" /></svg>
          </button>
        </div>
        <div v-if="state.players.length < 2" class="lob-p ghost">Waiting for friends to join...</div>
      </div>
    </div>

    <div class="panel lob-settings">
      <h3 class="disp">Game settings</h3>
      <SettingsForm :model-value="settings" :readonly="!isHost" @update:model-value="change" />
      <div class="lob-start">
        <template v-if="isHost">
          <button class="big" :disabled="state.players.length < 2" @click="send('start')">スタート!</button>
          <div v-if="state.players.length < 2" class="lob-hint">You need at least 2 players.</div>
        </template>
        <div v-else class="lob-wait">Waiting for {{ host?.name }} to start the game</div>
      </div>
    </div>
  </section>
</template>

<style>
.lobby { position: relative; z-index: 1; display: flex; flex-wrap: wrap; gap: 24px; justify-content: center; align-items: flex-start; align-content: center; padding: 10px 28px 60px; overflow: auto; }
.lob-room { width: 300px; }
.lob-players { flex: 1 1 340px; max-width: 520px; }
.lob-settings { width: 400px; }
.lob-room { text-align: center; transform: rotate(-1.5deg); }
.lob-room small { font-weight: 900; letter-spacing: 0.2em; opacity: 0.6; }
.lob-code { font-size: 72px; line-height: 1; letter-spacing: 0.12em; color: var(--yellow); -webkit-text-stroke: 4px var(--ink); paint-order: stroke fill; text-shadow: 0 5px 0 var(--ink); margin: 6px 0 12px; }
.lob-link { display: flex; flex-direction: column; gap: 8px; align-items: center; font-weight: 800; font-size: 13px; word-break: break-all; }
.lob-how { margin-top: 14px; background: none; border: 0; font-weight: 900; text-decoration: underline; }
.lob-count { font-family: Nunito; font-weight: 900; font-size: 16px; opacity: 0.55; }
.lob-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; margin-top: 12px; }
.lob-p { position: relative; display: flex; flex-direction: column; align-items: center; gap: 4px; background: #fff; border: 3px solid var(--ink); border-radius: 16px; padding: 12px 8px 10px; box-shadow: 0 4px 0 var(--ink); animation: pop 0.45s cubic-bezier(0.3, 1.6, 0.5, 1); }
.lob-p.me { background: #fff4c2; }
.lob-p.away { opacity: 0.55; }
.lob-p.ghost { justify-content: center; font-weight: 800; opacity: 0.6; border-style: dashed; box-shadow: none; text-align: center; }
.lob-av { width: 64px; height: 64px; }
.lob-name { font-weight: 900; font-size: 17px; }
.lob-tag { font-size: 10px; font-weight: 900; letter-spacing: 0.15em; background: var(--purple); color: #fff; border-radius: 6px; padding: 1px 6px; }
.lob-tag.grey { background: #8a8299; }
.lob-x { position: absolute; top: 6px; right: 6px; width: 26px; height: 26px; border-radius: 50%; border: 2px solid var(--ink); background: #fff; padding: 4px; color: #c9184a; }
.lob-x svg { width: 100%; height: 100%; display: block; }
.lob-start { margin-top: 18px; text-align: center; }
.lob-hint { font-weight: 800; font-size: 13px; margin-top: 10px; opacity: 0.7; }
.lob-wait { font-weight: 900; background: #fff; border: 3px dashed var(--ink); border-radius: 14px; padding: 10px; }
</style>
