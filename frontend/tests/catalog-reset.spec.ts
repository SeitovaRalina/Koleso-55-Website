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
  await page.route(/^http:\/\/127\.0\.0\.1:4173\/api\//, async route => {
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

async function mockPaginatedCatalog(page: Page, total = 60) {
  await page.route(/^http:\/\/127\.0\.0\.1:4173\/api\//, async route => {
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/categories/')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ count: 1, next: null, previous: null, results: [category] }) })
      return
    }
    if (url.pathname.endsWith('/excursions/')) {
      const currentPage = Number(url.searchParams.get('page') || '1')
      const results = Array.from({ length: 12 }, (_, index) => ({
        ...excursion,
        id: (currentPage - 1) * 12 + index + 1,
        title: `Экскурсия ${currentPage}-${index + 1}`,
      }))
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ count: total, next: null, previous: null, results }) })
      return
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
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
  const sidebar = page.getByRole('complementary', { name: 'Фильтры каталога' })
  await expect(sidebar).toHaveCSS('position', 'sticky')
  await expect(sidebar).toHaveCSS('overflow-y', 'visible')
  if (env.KOLE_SCREENSHOT_DIR) {
    await mkdir(env.KOLE_SCREENSHOT_DIR, { recursive: true })
    await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, 'catalog-filters-visible.png'), fullPage: true })
  }
  await page.getByRole('button', { name: 'Скрыть фильтры' }).click()
  await expect(page.getByRole('complementary', { name: 'Фильтры каталога' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Показать фильтры' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Прогулка по Омску' }).first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'Вторая экскурсия' }).first()).toBeVisible()
  if (env.KOLE_SCREENSHOT_DIR) {
    await mkdir(env.KOLE_SCREENSHOT_DIR, { recursive: true })
    await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, 'catalog-filters-hidden.png'), fullPage: true })
  }
})

test('desktop hidden filters use four-column grid without changing the smaller layouts', async ({ page }) => {
  await mockPaginatedCatalog(page)
  await page.goto('/catalog')
  await expect(page.locator('article')).toHaveCount(12)
  await expect(page.locator('article').first()).toBeVisible()
  await expect(page.locator('article').nth(3)).toBeVisible()

  await page.getByRole('button', { name: 'Скрыть фильтры' }).click()
  const cardGrid = page.locator('article').first().locator('xpath=..')
  await expect(cardGrid).toHaveClass(/xl:grid-cols-4/)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
})

test('desktop filter panel uses the same in-layout sticky treatment as certificate help', async ({ page }) => {
  await mockPaginatedCatalog(page)
  await page.goto('/catalog')
  const sidebar = page.getByRole('complementary', { name: 'Фильтры каталога' })
  await expect(sidebar).toBeVisible()
  await expect(sidebar).toHaveCSS('position', 'sticky')
  await expect(sidebar).toHaveCSS('top', '96px')
  await expect(sidebar).toHaveCSS('overflow-y', 'visible')
  await page.evaluate(() => window.scrollTo(0, 700))
  await expect.poll(() => sidebar.evaluate(element => Math.round(element.getBoundingClientRect().top))).toBe(96)
})

test('pagination keeps the query, uses Russian controls and returns to result controls', async ({ page }) => {
  await mockPaginatedCatalog(page, 120)
  await page.goto('/catalog?search=Омск')
  await expect(page.getByText('Найдено 120 экскурсий')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Следующая' })).toBeVisible()
  await expect(page.getByText('Вперед', { exact: true })).toHaveCount(0)
  await expect(page.getByText('…')).toHaveCount(1)

  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))
  await page.getByRole('button', { name: 'Страница 2' }).click()
  await expect(page).toHaveURL(/search=%D0%9E%D0%BC%D1%81%D0%BA&page=2/)
  await expect(page.getByRole('button', { name: 'Страница 2' })).toHaveAttribute('aria-current', 'page')
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeLessThan(500)

  await page.goto('/catalog?page=5')
  await expect(page.getByRole('button', { name: 'Страница 4' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Страница 5' })).toHaveAttribute('aria-current', 'page')
  await expect(page.getByRole('button', { name: 'Страница 6' })).toBeVisible()
  await expect(page.getByText('…')).toHaveCount(2)
})

test('certificate help panel is desktop-sticky, useful and remains in normal mobile flow', async ({ page }) => {
  await page.goto('/certificates')
  const panel = page.getByText('Подарите впечатления, которые остаются').locator('..')
  await expect(panel).toBeVisible()
  await expect(page.getByText('Менеджер уточнит детали и подготовит сертификат.')).toBeVisible()
  await expect(page.getByRole('link', { name: /Ирина Руснак/ })).toBeVisible()
  await expect(panel).toHaveCSS('position', 'sticky')
  await expect(panel).toHaveCSS('overflow-y', 'visible')
  if (env.KOLE_SCREENSHOT_DIR) {
    await mkdir(env.KOLE_SCREENSHOT_DIR, { recursive: true })
    await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, 'certificates-desktop.png'), fullPage: true })
  }

  await page.setViewportSize({ width: 390, height: 844 })
  await expect(panel).toHaveCSS('position', 'static')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  if (env.KOLE_SCREENSHOT_DIR) {
    await page.screenshot({ path: join(env.KOLE_SCREENSHOT_DIR, 'certificates-mobile.png'), fullPage: true })
  }
})
