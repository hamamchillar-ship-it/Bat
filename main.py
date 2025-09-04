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
                    # Try to find chrome in PATH
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
                '--no-sandbox',  # Move this to args list for proper handling
                '--disable-setuid-sandbox',
                '--disable-seccomp-filter-sandbox',
                '--disable-namespace-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',  # Important for Replit
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--disable-background-networking',
                '--enable-logging',
                '--log-level=0',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=VizDisplayCompositor,site-per-process',
                '--disable-default-apps',
                '--disable-component-extensions-with-background-pages',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
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
                    # Try to find chrome in PATH
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
            'headless': True,  # Use headless for Replit
            'user_data_dir': None,  # Use temporary profile
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-seccomp-filter-sandbox',
                '--disable-namespace-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--single-process',  # Important for Replit
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-hang-monitor',
                '--disable-prompt-on-repost',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--disable-background-networking',
                '--enable-logging',
                '--log-level=0',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=VizDisplayCompositor,site-per-process',
                '--disable-default-apps',
                '--disable-component-extensions-with-background-pages',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
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

        # Execute enhanced stealth scripts to avoid detection
        await self.page.evaluate("""
            // Remove webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });

            // Add chrome object
            window.chrome = {
                runtime: {},
                app: {
                    isInstalled: false,
                },
                webstore: {
                    onInstallStageChanged: {},
                    onDownloadProgress: {},
                }
            };

            // Override plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });

            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );

            // Override getUserMedia
            Object.defineProperty(navigator.mediaDevices, 'getUserMedia', {
                writable: true,
                configurable: true,
                value: () => Promise.reject(new Error('Permission denied'))
            });

            // Override connection
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                    saveData: false
                })
            });

            // Remove automation indicators
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        """)

        print("Browser started successfully!")

    async def navigate_with_retry(self, url: str, max_retries: int = 3) -> bool:
        """Navigate to URL with retry logic for Cloudflare bypass"""
        for attempt in range(max_retries):
            try:
                print(f"Navigating to {url} (attempt {attempt + 1})")
                await self.page.get(url, timeout=30000)

                # Wait for initial page load
                await asyncio.sleep(3)

                # Check for Cloudflare protection patterns
                page_content = await self.page.get_content()
                cf_indicators = [
                    'cloudflare', 'challenge', 'checking your browser',
                    'ddos protection', 'cf-browser-verification',
                    'cf-challenge-running', 'ray id:', 'please wait',
                    'security check', 'browser verification'
                ]

                if any(indicator in page_content.lower() for indicator in cf_indicators):
                    print("🛡️ Cloudflare protection detected, attempting bypass...")

                    # Wait for challenge resolution
                    for wait_time in [5, 10, 15]:
                        await asyncio.sleep(wait_time)
                        current_content = await self.page.get_content()

                        # Check if we're still on a challenge page
                        if not any(indicator in current_content.lower() for indicator in cf_indicators):
                            print("✅ Cloudflare challenge bypassed!")
                            break
                        else:
                            print(f"⏳ Still waiting for challenge resolution... ({wait_time}s)")

                    # Try clicking the verification button if it exists
                    try:
                        verify_selectors = [
                            'input[type="button"][value*="Verify"]',
                            'button[type="submit"]',
                            '.cf-button',
                            '#challenge-form input[type="submit"]'
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

                # Final verification that we can access the page
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
                    print(f"⏳ Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    print("❌ All navigation attempts failed")
                    return False

        return False

    async def auto_navigate_traffic(self, url: str) -> Dict[str, Any]:
        """Automatically navigate through complex website traffic using Gemini AI"""
        print(f"Starting intelligent navigation for {url}")

        if not await self.navigate_with_retry(url):
            return {'error': 'Failed initial navigation'}

        navigation_log = []
        current_url = url

        for step in range(5):  # Max 5 navigation steps
            try:
                # Take screenshot and analyze page
                await asyncio.sleep(2)
                page_content = await self.page.get_content()
                current_url = await self.page.evaluate('window.location.href')

                # Get page analysis from Gemini
                analysis_prompt = f"""
                Analyze this webpage content and determine next navigation steps:

                Current URL: {current_url}
                Step: {step + 1}/5

                Webpage HTML (first 3000 chars):
                {page_content[:3000]}

                Instructions:
                1. Identify if this is a blocking page (CAPTCHA, age verification, cookie consent, etc.)
                2. Look for navigation elements (buttons, links, forms)
                3. Suggest the best action to take:
                   - Click a specific element (provide selector)
                   - Fill a form (provide selectors and values)
                   - Wait for something to load
                   - Navigate to a different URL
                   - Stop here (if we've reached target content)

                Respond with JSON format:
                {{
                    "action": "click|fill|wait|navigate|stop",
                    "selector": "CSS selector if needed",
                    "value": "text to fill if needed",
                    "url": "URL to navigate to if needed",
                    "reasoning": "why this action"
                }}
                """

                ai_decision = self.analyze_with_gemini({'content': page_content[:2000]}, analysis_prompt)
                navigation_log.append({
                    'step': step + 1,
                    'url': current_url,
                    'ai_decision': ai_decision
                })

                print(f"Step {step + 1}: AI Decision - {ai_decision[:200]}...")

                # Try to parse AI decision as JSON and execute
                try:
                    import json
                    import re

                    # Extract JSON from AI response
                    json_match = re.search(r'\{.*\}', ai_decision, re.DOTALL)
                    if json_match:
                        decision = json.loads(json_match.group())

                        if decision.get('action') == 'stop':
                            print("AI decided to stop navigation - target reached")
                            break
                        elif decision.get('action') == 'click':
                            selector = decision.get('selector')
                            if selector:
                                elements = await self.page.select_all(selector)
                                if elements:
                                    await elements[0].click()
                                    await asyncio.sleep(3)
                                    print(f"Clicked element: {selector}")
                        elif decision.get('action') == 'fill':
                            selector = decision.get('selector')
                            value = decision.get('value')
                            if selector and value:
                                elements = await self.page.select_all(selector)
                                if elements:
                                    await elements[0].send_keys(value)
                                    await asyncio.sleep(2)
                                    print(f"Filled {selector} with {value}")
                        elif decision.get('action') == 'navigate':
                            new_url = decision.get('url')
                            if new_url:
                                await self.page.get(new_url)
                                await asyncio.sleep(3)
                                print(f"Navigated to: {new_url}")
                        elif decision.get('action') == 'wait':
                            print("AI decided to wait...")
                            await asyncio.sleep(5)

                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Could not parse AI decision: {e}")
                    # Fallback: just wait and continue
                    await asyncio.sleep(3)

            except Exception as e:
                print(f"Error in navigation step {step + 1}: {e}")
                break

        # Final data extraction
        final_data = await self.extract_data()

        return {
            'navigation_log': navigation_log,
            'final_url': current_url,
            'final_data': final_data,
            'steps_completed': len(navigation_log)
        }

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
            # Choose navigation mode
            print("\n🚀 Choose navigation mode:")
            print("1. Simple scrape (direct URL)")
            print("2. Auto-navigate through traffic (AI-powered)")

            # For demo, let's use auto-navigation
            mode = 2  # You can change this or make it user input

            if mode == 1:
                # Simple scraping
                url = "https://httpbin.org/html"
                custom_selectors = {
                    'title': 'title',
                    'main_content': 'main, article, .content',
                    'navigation': 'nav a',
                    'metadata': 'meta[name="description"]'
                }
                analysis_prompt = """
                Please analyze this webpage and:
                1. Identify the main topic and purpose
                2. Extract any contact information, prices, or important data
                3. Suggest what other pages might be worth scraping
                4. Identify any potential data patterns or structures
                """
                result = await scraper.smart_scrape(url, custom_selectors, analysis_prompt)
            else:
                # Auto-navigation with AI
                url = "https://example.com"  # Change to target site
                print(f"🤖 Starting AI-powered navigation for: {url}")
                result = await scraper.auto_navigate_traffic(url)

            # Display results
            print("\n" + "="*50)
            print("SCRAPING RESULTS")
            print("="*50)

            if 'navigation_log' in result:
                # Auto-navigation results
                print(f"Final URL: {result.get('final_url', 'N/A')}")
                print(f"Steps completed: {result.get('steps_completed', 0)}")

                print("\nNAVIGATION LOG:")
                print("-" * 30)
                for log_entry in result.get('navigation_log', []):
                    print(f"Step {log_entry['step']}: {log_entry['url']}")
                    print(f"  AI Decision: {log_entry['ai_decision'][:100]}...")
                    print()

                print("\nFINAL EXTRACTED DATA:")
                print("-" * 30)
                for key, value in result.get('final_data', {}).items():
                    print(f"{key.upper()}:")
                    if isinstance(value, list):
                        for i, item in enumerate(value[:3]):
                            print(f"  {i+1}. {item}")
                        if len(value) > 3:
                            print(f"  ... and {len(value) - 3} more")
                    else:
                        print(f"  {value}")
                    print()
            else:
                # Regular scraping results
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