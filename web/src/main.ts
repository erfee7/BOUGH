import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import 'md-editor-v3/lib/style.css';
import './styles/global.css';
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router) // Router must be registered after Pinia
app.mount('#app')