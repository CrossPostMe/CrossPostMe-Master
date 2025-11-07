// playwright.config.js
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './playwright-tests',
  globalSetup: require.resolve('./playwright-tests/playwright.setup.js'),
  webServer: {
    command: 'yarn start',
    port: 3000,
    timeout: 120 * 1000,
    reuseExistingServer: true,
  },
});
