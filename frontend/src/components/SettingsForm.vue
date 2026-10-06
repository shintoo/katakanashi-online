<script setup>
const props = defineProps({ modelValue: Object, readonly: Boolean })
const emit = defineEmits(['update:modelValue'])

const ROUNDS = [[3, '3'], [5, '5'], [10, '10'], [null, 'Endless']]
const TIMES = [[30, '30s'], [60, '1 min'], [120, '2 min'], [300, '5 min'], [null, 'No limit']]
const FIRST = [['random', 'Spin the wheel'], ['host', 'Host goes first']]

const set = (key, value) => emit('update:modelValue', { ...props.modelValue, [key]: value })
</script>

<template>
  <div class="setform">
    <div class="setrow">
      <b>Rounds</b>
      <div class="chips">
        <button v-for="[v, label] in ROUNDS" :key="label" type="button" class="chip" :class="{ on: modelValue.rounds === v }" :disabled="readonly" @click="set('rounds', v)">{{ label }}</button>
      </div>
    </div>
    <div class="setrow">
      <b>Time per card</b>
      <div class="chips">
        <button v-for="[v, label] in TIMES" :key="label" type="button" class="chip" :class="{ on: modelValue.time_limit === v }" :disabled="readonly" @click="set('time_limit', v)">{{ label }}</button>
      </div>
    </div>
    <div class="setrow">
      <b>First player</b>
      <div class="chips">
        <button v-for="[v, label] in FIRST" :key="v" type="button" class="chip" :class="{ on: modelValue.first === v }" :disabled="readonly" @click="set('first', v)">{{ label }}</button>
      </div>
    </div>
  </div>
</template>

<style>
.setrow { margin-bottom: 14px; }
.setrow b { display: block; margin-bottom: 6px; }
</style>
