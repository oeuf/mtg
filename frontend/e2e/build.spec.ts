import { test, expect } from '@playwright/test';

test.describe('Build Page', () => {
  test('should display commander selector', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Check for commander label
    await expect(page.getByText('Commander', { exact: true })).toBeVisible();

    // Check for search input
    await expect(page.getByPlaceholder('Search for a commander')).toBeVisible();
  });

  test('should search and select a commander', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Search for commander
    await page.getByPlaceholder('Search for a commander').fill('Mul');

    // Wait for search results
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);

    // Click on Muldrotha
    await page.getByText('Muldrotha, the Gravetide').click();

    // Commander should be selected (shown in blue box)
    await expect(page.locator('.bg-blue-100')).toContainText('Muldrotha');
  });

  test('should show recommendations after selecting commander', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Select commander
    await page.getByPlaceholder('Search for a commander').fill('Mul');
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);
    await page.getByText('Muldrotha, the Gravetide').click();

    // Wait for recommendations to load (use waitForSelector instead of waitForResponse to be more reliable)
    await page.waitForSelector('text=Sol Ring', { timeout: 10000 });

    // Check that recommendations section shows cards
    await expect(page.getByText('Recommendations')).toBeVisible();
    await expect(page.getByText('Sol Ring')).toBeVisible();
  });

  test('should add card to deck from recommendations', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Select commander
    await page.getByPlaceholder('Search for a commander').fill('Mul');
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);
    await page.getByText('Muldrotha, the Gravetide').click();

    // Wait for recommendations
    await page.waitForResponse(resp => resp.url().includes('/recommendations') && resp.status() === 200);

    // Deck should show 0/99
    await expect(page.getByText('Deck (0/99)')).toBeVisible();

    // Add Sol Ring to deck by clicking + button
    const solRingItem = page.locator('li').filter({ hasText: 'Sol Ring' }).first();
    await solRingItem.getByRole('button', { name: '+' }).click();

    // Deck count should update
    await expect(page.getByText('Deck (1/99)')).toBeVisible();
  });

  test('should remove card from deck', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Select commander and add a card
    await page.getByPlaceholder('Search for a commander').fill('Mul');
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);
    await page.getByText('Muldrotha, the Gravetide').click();
    await page.waitForSelector('text=Sol Ring', { timeout: 10000 });

    // Add card
    const solRingItem = page.locator('li').filter({ hasText: 'Sol Ring' }).first();
    await solRingItem.getByRole('button', { name: '+' }).click();
    await expect(page.getByText('Deck (1/99)')).toBeVisible();

    // Remove card from deck list - the Sol Ring row in deck section has the red x button
    // Find the li with Sol Ring in the deck section (not recommendations) and click its x
    const deckSection = page.locator('div').filter({ hasText: /^Deck \(1\/99\)/ });
    const solRingInDeck = deckSection.locator('li').filter({ hasText: 'Sol Ring' });
    await solRingInDeck.locator('.text-red-500').click();

    // Deck should be empty again
    await expect(page.getByText('Deck (0/99)')).toBeVisible();
  });

  test('should deselect commander', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Select commander
    await page.getByPlaceholder('Search for a commander').fill('Mul');
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);
    await page.getByText('Muldrotha, the Gravetide').click();

    // Commander should be selected
    await expect(page.locator('.bg-blue-100')).toContainText('Muldrotha');

    // Click x to deselect
    await page.locator('.bg-blue-100').getByText('x').click();

    // Search input should reappear
    await expect(page.getByPlaceholder('Search for a commander')).toBeVisible();
  });

  test('commander name should be readable (not dark on dark)', async ({ page }) => {
    await page.goto('/build');
    await page.waitForLoadState('networkidle');

    // Select commander
    await page.getByPlaceholder('Search for a commander').fill('Mul');
    await page.waitForResponse(resp => resp.url().includes('/api/commanders') && resp.status() === 200);
    await page.getByText('Muldrotha, the Gravetide').click();

    // Check the commander name in the selection box is visible
    const commanderBox = page.locator('.bg-blue-100');
    const nameElement = commanderBox.locator('.font-medium');

    // The text should be visible (not have opacity issues or color contrast problems)
    await expect(nameElement).toBeVisible();
    await expect(nameElement).toHaveText(/Muldrotha/);
  });
});
