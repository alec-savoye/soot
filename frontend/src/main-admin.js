import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import { fetchAllTokens, generateToken } from './api/admin.js'

createApp(App).mount('#app')
