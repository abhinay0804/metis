const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => {
    console.log(`[Browser Console] ${msg.type().toUpperCase()}: ${msg.text()}`);
  });
  
  page.on('pageerror', error => {
    console.error(`[Browser PageError]: ${error.message}`);
  });

  page.on('requestfailed', request => {
    console.error(`[Request Failed]: ${request.url()} - ${request.failure().errorText}`);
  });

  console.log('Navigating to http://localhost:5173/ ...');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0' });
  
  console.log('Navigating to http://localhost:5173/dashboard ...');
  await page.goto('http://localhost:5173/dashboard', { waitUntil: 'networkidle0' });

  await browser.close();
})();
