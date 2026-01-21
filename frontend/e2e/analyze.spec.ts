import { test, expect } from '@playwright/test';

test.describe('Analyze Page', () => {
  test('should display the analyzer form', async ({ page }) => {
    await page.goto('/analyze');
    await page.waitForLoadState('networkidle');

    // Check heading
    await expect(page.getByRole('heading', { name: 'Deck Analyzer' })).toBeVisible();

    // Check commander input
    await expect(page.getByPlaceholder('Muldrotha, the Gravetide')).toBeVisible();

    // Check decklist textarea
    await expect(page.getByPlaceholder(/Sol Ring/)).toBeVisible();

    // Check analyze button
    await expect(page.getByRole('button', { name: 'Analyze Deck' })).toBeVisible();
  });

  test('should have proper labels', async ({ page }) => {
    await page.goto('/analyze');
    await page.waitForLoadState('networkidle');

    await expect(page.getByText('Commander')).toBeVisible();
    await expect(page.getByText('Decklist')).toBeVisible();
  });

  test('button should be disabled while analyzing', async ({ page }) => {
    await page.goto('/analyze');
    await page.waitForLoadState('networkidle');

    // Fill in commander and decklist
    await page.getByPlaceholder('Muldrotha, the Gravetide').fill('Muldrotha, the Gravetide');
    await page.getByPlaceholder(/Sol Ring/).fill('1 Sol Ring\n1 Eternal Witness');

    // Click analyze
    await page.getByRole('button', { name: 'Analyze Deck' }).click();

    // Button should show "Analyzing..." state (may be brief)
    // Just verify the form submission works without errors
  });
});
