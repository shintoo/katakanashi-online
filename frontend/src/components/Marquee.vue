<script setup>
defineProps({ big: Boolean })
</script>

<template>
  <div class="marquee" :class="{ big }">
    <div class="bulbs">
      <template v-for="i in 14" :key="i">
        <i :style="{ left: ((i - 1) / 13) * 100 + '%', top: '-10px' }"></i>
        <i :style="{ left: ((i - 1) / 13) * 100 + '%', bottom: '-10px' }"></i>
      </template>
    </div>
    <h1 class="disp">KATAKANASHI!</h1>
    <div class="sub jp">カタカナシ</div>
  </div>
</template>

<style>
.marquee {
  position: relative; background: var(--red); border: 5px solid var(--ink); border-radius: 20px;
  padding: 6px 30px 10px; box-shadow: 0 7px 0 var(--ink); transform: rotate(-2deg);
}
.marquee h1 { margin: 0; font-size: 40px; color: #fff; -webkit-text-stroke: 2px var(--ink); paint-order: stroke fill; text-shadow: 0 4px 0 var(--ink); }
.marquee .sub { color: var(--yellow); font-size: 14px; letter-spacing: 0.3em; text-align: center; margin-top: -4px; }
.marquee.big { padding: 14px 54px 18px; }
.marquee.big h1 { font-size: 76px; -webkit-text-stroke: 3px var(--ink); text-shadow: 0 7px 0 var(--ink); }
.marquee.big .sub { font-size: 24px; }
.bulbs { position: absolute; inset: 6px; pointer-events: none; }
.bulbs i {
  position: absolute; width: 9px; height: 9px; border-radius: 50%; background: #fff6c2;
  box-shadow: 0 0 6px #fff6a0; animation: blink 1s infinite;
}
.bulbs i:nth-child(4n), .bulbs i:nth-child(4n + 1) { animation-delay: 0.5s; }
@keyframes blink { 50% { background: #a08a3a; box-shadow: none; } }
</style>
