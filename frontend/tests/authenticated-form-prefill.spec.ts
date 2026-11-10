import { mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { env } from 'node:process'
import { expect, test, type Page } from '@playwright/test'

const expectedName = env.KOLE_E2E_NAME || 'Тестова Ирина Сергеевна'
const expectedPhone = env.KOLE_E2E_PHONE || '+79991112233'
const expectedFormattedPhone = env.KOLE_E2E_FORMATTED_PHONE || '+7 (999) 111-22-33'

async function capture(page: Page, filename: string) {
  if (!env.KOLE_SCREENSHOT_DIR) return
  await mkdir(env.KOLE_SCREENSHOT_DIR, { recursive: true })
  await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, filename), fullPage: true })
}

test.beforeEach(async ({ page }) => {
  const email = env.KOLE_E2E_EMAIL
  const password = env.KOLE_E2E_PASSWORD
  if (!email || !password) test.skip(true, 'KOLE_E2E_EMAIL and KOLE_E2E_PASSWORD are required')

  await page.goto('/login')
  await page.getByLabel('Email или телефон').fill(email!)
  await page.getByLabel('Пароль').fill(password!)
  await page.getByRole('button', { name: 'Войти' }).click()
  await expect(page).not.toHaveURL(/\/login$/)
})

test('prefills the custom-tour form from the authenticated profile', async ({ page }) => {
  await page.goto('/custom-tour')
  await expect(page.getByPlaceholder('Иван Иванов')).toHaveValue(expectedName)
  await expect(page.getByPlaceholder('+7 (999) 123-45-67')).toHaveValue(expectedPhone)
  await expect(page.getByPlaceholder('example@mail.ru')).toHaveValue(env.KOLE_E2E_EMAIL!)
  await expect(page.getByText('Укажите email и подтвердите его после регистрации, чтобы позже увидеть заявку в личном кабинете.')).toHaveCount(0)
  await capture(page, 'custom-tour-prefill.png')
})

test('prefills the certificate buyer fields from the authenticated profile', async ({ page }) => {
  await page.goto('/certificates')
  const form = page.locator('form').first()
  await expect(form.locator('input[type="text"]').first()).toHaveValue(expectedName)
  await expect(form.locator('input[type="tel"]').first()).toHaveValue(expectedPhone)
  await expect(form.locator('input[type="email"]').first()).toHaveValue(env.KOLE_E2E_EMAIL!)
  await expect(page.getByText('По этому email заявку можно будет увидеть в личном кабинете после подтверждения адреса.')).toHaveCount(0)
  await capture(page, 'certificate-prefill.png')
})

test('prefills the question and booking forms from the authenticated profile', async ({ page }) => {
  await page.goto('/excursion/7')
  await expect(page.getByLabel('Ваше имя *')).toHaveValue(expectedName)
  await expect(page.getByLabel('Телефон *').first()).toHaveValue(expectedFormattedPhone)
  await expect(page.getByLabel('Email').first()).toHaveValue(env.KOLE_E2E_EMAIL!)
  await capture(page, 'question-prefill.png')

  await page.getByRole('button', { name: /Осталось мест:/ }).first().click()
  await page.getByRole('button', { name: 'Оставить заявку' }).first().click()
  const modal = page.getByText('Данные автоматически заполнены из вашего аккаунта. Email нельзя изменить вручную.').locator('..').locator('..')
  await expect(modal.getByPlaceholder('Иванов Иван Иванович')).toHaveValue(expectedName)
  await expect(modal.getByPlaceholder('+7 (___) ___-__-__')).toHaveValue(expectedPhone)
  await expect(modal.getByPlaceholder('email@example.com')).toHaveValue(env.KOLE_E2E_EMAIL!)
  await capture(page, 'booking-prefill.png')
})
