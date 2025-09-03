
"""Configuration settings for the Gemini AI Enhanced Scraper"""

# Browser configuration
BROWSER_CONFIG = {
    'headless': False,  # Set to True for headless operation
    'user_data_dir': None,  # Use None for temporary profile
    'timeout': 30000,  # Page load timeout in milliseconds
    'wait_after_load': 3,  # Seconds to wait after page load
}

# Cloudflare bypass settings
CLOUDFLARE_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5,  # Seconds between retries
    'challenge_wait': 10,  # Seconds to wait for challenge resolution
}

# Default selectors for common web elements
DEFAULT_SELECTORS = {
    'title': 'title',
    'headings': 'h1, h2, h3, h4, h5, h6',
    'paragraphs': 'p',
    'links': 'a[href]',
    'images': 'img[src]',
    'articles': 'article, .article, .post',
    'navigation': 'nav, .nav, .navigation',
    'content': 'main, .main, .content, #content',
    'sidebar': 'aside, .sidebar, .side',
    'footer': 'footer, .footer',
}

# Gemini AI prompts
ANALYSIS_PROMPTS = {
    'general': """
    Analyze the following web page data and provide insights:
    1. Summarize the main content and purpose of the page
    2. Identify key information and important details
    3. Extract any structured data or patterns
    4. Highlight potential areas of interest for further scraping
    5. Suggest improvements for data extraction
    
    Please provide a clear, structured analysis.
    """,
    
    'ecommerce': """
    Analyze this e-commerce page data:
    1. Identify products, prices, and descriptions
    2. Extract product categories and specifications
    3. Find customer reviews and ratings
    4. Identify navigation patterns for product discovery
    5. Suggest optimal scraping strategy for this site
    """,
    
    'news': """
    Analyze this news/content page:
    1. Extract article headlines, authors, and publication dates
    2. Identify main topics and categories
    3. Find related articles or trending topics
    4. Analyze content structure and formatting
    5. Suggest content extraction improvements
    """,
}

# Rate limiting and politeness settings
SCRAPING_ETIQUETTE = {
    'delay_between_requests': 2,  # Seconds
    'max_concurrent_pages': 3,
    'respect_robots_txt': True,
    'user_agent_rotation': True,
}
