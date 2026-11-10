import { mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { env } from 'node:process'
import { expect, test } from '@playwright/test'

test('claimed guest request appears in the account', async ({ page }) => {
  const target = env.KOLE_SCREENSHOT_DIR
  const email = env.KOLE_E2E_EMAIL
  const password = env.KOLE_E2E_PASSWORD
  if (!target || !email || !password) {
    test.skip(true, 'KOLE_SCREENSHOT_DIR, KOLE_E2E_EMAIL and KOLE_E2E_PASSWORD are required')
  }
  await mkdir(target!, { recursive: true })

  await page.goto('/login')
  await page.getByLabel('Email или телефон').fill(email!)
  await page.getByLabel('Пароль').fill(password!)
  await page.getByRole('button', { name: 'Войти' }).click()
  await expect(page).not.toHaveURL(/\/login$/)
  await page.goto('/account?tab=requests')

  await expect(page.getByRole('region', { name: 'Мои заявки' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Экскурсия на заказ' })).toBeVisible()
  await expect(page.getByText('Проверка гостевой привязки')).toBeVisible()
  await expect(page.getByText('Новая')).toBeVisible()
  await page.screenshot({ path: join(target!, 'claimed-request-account.png'), fullPage: true })
})
