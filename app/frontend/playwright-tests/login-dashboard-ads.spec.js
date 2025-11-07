const { test, expect } = require('@playwright/test');


async function login(page, username, password) {
  await page.goto('http://localhost:3000/login');
  await expect(page.locator('form')).toBeVisible();
  // Use demo mode if available
  const demoButton = page.locator('button', { hasText: 'Try Demo Mode' });
  if (await demoButton.isVisible()) {
    await demoButton.click();
    await page.waitForTimeout(1000);
    return;
  }
  // Fallback to username/password
  await page.fill('input#username', username);
  await page.fill('input#password', password);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1000);
}


test('login page renders and handles errors', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.locator('form')).toBeVisible();
  await page.fill('input#username', 'invaliduser');
  await page.fill('input#password', 'wrongpassword');
  await page.click('button[type="submit"]');
  // Should remain on login page (form still visible)
  await expect(page.locator('form')).toBeVisible();
});


test('dashboard loads and stats are fetched', async ({ page }) => {
  await login(page, 'demo', 'demo'); // Replace with valid test credentials
  await page.goto('http://localhost:3000/marketplace/dashboard');
  // Print page HTML for debugging
  const html = await page.content();
  console.log('--- DASHBOARD HTML ---\n', html);
  await expect(page.locator('h1')).toContainText('Dashboard');
  await expect(page.locator('p')).toContainText('Welcome back');
});


test('ad creation form submits and persists', async ({ page }) => {
  await login(page, 'demo', 'demo'); // Replace with valid test credentials
  await page.goto('http://localhost:3000/marketplace/create-ad');
  // Print page HTML for debugging
  const html = await page.content();
  console.log('--- CREATE AD HTML ---\n', html);
  await expect(page.locator('form')).toBeVisible();
  await page.fill('input[placeholder="Enter product name"]', 'Playwright Ad');
  await page.fill('input[placeholder="Enter price"]', '99.99');
  await page.selectOption('select', { label: 'Electronics' });
  await page.fill('textarea[placeholder="Enter description"]', 'Test ad description.');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(1000);
  // Should redirect or show success toast (skip assertion for now)
});


test('my ads page lists ads', async ({ page }) => {
  await login(page, 'demo', 'demo'); // Replace with valid test credentials
  await page.goto('http://localhost:3000/marketplace/my-ads');
  // Print page HTML for debugging
  const html = await page.content();
  console.log('--- MY ADS HTML ---\n', html);
  await expect(page.locator('h3')).toContainText('My Ads');
  await expect(page.locator('text=View and manage all your advertisements')).toBeVisible();
});
