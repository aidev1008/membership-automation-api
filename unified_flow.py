#!/usr/bin/env python3
"""
Unified ACT Strategic ID extraction flow.
This function works exactly like simple_test.py and can be called from:
1. Command line 
2. FastAPI server (for n8n)
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv


async def extract_act_strategic_id():
    """
    Extract ID from ACT Strategic exactly like simple_test.py does.
    
    Flow:
    1. Login to https://actstrategic.ai/myaccount/
    2. Navigate to https://actstrategic.ai/myaccount/fix-my-ads/
    3. Extract ID from table first row, first column
    4. Return the ID
    
    Returns:
        str: The extracted ID (e.g., "15") or None if failed
    """
    
    load_dotenv()
    username = os.getenv('SCHMICK_USER', '')
    password = os.getenv('SCHMICK_PASS', '')
    
    if not username or not password:
        raise ValueError("Missing SCHMICK_USER or SCHMICK_PASS in environment")
    
    print("🎯 ACT Strategic ID Extraction")
    print("=" * 40)
    
    playwright = None
    browser = None
    context = None
    
    try:
        playwright = await async_playwright().start()
        
        # Use the exact same Firefox configuration as simple_test.py
        browser = await playwright.firefox.launch(
            headless=False,  # Keep visible like simple_test.py
            slow_mo=1000,    # Same timing
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # STEP 1: LOGIN (exactly like simple_test.py)
        print("🔐 Step 1: Logging in...")
        await page.goto("https://actstrategic.ai/myaccount/", wait_until='networkidle', timeout=15000)
        
        # Use working selectors from simple_test.py
        await page.wait_for_selector("#username", timeout=10000)
        await page.fill("#username", username)
        print(f"   ✅ Filled username: {username}")
        
        await page.wait_for_selector("#password", timeout=10000)  
        await page.fill("#password", password)
        print("   ✅ Filled password")
        
        # Submit login using working selector from simple_test.py
        await page.click("button:has-text('Log in')")
        print("   🚀 Clicked login button")
        
        # Wait for login to complete
        await page.wait_for_timeout(5000)
        print(f"   🔗 URL after login: {page.url}")
        
        # STEP 2: NAVIGATE TO RESULTS PAGE (exactly like simple_test.py)
        print("\n📋 Step 2: Navigating to results page...")
        await page.goto("https://actstrategic.ai/myaccount/fix-my-ads/", wait_until='networkidle', timeout=15000)
        
        # STEP 3: EXTRACT ID (exactly like simple_test.py)
        print("\n🔍 Step 3: Extracting ID from table...")
        
        # Use the same selectors that work in simple_test.py
        id_selectors = [
            ".widefat.striped.fixmyfunnel_submissions_lists tr:first-child td:first-child",
            ".widefat.striped.fixmyfunnel_submissions_lists tbody tr:first-child td:first-child",
            ".fixmyfunnel_submissions_lists tr:first-child td:first-child",
            ".widefat tr:first-child td:first-child",
            "table.widefat tr:first-child td:first-child",
            "table tr:first-child td:first-child"
        ]
        
        extracted_id = None
        
        for selector in id_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    extracted_id = await page.locator(selector).first.text_content()
                    if extracted_id and extracted_id.strip():
                        extracted_id = extracted_id.strip()
                        print(f"   ✅ EXTRACTED ID: '{extracted_id}' using selector: {selector}")
                        break
            except Exception as e:
                print(f"   ⚠️ Selector {selector} failed: {e}")
                continue
        
        if extracted_id:
            print(f"\n🎉 SUCCESS! ID extracted: {extracted_id}")
            
            # Save to file like simple_test.py does
            with open("extracted_id.txt", "w") as f:
                f.write(extracted_id)
            print(f"💾 ID saved to 'extracted_id.txt'")
            
            # Keep browser open briefly to see result (like simple_test.py)
            print("⏳ Keeping browser open for 3 seconds...")
            await page.wait_for_timeout(3000)
            
            return extracted_id
        else:
            print("❌ Could not extract ID from any selector")
            return None
            
    except Exception as e:
        print(f"❌ Error during ID extraction: {e}")
        return None
        
    finally:
        # Clean up
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()


async def main():
    """Command line interface - same as simple_test.py"""
    extracted_id = await extract_act_strategic_id()
    
    if extracted_id:
        print(f"\n🎯 FINAL RESULT: Extracted ID = '{extracted_id}'")
        print("🎉 ID successfully extracted!")
        print("📋 You can now use this ID in your application!")
        return extracted_id
    else:
        print("\n❌ No ID was extracted")
        return None


if __name__ == "__main__":
    # Run from command line - same interface as simple_test.py
    result = asyncio.run(main())
    print(f"\nCommand line result: {result}")