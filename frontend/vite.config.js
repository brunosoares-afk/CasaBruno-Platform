import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

// Servido sob /casa tanto direto (dev, porta 5173) quanto via HTTPS pelo
// nginx-proxy-manager (hda08fx9s7v.sn.mynetname.net/casa) — precisa de
// HTTPS de verdade pro microfone (Web Speech API) funcionar no Chrome do
// Android, que bloqueia getUserMedia em origem insegura mesmo na LAN (ver
// memória casa-bruno-custom-frontend-dashboard). API do backend fica em
// /casa/api, sem prefixo nenhum no FastAPI — o proxy abaixo tira o prefixo
// antes de repassar pro backend (127.0.0.1:8090).
export default defineConfig({
  plugins: [react()],
  base: "/casa/",
  server: {
    host: "0.0.0.0",
    port: 5173,
    allowedHosts: true,
    proxy: {
      "/casa/api": {
        target: "http://127.0.0.1:8090",
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/casa\/api/, ""),
      },
    },
  },
})
