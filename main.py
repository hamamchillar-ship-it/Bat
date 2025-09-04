import asyncio
import nodriver as uc
import google.generativeai as genai
import json
import time
import glob
from typing import Optional, Dict, Any, List
import os
from flask import Flask
import re

# --- Flask App Setup to Keep the Service Alive ---
app = Flask(__name__)

@app.route('/')
def hello():
    return "AI scraping script has finished its run. Check the logs for output."
# -------------------------------------------------

class GeminiEnhancedScraper:
    def __init__(self, gemini_api_key: str):
        """Initialize the scraper with Gemini AI integration"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        # <<< --- AI MODEL UPDATED HERE --- >>>
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
        self.browser = None
        self.page = None

    async def start_browser(self):
        """Starts the browser with robust settings for a container environment."""
        print("Starting undetected browser...")
        browser_args = {
            'headless': True,
            'user_data_dir': None,
            'args': [
                '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                '--disable-gpu', '--single-process', '--no-zygote'
            ]
        }
        try:
            # Check for system-installed Chrome first
            import shutil
            chrome_path = shutil.which('google-chrome') or shutil.which('chromium')
            if chrome_path:
                print(f"Using system Chrome found at: {chrome_path}")
                browser_args['browser_executable_path'] = chrome_path
        except Exception:
            print("Could not find system Chrome, letting nodriver handle it.")

        try:
            self.browser = await uc.start(**browser_args)
            self.page = self.browser.main_tab
            await self.page.get('about:blank')
            print("✅ Browser is fully operational!")
        except Exception as e:
            print(f"❌ Failed to start browser: {e}")
            raise

    async def get_ai_scraping_plan(self, query: str) -> Optional[Dict[str, Any]]:
        """
        AI Planner: Takes a user query and generates a URL and data extraction plan.
        """
        print(f"🧠 Step 1: Creating AI scraping plan for query: '{query}'")
        prompt = f"""
        You are an AI assistant that generates a web scraping plan from a natural language query.
        Based on the user's query, determine the target website and the search term.
        Construct a valid search URL.
        Also, identify the key pieces of information the user likely wants.

        User Query: "{query}"

        Respond ONLY with a JSON object in the following format:
        {{
          "search_url": "The full, direct URL to visit for the search results.",
          "data_to_extract": ["product_name", "price", "rating", "reviews_count", "product_url"]
        }}
        """
        response = None # Define response here to access it in except block
        try:
            response = self.model.generate_content(prompt)
            plan = json.loads(response.text)
            print(f"✅ AI Plan Generated:\n{json.dumps(plan, indent=2)}")
            return plan
        except (json.JSONDecodeError, KeyError, Exception) as e:
            print(f"❌ Error generating or parsing AI plan: {e}")
            if response:
                print(f"Raw AI response was: {response.text}")
            return None

    async def extract_data_with_ai(self, html_content: str, fields: List[str]) -> Optional[List[Dict[str, Any]]]:
        """
        AI Extractor: Takes HTML and a list of fields, then extracts the data.
        """
        print(f"🧠 Step 3: Extracting data from HTML using AI...")
        # Reduce HTML size to avoid exceeding token limits
        simplified_html = re.sub(r'\s{2,}', ' ', html_content)[:20000]
        response = None # Define response here
        prompt = f"""
        You are an expert data extraction AI. From the provided HTML content, extract the information for each item you can find.
        The data points to extract are: {', '.join(fields)}.

        HTML Content:
        "{simplified_html}"

        Respond ONLY with a JSON list of objects. Each object represents one item.
        The keys in each object should be the requested fields.
        If a value is not found for a specific field, use `null`.
        Example format:
        [
          {{
            "product_name": "Example Product 1",
            "price": "$19.99",
            "rating": "4.5 out of 5 stars",
            "reviews_count": "150",
            "product_url": "https://example.com/product1"
          }}
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            # Use regex to find the JSON block, as AI can sometimes add extra text
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                extracted_data = json.loads(json_match.group())
                print(f"✅ AI successfully extracted {len(extracted_data)} items.")
                return extracted_data
            else:
                print("❌ AI did not return a valid JSON list.")
                print(f"Raw AI response was: {response.text}")
                return None
        except (json.JSONDecodeError, Exception) as e:
            print(f"❌ Error parsing AI extraction response: {e}")
            if response:
                print(f"Raw AI response was: {response.text}")
            return None
            
    async def intelligent_scroll(self):
        """Scrolls the page to trigger lazy-loading content."""
        print("📜 Scrolling page to load dynamic content...")
        try:
            last_height = await self.page.evaluate('document.body.scrollHeight')
            for _ in range(3): # Scroll 3 times
                await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
                await asyncio.sleep(2) # Wait for content to load
                new_height = await self.page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            print(f"Could not scroll page: {e}")


    async def intelligent_scrape(self, query: str):
        """Orchestrates the entire AI-driven scraping process."""
        # Step 1: Get the plan from the AI
        plan = await self.get_ai_scraping_plan(query)
        if not plan or 'search_url' not in plan:
            return {"error": "Could not create a valid scraping plan."}

        # Step 2: Navigate to the planned URL
        print(f"🧭 Step 2: Navigating to {plan['search_url']}...")
        try:
            await self.page.get(plan['search_url'])
            await asyncio.sleep(3) # Wait for initial page load
            print("✅ Navigation successful.")
        except Exception as e:
            return {"error": f"Failed to navigate to URL: {e}"}
            
        # Scroll to load more data
        await self.intelligent_scroll()

        # Step 3: Get HTML and pass to AI Extractor
        html = await self.page.get_content()
        extracted_data = await self.extract_data_with_ai(html, plan['data_to_extract'])

        return {
            "query": query,
            "planned_url": plan['search_url'],
            "scraped_data": extracted_data
        }

    async def close(self):
        """Robustly closes the browser."""
        try:
            if self.browser:
                await self.browser.stop()
                print("Browser closed successfully!")
        except Exception as e:
            print(f"Warning: Error closing browser (might have already crashed): {e}")

async def run_scraper():
    """The main async function that runs the scraper."""
    scraper = None
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY environment variable not set! Cannot run.")
        return

    try:
        scraper = GeminiEnhancedScraper(GEMINI_API_KEY)
        await scraper.start_browser()

        # <<< --- CHANGE YOUR QUERY HERE --- >>>
        user_query = "Rolex watch on Amazon.com"
        
        result = await scraper.intelligent_scrape(user_query)

        print("\n" + "="*50)
        print("      FINAL SCRAPING RESULTS")
        print("="*50)
        print(json.dumps(result, indent=2))

        # Save results to file
        with open('scraping_results.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("\n✅ Results saved to scraping_results.json")

    except Exception as e:
        print(f"A critical error occurred: {e}")
    finally:
        if scraper:
            await scraper.close()

if __name__ == "__main__":
    print("🚀 Gemini AI Enhanced Web Scraper 🚀")
    print("=" * 40)
    
    # Run the main scraping logic first
    asyncio.run(run_scraper())
    
    # After scraping is done, start the web server to keep the Render service alive
    print("\n✅ Scraping finished. Starting web server to keep the service running.")
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
