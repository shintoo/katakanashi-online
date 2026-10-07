<script setup>
import { ref } from 'vue'
import { createRoom, roomInfo, saveProfile, saveSeat } from '../lib/api'
import Marquee from './Marquee.vue'
import MuteButton from './MuteButton.vue'
import PlayerForm from './PlayerForm.vue'

defineProps({ message: String })
const emit = defineEmits(['enter'])

const step = ref('home')
const code = ref('')
const error = ref('')
const busy = ref(false)

async function lookup() {
  error.value = ''
  const c = code.value.trim().toUpperCase()
  if (!c) return
  busy.value = true
  try {
    await roomInfo(c)
    emit('enter', c)
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}

async function create(profile) {
  error.value = ''
  busy.value = true
  try {
    const seat = await createRoom(profile.name, profile.icon)
    saveProfile(profile)
    saveSeat(seat.code, seat)
    emit('enter', seat.code)
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="title">
    <MuteButton class="corner" />
    <Marquee big />
    <div v-if="message" class="title-msg">{{ message }}</div>

    <div v-if="step === 'home'" class="title-cards">
      <div class="panel tcard">
        <h3 class="disp">Host a game</h3>
        <p>Make a new room and invite your friends with a code or a link.</p>
        <button class="big" @click="(step = 'create'), (error = '')">Create a room</button>
      </div>
      <form class="panel tcard" @submit.prevent="lookup">
        <h3 class="disp">Join a game</h3>
        <p>Got a room code from a friend? Type it here.</p>
        <div class="tjoin">
          <input v-model="code" class="field code" maxlength="4" placeholder="A1B2" autocomplete="off" />
          <button class="big yellow" :disabled="busy || !code.trim()">Join</button>
        </div>
        <p v-if="error" class="pf-error">{{ error }}</p>
      </form>
    </div>

    <PlayerForm v-else-if="step === 'create'" title="Who's hosting?" button="Create room" :busy="busy" :error="error" @submit="create" @back="step = 'home'" />
  </div>
</template>

<style>
.title { position: relative; z-index: 1; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 40px; padding: 16px; }
.title-msg { background: var(--ink); color: #fff; font-weight: 800; padding: 8px 18px; border-radius: 999px; }
.title-cards { display: flex; gap: 28px; flex-wrap: wrap; justify-content: center; }
.tcard { width: 340px; display: flex; flex-direction: column; }
.tcard:nth-child(2) { transform: rotate(1.5deg); }
.tcard:first-child { transform: rotate(-1.5deg); }
.tcard p { flex: 1; }
.tjoin { display: flex; gap: 10px; }
.field.code { font-family: 'Lilita One'; font-size: 30px; letter-spacing: 0.2em; text-transform: uppercase; text-align: center; }
</style>
