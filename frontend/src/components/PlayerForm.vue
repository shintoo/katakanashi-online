<script setup>
import { ref } from 'vue'
import { getProfile } from '../lib/api'
import { ICON_SHAPES, PLAYER_COLORS } from '../lib/colors'
import Avatar from './Avatar.vue'

defineProps({ title: String, button: String, busy: Boolean, error: String })
const emit = defineEmits(['submit', 'back'])

const saved = getProfile()
const name = ref(saved?.name || '')
const shape = ref(saved?.icon?.shape ?? Math.floor(Math.random() * ICON_SHAPES))
const color = ref(saved?.icon?.color ?? PLAYER_COLORS[Math.floor(Math.random() * PLAYER_COLORS.length)])

function submit() {
  emit('submit', { name: name.value.trim(), icon: { shape: shape.value, color: color.value } })
}
</script>

<template>
  <form class="panel pform" @submit.prevent="submit">
    <h3 class="disp">{{ title }}</h3>
    <div class="pf-row">
      <div class="pf-preview"><Avatar :icon="{ shape, color }" /></div>
      <div class="pf-fields">
        <label class="pf-label" for="pname">Your name</label>
        <input id="pname" v-model="name" v-kb data-kb="text" data-kb-label="Your name" class="field" maxlength="14" autocomplete="off" placeholder="Hana" autofocus />
        <div class="pf-label">Face</div>
        <div class="pf-shapes">
          <button v-for="s in ICON_SHAPES" :key="s" type="button" class="pf-pick" :class="{ on: shape === s - 1 }" @click="shape = s - 1">
            <Avatar :icon="{ shape: s - 1, color }" />
          </button>
        </div>
        <div class="pf-label">Color</div>
        <div class="pf-colors">
          <button v-for="c in PLAYER_COLORS" :key="c" type="button" class="pf-color" :class="{ on: color === c }" :style="{ background: c }" @click="color = c" />
        </div>
      </div>
    </div>
    <p v-if="error" class="pf-error">{{ error }}</p>
    <div class="btns">
      <button class="big" :disabled="busy || !name.trim()">{{ button }}</button>
      <button type="button" class="big alt" @click="emit('back')">Back</button>
    </div>
  </form>
</template>

<style>
.pform { width: 560px; }
.pf-row { display: flex; gap: 24px; align-items: flex-start; margin: 12px 0 16px; }
.pf-preview { width: 120px; height: 120px; flex: none; margin-top: 18px; animation: hop2 1.6s ease-in-out infinite; }
@keyframes hop2 { 50% { transform: translateY(-6px) rotate(-3deg); } }
.pf-fields { flex: 1; }
.pf-label { display: block; font-weight: 900; margin: 10px 0 6px; }
.pf-label:first-child { margin-top: 0; }
.field {
  width: 100%; font-size: 22px; font-weight: 800; border: 4px solid var(--ink); border-radius: 14px;
  padding: 6px 12px; background: #fff; outline: none;
}
.field:focus { box-shadow: 0 4px 0 var(--ink); }
.pf-shapes, .pf-colors { display: flex; gap: 8px; flex-wrap: wrap; }
.pf-pick { width: 52px; height: 52px; padding: 4px; border: 3px solid transparent; border-radius: 14px; background: none; }
.pf-pick.on { border-color: var(--ink); background: #fff; box-shadow: 0 3px 0 var(--ink); }
.pf-color { width: 30px; height: 30px; border-radius: 50%; border: 3px solid var(--ink); padding: 0; }
.pf-color.on { transform: scale(1.25); box-shadow: 0 3px 0 var(--ink); }
.pf-error { color: #c9184a; }
</style>
