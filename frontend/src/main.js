import { createApp } from 'vue'
import './style.css'
// Message 为命令式调用,按需引入其样式(模板组件由 ArcoResolver 自动处理)
import '@arco-design/web-vue/es/message/style/css.js'
import App from './App.vue'

createApp(App).mount('#app')
