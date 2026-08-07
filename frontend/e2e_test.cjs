const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

(async () => {
  console.log('Starting E2E Dry Run...');
  const browser = await puppeteer.launch({ 
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800'],
    headless: "new"
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  page.on('console', msg => {
    if (msg.type() === 'error') console.log(`[Browser Console Error] ${msg.text()}`);
  });

  try {
    // 1. Sign up a new user
    console.log('Navigating to Sign Up page...');
    await page.goto('http://localhost:5173/signup', { waitUntil: 'networkidle0' });
    
    console.log('Filling out Sign Up form...');
    await page.type('#firstName', 'Test');
    await page.type('#lastName', 'User');
    const randomEmail = `testuser_${Date.now()}@example.com`;
    await page.type('#email', randomEmail);
    await page.type('#company', 'Acme Corp');
    await page.type('#password', 'Test@123456');
    await page.type('#confirmPassword', 'Test@123456');
    
    console.log('Submitting Sign Up form...');
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle0' }),
      page.click('button[type="submit"]')
    ]);

    // Check if we are on dashboard
    const url = page.url();
    if (!url.includes('/dashboard')) {
      throw new Error(`Failed to route to dashboard, current URL: ${url}`);
    }
    console.log('Successfully reached Dashboard!');

    // Wait a moment for any tours/popups
    await new Promise(r => setTimeout(r, 1000));
    
    // Dismiss the tour if present (Skip button)
    try {
      const skipButton = await page.$('button[aria-label="Skip"]');
      if (skipButton) {
        console.log('Skipping Guided Tour...');
        await skipButton.click();
        await new Promise(r => setTimeout(r, 500));
      }
    } catch (e) {}

    // 2. Upload file
    console.log('Uploading sample_data.json...');
    const fileInput = await page.$('input[type="file"]');
    await fileInput.uploadFile('/mnt/shared/Projects/Metis/sample_data.json');
    
    await new Promise(r => setTimeout(r, 500)); // wait for UI update

    // 3. Click Mask Data
    console.log('Clicking "Mask Data"...');
    // Using XPath or text search since the button has text 'Mask Data'
    const maskButton = await page.evaluateHandle(() => {
      return Array.from(document.querySelectorAll('button')).find(el => el.textContent === 'Mask Data');
    });
    
    if (maskButton) {
      await maskButton.click();
    } else {
      throw new Error('Mask Data button not found');
    }

    // Wait for the masking to complete (toast notification or processing state to finish)
    console.log('Waiting for Masking process...');
    await new Promise(r => setTimeout(r, 3000));

    // Check History Tab for the masked data
    console.log('Checking History Tab...');
    const historyTab = await page.evaluateHandle(() => {
      return Array.from(document.querySelectorAll('button[role="tab"]')).find(el => el.textContent.includes('History'));
    });
    if (historyTab) await historyTab.click();
    
    await new Promise(r => setTimeout(r, 1000));
    
    // Scrape history table
    const tableData = await page.evaluate(() => {
      const rows = document.querySelectorAll('table tbody tr');
      return Array.from(rows).map(row => {
        const cells = row.querySelectorAll('td');
        return Array.from(cells).map(cell => cell.textContent.trim());
      });
    });
    console.log('History Table Data:', tableData);
    
    if (tableData.length > 0) {
      console.log('SUCCESS: E2E Dry run completed. File was uploaded, masked, and recorded in history!');
    } else {
      throw new Error('History table is empty! Masking might have failed or not recorded.');
    }

  } catch (error) {
    console.error('E2E Test Failed:', error);
  } finally {
    await browser.close();
  }
})();
