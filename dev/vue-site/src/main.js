import './assets/main.css'
import 'element-plus/dist/index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import { ensureDemoStores } from './api/platformAccountsLocal'
import { ensureDemoEmployees } from './api/employeesLocal'
import { ensureDemoCompetitors } from './api/temuCompetitorsLocal'
import { ensureDefaultUser } from './api/authLocal'

ensureDefaultUser()
ensureDemoStores()
ensureDemoEmployees()
ensureDemoCompetitors()

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
