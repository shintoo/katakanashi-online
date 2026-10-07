<script setup>
import { muted } from '../lib/music'
</script>

<template>
  <button class="helpbtn mutebtn" :title="muted ? 'Turn music on' : 'Turn music off'" @click="muted = !muted">
    <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 9h4l5-4v14l-5-4H4z" fill="currentColor" />
      <template v-if="muted">
        <path d="M17 9l5 6M22 9l-5 6" />
      </template>
      <template v-else>
        <path d="M16.5 9.5a3.5 3.5 0 0 1 0 5" />
        <path d="M19 7a7 7 0 0 1 0 10" />
      </template>
    </svg>
  </button>
</template>

<style>
.mutebtn { display: grid; place-items: center; color: var(--ink); }
.mutebtn.corner { position: fixed; top: 16px; right: 28px; z-index: 10; }
</style>
