const playwright = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  console.log('Starting screenshot capture...');
  
  // Ensure assets directory exists
  const assetsDir = path.join(__dirname, '..', 'assets');
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
  }
  
  // Launch browser
  const browser = await playwright.chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();
  
  // Navigate to the frontend page
  // Since we're running locally without a web server, we'll read the HTML file
  const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  
  // Set the content directly
  await page.setContent(htmlContent, { waitUntil: 'networkidle' });
  
  // Wait for any dynamic content to load
  await page.waitForTimeout(2000);
  
  // Take screenshot
  const screenshotPath = path.join(assetsDir, 'screenshot.png');
  await page.screenshot({ 
    path: screenshotPath,
    fullPage: true
  });
  
  console.log(`Screenshot saved to ${screenshotPath}`);
  
  // Close browser
  await browser.close();
  
  console.log('Screenshot capture completed successfully!');
})();
