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
                        if matches:
                            chrome_binary = matches[0]
                            break
                    except Exception:
                        continue
                else:
                    if os.path.exists(path):
                        chrome_binary = path
                        break
            if not chrome_binary:
                import shutil
                chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium')
        except Exception as e:
            print(f"Error during Chrome detection: {e}")
        
        browser_args = {
            'headless': True,
            'user_data_dir': '/tmp/chrome_profile',
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
            raise

    async def simple_test(self, url: str = "https://httpbin.org/html"):
        print(f"🧪 Testing browser with URL: {url}")
        try:
            await self.page.get(url)
            await asyncio.sleep(2)
            title = await self.page.evaluate('document.title')
            print(f"✅ Successfully loaded page! Title: {title}")
            return True
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

    async def close(self):
        # FINAL FIX: Add a try/except block to make cleanup robust
        try:
            if self.browser:
                await self.browser.stop()
                print("Browser closed successfully!")
        except Exception as e:
            print(f"Warning: Error closing browser (might have already crashed): {e}")

class GeminiEnhancedScraper:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.browser = None
        self.page = None

    async def start_browser(self):
        # This function is complex, so we'll keep it as is from user's full version
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
                        if matches:
                            chrome_binary = matches[0]
                            break
                    except Exception:
                        continue
                else:
                    if os.path.exists(path):
                        chrome_binary = path
                        break
            if not chrome_binary:
                import shutil
                chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium')
        except Exception as e:
            print(f"Error during Chrome detection: {e}")
        
        browser_args = {
            'headless': True,
            'user_data_dir': None,
            'args': [
                '--no-sandbox', '--disable-setuid-sandbox', '--disable-seccomp-filter-sandbox',
                '--disable-namespace-sandbox', '--disable-dev-shm-usage', '--disable-accelerated-2d-canvas',
                '--no-first-run', '--no-zygote', '--single-process', '--disable-gpu'
            ]
        }
        if chrome_binary:
            print(f"Using Chrome binary: {chrome_binary}")
            browser_args['browser_executable_path'] = chrome_binary
        
        try:
            self.browser = await uc.start(**browser_args)
            print("Browser started successfully!")
            self.page = self.browser.main_tab
            await self.page.get('about:blank')
            print("Browser is fully operational!")
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            raise

    async def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
        for attempt in range(max_retries):
            try:
                print(f"Navigating to {url} (attempt {attempt + 1})")
                await self.page.get(url)
                await asyncio.sleep(3)
                print(f"✅ Successfully navigated to: {url}")
                return True
            except Exception as e:
                print(f"❌ Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    return False
        return False
    
    async def auto_navigate_traffic(self, url: str) -> Dict[str, Any]:
        print(f"Starting auto-navigation for {url}")
        if not await self.navigate_with_retry(url):
            return {'error': 'Failed initial navigation'}
        
        print("Extracting dynamic content...")
        title = await self.page.evaluate('document.title')
        content = await self.page.get_content()
        
        final_data = {"title": title, "content_length": len(content)}
        
        return {
            'navigation_log': [{'step': 1, 'url': url, 'ai_decision': 'mock decision'}],
            'final_url': await self.page.evaluate('window.location.href'),
            'final_data': final_data
        }

    async def close(self):
        # FINAL FIX: Add a try/except block to make cleanup robust
        try:
            if self.browser:
                await self.browser.stop()
                print("Browser closed successfully!")
        except Exception as e:
            print(f"Warning: Error closing browser (might have already crashed): {e}")

async def main():
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    scraper = None
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
        print(f"An error occurred during the main scraping process: {e}")
    finally:
        if scraper:
            await scraper.close()

if __name__ == "__main__":
    print("Gemini AI Enhanced Web Scraper")
    print("=" * 40)
    
    asyncio.run(main())
    
    print("Scraping finished. Starting web server to keep service alive.")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
