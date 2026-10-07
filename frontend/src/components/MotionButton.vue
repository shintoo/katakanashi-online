<script setup>
import { calm } from '../lib/motion'
</script>

<template>
  <button class="helpbtn mutebtn" :title="calm ? 'Turn motion on' : 'Turn motion off'" @click="calm = !calm">
    <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="15" cy="12" r="5" fill="currentColor" />
      <path d="M2 8h5M3 12h3M2 16h5" />
      <path v-if="calm" d="M3 3l18 18" stroke="#fff" stroke-width="6" />
      <path v-if="calm" d="M3 3l18 18" />
    </svg>
  </button>
</template>
