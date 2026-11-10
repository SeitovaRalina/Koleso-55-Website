import { env } from 'node:process'
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: 'http://127.0.0.1:4173',
    viewport: { width: 1440, height: 900 },
    launchOptions: env.KOLE_CHROME_PATH ? { executablePath: env.KOLE_CHROME_PATH } : undefined,
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://127.0.0.1:4173',
    reuseExistingServer: !env.CI,
    timeout: 30_000,
  },
})
