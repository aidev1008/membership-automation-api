#!/usr/bin/env python3
"""
Simple browser test to check if Playwright can launch Chrome properly on macOS.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def simple_browser_test():
    """Simple test to see if browser launches correctly."""
    
    print("🧪 Simple Browser Launch Test")
    print("=" * 40)
    
    try:
        print("🚀 Step 1: Starting Playwright...")
        playwright = await async_playwright().start()
        
        print("🌐 Step 2: Launching Chrome browser...")
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=1000,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        print("✅ Browser launched successfully!")
        print("📄 Step 3: Creating a new page...")
        
        context = await browser.new_context()
        page = await context.new_page()
        
        print("✅ Page created successfully!")
        print("🌐 Step 4: Navigating to Google (simple test)...")
        
        await page.goto("https://www.google.com", wait_until='networkidle', timeout=10000)
        
        print("✅ Navigation successful!")
        print("⏳ Keeping browser open for 5 seconds so you can see it...")
        
        await page.wait_for_timeout(5000)
        
        print("🔚 Step 5: Closing browser...")
        await context.close()
        await browser.close()
        await playwright.stop()
        
        print("✅ All tests passed! Browser is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Try running: python -m playwright install chromium")
        print("2. Make sure you have sufficient permissions")
        print("3. Try closing other Chrome windows")
        return False

async def test_actstrategic_navigation():
    """Test navigation to ACT Strategic if browser works."""
    
    load_dotenv()
    username = os.getenv('SCHMICK_USER', '')
    
    print("\n🎯 ACT Strategic Navigation Test")
    print("=" * 40)
    
    if not username or username == 'your-actstrategic-username-here':
        print("ℹ️  No real credentials found, will just test navigation to login page")
        test_credentials = False
    else:
        print(f"📧 Will test with username: {username}")
        test_credentials = True
    
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=2000,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🌐 Navigating to ACT Strategic login page...")
        await page.goto("https://actstrategic.ai/myaccount/", wait_until='networkidle', timeout=15000)
        
        print("✅ Successfully loaded ACT Strategic page!")
        print("🔍 Looking for form elements...")
        
        # Check what's on the page
        title = await page.title()
        print(f"📄 Page title: {title}")
        
        # Look for common input fields
        inputs = await page.locator("input").count()
        print(f"📝 Found {inputs} input fields on the page")
        
        # Look for forms
        forms = await page.locator("form").count()
        print(f"📋 Found {forms} forms on the page")
        
        if test_credentials and inputs > 0:
            print("🧪 Testing complete workflow: Login → Form → ID...")
            
            password = os.getenv('SCHMICK_PASS', '')
            
            try:
                # STEP 1: LOGIN
                print("🔐 Step 1: Attempting login...")
                
                # Use the working selectors we discovered
                await page.wait_for_selector("#username", timeout=10000)
                await page.fill("#username", username)
                print(f"   ✅ Filled username: {username}")
                
                await page.wait_for_selector("#password", timeout=10000)  
                await page.fill("#password", password)
                print("   ✅ Filled password")
                
                # Submit login
                await page.click("button:has-text('Log in')")
                print("   🚀 Clicked login button")
                
                # Wait for login to complete
                await page.wait_for_timeout(5000)
                print(f"   🔗 URL after login: {page.url}")
                
                # STEP 2: NAVIGATE TO FORM
                print("\n📝 Step 2: Navigating to Fix My Ads form...")
                await page.goto("https://actstrategic.ai/fixmyads/", wait_until='networkidle', timeout=15000)
                
                form_title = await page.title()
                print(f"   📄 Form page title: {form_title}")
                
                # Check for forms on this page
                form_count = await page.locator("form").count()
                form_inputs = await page.locator("input").count()
                print(f"   📋 Found {form_count} form(s) with {form_inputs} input(s)")
                
                if form_count > 0:
                    # STEP 3: FILL FORM
                    print("\n🖊️  Step 3: Attempting to fill form with test data...")
                    
                    test_data = {
                        "firstName": "John",
                        "lastName": "Doe", 
                        "email": "john.doe@example.com",
                        "phone": "555-123-4567"
                    }
                    
                    filled_count = 0
                    
                    # Try to fill common fields
                    field_mappings = [
                        ("firstName", ["input[name*='first']", "input[placeholder*='First']", "#first_name"]),
                        ("lastName", ["input[name*='last']", "input[placeholder*='Last']", "#last_name"]),
                        ("email", ["input[type='email']", "input[name*='email']", "#email"]),
                        ("phone", ["input[type='tel']", "input[name*='phone']", "#phone"])
                    ]
                    
                    for field_name, selectors in field_mappings:
                        if field_name in test_data:
                            for selector in selectors:
                                try:
                                    if await page.locator(selector).count() > 0:
                                        await page.fill(selector, test_data[field_name])
                                        print(f"   ✅ Filled {field_name}: {test_data[field_name]}")
                                        filled_count += 1
                                        break
                                except:
                                    continue
                    
                    print(f"   📊 Successfully filled {filled_count}/{len(test_data)} fields")
                    
                    # Look for submit button (but don't click it yet)
                    submit_selectors = ["button[type='submit']", "input[type='submit']", "button:has-text('Submit')"]
                    submit_found = False
                    
                    for selector in submit_selectors:
                        try:
                            if await page.locator(selector).count() > 0:
                                button_text = await page.locator(selector).first.text_content()
                                print(f"   🎯 Found submit button: '{button_text}'")
                                submit_found = True
                                break
                        except:
                            continue
                    
                    if submit_found and filled_count > 0:
                        print("\n🚀 Step 4: Ready to submit! (Not clicking in test mode)")
                        print("   💡 You can manually click submit to test the full workflow")
                        print("   📍 After submission, check: https://actstrategic.ai/myaccount/fix-my-ads/")
                        
                    else:
                        print("   ⚠️  Could not find submit button or no fields were filled")
                
                else:
                    print("   ❌ No forms found on /fixmyads/ page")
                    print("   💡 This might require login or the URL might be different")
                
            except Exception as login_error:
                print(f"   ❌ Login/form error: {login_error}")
                print("   � Analyzing login page instead...")
                
                # Fallback: analyze the login page structure
                all_inputs = await page.locator("input").all()
                for i, inp in enumerate(all_inputs):
                    try:
                        name = await inp.get_attribute("name") or "no-name"
                        type_attr = await inp.get_attribute("type") or "text"
                        id_attr = await inp.get_attribute("id") or "no-id"
                        placeholder = await inp.get_attribute("placeholder") or "no-placeholder"
                        print(f"   Input {i+1}: name='{name}' type='{type_attr}' id='{id_attr}' placeholder='{placeholder}'")
                    except:
                        print(f"   Input {i+1}: Could not read attributes")
        
        print("⏳ Keeping browser open for 10 seconds so you can inspect the page...")
        await page.wait_for_timeout(10000)
        
        await context.close()
        await browser.close()
        await playwright.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during ACT Strategic test: {e}")
        return False

async def main():
    """Run both tests."""
    print("🎬 Playwright Browser Test Suite")
    print("This will help diagnose any browser issues")
    print()
    
    # Test 1: Basic browser functionality
    browser_works = await simple_browser_test()
    
    if browser_works:
        # Test 2: ACT Strategic specific test
        await test_actstrategic_navigation()
    else:
        print("\n❌ Basic browser test failed. Fix browser issues before testing ACT Strategic.")
    
    print("\n🏁 Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())