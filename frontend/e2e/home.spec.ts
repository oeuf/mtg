import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('should display the title and navigation', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check title
    await expect(page).toHaveTitle(/MTG Commander/);

    // Check main heading
    await expect(page.getByRole('heading', { name: 'MTG Commander Deck Builder' })).toBeVisible();

    // Check navigation links (in nav bar)
    const nav = page.locator('nav');
    await expect(nav.getByRole('link', { name: 'MTG KB' })).toBeVisible();
    await expect(nav.getByRole('link', { name: 'Build' })).toBeVisible();
    await expect(nav.getByRole('link', { name: 'Analyze' })).toBeVisible();
    await expect(nav.getByRole('link', { name: 'Explore' })).toBeVisible();
  });

  test('should have working navigation links', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Click Deck Builder link
    await page.getByRole('link', { name: 'Deck Builder' }).click();
    await expect(page).toHaveURL('/build');

    // Go back and click Deck Analyzer
    await page.goto('/');
    await page.getByRole('link', { name: 'Deck Analyzer' }).click();
    await expect(page).toHaveURL('/analyze');

    // Go back and click Graph Explorer
    await page.goto('/');
    await page.getByRole('link', { name: 'Graph Explorer' }).click();
    await expect(page).toHaveURL('/explore');
  });

  test('should search for commanders', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Type in search box
    const searchInput = page.getByPlaceholder('Search for a commander');
    await searchInput.fill('Mul');

    // Wait for results to appear
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);

    // Check that Muldrotha appears in results
    await expect(page.getByText('Muldrotha, the Gravetide')).toBeVisible();
  });

  test('should navigate to commander page from search results', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Search for a commander
    await page.getByPlaceholder('Search for a commander').fill('Mul');
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);

    // Click on the commander
    await page.getByText('Muldrotha, the Gravetide').click();

    // Should navigate to commander page
    await expect(page).toHaveURL(/\/commander\/.+/);
  });
});
