#!/usr/bin/env python3
"""
Simple test to check form navigation and find submit button
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def simple_form_test():
    load_dotenv()
    username = os.getenv('SCHMICK_USER', 'lendly')
    password = os.getenv('SCHMICK_PASS', 'bluetruck25')
    
    print("🧪 Simple Form Navigation Test")
    print("=" * 35)
    
    playwright = None
    browser = None
    
    try:
        playwright = await async_playwright().start()
        browser = await playwright.firefox.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Login
        print("🔐 Logging in...")
        await page.goto("https://app.schmickclub.com/memberships/distributors", timeout=60000)
        await page.fill("#username", username)
        await page.fill("#password", password)  
        await page.click("#loginButton")
        await page.wait_for_timeout(5000)
        
        print(f"📍 After login URL: {page.url}")
        
        # Navigate to add member - try direct URL
        print("🔄 Navigating to add member form...")
        await page.goto("https://app.schmickclub.com/memberships/distributors/add-member", timeout=60000)
        await page.wait_for_timeout(3000)
        
        print(f"📍 Form page URL: {page.url}")
        print(f"📄 Page title: {await page.title()}")
        
        # Check if business name field exists (first field)
        try:
            await page.wait_for_selector("#businessName", timeout=10000)
            print("✅ Business name field found!")
            
            # Fill a test value
            await page.fill("#businessName", "Test Business")
            print("✅ Business name filled!")
            
        except Exception as e:
            print(f"❌ Business name field not found: {e}")
        
        # Look for submit buttons
        print("\n🔍 Looking for submit buttons...")
        buttons = await page.query_selector_all("button, input[type='submit']")
        
        for i, button in enumerate(buttons):
            button_type = await button.get_attribute('type')
            button_id = await button.get_attribute('id') 
            button_class = await button.get_attribute('class')
            button_text = await button.text_content()
            button_name = await button.get_attribute('name')
            print(f"  Button {i+1}: type='{button_type}' id='{button_id}' class='{button_class}' name='{button_name}' text='{button_text}'")
            
        print(f"\n⏳ Keeping browser open for 20 seconds...")
        await page.wait_for_timeout(20000)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()

if __name__ == "__main__":
    asyncio.run(simple_form_test())