import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  base: "",
  // publicDir: "/public/explosivemap/",
  plugins: [vue()],
  // server: {
  //   proxy: {
  //     '/explosiveapi': {
  //       target: 'http://172.18.18.2:8000/explosiveapi',
  //       changeOrigin: true,
  //       rewrite: (path) => path.replace(/^\/explosiveapi/, '/explosiveapi')
  //     }

  //   }
  // }
})
