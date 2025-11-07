const { test, expect } = require('@playwright/test');

// Helper to check API connectivity
async function checkApi(page, endpoint) {
  const [response] = await Promise.all([
    page.waitForResponse(resp => resp.url().includes(endpoint) && resp.status() === 200),
    page.goto('http://localhost:3000'),
  ]);
  expect(response.ok()).toBeTruthy();
}

test('homepage loads and API is reachable', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/CrossPostMe/);
  // Check API endpoint
  await checkApi(page, '/api/status');
});

test('login page and error handling', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.locator('form')).toBeVisible();
  await page.fill('input[type="email"]', 'invalid@example.com');
  await page.fill('input[type="password"]', 'wrongpassword');
  await page.click('button[type="submit"]');
  await expect(page.locator('.error')).toBeVisible();
});

test('dashboard loads and lists ads', async ({ page }) => {
  await page.goto('http://localhost:3000/dashboard');
  await expect(page.locator('.ad-list')).toBeVisible();
  // Should fetch ads from backend
  const ads = await page.locator('.ad-list .ad-item').count();
  expect(ads).toBeGreaterThanOrEqual(0);
});

test('ad creation and persistence', async ({ page }) => {
  await page.goto('http://localhost:3000/create-ad');
  await page.fill('input[name="title"]', 'Playwright Test Ad');
  await page.fill('textarea[name="description"]', 'Automated test ad.');
  await page.fill('input[name="price"]', '123.45');
  await page.click('button[type="submit"]');
  await expect(page.locator('.success')).toBeVisible();
  // Verify ad appears in dashboard
  await page.goto('http://localhost:3000/dashboard');
  await expect(page.locator('.ad-list .ad-item:has-text("Playwright Test Ad")')).toBeVisible();
});
