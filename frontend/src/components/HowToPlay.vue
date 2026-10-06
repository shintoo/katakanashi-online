<script setup>
const emit = defineEmits(['close'])
</script>

<template>
  <div class="ov" @click.self="emit('close')">
    <div class="panel how">
      <h3 class="disp">How to play</h3>
      <div class="how-sub">Quick version. You'll get it after one round.</div>
      <div class="steps">
        <div class="stepc">
          <svg viewBox="0 0 48 48"><rect x="12" y="6" width="24" height="34" rx="5" fill="#ff8c42" stroke="#2a1f3d" stroke-width="4" /><path d="M24 44 L24 30 M18 36 L24 30 L30 36" stroke="#2a1f3d" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" /></svg>
          <b>Draw</b><span>On your turn, click the deck to draw a card with 6 katakana words.</span>
        </div>
        <div class="stepc">
          <svg viewBox="0 0 48 48"><rect x="10" y="6" width="28" height="36" rx="6" fill="#ffd23f" stroke="#2a1f3d" stroke-width="4" /><text x="24" y="33" text-anchor="middle" font-family="Lilita One" font-size="22" fill="#2a1f3d">3</text></svg>
          <b>Peek</b><span>The <i>next</i> card's number picks your word. It gets highlighted for you.</span>
        </div>
        <div class="stepc">
          <svg viewBox="0 0 48 48"><path d="M6 10 h36 a4 4 0 0 1 4 4 v16 a4 4 0 0 1 -4 4 h-20 l-10 8 v-8 h-6 a4 4 0 0 1 -4 -4 v-16 a4 4 0 0 1 4 -4z" fill="#3ec5ff" stroke="#2a1f3d" stroke-width="4" stroke-linejoin="round" /><path d="M14 22 h20" stroke="#2a1f3d" stroke-width="4" stroke-linecap="round" /></svg>
          <b>Describe</b><span>Explain it in Japanese, but no katakana words allowed!</span>
        </div>
        <div class="stepc">
          <svg viewBox="0 0 48 48"><polygon points="24,4 30,18 45,18 33,27 37,42 24,33 11,42 15,27 3,18 18,18" fill="#5ee07a" stroke="#2a1f3d" stroke-width="4" stroke-linejoin="round" /></svg>
          <b>Give</b><span>Click whoever guesses first. They keep the card as a point.</span>
        </div>
      </div>
      <div class="voice">
        <svg viewBox="0 0 48 48"><path d="M8 28 v-6 a16 16 0 0 1 32 0 v6" fill="none" stroke="#fff" stroke-width="4" /><rect x="5" y="26" width="10" height="14" rx="4" fill="#ffd23f" stroke="#fff" stroke-width="3" /><rect x="33" y="26" width="10" height="14" rx="4" fill="#ffd23f" stroke="#fff" stroke-width="3" /></svg>
        This game has no voice built in. Hop into a Discord (or any) voice call with everyone before starting!
      </div>
      <button class="big yellow how-go" @click="emit('close')">Got it, let's play!</button>
    </div>
  </div>
</template>

<style>
.how { width: min(760px, 92vw); }
.how-sub { font-weight: 700; opacity: 0.7; margin-bottom: 16px; }
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stepc { border: 3px solid var(--ink); border-radius: 16px; padding: 12px; background: #fff; box-shadow: 3px 3px 0 var(--ink); }
.stepc svg { width: 40px; height: 40px; }
.stepc b { display: block; font-size: 17px; }
.stepc span { font-size: 14px; line-height: 1.3; display: block; font-weight: 700; }
.stepc:nth-child(1) { background: #fff4c2; }
.stepc:nth-child(2) { background: #ffe0ee; }
.stepc:nth-child(3) { background: #dff6ff; }
.stepc:nth-child(4) { background: #e2fbe6; }
.voice { margin-top: 16px; display: flex; align-items: center; gap: 12px; background: var(--ink); color: #fff; border-radius: 14px; padding: 10px 14px; font-weight: 700; }
.voice svg { width: 36px; height: 36px; flex: none; }
.how-go { margin-top: 16px; width: 100%; }
</style>
