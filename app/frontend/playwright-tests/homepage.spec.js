const { test, expect } = require('@playwright/test');

test('homepage loads and has correct title', async ({ page }) => {
  // Change the URL if your dev server runs on a different port
  await page.goto('http://localhost:3000');
  await expect(page).toHaveTitle(/CrossPostMe/);
});
