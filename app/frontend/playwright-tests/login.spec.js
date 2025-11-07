const { test, expect } = require('@playwright/test');

test('login page loads and shows form', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await expect(page.locator('form')).toBeVisible();
  await expect(page.locator('input[type="email"]')).toBeVisible();
  await expect(page.locator('input[type="password"]')).toBeVisible();
});

test('login with invalid credentials shows error', async ({ page }) => {
  await page.goto('http://localhost:3000/login');
  await page.fill('input[type="email"]', 'invalid@example.com');
  await page.fill('input[type="password"]', 'wrongpassword');
  await page.click('button[type="submit"]');
  await expect(page.locator('.error')).toBeVisible();
});
