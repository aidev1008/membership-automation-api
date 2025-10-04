#!/usr/bin/env python3
"""
Login-Only Test for ACT Strategic
This script will ONLY test the login functionality so you can see it working in the browser.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def test_login_only():
    """Test only the login functionality with visible browser."""
    
    # Load environment
    load_dotenv()
    
    username = os.getenv('SCHMICK_USER')
    password = os.getenv('SCHMICK_PASS')
    
    print("🎯 ACT Strategic Login Test")
    print("=" * 40)
    print(f"📧 Username: {username}")
    print(f"🔐 Password: {'*' * len(password) if password else 'NOT SET'}")
    print(f"🌐 URL: https://actstrategic.ai/myaccount/")
    print("=" * 40)
    
    if not username or username == 'your-actstrategic-username-here':
        print("❌ Please update SCHMICK_USER in .env file with real credentials!")
        return
        
    if not password or password == 'your-actstrategic-password-here':
        print("❌ Please update SCHMICK_PASS in .env file with real credentials!")
        return
    
    # Start Playwright
    print("🚀 Starting browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=False,  # Visible browser
        slow_mo=2000     # 2 second delay between actions so you can see what's happening
    )
    
    try:
        # Create a new page
        page = await browser.new_page()
        
        print("📖 Step 1: Navigating to login page...")
        await page.goto("https://actstrategic.ai/myaccount/", wait_until='networkidle')
        
        print("⏳ Waiting 3 seconds for you to see the page...")
        await page.wait_for_timeout(3000)
        
        print("🔍 Step 2: Looking for username field...")
        # Try the username selectors you configured
        username_selectors = [
            "input[name='username']",
            "input[type='text']", 
            "#username"
        ]
        
        username_field = None
        for selector in username_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    username_field = selector
                    print(f"✅ Found username field with selector: {selector}")
                    break
            except:
                continue
        
        if not username_field:
            print("❌ Could not find username field. Available input fields:")
            inputs = await page.locator("input").all()
            for i, input_elem in enumerate(inputs):
                name = await input_elem.get_attribute("name") or "no-name"
                type_attr = await input_elem.get_attribute("type") or "no-type"
                id_attr = await input_elem.get_attribute("id") or "no-id"
                print(f"   Input {i+1}: name='{name}' type='{type_attr}' id='{id_attr}'")
            
            print("\n💡 Update the username selector in website_selectors.py based on the above")
            await page.wait_for_timeout(10000)  # Wait 10 seconds to inspect
            return
        
        print("🔍 Step 3: Looking for password field...")
        # Try the password selectors you configured
        password_selectors = [
            "input[name='password']",
            "input[type='password']", 
            "#password"
        ]
        
        password_field = None
        for selector in password_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    password_field = selector
                    print(f"✅ Found password field with selector: {selector}")
                    break
            except:
                continue
        
        if not password_field:
            print("❌ Could not find password field!")
            await page.wait_for_timeout(10000)  # Wait 10 seconds to inspect
            return
        
        print("✏️  Step 4: Filling username...")
        await page.fill(username_field, username)
        await page.wait_for_timeout(1000)  # Pause to see it
        
        print("✏️  Step 5: Filling password...")
        await page.fill(password_field, password)
        await page.wait_for_timeout(1000)  # Pause to see it
        
        print("🔍 Step 6: Looking for submit button...")
        # Try the submit button selectors you configured
        submit_selectors = [
            "button[type='submit']",
            "button[name='login']", 
            ".login-button",
            ".submit-btn"
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                if await page.locator(selector).count() > 0:
                    submit_button = selector
                    print(f"✅ Found submit button with selector: {selector}")
                    break
            except:
                continue
        
        if not submit_button:
            print("❌ Could not find submit button. Available buttons:")
            buttons = await page.locator("button, input[type='submit']").all()
            for i, btn in enumerate(buttons):
                name = await btn.get_attribute("name") or "no-name"
                type_attr = await btn.get_attribute("type") or "no-type"
                text = await btn.text_content() or "no-text"
                print(f"   Button {i+1}: name='{name}' type='{type_attr}' text='{text.strip()}'")
                
            print("\n💡 Update the submit selector in website_selectors.py based on the above")
            await page.wait_for_timeout(10000)  # Wait 10 seconds to inspect
            return
        
        print("🚀 Step 7: Clicking submit button...")
        await page.click(submit_button)
        
        print("⏳ Step 8: Waiting for login to complete...")
        try:
            # Wait for page to change (either success or error)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            current_url = page.url
            print(f"📍 Current URL after login: {current_url}")
            
            if "login" not in current_url.lower() and current_url != "https://actstrategic.ai/myaccount/":
                print("🎉 LOGIN SUCCESS! You've been redirected to a different page!")
            else:
                print("⚠️  Still on login page - check for error messages")
                
                # Look for error messages
                error_selectors = [".error", ".alert", ".message", ".notification"]
                for selector in error_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            error_text = await page.locator(selector).text_content()
                            print(f"❌ Error message: {error_text}")
                    except:
                        pass
            
        except:
            print("⏳ Login taking longer than expected...")
        
        print("👀 Keeping browser open for 10 seconds so you can inspect the result...")
        await page.wait_for_timeout(10000)
        
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        await page.wait_for_timeout(10000)  # Keep browser open to see what happened
        
    finally:
        print("🔚 Closing browser...")
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    print("🎬 Starting ACT Strategic Login Test")
    print("This will open a visible Chrome browser and attempt to login")
    print("Watch the browser to see each step!")
    print()
    
    asyncio.run(test_login_only())