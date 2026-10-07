import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { setupMobile } from './lib/mobile'
import { setupMusic } from './lib/music'

setupMobile()
setupMusic()

createApp(App).mount('#app')
