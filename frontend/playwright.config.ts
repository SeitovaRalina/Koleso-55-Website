import { env } from 'node:process'
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: 'http://localhost:5173',
    viewport: { width: 1440, height: 900 },
    launchOptions: env.KOLE_CHROME_PATH ? { executablePath: env.KOLE_CHROME_PATH } : undefined,
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: false,
    timeout: 30_000,
  },
})
