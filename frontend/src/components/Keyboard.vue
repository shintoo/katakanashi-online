<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

// Our own keyboard for touch screens. The phone's keyboard covers half the game, so text fields
// marked with v-kb never open it, and this one types into them instead.

const LETTERS = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
const DIGITS = '23456789'
const QWERTY = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
const KANA = [
  'アカサタナハマヤラワ',
  'イキシチニヒミ リヲ',
  'ウクスツヌフムユルン',
  'エケセテネヘメ レー',
  'オコソトノホモヨロ・',
]
// The ゛゜小 key turns the last letter into the next one in its group (カ→ガ→カ, ハ→バ→パ, ツ→ッ→ヅ).
const VARIANTS = ['アァ', 'イィ', 'ウゥヴ', 'エェ', 'オォ', 'カガ', 'キギ', 'クグ', 'ケゲ', 'コゴ', 'サザ', 'シジ', 'スズ', 'セゼ', 'ソゾ', 'タダ', 'チヂ', 'ツッヅ', 'テデ', 'トド', 'ハバパ', 'ヒビピ', 'フブプ', 'ヘベペ', 'ホボポ', 'ヤャ', 'ユュ', 'ヨョ', 'ワヮ']

const root = ref(null)
const input = ref(null)
const value = ref('')
const mode = ref('abc')
const shift = ref(false)

const isCode = computed(() => input.value?.dataset.kb === 'code')
const label = computed(() => input.value?.dataset.kbLabel || '')
const full = computed(() => input.value && input.value.maxLength > 0 && value.value.length >= input.value.maxLength)
const upper = computed(() => shift.value || !value.value || value.value.endsWith(' '))
const codeWants = computed(() => (value.value.length % 2 ? 'digit' : 'letter'))

function set(v) {
  value.value = v
  input.value.value = v
  input.value.dispatchEvent(new Event('input', { bubbles: true }))
}
function type(ch) {
  if (!ch.trim() && (!value.value || value.value.endsWith(' '))) return
  if (full.value) return
  set(value.value + ch)
  shift.value = false
}
function letter(ch) {
  type(upper.value ? ch : ch.toLowerCase())
}
function back() {
  if (value.value) set(value.value.slice(0, -1))
}
function variant() {
  const last = value.value.slice(-1)
  const group = VARIANTS.find((g) => g.includes(last))
  if (group) set(value.value.slice(0, -1) + group[(group.indexOf(last) + 1) % group.length])
}
function close() {
  input.value?.blur()
  input.value = null
}
function ok() {
  const form = input.value?.form
  const submit = isCode.value && value.value.length === 4
  close()
  if (submit) form?.requestSubmit()
}

function onFocus(e) {
  const el = e.target
  if (!el.matches?.('input[data-kb]')) return
  input.value = el
  value.value = el.value
  shift.value = false
}
function onPress(e) {
  if (input.value && !root.value?.contains(e.target) && e.target !== input.value) close()
}
// Tablets with a real keyboard plugged in can still type.
function onKey(e) {
  if (!input.value || e.ctrlKey || e.metaKey || e.altKey) return
  if (e.key === 'Backspace') back()
  else if (e.key === 'Enter') ok()
  else if (e.key === 'Escape') close()
  else if (e.key.length === 1) {
    if (!isCode.value) type(e.key)
    else if ((codeWants.value === 'letter' ? LETTERS : DIGITS).includes(e.key.toUpperCase())) type(e.key.toUpperCase())
  } else return
  e.preventDefault()
}

onMounted(() => {
  document.addEventListener('focusin', onFocus)
  document.addEventListener('pointerdown', onPress, true)
  document.addEventListener('keydown', onKey)
})
onUnmounted(() => {
  document.removeEventListener('focusin', onFocus)
  document.removeEventListener('pointerdown', onPress, true)
  document.removeEventListener('keydown', onKey)
})
</script>

<template>
  <Transition name="kb">
    <div v-if="input" ref="root" class="kb" :class="{ kana: mode === 'kana' && !isCode }" @pointerdown.prevent>
      <div class="kb-bar">
        <span v-if="label" class="kb-label">{{ label }}</span>
        <div class="kb-show" :class="{ code: isCode }">{{ value }}<i class="kb-caret"></i></div>
        <button v-if="!isCode" class="kb-mode disp" @click="mode = mode === 'abc' ? 'kana' : 'abc'">{{ mode === 'abc' ? 'カナ' : 'ABC' }}</button>
        <button class="kb-ok disp" :disabled="isCode && value.length < 4" @click="ok">{{ isCode ? 'Join' : 'OK' }}</button>
      </div>

      <div v-if="isCode" class="kb-keys kb-code">
        <button v-for="(ch, i) in LETTERS" :key="ch" class="kb-k disp" :style="{ gridRow: Math.floor(i / 8) + 1, gridColumn: (i % 8) + 1 }" :disabled="full || codeWants !== 'letter'" @click="type(ch)">{{ ch }}</button>
        <button v-for="(ch, i) in DIGITS" :key="ch" class="kb-k disp" :style="{ gridRow: Math.floor(i / 4) + 1, gridColumn: (i % 4) + 10 }" :disabled="full || codeWants !== 'digit'" @click="type(ch)">{{ ch }}</button>
        <button class="kb-k back" @click="back"><svg viewBox="0 0 32 20"><path d="M10 2 H30 V18 H10 L2 10Z M15 6 L23 14 M23 6 L15 14" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" /></svg></button>
      </div>

      <div v-else-if="mode === 'abc'" class="kb-keys kb-abc">
        <div v-for="(row, i) in QWERTY" :key="row" class="kb-row">
          <button v-if="i === 2" class="kb-k wide" :class="{ on: shift }" @click="shift = !shift"><svg viewBox="0 0 24 24"><path d="M12 3 L21 12 H16 V20 H8 V12 H3Z" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round" /></svg></button>
          <button v-for="ch in row" :key="ch" class="kb-k" @click="letter(ch)">{{ upper ? ch : ch.toLowerCase() }}</button>
          <button v-if="i === 0" class="kb-k back" @click="back"><svg viewBox="0 0 32 20"><path d="M10 2 H30 V18 H10 L2 10Z M15 6 L23 14 M23 6 L15 14" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" /></svg></button>
          <button v-if="i === 1" class="kb-k" @click="type('-')">-</button>
          <button v-if="i === 2" class="kb-k space" @click="type(' ')">space</button>
        </div>
      </div>

      <div v-else class="kb-keys kb-kana">
        <div v-for="(row, i) in KANA" :key="row" class="kb-row">
          <template v-for="(ch, j) in row" :key="j">
            <span v-if="ch === ' '" class="kb-gap"></span>
            <button v-else class="kb-k jp" @click="type(ch)">{{ ch }}</button>
          </template>
          <button v-if="i === 0" class="kb-k back" @click="back"><svg viewBox="0 0 32 20"><path d="M10 2 H30 V18 H10 L2 10Z M15 6 L23 14 M23 6 L15 14" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" /></svg></button>
          <button v-if="i === 1" class="kb-k jp wide" @click="variant">゛゜小</button>
          <button v-if="i === 2" class="kb-k wide" @click="type(' ')">space</button>
          <span v-if="i > 2" class="kb-gap wide"></span>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style>
/* Sized in real screen pixels (--u), so keys stay finger-sized however small the game is drawn. */
.kb {
  --u: calc(1px / var(--scale, 1));
  --kh: calc(40 * var(--u));
  position: fixed; left: 50%; bottom: 0; z-index: 150; transform: translateX(-50%);
  width: min(var(--sw), calc(760 * var(--u)));
  background: var(--paper); border: calc(3 * var(--u)) solid var(--ink); border-bottom: none;
  border-radius: calc(16 * var(--u)) calc(16 * var(--u)) 0 0;
  padding: calc(8 * var(--u)) calc(8 * var(--u)) calc(10 * var(--u));
  box-shadow: 0 calc(-4 * var(--u)) 0 rgba(42, 31, 61, 0.25);
  display: flex; flex-direction: column; gap: calc(6 * var(--u));
  font-size: calc(18 * var(--u));
}
.kb.kana { --kh: calc(34 * var(--u)); }
.kb-enter-active, .kb-leave-active { transition: transform 0.2s ease-out; }
.kb-enter-from, .kb-leave-to { transform: translate(-50%, 100%); }

.kb-bar { display: flex; align-items: center; gap: calc(8 * var(--u)); }
.kb-label { font-weight: 900; white-space: nowrap; }
.kb-show {
  flex: 1; height: calc(38 * var(--u)); display: flex; align-items: center; overflow: hidden; white-space: pre;
  background: #fff; border: calc(3 * var(--u)) solid var(--ink); border-radius: calc(10 * var(--u));
  padding: 0 calc(10 * var(--u)); font-weight: 800; font-size: calc(20 * var(--u));
}
.kb-show.code { font-family: 'Lilita One', 'M PLUS Rounded 1c'; letter-spacing: 0.2em; justify-content: center; }
.kb-caret { display: inline-block; width: calc(3 * var(--u)); height: 1.1em; background: var(--ink); margin-left: 1px; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
.kb-mode, .kb-ok {
  height: calc(38 * var(--u)); padding: 0 calc(16 * var(--u)); font-size: calc(20 * var(--u));
  border: calc(3 * var(--u)) solid var(--ink); border-radius: calc(10 * var(--u)); box-shadow: 0 calc(3 * var(--u)) 0 var(--ink);
}
.kb-mode { background: var(--yellow); }
.kb-ok { background: var(--green); }

.kb-keys { display: flex; flex-direction: column; gap: calc(5 * var(--u)); }
.kb-row { display: flex; gap: calc(5 * var(--u)); justify-content: center; }
.kb-k {
  flex: 1 1 0; min-width: 0; height: var(--kh); padding: 0; display: grid; place-items: center;
  background: #fff; border: calc(2.5 * var(--u)) solid var(--ink); border-radius: calc(8 * var(--u));
  box-shadow: 0 calc(3 * var(--u)) 0 var(--ink); font-weight: 900; font-size: inherit;
}
.kb-k:active:not(:disabled) { transform: translateY(calc(2 * var(--u))); box-shadow: 0 calc(1 * var(--u)) 0 var(--ink); background: var(--yellow); }
.kb-k:disabled { opacity: 0.3; }
.kb-k svg { width: calc(26 * var(--u)); height: calc(20 * var(--u)); }
.kb-k.on { background: var(--yellow); }
.kb-k.wide, .kb-gap.wide { flex-grow: 1.5; }
.kb-k.space { flex-grow: 3; }
.kb-k.back { background: #ffe3ea; }
.kb-gap { flex: 1 1 0; }
.kb-code { display: grid; grid-template-columns: repeat(8, 1fr) calc(14 * var(--u)) repeat(4, 1fr); }
.kb-code .back { grid-row: 3; grid-column: 10 / span 4; }
.kb-kana { display: grid; grid-template-columns: repeat(10, 1fr) 1.5fr; gap: calc(5 * var(--u)); }
.kb-kana .kb-row { display: contents; }
.kb-kana .kb-k { font-size: calc(20 * var(--u)); }
</style>
