import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Components from 'unplugin-vue-components/vite'
import { ArcoResolver } from 'unplugin-vue-components/resolvers'

// Arco 按需引入:模板里用到的组件与样式自动引入(sideEffect)
// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    Components({
      resolvers: [ArcoResolver({ sideEffect: true })],
    }),
  ],
  server: {
    port: 5173,
    proxy: {
      // 开发期把 /api 反代到后端 FastAPI(默认 8000)
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
