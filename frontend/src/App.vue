<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Backdrop from './components/Backdrop.vue'
import RoomView from './components/RoomView.vue'
import TitleScreen from './components/TitleScreen.vue'

const code = ref(null)
const message = ref('')
const glow = ref(false)

function fromUrl() {
  const m = location.pathname.match(/^\/r\/([A-Za-z]{4})\/?$/)
  code.value = m ? m[1].toUpperCase() : null
}

function enter(c) {
  message.value = ''
  history.pushState({}, '', `/r/${c}`)
  code.value = c
}

function leave(msg = '') {
  message.value = msg
  history.pushState({}, '', '/')
  code.value = null
  glow.value = false
  document.documentElement.style.removeProperty('--table')
}

onMounted(() => {
  fromUrl()
  window.addEventListener('popstate', fromUrl)
})
onUnmounted(() => window.removeEventListener('popstate', fromUrl))
</script>

<template>
  <Backdrop :glow="glow" />
  <RoomView v-if="code" :key="code" :code="code" @leave="leave" @glow="glow = $event" />
  <TitleScreen v-else :message="message" @enter="enter" />
</template>
