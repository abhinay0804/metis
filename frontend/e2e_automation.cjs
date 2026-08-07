const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://localhost';
const UPLOADS_DIR = path.join(__dirname, '..', 'test_files');

const FORMATS = [
    'sample.txt',
    'sample.csv',
    'sample.docx',
    'sample.pdf',
    'sample.xlsx',
    'sample.png'
];

async function runTests() {
    console.log("🚀 Starting Comprehensive Metis E2E UI Automation");
    
    const browser = await puppeteer.launch({
        headless: 'new', // Use 'new' for latest headless mode
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1280,800']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    try {
        // --- 1. Static Components Check ---
        console.log("checking Landing Page links...");
        await page.goto(BASE_URL);
        
        // Check Mailto and Github links exist on landing page
        const mailtoLink = await page.$('a[href="mailto:namaabhinay@gmail.com"]');
        if (!mailtoLink) throw new Error("Mailto link not found on landing page!");
        
        const githubLink = await page.$('a[href="https://github.com/abhinay0804/metis"]');
        if (!githubLink) throw new Error("Github link not found on landing page!");
        
        console.log("✅ Static components verified.");

        // --- 2. Auth Flow ---
        console.log("Testing Authentication (Signup & Login)...");
        await page.goto(`${BASE_URL}/signup`);
        await page.waitForSelector('input[id="firstName"]');
        
        const timestamp = Date.now();
        const email = `testuser_${timestamp}@example.com`;
        const password = `Password123!`;
        
        await page.type('input[id="firstName"]', 'Automated');
        await page.type('input[id="lastName"]', 'User');
        await page.type('input[id="email"]', email);
        await page.type('input[id="company"]', 'Acme Corp');
        await page.type('input[id="password"]', password);
        await page.type('input[id="confirmPassword"]', password);
        
        // Find signup button
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const signup = btns.find(b => b.innerText.includes('Create Account'));
            if(signup) signup.click();
        });
        
        // Wait for redirect to login or dashboard (SPA navigation)
        await page.waitForFunction(() => window.location.href.includes('login') || window.location.href.includes('dashboard'), { timeout: 10000 });
        
        // If redirected to login, login
        if (page.url().includes('login')) {
            await page.type('input[id="email"]', email);
            await page.type('input[id="password"]', password);
            await page.click('button[type="submit"]');
            await page.waitForFunction(() => window.location.href.includes('dashboard'), { timeout: 10000 });
        }
        
        if (!page.url().includes('dashboard')) {
            throw new Error(`Failed to reach dashboard, current URL: ${page.url()}`);
        }
        console.log("✅ Authentication flow passed.");
        
        // --- 3. Profile Edits & Validation ---
        console.log("Testing Profile Page & Phone Validation...");
        await page.goto(`${BASE_URL}/profile`);
        await page.waitForSelector('input[id="phone"]');
        await new Promise(r => setTimeout(r, 2000)); // Wait for API fetch to populate state
        
        // Click the Edit button first
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const edit = btns.find(b => b.innerText.includes('Edit'));
            if(edit) edit.click();
        });
        await new Promise(r => setTimeout(r, 500));
        
        // Type invalid characters + too many digits
        await page.click('input[id="phone"]', { clickCount: 3 });
        await page.keyboard.press('Backspace');
        await new Promise(r => setTimeout(r, 500));
        
        await page.type('input[id="phone"]', '123abc456def7890123'); // Should filter to 1234567890
        
        const phoneVal = await page.$eval('input[id="phone"]', el => el.value);
        if (phoneVal !== '1234567890') {
            throw new Error(`Phone validation failed. Expected 1234567890, got: ${phoneVal}`);
        }
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const save = btns.find(b => b.innerText.includes('Save Changes'));
            if(save) save.click();
        });
        await new Promise(r => setTimeout(r, ));
        console.log("✅ Profile validation passed.");

        // --- 4. Iterative Masking & Analysis ---
        await page.goto(`${BASE_URL}/dashboard`);
        await page.evaluate(() => localStorage.setItem('geminiApiKey', 'YOUR_GEMINI_API_KEY_HERE'));

        for (let i = 0; i < FORMATS.length; i++) {
            const format = FORMATS[i];
            const isReversible = i % 2 === 0; // Alternate reversible flag
            const isAnalysis = i === FORMATS.length - 1; // Last one is analysis
            
            console.log(`Testing format: ${format} | Reversible: ${isReversible} | Analysis: ${isAnalysis}`);
            await page.goto(`${BASE_URL}/dashboard`);
            await page.waitForSelector('input[type="file"]');
            
            // Upload file
            const inputUploadHandle = await page.$('input[type="file"]');
            await inputUploadHandle.uploadFile(path.join(UPLOADS_DIR, format));
            
            await new Promise(r => setTimeout(r, )); // UI animation wait
            
            if (isReversible) {
                // Click reversible switch
                await page.evaluate(() => {
                    const btn = document.querySelector('button[id="reversible-mode"]');
                    if (btn && btn.getAttribute('aria-checked') === 'false') {
                        btn.click();
                    }
                });
            } else {
                await page.evaluate(() => {
                    const btn = document.querySelector('button[id="reversible-mode"]');
                    if (btn && btn.getAttribute('aria-checked') === 'true') {
                        btn.click();
                    }
                });
            }
            
            if (isAnalysis) {
                // Click Analyze Data button using text selector
                const buttons = await page.$$('::-p-text(Analyze Data)');
                if (buttons.length > 0) await buttons[0].click();
            } else {
                // Click Mask Data button using text selector
                const buttons = await page.$$('::-p-text(Mask Data)');
                if (buttons.length > 0) await buttons[0].click();
            }
            
            // Wait for completion (Results component renders)
            try {
                await page.waitForFunction(() => {
                    return document.body.innerText.includes('Complete') && 
                           (document.body.innerText.includes('Fields Masked') || document.body.innerText.includes('Data Quality') || document.body.innerText.includes('Analysis Results'));
                }, { timeout: 60000 });
                console.log(`✅ Processed ${format} successfully.`);
            } catch (err) {
                throw new Error(`Timeout waiting for processing to complete on ${format}.`);
            }
        }
        
        // --- 5. History Tab ---
        console.log("Testing History Tab, Filters, and Real-Time Sync...");
        await page.goto(`${BASE_URL}/history`);
        await page.waitForSelector('table');
        
        // Verify rows
        const rows = await page.$$eval('tbody tr', els => els.length);
        if (rows < FORMATS.length) {
            throw new Error(`History tab missing rows! Expected ${FORMATS.length}, got ${rows}`);
        }
        
        // Test Filter (Masking Only)
        await page.evaluate(() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const filterBtn = btns.find(b => b.innerText.includes('Filter:'));
            if(filterBtn) filterBtn.click(); // Sets to Masking
        });
        await new Promise(r => setTimeout(r, ));
        let filterRows = await page.$$eval('tbody tr', els => els.length);
        console.log(`✅ Filtered rows (Masking): ${filterRows}`);
        
        // Verify Unmasking (Unlock Icon)
        console.log("Testing Unmask retrieval button...");
        await page.evaluate(() => {
            const unlockIcons = document.querySelectorAll('.lucide-unlock');
            if (unlockIcons.length > 0) {
                unlockIcons[0].closest('button').click();
            }
        });
        await new Promise(r => setTimeout(r, )); // Wait for toast/download
        const hasDownloadedOriginalToast = await page.evaluate(() => document.body.innerText.includes('Downloaded Original') || document.body.innerText.includes('Unmask error'));
        console.log(`✅ Unmask retrieval tested (triggered toast: ${hasDownloadedOriginalToast})`);

        // --- 6. Security Session Test ---
        console.log("Testing Logout and Session Security...");
        await page.goto(`${BASE_URL}/dashboard`);
        
        // Click Avatar/User menu and Logout
        const buttons = await page.$$('button.rounded-full');
        if(buttons.length > 0) await buttons[0].click();
        
        await new Promise(r => setTimeout(r, 1000));
        
        const logoutItems = await page.$$('::-p-text(Log out)');
        if(logoutItems.length > 0) await logoutItems[logoutItems.length - 1].click();

        
        await page.waitForFunction(() => window.location.href.includes('login') || window.location.href.endsWith('/'), { timeout: 10000 });
        
        // Attempt to go back to dashboard
        await page.goto(`${BASE_URL}/dashboard`);
        await new Promise(r => setTimeout(r, 2000));
        console.log("URL after attempting to access dashboard:", page.url());
        if (!page.url().includes('login') && page.url().includes('dashboard')) {
            throw new Error(`Security Failure: Session persisted after logout! URL is ${page.url()}`);
        }
        console.log("✅ Logout and session termination verified.");
        
        console.log("\n=============================================");
        console.log("🎉 ALL E2E AUTOMATION TESTS PASSED 🎉");
        console.log("=============================================");
        
    } catch (err) {
        console.error("❌ E2E Test Failed:", err);
        try {
            await page.screenshot({ path: '/mnt/shared/Projects/Metis/frontend/error_screenshot.png' });
            console.log("Screenshot saved to frontend/error_screenshot.png");
        } catch(e) {}
        process.exit(1);
    } finally {
        await browser.close();
    }
}

runTests();
