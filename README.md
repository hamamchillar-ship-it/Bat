
# Gemini AI Enhanced Web Scraper

A powerful web scraper that combines the stealth capabilities of `nodriver` (undetected Chrome automation) with Google's Gemini AI for intelligent data analysis. This scraper is designed to bypass Cloudflare protection and other anti-bot measures.

## Features

- **Cloudflare Bypass**: Uses undetected Chrome automation to avoid detection
- **AI-Powered Analysis**: Integrates Google Gemini AI for intelligent data interpretation
- **Stealth Mode**: Multiple anti-detection techniques implemented
- **Retry Logic**: Automatic retry with exponential backoff for failed requests
- **Flexible Data Extraction**: Customizable selectors for different website structures
- **Smart Analysis**: AI-driven insights and recommendations for scraping optimization

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Set it as an environment variable:
     ```bash
     export GEMINI_API_KEY="your-api-key-here"
     ```

3. **Run the Scraper**:
   ```bash
   python main.py
   ```

## Usage

### Basic Usage

```python
import asyncio
from main import GeminiEnhancedScraper

async def scrape_website():
    scraper = GeminiEnhancedScraper("your-gemini-api-key")
    
    await scraper.start_browser()
    result = await scraper.smart_scrape("https://example.com")
    
    print(result['ai_analysis'])
    await scraper.close()

asyncio.run(scrape_website())
```

### Advanced Usage with Custom Selectors

```python
custom_selectors = {
    'product_names': '.product-title',
    'prices': '.price',
    'descriptions': '.product-description',
    'reviews': '.review-text'
}

result = await scraper.smart_scrape(
    "https://shop.example.com",
    custom_selectors=custom_selectors,
    analysis_prompt="Focus on product data and pricing patterns"
)
```

## Anti-Detection Features

1. **Browser Fingerprint Masking**: Removes automation indicators
2. **Stealth JavaScript**: Overrides navigator.webdriver and other detection points
3. **Random Delays**: Mimics human browsing patterns
4. **User Agent Rotation**: Uses realistic browser signatures
5. **Cloudflare Challenge Handling**: Automatic challenge resolution

## Configuration

Edit `config.py` to customize:
- Browser settings (headless mode, timeouts)
- Cloudflare bypass parameters
- Default selectors for common elements
- AI analysis prompts
- Rate limiting settings

## Best Practices

1. **Respect robots.txt**: Always check and respect website policies
2. **Use delays**: Don't overwhelm servers with rapid requests
3. **Monitor performance**: Watch for IP blocks or rate limiting
4. **Rotate proxies**: Consider using proxy rotation for large-scale scraping
5. **Handle errors gracefully**: Implement proper error handling and logging

## Troubleshooting

**Browser won't start**:
- Ensure you have sufficient permissions
- Try running with `headless=True`
- Check Chrome/Chromium installation

**Cloudflare still blocking**:
- Increase wait times in configuration
- Try different user agents
- Consider using residential proxies

**Gemini API errors**:
- Verify your API key is valid
- Check your quota and billing
- Reduce the amount of data sent to Gemini

## Legal Notice

This tool is for educational and legitimate research purposes only. Always:
- Respect website terms of service
- Follow applicable laws and regulations
- Obtain permission when required
- Use responsibly and ethically

## License

MIT License - see LICENSE file for details.
