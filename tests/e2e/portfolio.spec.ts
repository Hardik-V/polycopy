import { expect, test, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const ARTIFACTS = path.join(process.cwd(), 'tests', 'artifacts');

async function waitForEngine(page: Page) {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#canvas')).toBeVisible();
  await expect(page.locator('#ui')).toBeVisible();

  // Preloader fades out once WebGL assets are ready.
  await page
    .locator('#preloader')
    .waitFor({ state: 'hidden', timeout: 90_000 })
    .catch(() => {
      /* some builds keep it in DOM with opacity 0 */
    });

  await page.waitForTimeout(2500);
}

async function scrollToSection(page: Page, sectionId: string) {
  await page.evaluate((id) => {
    const el = document.getElementById(id);
    if (!el) throw new Error(`missing #${id}`);
    const top =
      el.getBoundingClientRect().top + window.scrollY - window.innerHeight * 0.15;
    window.scrollTo({ top: Math.max(0, top), behavior: 'instant' });
  }, sectionId);
  await page.waitForTimeout(2000);
}

async function screenshotSection(page: Page, name: string) {
  fs.mkdirSync(ARTIFACTS, { recursive: true });
  await page.screenshot({
    path: path.join(ARTIFACTS, `${name}.png`),
    fullPage: false,
  });
}

test.describe('Hardik portfolio — visual smoke', () => {
  test.beforeAll(() => {
    fs.mkdirSync(ARTIFACTS, { recursive: true });
  });

  test('hero: glass card collapsed off-screen', async ({ page }) => {
    await waitForEngine(page);
    await screenshotSection(page, '01-hero');

    const card = page.locator('#hero-card');
    await expect(card).toBeAttached();

    const box = await card.boundingBox();
    expect(box).not.toBeNull();
    // overrides.css pins card to 1×1 off-screen
    expect(box!.width).toBeLessThanOrEqual(2);
    expect(box!.height).toBeLessThanOrEqual(2);
    expect(box!.x).toBeLessThan(-1000);

    const headerText = page.locator('#hero-card-header');
    await expect(headerText).toBeHidden();
  });

  test('features: table scene renders (coin on desk)', async ({ page }) => {
    await waitForEngine(page);
    await scrollToSection(page, 'features');
    await screenshotSection(page, '02-features-table');

    const canvas = page.locator('#canvas');
    await expect(canvas).toBeVisible();
    const hasWebgl = await page.evaluate(() => {
      const c = document.querySelector('#canvas') as HTMLCanvasElement | null;
      const gl = c?.getContext('webgl2') || c?.getContext('webgl');
      return !!gl;
    });
    expect(hasWebgl).toBe(true);
  });

  test('sustainability: DOM copy and section layout', async ({ page }) => {
    await waitForEngine(page);
    await scrollToSection(page, 'sustainability');
    await page.waitForTimeout(1500);
    await screenshotSection(page, '03-sustainability-mid');

    // Scroll deeper into sustainability for bark / peel phase
    await page.evaluate(() => {
      const el = document.getElementById('sustainability');
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY + window.innerHeight * 0.6;
      window.scrollTo({ top, behavior: 'instant' });
    });
    await page.waitForTimeout(2500);
    await screenshotSection(page, '04-sustainability-bark');

    const titleMain = page.locator('#sustainability-title-main');
    await expect(titleMain).toHaveText(/hardik verma/i);

    const titleText = (await titleMain.textContent())?.trim() ?? '';
    expect(titleText.toLowerCase()).not.toContain('sustainability');
    expect(titleText.toLowerCase()).not.toContain('curiosity');
  });

  test('sustainability hero hidden until late scroll (no early overlap)', async ({ page }) => {
    await waitForEngine(page);
    await scrollToSection(page, 'sustainability');

    const hero = page.locator('#sustainability-hero');
    const visibility = await hero.evaluate((el) => getComputedStyle(el).visibility);
    expect(visibility).toBe('hidden');
  });
});
