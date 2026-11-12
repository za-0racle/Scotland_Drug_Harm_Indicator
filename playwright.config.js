import { defineConfig } from '@playwright/test';

// Allow isolated browser checks without replacing an existing developer server.
const localPort=Number(process.env.E2E_LOCAL_PORT??5173);
if(!Number.isInteger(localPort)||localPort<1024||localPort>65535)throw new Error('Invalid E2E_LOCAL_PORT.');

export default defineConfig({
  testDir: './e2e',
  timeout: 120000,
  expect: { timeout: 60000 },
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:4173',
    channel: process.platform === 'win32' ? 'msedge' : undefined,
    viewport: { width: 1440, height: 1100 },
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: `${process.platform === 'win32' ? '".\\analysis\\.venv\\Scripts\\python.exe"' : 'analysis/.venv/bin/python'} -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`,
      url: 'http://127.0.0.1:8000/api/v1/health',
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 4173 --strictPort',
      url: 'http://127.0.0.1:4173/api/v1/health',
      reuseExistingServer: !process.env.CI,
    },
    {
      command: `npm run dev -- --host localhost --port ${localPort} --strictPort`,
      url: `http://localhost:${localPort}`,
      reuseExistingServer: !process.env.CI,
    },
  ],
});
