import asyncio
import nodriver as uc
import google.generativeai as genai
import json
import time
import glob
from typing import Optional, Dict, Any
import os

class TestScraper:
    """Test scraper without Gemini AI for basic browser testing"""
    def __init__(self):
        self.browser = None
        self.page = None

    async def start_browser(self):
        """Start the undetected browser (same as GeminiEnhancedScraper)"""
        print("Starting undetected browser...")
        # Try to find Chrome binary in common locations
        chrome_paths = [
            '/nix/store/*/bin/google-chrome-stable',
            '/nix/store/*/bin/google-chrome',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]

        chrome_binary = None
        print("Searching for Chrome binary...")
        for path in chrome_paths:
            if '*' in path:
                matches = glob.glob(path)
                print(f"Checking glob pattern {path}: {matches}")
                if matches:
                    chrome_binary = matches[0]
                    print(f"Found Chrome at: {chrome_binary}")
                    break
            else:
                print(f"Checking path: {path}")
                if os.path.exists(path):
                    chrome_binary = path
                    print(f"Found Chrome at: {chrome_binary}")
                    break

        if not chrome_binary:
            print("Chrome not found in expected locations. Attempting to use system PATH...")
            import shutil
            chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium')
            if chrome_binary:
                print(f"Found Chrome in PATH: {chrome_binary}")
            else:
                print("Warning: Chrome binary not found. Browser may fail to start.")

        browser_args = {
            'headless': True,
            'user_data_dir': None,
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--disable-background-networking',
                '--enable-logging',
                '--log-level=0'
            ]
        }

        if chrome_binary:
            print(f"Using Chrome binary: {chrome_binary}")
            browser_args['browser_executable_path'] = chrome_binary

        try:
            print("Starting browser with nodriver...")
            self.browser = await asyncio.wait_for(uc.start(**browser_args), timeout=60)
            print("Browser started successfully!")

            print("Getting initial page...")
            self.page = self.browser.main_tab
            if not self.page:
                self.page = await asyncio.wait_for(self.browser.get('about:blank'), timeout=20)
            print("Initial page loaded successfully!")

        except asyncio.TimeoutError:
            print("❌ Browser startup timed out. This might be due to Replit environment limitations.")
            print("💡 Try running again or check if Chrome is properly installed.")
            raise Exception("Browser startup timeout")
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            print(f"Error type: {type(e).__name__}")
            raise

    async def simple_test(self, url: str = "https://httpbin.org/html"):
        """Simple test without AI analysis"""
        print(f"🧪 Testing browser with URL: {url}")
        try:
            await self.page.get(url, timeout=15000)
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

        # Try to find Chrome binary in common locations
        chrome_paths = [
            '/nix/store/*/bin/google-chrome-stable',
            '/nix/store/*/bin/google-chrome',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser'
        ]

        chrome_binary = None
        print("Searching for Chrome binary...")
        for path in chrome_paths:
            if '*' in path:
                # Handle Nix store paths with wildcards
                matches = glob.glob(path)
                print(f"Checking glob pattern {path}: {matches}")
                if matches:
                    chrome_binary = matches[0]
                    print(f"Found Chrome at: {chrome_binary}")
                    break
            else:
                print(f"Checking path: {path}")
                if os.path.exists(path):
                    chrome_binary = path
                    print(f"Found Chrome at: {chrome_binary}")
                    break

        if not chrome_binary:
            print("Chrome not found in expected locations. Attempting to use system PATH...")
            # Try to find chrome in PATH
            import shutil
            chrome_binary = shutil.which('google-chrome') or shutil.which('google-chrome-stable') or shutil.which('chromium')
            if chrome_binary:
                print(f"Found Chrome in PATH: {chrome_binary}")
            else:
                print("Warning: Chrome binary not found. Browser may fail to start.")

        browser_args = {
            'headless': True,  # Use headless for Replit
            'user_data_dir': None,  # Use temporary profile
            # Additional options to avoid detection and work in Replit
            'args': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--disable-background-networking',
                '--enable-logging',
                '--log-level=0'
            ]
        }

        if chrome_binary:
            print(f"Using Chrome binary: {chrome_binary}")
            browser_args['browser_executable_path'] = chrome_binary

        try:
            print("Starting browser with nodriver...")
            self.browser = await asyncio.wait_for(uc.start(**browser_args), timeout=60)
            print("Browser started successfully!")

            print("Getting initial page...")
            self.page = self.browser.main_tab
            if not self.page:
                self.page = await asyncio.wait_for(self.browser.get('about:blank'), timeout=20)
            print("Initial page loaded successfully!")

        except asyncio.TimeoutError:
            print("❌ Browser startup timed out. This might be due to Replit environment limitations.")
            print("💡 Try running again or check if Chrome is properly installed.")
            raise Exception("Browser startup timeout")
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            print(f"Error type: {type(e).__name__}")
            raise

        # Execute stealth scripts to avoid detection
        await self.page.evaluate("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            window.chrome = {
                runtime: {},
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
        """)

        print("Browser started successfully!")

    async def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
        """Navigate to URL with retry logic for Cloudflare bypass"""
        for attempt in range(max_retries):
            try:
                print(f"Navigating to {url} (attempt {attempt + 1})")
                await self.page.get(url, timeout=30000)

                # Wait for page load and check for Cloudflare
                await asyncio.sleep(3)

                # Check if we hit Cloudflare protection
                page_content = await self.page.get_content()
                if "cloudflare" in page_content.lower() or "challenge" in page_content.lower():
                    print("Cloudflare detected, waiting for challenge resolution...")
                    await asyncio.sleep(10)  # Wait for challenge to complete

                # Verify we can access the page
                await self.page.wait_for(selector='body', timeout=10000)
                print("Successfully navigated to page!")
                return True

            except Exception as e:
                print(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                else:
                    return False

        return False

    async def extract_data(self, selectors: Dict[str, str] = None) -> Dict[str, Any]:
        """Extract data from the current page"""
        if not selectors:
            # Default selectors for common elements
            selectors = {
                'title': 'title',
                'headings': 'h1, h2, h3',
                'paragraphs': 'p',
                'links': 'a',
                'images': 'img'
            }

        extracted_data = {}

        for key, selector in selectors.items():
            try:
                elements = await self.page.select_all(selector)
                if elements:
                    if key == 'title':
                        extracted_data[key] = await elements[0].get_attribute('textContent')
                    elif key == 'links':
                        links = []
                        for elem in elements[:10]:  # Limit to first 10 links
                            text = await elem.get_attribute('textContent')
                            href = await elem.get_attribute('href')
                            if text and href:
                                links.append({'text': text.strip(), 'href': href})
                        extracted_data[key] = links
                    elif key == 'images':
                        images = []
                        for elem in elements[:5]:  # Limit to first 5 images
                            src = await elem.get_attribute('src')
                            alt = await elem.get_attribute('alt')
                            if src:
                                images.append({'src': src, 'alt': alt or ''})
                        extracted_data[key] = images
                    else:
                        texts = []
                        for elem in elements[:10]:  # Limit to first 10 elements
                            text = await elem.get_attribute('textContent')
                            if text and text.strip():
                                texts.append(text.strip())
                        extracted_data[key] = texts

            except Exception as e:
                print(f"Error extracting {key}: {e}")
                extracted_data[key] = []

        return extracted_data

    def analyze_with_gemini(self, data: Dict[str, Any], analysis_prompt: str = None) -> str:
        """Analyze extracted data using Gemini AI"""
        if not analysis_prompt:
            analysis_prompt = """
            Analyze the following web page data and provide insights:
            1. Summarize the main content and purpose of the page
            2. Identify key information and important details
            3. Extract any structured data or patterns
            4. Highlight potential areas of interest for further scraping

            Please provide a clear, structured analysis.
            """

        # Prepare data for Gemini
        data_text = json.dumps(data, indent=2, ensure_ascii=False)[:4000]  # Limit size

        prompt = f"{analysis_prompt}\n\nWeb Page Data:\n{data_text}"

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error analyzing with Gemini: {e}"

    async def smart_scrape(self, url: str, custom_selectors: Dict[str, str] = None, 
                          analysis_prompt: str = None) -> Dict[str, Any]:
        """Perform intelligent scraping with Gemini analysis"""
        print(f"Starting smart scrape of {url}")

        # Navigate to the page
        if not await self.navigate_with_retry(url):
            return {'error': 'Failed to navigate to URL'}

        # Extract data
        print("Extracting data from page...")
        extracted_data = await self.extract_data(custom_selectors)

        # Analyze with Gemini
        print("Analyzing data with Gemini AI...")
        ai_analysis = self.analyze_with_gemini(extracted_data, analysis_prompt)

        result = {
            'url': url,
            'timestamp': time.time(),
            'extracted_data': extracted_data,
            'ai_analysis': ai_analysis
        }

        return result

    async def close(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.stop()
            print("Browser closed successfully!")

async def main():
    # Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY environment variable not set!")
        print("📝 Please add your Gemini API key using the Secrets tool:")
        print("   1. Click on 'Secrets' in the left sidebar")
        print("   2. Add a new secret with key: GEMINI_API_KEY")
        print("   3. Add your Gemini API key as the value")
        print("   4. Get your API key from: https://makersuite.google.com/app/apikey")
        print("\n🧪 Running in TEST MODE (browser only, no AI analysis)...")
        scraper = TestScraper()  # Use test mode without Gemini
    else:
        scraper = GeminiEnhancedScraper(GEMINI_API_KEY)

    try:
        # Start the browser
        await scraper.start_browser()

        # Check if we're in test mode
        if isinstance(scraper, TestScraper):
            # Just do a simple browser test
            success = await scraper.simple_test()
            if success:
                print("\n✅ Browser test completed successfully!")
                print("🔑 To enable AI analysis, set up your GEMINI_API_KEY in Secrets")
            else:
                print("\n❌ Browser test failed")
        else:
            # Full scraping with AI analysis
            url = "https://httpbin.org/html"  # Simple test page

            # Custom selectors for specific data extraction
            custom_selectors = {
                'title': 'title',
                'main_content': 'main, article, .content',
                'navigation': 'nav a',
                'metadata': 'meta[name="description"]'
            }

            # Custom analysis prompt
            analysis_prompt = """
            Please analyze this webpage and:
            1. Identify the main topic and purpose
            2. Extract any contact information, prices, or important data
            3. Suggest what other pages might be worth scraping
            4. Identify any potential data patterns or structures
            """

            # Perform the scrape
            result = await scraper.smart_scrape(url, custom_selectors, analysis_prompt)

            # Display results
            print("\n" + "="*50)
            print("SCRAPING RESULTS")
            print("="*50)
            print(f"URL: {result.get('url', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")

            print("\nEXTRACTED DATA:")
            print("-" * 30)
            for key, value in result.get('extracted_data', {}).items():
                print(f"{key.upper()}:")
                if isinstance(value, list):
                    for i, item in enumerate(value[:3]):  # Show first 3 items
                        print(f"  {i+1}. {item}")
                    if len(value) > 3:
                        print(f"  ... and {len(value) - 3} more")
                else:
                    print(f"  {value}")
                print()

            print("\nAI ANALYSIS:")
            print("-" * 30)
            print(result.get('ai_analysis', 'No analysis available'))

            # Save results to file
            with open('scraping_results.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to scraping_results.json")

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        # Always close the browser
        await scraper.close()

if __name__ == "__main__":
    print("Gemini AI Enhanced Web Scraper")
    print("=" * 40)
    asyncio.run(main())