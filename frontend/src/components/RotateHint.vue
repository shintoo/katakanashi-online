<script setup>
const canLock = !!(document.documentElement.requestFullscreen && screen.orientation?.lock)
</script>

<template>
  <div class="rotate">
    <div class="phone"><span class="jp">カ</span></div>
    <div class="rtitle disp shadowtext">Turn your phone sideways!</div>
    <button v-if="canLock" class="big">Play</button>
  </div>
</template>

<style>
.rotate {
  position: fixed; inset: 0; z-index: 200; background: var(--table); display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 28px; padding: 24px; text-align: center;
}
.rotate .phone {
  width: 90px; height: 150px; border: 6px solid var(--ink); border-radius: 18px; background: var(--paper);
  box-shadow: 0 6px 0 var(--ink); display: grid; place-items: center; animation: tilt 2.4s ease-in-out infinite;
}
.rotate .phone span { font-size: 48px; color: var(--green); -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; text-shadow: 0 3px 0 var(--blue); }
@keyframes tilt { 0%, 30% { transform: rotate(0); } 55%, 85% { transform: rotate(-90deg); } 100% { transform: rotate(0); } }
.rtitle { font-size: 34px; line-height: 1.1; }
</style>
