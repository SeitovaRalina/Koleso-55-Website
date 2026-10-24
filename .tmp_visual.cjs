const { chromium } = require('./.visual-tools/node_modules/playwright-core')
const path = require('path')

async function main() {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    headless: true,
  })
  try {
    for (const [name, route, width, height] of [
      ['catalog-desktop', '/catalog', 1440, 900],
      ['catalog-mobile', '/catalog', 390, 844],
      ['short-detail', '/excursion/1', 1440, 900],
      ['multi-detail', '/excursion/2', 390, 844],
    ]) {
      const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: 1 })
      await page.goto(`http://127.0.0.1:8765${route}`, { waitUntil: 'networkidle' })
      await page.screenshot({ path: path.join('.visual-shots', `${name}.png`), fullPage: true })
      console.log(name, await page.evaluate(() => ({ width: innerWidth, scrollWidth: document.documentElement.scrollWidth })))
      await page.close()
    }
  } finally {
    await browser.close()
  }
}

main().catch(error => { console.error(error); process.exitCode = 1 })
