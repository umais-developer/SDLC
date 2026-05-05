import { test, expect } from '@playwright/test';

test.describe('Pomodoro App — smoke tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('./');
  });

  test('page loads without 404', async ({ page }) => {
    await expect(page).not.toHaveTitle(/404|File not found|Page not found/i);
    await expect(page).toHaveTitle(/Pomodoro/i);
  });

  test('timer displays 25:00 on initial load', async ({ page }) => {
    const timer = page.getByText('25:00');
    await expect(timer).toBeVisible();
  });

  test('Work Session label is visible', async ({ page }) => {
    const label = page.getByText('Work Session');
    await expect(label).toBeVisible();
  });

  test('Start button is present and clickable', async ({ page }) => {
    const startBtn = page.getByRole('button', { name: /Start timer/i });
    await expect(startBtn).toBeVisible();
    await expect(startBtn).toBeEnabled();
  });

  test('timer counts down after clicking Start', async ({ page }) => {
    const startBtn = page.getByRole('button', { name: /Start timer/i });
    await startBtn.click();

    // Wait up to 3 seconds for the timer to have ticked at least once
    await expect(async () => {
      const text = await page.getByText(/^\d{2}:\d{2}$/).textContent();
      expect(text).not.toBe('25:00');
    }).toPass({ timeout: 3000 });
  });

  test('Settings button opens settings panel', async ({ page }) => {
    const settingsBtn = page.getByRole('button', { name: /settings/i });
    await expect(settingsBtn).toBeVisible();
    await settingsBtn.click();
    await expect(page.getByText(/Work Duration/i)).toBeVisible();
  });
});
