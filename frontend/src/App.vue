<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const status = ref('connecting...')
let socket

onMounted(() => {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  socket = new WebSocket(`${proto}://${location.host}/ws`)
  socket.onopen = () => socket.send(JSON.stringify({ type: 'ping' }))
  socket.onmessage = (e) => {
    if (JSON.parse(e.data).type === 'pong') status.value = 'connected'
  }
  socket.onclose = () => (status.value = 'disconnected')
})

onUnmounted(() => socket?.close())
</script>

<template>
  <main>
    <h1>Katakanashi Online</h1>
    <p>Server: <strong>{{ status }}</strong></p>
  </main>
</template>

<style scoped>
main {
  padding: 48px;
}
</style>
