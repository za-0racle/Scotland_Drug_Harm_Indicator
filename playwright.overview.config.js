import {defineConfig} from '@playwright/test';
import base from './playwright.config.js';

// Check the built frontend without HMR; leave the developer's 5173 port untouched.
export default defineConfig({...base,webServer:base.webServer.filter(server=>!server.url.includes('localhost:5173')).map(server=>server.url.includes('127.0.0.1:4173')?{...server,command:'npm run preview -- --host 127.0.0.1 --port 4173 --strictPort'}:server)});
