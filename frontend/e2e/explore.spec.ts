import { test, expect } from '@playwright/test';

test.describe('Explore Page', () => {
  test('should display the graph explorer', async ({ page }) => {
    await page.goto('/explore');
    await page.waitForLoadState('networkidle');

    // Check heading
    await expect(page.getByRole('heading', { name: 'Graph Explorer' })).toBeVisible();

    // Check search input
    await expect(page.getByPlaceholder('Enter card name to explore')).toBeVisible();

    // Check explore button
    await expect(page.getByRole('button', { name: 'Explore' })).toBeVisible();
  });

  test('should have legend', async ({ page }) => {
    await page.goto('/explore');
    await page.waitForLoadState('networkidle');

    // Check legend
    await expect(page.getByText('Legend')).toBeVisible();
    await expect(page.getByText('Card')).toBeVisible();
    await expect(page.getByText('Mechanic')).toBeVisible();
    await expect(page.getByText('Role')).toBeVisible();
  });

  test('should show node details panel', async ({ page }) => {
    await page.goto('/explore');
    await page.waitForLoadState('networkidle');

    // Check node details section
    await expect(page.getByText('Node Details')).toBeVisible();
    await expect(page.getByText('Click a node to see details')).toBeVisible();
  });
});
