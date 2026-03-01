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
    viewport: { width: 1440, height: 900 }
  });
  
  const page = await context.newPage();
  
  // Navigate to the frontend page
  const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
  const htmlContent = fs.readFileSync(htmlPath, 'utf-8');
  
  // Set the content directly
  await page.setContent(htmlContent, { waitUntil: 'networkidle' });
  
  // Wait for any dynamic content to load
  await page.waitForTimeout(3000);
  
  // Define tabs to screenshot
  const tabs = [
    { id: 'students', name: '学生管理', emoji: '👨‍🎓' },
    { id: 'permissions', name: '权限管理', emoji: '🔐' },
    { id: 'courses', name: '课程表', emoji: '📚' },
    { id: 'card', name: '饭卡余额', emoji: '💳' },
    { id: 'logs', name: '学校日志', emoji: '📢' },
    { id: 'map', name: '学校平面图', emoji: '🗺️' },
    { id: 'website', name: '官网信息', emoji: '🌐' }
  ];
  
  // Take screenshot of each tab
  for (const tab of tabs) {
    console.log(`Capturing ${tab.name}...`);
    
    // Click the tab
    const tabButton = await page.$(`button[onclick="switchTab('${tab.id}')"]`);
    if (tabButton) {
      await tabButton.click();
      await page.waitForTimeout(1000);
      
      // Scroll to top
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.waitForTimeout(500);
      
      // Take screenshot
      const screenshotPath = path.join(assetsDir, `${tab.id}.png`);
      await page.screenshot({ 
        path: screenshotPath,
        fullPage: false
      });
      
      console.log(`Saved: ${screenshotPath}`);
    }
  }
  
  // Close browser
  await browser.close();
  
  console.log('Screenshot capture completed successfully!');
  console.log(`Captured ${tabs.length} tabs.`);
})();
