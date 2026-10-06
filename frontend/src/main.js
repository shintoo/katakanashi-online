import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { setupMobile } from './lib/mobile'

setupMobile()

createApp(App).mount('#app')
