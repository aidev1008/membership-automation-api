#!/usr/bin/env python3
"""
MacOS-optimized browser test for ACT Strategic login.
Uses more robust browser launch options for macOS compatibility.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def test_with_robust_options():
    """Test with macOS-optimized browser options."""
    
    load_dotenv()
    username = os.getenv('SCHMICK_USER', '')
    password = os.getenv('SCHMICK_PASS', '')
    
    print("🍎 macOS-Optimized ACT Strategic Login Test")
    print("=" * 50)
    print(f"📧 Username: {username}")
    print(f"🔐 Password: {'*' * len(password) if password else 'NOT SET'}")
    print("=" * 50)
    
    playwright = None
    browser = None
    context = None
    
    try:
        print("🚀 Starting Playwright...")
        playwright = await async_playwright().start()
        
        print("🌐 Launching Chrome with macOS-optimized settings...")
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=3000,  # 3 second delay between actions
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-first-run',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        print("✅ Browser launched!")
        print("📄 Creating browser context...")
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        print("✅ Context created!")
        print("📱 Creating new page...")
        
        page = await context.new_page()
        
        print("✅ Page created successfully!")
        print("🌐 Navigating to ACT Strategic...")
        
        # Navigate to ACT Strategic
        response = await page.goto(
            "https://actstrategic.ai/myaccount/",
            wait_until='domcontentloaded',
            timeout=20000
        )
        
        print(f"✅ Navigation complete! Status: {response.status}")
        
        # Wait for page to fully load
        print("⏳ Waiting for page to fully load...")
        await page.wait_for_load_state('networkidle', timeout=10000)
        
        # Get page info
        title = await page.title()
        url = page.url
        print(f"📄 Page title: {title}")
        print(f"🔗 Current URL: {url}")
        
        # Look for login elements
        print("🔍 Analyzing page structure...")
        
        # Count elements
        inputs = await page.locator("input").count()
        buttons = await page.locator("button").count()
        forms = await page.locator("form").count()
        
        print(f"📝 Found {inputs} input fields")
        print(f"🔘 Found {buttons} buttons")
        print(f"📋 Found {forms} forms")
        
        if inputs > 0:
            print("\n🔍 Analyzing input fields...")
            all_inputs = await page.locator("input").all()
            
            for i, inp in enumerate(all_inputs[:10]):  # Show first 10 inputs
                try:
                    name = await inp.get_attribute("name") or ""
                    type_attr = await inp.get_attribute("type") or ""
                    id_attr = await inp.get_attribute("id") or ""
                    placeholder = await inp.get_attribute("placeholder") or ""
                    class_attr = await inp.get_attribute("class") or ""
                    
                    print(f"   Input {i+1}:")
                    if name: print(f"      name='{name}'")
                    if type_attr: print(f"      type='{type_attr}'")
                    if id_attr: print(f"      id='{id_attr}'")
                    if placeholder: print(f"      placeholder='{placeholder}'")
                    if class_attr: print(f"      class='{class_attr}'")
                    print()
                    
                except Exception as e:
                    print(f"   Input {i+1}: Error reading attributes - {e}")
        
        # Test login if we have credentials
        if username and username != 'your-actstrategic-username-here' and inputs >= 2:
            print("🧪 Testing login with provided credentials...")
            
            # Try to find and fill username field
            username_filled = False
            username_selectors = [
                "input[name='username']",
                "input[name='user']", 
                "input[name='email']",
                "input[type='email']",
                "input[name='log']",
                "input[id*='user']",
                "input[id*='email']"
            ]
            
            for selector in username_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        print(f"✏️  Filling username with selector: {selector}")
                        await page.fill(selector, username)
                        username_filled = True
                        break
                except Exception as e:
                    continue
            
            if username_filled:
                # Try to find and fill password field
                password_selectors = [
                    "input[name='password']",
                    "input[name='pass']",
                    "input[type='password']",
                    "input[id*='pass']"
                ]
                
                password_filled = False
                for selector in password_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            print(f"🔐 Filling password with selector: {selector}")
                            await page.fill(selector, password)
                            password_filled = True
                            break
                    except Exception as e:
                        continue
                
                if password_filled:
                    # Try to find and click submit button
                    submit_selectors = [
                        "button[type='submit']",
                        "input[type='submit']",
                        "button[name='login']",
                        "button[name='submit']",
                        ".login-button",
                        ".submit-btn",
                        "button:has-text('Login')",
                        "button:has-text('Sign In')"
                    ]
                    
                    submit_clicked = False
                    for selector in submit_selectors:
                        try:
                            if await page.locator(selector).count() > 0:
                                print(f"🚀 Clicking submit with selector: {selector}")
                                await page.click(selector)
                                submit_clicked = True
                                break
                        except Exception as e:
                            continue
                    
                    if submit_clicked:
                        print("⏳ Waiting for login result...")
                        try:
                            await page.wait_for_load_state('networkidle', timeout=10000)
                            new_url = page.url
                            print(f"🔗 URL after login: {new_url}")
                            
                            if new_url != url:
                                print("🎉 LOGIN SUCCESS - URL changed!")
                            else:
                                print("⚠️  Still on same page - check for errors")
                        except:
                            print("⏳ Login taking longer than expected...")
                    else:
                        print("❌ Could not find submit button")
                else:
                    print("❌ Could not find password field")
            else:
                print("❌ Could not find username field")
        
        print("\n👀 Keeping browser open for 15 seconds so you can inspect...")
        await page.wait_for_timeout(15000)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("🔚 Cleaning up...")
        try:
            if context:
                await context.close()
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()
        except:
            pass
        
        print("✅ Cleanup completed!")

if __name__ == "__main__":
    asyncio.run(test_with_robust_options())