<script setup>
defineProps({ big: Boolean })
</script>

<template>
  <div class="marquee" :class="{ big }">
    <h1 class="jp" aria-label="Katakanashi">カタカナーシ</h1>
  </div>
</template>

<style>
.marquee {
  --lemon: #fff23a;
  --kana-green: #3fdc5c;
  --kana-blue: #29aee8;
  position: relative; border: 5px solid var(--ink); border-radius: 20px;
  padding: 4px 22px 10px; box-shadow: 0 7px 0 var(--ink); transform: rotate(-2deg);
  background-color: var(--lemon);
  background-image:
    radial-gradient(circle, #fff 0 38%, transparent 40%),
    radial-gradient(circle, #fff 0 18%, transparent 20%);
  background-size: 24px 24px;
  background-position: 0 0, 12px 12px;
}
.marquee h1 {
  --d: 4px;
  margin: 0; font-size: 38px; font-weight: 800; line-height: 1.15; white-space: nowrap;
  color: var(--kana-green); letter-spacing: -0.02em;
  text-shadow:
    calc(var(--d) * 0.25) calc(var(--d) * 0.25) 0 var(--kana-blue),
    calc(var(--d) * 0.5) calc(var(--d) * 0.5) 0 var(--kana-blue),
    calc(var(--d) * 0.75) calc(var(--d) * 0.75) 0 var(--kana-blue),
    var(--d) var(--d) 0 var(--kana-blue);
}
.marquee.big { padding: 10px 40px 20px; background-size: 40px 40px; background-position: 0 0, 20px 20px; }
.marquee.big h1 { --d: 9px; font-size: clamp(44px, 12vw, 92px); }
</style>
