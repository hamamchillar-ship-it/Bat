import asyncio
import nodriver as uc
import google.generativeai as genai
import json
import time
import glob
from typing import Optional, Dict, Any
import os
from flask import Flask

# --- Add Flask App Setup ---
app = Flask(__name__)

@app.route('/')
def hello():
    # This will be shown if you visit your Render URL after the scrape is done.
    return "Scraping script has finished its run. Check the logs for output."
# -------------------------


class TestScraper:
    """Test scraper without Gemini AI for basic browser testing"""
    def __init__(self):
        self.browser = None
        self.page = None

    async def start_browser(self):
        """Start the undetected browser (same as GeminiEnhancedScraper)"""
        print("Starting undetected browser...")
        chrome_paths = [
            '/nix/store/bvqn8vwhfxary4j5ydb9l757jacbql96-google-chrome-138.0.7204.92/bin/google-chrome-stable',
            '/nix/store/*/bin/google-chrome-stable',
            '/nix/store/*/bin/google-chrome',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        chrome_binary = None
        print("Searching for Chrome binary...")
        try:
            for path in chrome_paths:
                if '*' in path:
                    try:
                        matches = glob.glob(path)
                        print(f"Checking glob pattern {path}: {matches}")
                        if matches:
                            chrome_binary = matches[0]
                            print(f"Found Chrome at: {chrome_binary}")
                            break
                    except Exception as e:
                        print(f"Error checking glob pattern {path}: {e}")
                        continue
                else:
                    print(f"Checking path: {path}")
                    try:
                        if os.path.exists(path):
                            chrome_binary = path
                            print(f"Found Chrome at: {chrome_binary}")
                            break
                    except Exception as e:
                        print(f"Error checking path {path}: {e}")
                        continue
            if not chrome_binary:
                print("Chrome not found in expected locations. Attempting to use system PATH...")
                try:
                    import shutil
                    chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium')
                    if chrome_binary:
                        print(f"Found Chrome in PATH: {chrome_binary}")
                    else:
                        print("Warning: Chrome binary not found. Browser may fail to start.")
                except Exception as e:
                    print(f"Error searching PATH: {e}")
        except Exception as e:
            print(f"Error during Chrome detection: {e}")
            print("Proceeding without explicit Chrome path...")
        browser_args = {
            'headless': True,
            'user_data_dir': '/tmp/chrome_profile',
            'lang': 'en-US',
            'version_main': None,
            'args': ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        }
        if chrome_binary:
            print(f"Using Chrome binary: {chrome_binary}")
            browser_args['browser_executable_path'] = chrome_binary
        try:
            print("Starting browser with nodriver...")
            self.browser = await uc.start(**browser_args)
            print("Browser started successfully!")
            self.page = self.browser.main_tab
            print("Initial page ready!")
            await self.page.get('about:blank')
            print("Browser is fully operational!")
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            print("💡 This could be due to Replit environment constraints.")
            print("💡 nodriver requires specific permissions that may not be available.")
            raise

    async def simple_test(self, url: str = "https://httpbin.org/html"):
        """Simple test without AI analysis"""
        print(f"🧪 Testing browser with URL: {url}")
        try:
            await self.page.get(url)
            await asyncio.sleep(2)
            title = await self.page.evaluate('document.title')
            print(f"✅ Successfully loaded page! Title: {title}")
            content = await self.page.get_content()
            print(f"📄 Page content length: {len(content)} characters")
            return True
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

    async def close(self):
        if self.browser:
            await self.browser.stop()
            print("Browser closed successfully!")

class GeminiEnhancedScraper:
    def __init__(self, gemini_api_key: str):
        """Initialize the scraper with Gemini AI integration"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.browser = None
        self.page = None

    async def start_browser(self):
        """Start the undetected browser"""
        print("Starting undetected browser...")
        chrome_paths = [
            '/nix/store/bvqn8vwhfxary4j5ydb9l757jacbql96-google-chrome-138.0.7204.92/bin/google-chrome-stable',
            '/nix/store/*/bin/google-chrome-stable',
            '/nix/store/*/bin/google-chrome',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]
        chrome_binary = None
        print("Searching for Chrome binary...")
        try:
            for path in chrome_paths:
                if '*' in path:
                    try:
                        matches = glob.glob(path)
                        print(f"Checking glob pattern {path}: {matches}")
                        if matches:
                            chrome_binary = matches[0]
                            print(f"Found Chrome at: {chrome_binary}")
                            break
                    except Exception as e:
                        print(f"Error checking glob pattern {path}: {e}")
                        continue
                else:
                    print(f"Checking path: {path}")
                    try:
                        if os.path.exists(path):
                            chrome_binary = path
                            print(f"Found Chrome at: {chrome_binary}")
                            break
                    except Exception as e:
                        print(f"Error checking path {path}: {e}")
                        continue
            if not chrome_binary:
                print("Chrome not found in expected locations. Attempting to use system PATH...")
                try:
                    import shutil
                    chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium')
                    if chrome_binary:
                        print(f"Found Chrome in PATH: {chrome_binary}")
                    else:
                        print("Warning: Chrome binary not found. Browser may fail to start.")
                except Exception as e:
                    print(f"Error searching PATH: {e}")
        except Exception as e:
            print(f"Error during Chrome detection: {e}")
            print("Proceeding without explicit Chrome path...")
        browser_args = {
            'headless': True,
            'user_data_dir': None,
            'args': [
                '--no-sandbox', '--disable-setuid-sandbox', '--disable-seccomp-filter-sandbox',
                '--disable-namespace-sandbox', '--disable-dev-shm-usage', '--disable-accelerated-2d-canvas',
                '--no-first-run', '--no-zygote', '--single-process', '--disable-gpu',
                '--disable-software-rasterizer', '--disable-extensions', '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI', '--disable-ipc-flooding-protection',
                '--disable-hang-monitor', '--disable-prompt-on-repost', '--disable-sync',
                '--force-color-profile=srgb', '--metrics-recording-only', '--disable-background-networking',
                '--enable-logging', '--log-level=0', '--disable-blink-features=AutomationControlled',
                '--disable-web-security', '--allow-running-insecure-content',
                '--disable-features=VizDisplayCompositor,site-per-process', '--disable-default-apps',
                '--disable-component-extensions-with-background-pages',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            ]
        }
        if chrome_binary:
            print(f"Using Chrome binary: {chrome_binary}")
            browser_args['browser_executable_path'] = chrome_binary
        try:
            print("Starting browser with nodriver...")
            self.browser = await uc.start(**browser_args)
            print("Browser started successfully!")
            self.page = self.browser.main_tab
            print("Initial page ready!")
            await self.page.get('about:blank')
            print("Browser is fully operational!")
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            print("💡 This could be due to Replit environment constraints.")
            print("💡 nodriver requires specific permissions that may not be available.")
            raise
        await self.page.evaluate("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {}, app: { isInstalled: false }, webstore: { onInstallStageChanged: {}, onDownloadProgress: {} } };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : originalQuery(parameters)
            );
            Object.defineProperty(navigator.mediaDevices, 'getUserMedia', { writable: true, configurable: true, value: () => Promise.reject(new Error('Permission denied')) });
            Object.defineProperty(navigator, 'connection', { get: () => ({ effectiveType: '4g', rtt: 50, downlink: 10, saveData: false }) });
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)
        print("Browser stealth enhanced!")

    async def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
        for attempt in range(max_retries):
            try:
                print(f"Navigating to {url} (attempt {attempt + 1})")
                await self.page.get(url)
                await asyncio.sleep(3)
                page_content = await self.page.get_content()
                cf_indicators = [
                    'cloudflare', 'challenge', 'checking your browser',
                    'ddos protection', 'cf-browser-verification', 'cf-challenge-running',
                    'ray id:', 'please wait', 'security check', 'browser verification'
                ]
                if any(indicator in page_content.lower() for indicator in cf_indicators):
                    print("🛡️ Cloudflare protection detected, attempting bypass...")
                    for wait_time in [5, 10, 15]:
                        await asyncio.sleep(wait_time)
                        current_content = await self.page.get_content()
                        if not any(indicator in current_content.lower() for indicator in cf_indicators):
                            print("✅ Cloudflare challenge bypassed!")
                            break
                        else:
                            print(f"⏳ Still waiting for challenge resolution... ({wait_time}s)")
                    try:
                        verify_selectors = [
                            'input[type="button"][value*="Verify"]', 'button[type="submit"]',
                            '.cf-button', '#challenge-form input[type="submit"]'
                        ]
                        for selector in verify_selectors:
                            elements = await self.page.select_all(selector)
                            if elements:
                                print(f"🖱️ Clicking verification button: {selector}")
                                await elements[0].click()
                                await asyncio.sleep(5)
                                break
                    except Exception as e:
                        print(f"Could not click verification button: {e}")
                try:
                    await self.page.wait_for(selector='body', timeout=10000)
                    final_url = await self.page.evaluate('window.location.href')
                    print(f"✅ Successfully navigated to: {final_url}")
                    return True
                except:
                    pass
            except Exception as e:
                print(f"❌ Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print("⏳ Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    print("❌ All navigation attempts failed")
                    return False
        return False

    async def extract_dynamic_content(self, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Placeholder for the original function"""
        print("Extracting dynamic content...")
        # A simplified version for brevity
        await asyncio.sleep(2) # Simulate work
        return {"title": await self.page.evaluate('document.title'), "content_length": len(await self.page.get_content())}

    async def auto_navigate_traffic(self, url: str) -> Dict[str, Any]:
        """Placeholder for the original function"""
        print(f"Starting auto-navigation for {url}")
        if not await self.navigate_with_retry(url):
            return {'error': 'Failed initial navigation'}
        
        final_data = await self.extract_dynamic_content()
        return {
            'navigation_log': [{'step': 1, 'url': url, 'ai_decision': 'mock decision'}],
            'final_url': await self.page.evaluate('window.location.href'),
            'final_data': final_data
        }

    def analyze_with_gemini(self, data: Dict[str, Any], analysis_prompt: str = None) -> str:
        """Placeholder for the original function"""
        print("Analyzing with Gemini...")
        return "Mock AI analysis based on the data."

    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.stop()
            print("Browser closed successfully!")

async def main():
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("\n🧪 Running in TEST MODE (browser only, no AI analysis)...")
        scraper = TestScraper()
    else:
        scraper = GeminiEnhancedScraper(GEMINI_API_KEY)

    try:
        await scraper.start_browser()
        if isinstance(scraper, TestScraper):
            success = await scraper.simple_test()
            if success:
                print("\n✅ Browser test completed successfully!")
            else:
                print("\n❌ Browser test failed")
        else:
            url = "https://example.com"
            print(f"🤖 Starting AI-powered navigation for: {url}")
            result = await scraper.auto_navigate_traffic(url)
            print("\n" + "="*50)
            print("SCRAPING RESULTS")
            print("="*50)
            print(json.dumps(result, indent=2))
            with open('scraping_results.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print("\nResults saved to scraping_results.json")
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        await scraper.close()

if __name__ == "__main__":
    print("Gemini AI Enhanced Web Scraper")
    print("=" * 40)
    
    # Run the main scraping logic
    asyncio.run(main())
    
    # --- Start the Flask server AFTER scraping is done ---
    print("Scraping finished. Starting web server to keep service alive.")
    port = int(os.environ.get('PORT', 10000))
    # This line below is what keeps the Render service "Live"
    app.run(host='0.0.0.0', port=port)
