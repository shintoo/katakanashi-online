<script setup>
import MotionButton from './MotionButton.vue'
import MuteButton from './MuteButton.vue'
</script>

<template>
  <div class="cornerbtns">
    <MotionButton />
    <MuteButton />
  </div>
</template>

<style>
.cornerbtns { display: flex; gap: 16px; }
.cornerbtns.corner { position: fixed; top: 16px; right: 28px; z-index: 10; }
</style>
