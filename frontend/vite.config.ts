import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // 127.0.0.1 statt localhost: muss zum Backend-Origin passen (siehe FRONTEND_URL
  // in .env), sonst blockt SameSite=Lax den Session-Cookie nach dem Spotify-Login.
  server: {
    host: '127.0.0.1',
  },
})
