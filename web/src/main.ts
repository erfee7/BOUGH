import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'md-editor-v3/lib/style.css';
import './styles/global.css';
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.mount('#app')