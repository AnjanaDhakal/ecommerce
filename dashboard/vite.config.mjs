import path from "path"
import { fileURLToPath } from "url"
import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import frappeui from "frappe-ui/vite"
import Icons from "unplugin-icons/vite"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
  plugins: [
    frappeui({
      buildConfig: {
        indexHtmlPath: path.resolve(__dirname, "index.html"),
      },
    }),
    vue(),
    Icons({ autoInstall: true }),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },

  build: {
    outDir: "../ecommerce/public/dashboard",
    emptyOutDir: true,
    target: "es2015",
  },

  optimizeDeps: {
    include: [
      "frappe-ui > feather-icons",
      "showdown",
      "engine.io-client",
      "socket.io-client",
      "socket.io-parser",
      "debug",
    ],
  },

  server: {
    host: "0.0.0.0",
    port: 8080,
    allowedHosts: true,
  },
})
