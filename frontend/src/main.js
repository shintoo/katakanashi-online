import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { isTouch, setupMobile } from './lib/mobile'
import { setupMusic } from './lib/music'

setupMobile()
setupMusic()

// v-kb marks a text field that uses our own keyboard on touch screens instead of the phone's.
createApp(App)
  .directive('kb', (el) => {
    if (!isTouch) return
    el.readOnly = true
    el.inputMode = 'none'
  })
  .mount('#app')
