import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: "",
  // publicDir: "/public/explosivemap/",
  plugins: [vue()],
  // server: {
  //   proxy: {
  //     '/map': {
  //       target: 'https://wmts.nlsc.gov.tw',
  //       changeOrigin: true,
  //       rewrite: (path) => path.replace(/^\/map/, '')
  //     }

  //   }
  // }
})
