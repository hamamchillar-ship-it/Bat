
"""
Advanced automation utilities inspired by Playwright_Auto
Provides intelligent page interaction and element detection
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional

class AutomationPatterns:
    """Collection of automation patterns for common website interactions"""
    
    @staticmethod
    def get_bypass_selectors() -> Dict[str, List[str]]:
        """Get selectors for common blocking elements"""
        return {
            'cookie_banners': [
                '[id*="cookie"] button[id*="accept"]',
                '[class*="cookie"] button[class*="accept"]',
                '[id*="cookie"] button[id*="allow"]',
                'button[data-testid*="cookie-accept"]',
                '.cookie-banner button',
                '[data-cookiebanner] button',
                '#cookieConsent button',
                '.gdpr-banner button'
            ],
            'age_verification': [
                '[class*="age-verify"] button',
                '[id*="age-confirm"] button',
                'button[class*="confirm-age"]',
                '[data-age-gate] button',
                '.age-gate button[value*="yes"]',
                '.age-verification button'
            ],
            'newsletter_popups': [
                '[class*="newsletter"] [class*="close"]',
                '[class*="signup"] [class*="close"]',
                '[id*="newsletter"] [class*="close"]',
                '.newsletter-popup .close',
                '[data-modal="newsletter"] .close'
            ],
            'general_modals': [
                '[class*="modal"] [class*="close"]',
                '[class*="popup"] [class*="close"]',
                '[class*="overlay"] [class*="close"]',
                'button[aria-label*="close"]',
                '[data-dismiss="modal"]',
                '.modal-backdrop',
                '.overlay-close'
            ]
        }
    
    @staticmethod
    def get_content_selectors() -> Dict[str, str]:
        """Get enhanced selectors for content extraction"""
        return {
            'main_content': 'main, article, [role="main"], .content, .main-content, #content, .article-body',
            'product_info': '[itemtype*="Product"], .product, [data-product], .product-detail, .item-detail',
            'pricing': '[class*="price"], [data-price], .currency, [class*="cost"], [class*="amount"]',
            'reviews': '[class*="review"], .rating, [data-rating], .testimonial, .comment',
            'navigation': 'nav a, [class*="nav"] a, [role="navigation"] a, .menu a, .navigation a',
            'pagination': '.pagination a, [class*="pager"] a, [class*="next"], [class*="prev"]',
            'social_links': '[href*="facebook"], [href*="twitter"], [href*="instagram"], [href*="linkedin"]',
            'contact_info': '[href^="mailto:"], [href^="tel:"], .contact, .phone, .email'
        }

class IntelligentWaiter:
    """Smart waiting strategies for dynamic content"""
    
    def __init__(self, page):
        self.page = page
    
    async def wait_for_network_idle(self, timeout: int = 30) -> bool:
        """Wait for network activity to settle"""
        try:
            # Monitor network requests
            start_time = asyncio.get_event_loop().time()
            stable_duration = 0
            last_request_time = start_time
            
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                # Check if page is still loading
                ready_state = await self.page.evaluate('document.readyState')
                if ready_state == 'complete':
                    current_time = asyncio.get_event_loop().time()
                    if current_time - last_request_time > 2:  # 2 seconds of quiet
                        stable_duration += 0.5
                        if stable_duration >= 2:  # Stable for 2 seconds
                            return True
                    else:
                        stable_duration = 0
                        last_request_time = current_time
                
                await asyncio.sleep(0.5)
            
            return False
        except:
            return False
    
    async def wait_for_content_change(self, selector: str, timeout: int = 30) -> bool:
        """Wait for content in selector to change"""
        try:
            initial_content = ""
            elements = await self.page.select_all(selector)
            if elements:
                initial_content = await elements[0].get_attribute('textContent')
            
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) < timeout:
                elements = await self.page.select_all(selector)
                if elements:
                    current_content = await elements[0].get_attribute('textContent')
                    if current_content != initial_content:
                        return True
                await asyncio.sleep(1)
            
            return False
        except:
            return False

class SmartFormFiller:
    """Intelligent form filling with pattern recognition"""
    
    def __init__(self, page):
        self.page = page
    
    async def detect_form_fields(self, form_element) -> Dict[str, Any]:
        """Analyze form and detect field types"""
        fields = {}
        
        try:
            inputs = await form_element.select_all('input, select, textarea')
            
            for inp in inputs:
                field_type = await inp.get_attribute('type') or 'text'
                name = await inp.get_attribute('name')
                placeholder = await inp.get_attribute('placeholder')
                label_text = ""
                
                # Try to find associated label
                field_id = await inp.get_attribute('id')
                if field_id:
                    labels = await form_element.select_all(f'label[for="{field_id}"]')
                    if labels:
                        label_text = await labels[0].get_attribute('textContent')
                
                if not label_text:
                    # Look for nearby text
                    parent = inp
                    for _ in range(3):  # Check up to 3 levels up
                        try:
                            parent_elem = await parent.select('../')
                            if parent_elem:
                                parent = parent_elem[0]
                                text_content = await parent.get_attribute('textContent')
                                if text_content and len(text_content.strip()) < 100:
                                    label_text = text_content.strip()
                                    break
                        except:
                            break
                
                if name:
                    fields[name] = {
                        'type': field_type,
                        'label': label_text,
                        'placeholder': placeholder or '',
                        'element': inp
                    }
        
        except Exception as e:
            print(f"Error detecting form fields: {e}")
        
        return fields
    
    async def smart_fill_field(self, field_info: Dict[str, Any], context: str = "") -> bool:
        """Fill field based on its detected type and context"""
        try:
            field_type = field_info['type'].lower()
            label = field_info['label'].lower()
            placeholder = field_info['placeholder'].lower()
            element = field_info['element']
            
            # Determine appropriate value based on field characteristics
            value = ""
            
            if 'email' in field_type or 'email' in label or 'email' in placeholder:
                value = "test@example.com"
            elif 'password' in field_type or 'password' in label:
                value = "TestPassword123"
            elif 'phone' in label or 'tel' in field_type or 'phone' in placeholder:
                value = "+1234567890"
            elif 'name' in label and 'first' in label:
                value = "John"
            elif 'name' in label and 'last' in label:
                value = "Doe"
            elif 'name' in label:
                value = "John Doe"
            elif 'address' in label:
                value = "123 Main St"
            elif 'city' in label:
                value = "New York"
            elif 'zip' in label or 'postal' in label:
                value = "10001"
            elif 'age' in label and field_type == 'number':
                value = "25"
            elif 'search' in field_type or 'search' in label or 'search' in placeholder:
                value = context[:50] if context else "test search"
            elif field_type == 'checkbox':
                await element.click()
                return True
            elif field_type == 'radio':
                await element.click()
                return True
            else:
                value = f"test {label[:20]}" if label else "test input"
            
            if value:
                await element.send_keys(value)
                await asyncio.sleep(0.5)
                return True
                
        except Exception as e:
            print(f"Error filling field: {e}")
        
        return False

def create_automation_prompt() -> str:
    """Create an enhanced prompt for AI-driven automation"""
    return """
    You are an expert web automation agent. Analyze the current page state and determine the optimal next action.

    Available automation capabilities:
    1. BYPASS: Handle blocking elements (cookies, age gates, popups)
    2. NAVIGATE: Click links, buttons, or navigate to URLs
    3. EXTRACT: Collect specific data from current page
    4. FORM_FILL: Complete forms intelligently
    5. SCROLL: Load dynamic content through scrolling
    6. WAIT: Wait for elements or content to load
    7. STOP: End automation (goal achieved)

    Analysis focus:
    - Identify blocking elements that prevent access to content
    - Look for pagination, "load more", or infinite scroll triggers
    - Find forms that need completion for access
    - Locate primary content areas and data-rich sections
    - Detect navigation patterns and site structure

    Response format (JSON):
    {
        "action": "BYPASS|NAVIGATE|EXTRACT|FORM_FILL|SCROLL|WAIT|STOP",
        "target": "CSS selector or URL",
        "data": {"key": "value for form fills"},
        "reasoning": "detailed explanation",
        "confidence": "high|medium|low",
        "expected_outcome": "what should happen next"
    }

    Prioritize actions that:
    1. Remove barriers to content access
    2. Trigger loading of more content
    3. Navigate to data-rich pages
    4. Complete necessary interactions for full access
    """
