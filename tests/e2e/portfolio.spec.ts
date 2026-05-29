import { expect, test, type Page } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const ARTIFACTS = path.join(process.cwd(), 'tests', 'artifacts');
const DOCS_SHOTS = path.join(process.cwd(), 'docs', 'e2e-screenshots');

/** Sections in scroll order on #home */
const SECTION_SHOTS: { id: string; file: string; dwellMs?: number }[] = [
  { id: 'hero', file: '01-hero' },
  { id: 'ai', file: '02-ai' },
  { id: 'wearable', file: '03-wearable' },
  { id: 'features', file: '04-features' },
  { id: 'encryption', file: '05-encryption-sentiment' },
  { id: 'grip', file: '06-grip' },
  { id: 'testimonies', file: '08-testimonies' },
  { id: 'social-content', file: '09-social-content' },
  { id: 'product', file: '10-product' },
  { id: 'open-weight', file: '11-open-weight' },
  { id: 'footer', file: '12-footer' },
];

async function waitForEngine(page: Page) {
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await expect(page.locator('#canvas')).toBeVisible();
  await expect(page.locator('#ui')).toBeVisible();
  await page
    .locator('#preloader')
    .waitFor({ state: 'hidden', timeout: 90_000 })
    .catch(() => {});
  await page.waitForTimeout(3000);
}

async function scrollToSection(page: Page, sectionId: string, viewportAnchor = 0.2) {
  await page.evaluate(
    ({ id, anchor }) => {
      const el = document.getElementById(id);
      if (!el) throw new Error(`missing #${id}`);
      const top = el.getBoundingClientRect().top + window.scrollY - window.innerHeight * anchor;
      window.scrollTo({ top: Math.max(0, top), behavior: 'instant' });
    },
    { id: sectionId, anchor: viewportAnchor },
  );
}

async function capture(page: Page, file: string, dwellMs = 2200) {
  fs.mkdirSync(ARTIFACTS, { recursive: true });
  fs.mkdirSync(DOCS_SHOTS, { recursive: true });
  await page.waitForTimeout(Math.min(dwellMs, 1800));
  const artifactPath = path.join(ARTIFACTS, `${file}.png`);
  const docsPath = path.join(DOCS_SHOTS, `${file}.png`);
  await page.screenshot({ path: artifactPath, fullPage: false, timeout: 60_000 });
  fs.copyFileSync(artifactPath, docsPath);
}

test.describe('Hardik portfolio — full scroll captures', () => {
  test('capture all major sections + coin checks', async ({ page }) => {
    test.setTimeout(600_000);
    await waitForEngine(page);

    for (const { id, file, dwellMs } of SECTION_SHOTS) {
      await scrollToSection(page, id, id === 'footer' ? 0.05 : 0.2);
      await capture(page, file, dwellMs ?? 1600);
    }

    // Extra: features — coin lifted above SDF (coin-sdf mesh) + transform anims
    await scrollToSection(page, 'features', 0.35);
    await page.waitForTimeout(500);
    await page.evaluate(() => {
      window.scrollBy({ top: window.innerHeight * 0.15, behavior: 'instant' });
    });
    await capture(page, '04b-features-coin-close', 2800);

    // Extra: hand scene
    await scrollToSection(page, 'ai', 0.45);
    await capture(page, '02b-ai-hand', 2500);

    // Sustainability act: dark bark zoom then light DOM text (main branch behaviour)
    await scrollToSection(page, 'sustainability', 0.1);
    await page.evaluate(() => {
      const el = document.getElementById('sustainability');
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY;
      window.scrollTo({ top: top + window.innerHeight * 0.55, behavior: 'instant' });
    });
    await capture(page, '07-sustainability-dark-bark', 2800);

    await page.evaluate(() => {
      const el = document.getElementById('sustainability');
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY;
      // Engine shows #sustainability-hero when showScreenOffset >= ~1.8
      window.scrollTo({ top: top + window.innerHeight * 2.35, behavior: 'instant' });
    });
    await page.waitForTimeout(2000);
    const hero = page.locator('#sustainability-hero');
    await expect(hero).toBeVisible();
    await capture(page, '07b-sustainability-light-text', 2500);

    await page.evaluate(() => {
      const el = document.getElementById('sustainability');
      if (!el) return;
      const top = el.getBoundingClientRect().top + window.scrollY;
      window.scrollTo({ top: top + window.innerHeight * 3.6, behavior: 'instant' });
    });
    await capture(page, '07c-sustainability-stats', 2200);

    await expect(page.locator('#sustainability-title-main')).toHaveText(/sustainability/i);

    // Hero glass card still collapsed
    await scrollToSection(page, 'hero', 0.15);
    const box = await page.locator('#hero-card').boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeLessThanOrEqual(2);
    expect(box!.height).toBeLessThanOrEqual(2);
  });
});
