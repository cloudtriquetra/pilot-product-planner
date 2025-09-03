/**
 * E2E Tests: Complete Trade Workflow
 * Tests the entire user journey from entry to confirmation
 */

import { test, expect } from '@playwright/test';

test.describe('Voice Trade E2E Workflow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('file://' + process.cwd() + '/workspace/electronification-of-voice-trades-under-1million/_wip/index.html');
    
    // Clear localStorage to start fresh
    await page.evaluate(() => localStorage.clear());
  });

  test('Complete trade submission workflow', async ({ page }) => {
    // Verify page loads correctly
    await expect(page.locator('h1')).toContainText('Voice Trade Electronification');
    
    // Fill in trade details
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'AAPL');
    await page.fill('#quantity', '100');
    await page.fill('#price', '150.50');
    await page.fill('#counterparty', 'Goldman Sachs');
    await page.fill('#trader', 'John Smith');
    await page.fill('#notes', 'Voice trade from client call at 10:30 AM');
    
    // Submit the trade
    await page.click('button[type="submit"]');
    
    // Verify success toast
    const toast = page.locator('#toast');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('processed successfully');
    
    // Verify trade appears in the list
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('AAPL');
    await expect(tradeList).toContainText('$15,050');
    await expect(tradeList).toContainText('pending');
    
    // Wait for auto-confirmation
    await page.waitForTimeout(2100);
    await expect(tradeList).toContainText('confirmed');
    
    // Verify summary updates
    await expect(page.locator('#totalTrades')).toContainText('1');
    await expect(page.locator('#totalVolume')).toContainText('$15,050');
    await expect(page.locator('#avgSize')).toContainText('$15,050');
  });

  test('Quick action buttons workflow', async ({ page }) => {
    // Test quick buy button
    await page.click('button:has-text("Quick Buy")');
    await expect(page.locator('#tradeType')).toHaveValue('BUY');
    
    // Test quick sell button
    await page.click('button:has-text("Quick Sell")');
    await expect(page.locator('#tradeType')).toHaveValue('SELL');
    
    // Test equity button
    await page.click('button:has-text("Equity")');
    await expect(page.locator('#instrument')).toHaveValue('EQUITY');
    
    // Test bond button
    await page.click('button:has-text("Bond")');
    await expect(page.locator('#instrument')).toHaveValue('BOND');
  });

  test('Form validation prevents invalid submission', async ({ page }) => {
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Check that no trade was added
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('No trades recorded yet');
    
    // Fill partial form and verify field validation
    await page.fill('#quantity', '-10');
    await page.fill('#price', '0');
    
    // Check HTML5 validation
    const quantityInput = page.locator('#quantity');
    const isQuantityValid = await quantityInput.evaluate(el => el.validity.valid);
    expect(isQuantityValid).toBe(false);
    
    const priceInput = page.locator('#price');
    const isPriceValid = await priceInput.evaluate(el => el.validity.valid);
    expect(isPriceValid).toBe(false);
  });

  test('Trade over $1M limit is rejected', async ({ page }) => {
    // Fill in trade over $1M
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'EXPENSIVE');
    await page.fill('#quantity', '10000');
    await page.fill('#price', '100');
    await page.fill('#counterparty', 'Big Bank');
    await page.fill('#trader', 'Rich Trader');
    
    // Submit the trade
    await page.click('button[type="submit"]');
    
    // Verify error toast
    const toast = page.locator('#toast');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('exceeds $1M limit');
    
    // Verify trade was not added
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('No trades recorded yet');
  });

  test('Multiple trades workflow', async ({ page }) => {
    // Submit first trade
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'MSFT');
    await page.fill('#quantity', '200');
    await page.fill('#price', '300');
    await page.fill('#counterparty', 'Morgan Stanley');
    await page.fill('#trader', 'Alice Johnson');
    await page.click('button[type="submit"]');
    
    // Wait for form to clear
    await page.waitForTimeout(100);
    
    // Submit second trade
    await page.selectOption('#tradeType', 'SELL');
    await page.selectOption('#instrument', 'BOND');
    await page.fill('#symbol', 'US10Y');
    await page.fill('#quantity', '1000');
    await page.fill('#price', '98.50');
    await page.fill('#counterparty', 'JP Morgan');
    await page.fill('#trader', 'Bob Wilson');
    await page.click('button[type="submit"]');
    
    // Wait for form to clear
    await page.waitForTimeout(100);
    
    // Submit third trade
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'FX');
    await page.fill('#symbol', 'EURUSD');
    await page.fill('#quantity', '50000');
    await page.fill('#price', '1.08');
    await page.fill('#counterparty', 'Citi');
    await page.fill('#trader', 'Charlie Brown');
    await page.click('button[type="submit"]');
    
    // Verify all trades appear
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('MSFT');
    await expect(tradeList).toContainText('US10Y');
    await expect(tradeList).toContainText('EURUSD');
    
    // Verify summary calculations
    await expect(page.locator('#totalTrades')).toContainText('3');
    
    // Total: $60,000 + $98,500 + $54,000 = $212,500
    await expect(page.locator('#totalVolume')).toContainText('212,500');
    
    // Average: $212,500 / 3 = $70,833.33
    await expect(page.locator('#avgSize')).toContainText('70,833');
  });

  test('Keyboard shortcuts', async ({ page }) => {
    // Fill form
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'KEYS');
    await page.fill('#quantity', '50');
    await page.fill('#price', '75');
    await page.fill('#counterparty', 'Test');
    await page.fill('#trader', 'Keyboard User');
    
    // Submit with Ctrl+Enter (or Cmd+Enter on Mac)
    await page.keyboard.down('Control');
    await page.keyboard.press('Enter');
    await page.keyboard.up('Control');
    
    // Verify trade was submitted
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('KEYS');
    
    // Clear form with Escape
    await page.fill('#symbol', 'CLEAR_ME');
    await page.keyboard.press('Escape');
    
    // Verify form was cleared
    await expect(page.locator('#symbol')).toHaveValue('');
  });

  test('Trade persistence across page reloads', async ({ page }) => {
    // Submit a trade
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'PERSIST');
    await page.fill('#quantity', '100');
    await page.fill('#price', '50');
    await page.fill('#counterparty', 'Test Corp');
    await page.fill('#trader', 'Test Trader');
    await page.click('button[type="submit"]');
    
    // Wait for trade to be saved
    await page.waitForTimeout(100);
    
    // Reload the page
    await page.reload();
    
    // Verify trade persisted
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('PERSIST');
    await expect(tradeList).toContainText('$5,000');
    
    // Verify summary persisted
    await expect(page.locator('#totalTrades')).toContainText('1');
    await expect(page.locator('#totalVolume')).toContainText('$5,000');
  });

  test('Click on trade to view details', async ({ page }) => {
    // Submit a trade
    await page.selectOption('#tradeType', 'SELL');
    await page.selectOption('#instrument', 'COMMODITY');
    await page.fill('#symbol', 'GOLD');
    await page.fill('#quantity', '10');
    await page.fill('#price', '1950');
    await page.fill('#counterparty', 'Commodity Traders Inc');
    await page.fill('#trader', 'Gold Trader');
    await page.click('button[type="submit"]');
    
    // Wait for trade to appear
    await page.waitForTimeout(100);
    
    // Click on the trade item
    await page.click('.trade-item');
    
    // Verify toast shows trade details
    const toast = page.locator('#toast');
    await expect(toast).toBeVisible();
    await expect(toast).toContainText('GOLD');
    await expect(toast).toContainText('1950');
  });

  test('Voice indicator is visible', async ({ page }) => {
    // Check for voice indicator
    const voiceIndicator = page.locator('.voice-indicator');
    await expect(voiceIndicator).toBeVisible();
    await expect(voiceIndicator).toContainText('Voice Trade');
    
    // Check for pulse animation
    const pulse = page.locator('.pulse');
    await expect(pulse).toBeVisible();
  });

  test('Responsive design on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Verify panels stack vertically
    const mainGrid = page.locator('.main-grid');
    const gridStyle = await mainGrid.evaluate(el => 
      window.getComputedStyle(el).gridTemplateColumns
    );
    
    // On mobile, should be single column
    expect(gridStyle).toBe('1fr');
    
    // Verify all elements are still accessible
    await expect(page.locator('#tradeForm')).toBeVisible();
    await expect(page.locator('#tradeList')).toBeVisible();
    await expect(page.locator('.summary-panel')).toBeVisible();
  });

  test('Symbol uppercase conversion', async ({ page }) => {
    // Enter lowercase symbol
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'lowercase');
    await page.fill('#quantity', '100');
    await page.fill('#price', '50');
    await page.fill('#counterparty', 'Test');
    await page.fill('#trader', 'Test');
    await page.click('button[type="submit"]');
    
    // Verify symbol was converted to uppercase
    const tradeList = page.locator('#tradeList');
    await expect(tradeList).toContainText('LOWERCASE');
  });

  test('Clear button functionality', async ({ page }) => {
    // Fill all form fields
    await page.selectOption('#tradeType', 'BUY');
    await page.selectOption('#instrument', 'EQUITY');
    await page.fill('#symbol', 'TEST');
    await page.fill('#quantity', '100');
    await page.fill('#price', '50');
    await page.fill('#counterparty', 'Test Corp');
    await page.fill('#trader', 'Test Trader');
    await page.fill('#notes', 'Test notes');
    
    // Click clear button
    await page.click('button:has-text("Clear")');
    
    // Verify all fields are cleared
    await expect(page.locator('#tradeType')).toHaveValue('');
    await expect(page.locator('#instrument')).toHaveValue('');
    await expect(page.locator('#symbol')).toHaveValue('');
    await expect(page.locator('#quantity')).toHaveValue('');
    await expect(page.locator('#price')).toHaveValue('');
    await expect(page.locator('#counterparty')).toHaveValue('');
    await expect(page.locator('#trader')).toHaveValue('');
    await expect(page.locator('#notes')).toHaveValue('');
  });
});