import { mkdir } from 'node:fs/promises'
import { join } from 'node:path'
import { env } from 'node:process'
import { expect, test, type Page } from '@playwright/test'

const category = { id: 1, name: 'Категория 1', slug: 'cat-1' }
const excursion = {
  id: 1,
  slug: 'omsk-walk',
  title: 'Прогулка по Омску',
  short_description: 'История города',
  price: '1500.00',
  duration: 120,
  average_rating: 4.8,
  review_count: 12,
  category,
  main_image: null,
  nearest_slots: [],
}

async function mockCatalog(page: Page) {
  await page.route('http://localhost:8001/api/**', async route => {
    const url = new URL(route.request().url())
    const filtered = url.searchParams.has('category') || url.searchParams.has('search') || url.searchParams.has('location_type')
    const body = url.pathname.endsWith('/categories/')
      ? { count: 1, next: null, previous: null, results: [category] }
      : url.pathname.endsWith('/excursions/')
        ? { count: filtered ? 1 : 2, next: null, previous: null, results: filtered ? [excursion] : [excursion, { ...excursion, id: 2, title: 'Вторая экскурсия' }] }
        : {}
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      headers: { 'access-control-allow-origin': '*' },
      body: JSON.stringify(body),
    })
  })
}

test('global reset restores initial catalog from direct link, after repeat and reload', async ({ page }) => {
  await mockCatalog(page)
  await page.goto('/catalog?category=cat-1&location_type=city&min_price=1000&date_from=2026-11-01&search=Омск&ordering=price&page=2')
  await expect(page.getByRole('checkbox', { name: 'Категория 1' })).toBeChecked()
  await expect(page.getByRole('searchbox', { name: 'Поиск экскурсий' })).toHaveValue('Омск')

  await page.getByRole('button', { name: 'Сбросить все фильтры' }).click()
  await expect(page).toHaveURL(/\/catalog$/)
  await expect(page.getByRole('searchbox', { name: 'Поиск экскурсий' })).toHaveValue('')
  await expect(page.getByRole('checkbox', { name: 'Категория 1' })).not.toBeChecked()
  await expect(page.getByText('Найдено 2 экскурсий')).toBeVisible()

  await page.getByRole('button', { name: 'Сбросить все фильтры' }).click()
  await expect(page).toHaveURL(/\/catalog$/)
  await page.reload()
  await expect(page.getByText('Найдено 2 экскурсий')).toBeVisible()
  await expect(page.getByRole('checkbox', { name: 'Категория 1' })).not.toBeChecked()
  if (env.KOLE_SCREENSHOT_DIR) {
    await mkdir(env.KOLE_SCREENSHOT_DIR, { recursive: true })
    await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, 'catalog-reset.png'), fullPage: true })
  }
})

test('category reset means all categories, including explicit empty selection', async ({ page }) => {
  await mockCatalog(page)
  await page.goto('/catalog?category=cat-1&location_type=city')
  await page.locator('aside section').first().getByRole('button', { name: 'Сбросить' }).click()
  await expect(page).toHaveURL(/\/catalog\?location_type=city$/)
  await expect(page.getByRole('checkbox', { name: 'Категория 1' })).not.toBeChecked()

  await page.goto('/catalog?category=')
  await expect(page.getByText('Выберите категорию или нажмите')).toBeVisible()
  await page.locator('aside section').first().getByRole('button', { name: 'Сбросить' }).click()
  await expect(page).toHaveURL(/\/catalog$/)
  await expect(page.getByText('Найдено 2 экскурсий')).toBeVisible()
  await page.reload()
  await expect(page.getByText('Найдено 2 экскурсий')).toBeVisible()
})

test('mobile reset clears direct-link filters without overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockCatalog(page)
  await page.goto('/catalog?category=cat-1&search=Омск')
  await page.getByRole('button', { name: 'Фильтры', exact: true }).click()
  await page.getByRole('button', { name: 'Сбросить все фильтры' }).click()
  await expect(page).toHaveURL(/\/catalog$/)
  await expect(page.getByText('Найдено 2 экскурсий')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
})

test('desktop hide removes entire filter panel and gives cards full width', async ({ page }) => {
  await mockCatalog(page)
  await page.goto('/catalog')
  await expect(page.getByText('Найдено 2 экскурсий')).toBeVisible()
  await page.getByRole('button', { name: 'Скрыть фильтры' }).click()
  await expect(page.getByRole('complementary', { name: 'Фильтры каталога' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Показать фильтры' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Прогулка по Омску' }).first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'Вторая экскурсия' }).first()).toBeVisible()
  if (env.KOLE_SCREENSHOT_DIR) {
    await mkdir(env.KOLE_SCREENSHOT_DIR, { recursive: true })
    await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, 'desktop-hidden.png'), fullPage: true })
  }
})
