// vite.config.ts (or .js)
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import * as path from 'node:path'

export default defineConfig(({ mode }) => ({
  plugins: [tailwindcss()],
  base: mode === 'production' ? '/' : '/static/',  // Use '/' in prod (django-vite adds /static/), '/static/' in dev
  root: path.resolve('./static'),  // Set root to static/ so paths don't include 'static/' prefix
  server: {
    host: true,
    port: 5173,
    hmr: { host: 'localhost' },
  },
  build: {
    manifest: 'manifest.json',  // Vite 7+ defaults to .vite/manifest.json; specify legacy path
    outDir: path.resolve('./static/dist'),         
    rollupOptions: {
      input: { 
        app: path.resolve('./static/src/app.js'),
        ticker: path.resolve('./static/src/ticker.js'),
      },  
    },
  },
}))
