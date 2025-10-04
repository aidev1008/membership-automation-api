#!/usr/bin/env python3
"""
System Chrome test for ACT Strategic login.
Uses the system's installed Chrome instead of Playwright's bundled Chromium.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def test_with_system_chrome():
    """Test using system Chrome instead of bundled Chromium."""
    
    load_dotenv()
    username = os.getenv('SCHMICK_USER', '')
    password = os.getenv('SCHMICK_PASS', '')
    
    print("🖥️  System Chrome ACT Strategic Login Test")
    print("=" * 50)
    print("Using your installed Google Chrome instead of bundled Chromium")
    print(f"📧 Username: {username}")
    print(f"🔐 Password: {'*' * len(password) if password else 'NOT SET'}")
    print("=" * 50)
    
    playwright = None
    browser = None
    
    try:
        print("🚀 Starting Playwright...")
        playwright = await async_playwright().start()
        
        print("🌐 Launching your system Chrome with persistent context...")
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir="/tmp/playwright-chrome",
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            headless=False,
            slow_mo=2000,  # 2 second delay between actions
            args=[
                '--no-first-run',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        
        print("✅ System Chrome launched successfully!")
        
        # Create page
        page = await context.new_page()
        
        print("✅ Page created successfully!")
        print("🌐 Navigating to ACT Strategic...")
        
        # Navigate to ACT Strategic
        await page.goto(
            "https://actstrategic.ai/myaccount/",
            wait_until='domcontentloaded',
            timeout=20000
        )
        
        print("✅ Successfully navigated to ACT Strategic!")
        
        # Wait for page to load
        await page.wait_for_load_state('networkidle', timeout=15000)
        
        # Get page info
        title = await page.title()
        url = page.url
        print(f"📄 Page title: {title}")
        print(f"🔗 Current URL: {url}")
        
        # Analyze the login form
        print("🔍 Analyzing login form...")
        
        # Look for form elements
        forms = await page.locator("form").count()
        inputs = await page.locator("input").count()
        buttons = await page.locator("button").count()
        
        print(f"📋 Found {forms} form(s)")
        print(f"📝 Found {inputs} input field(s)")  
        print(f"🔘 Found {buttons} button(s)")
        
        if inputs > 0:
            print("\n📝 Input Field Analysis:")
            all_inputs = await page.locator("input").all()
            
            username_candidates = []
            password_candidates = []
            
            for i, inp in enumerate(all_inputs):
                try:
                    name = await inp.get_attribute("name") or ""
                    type_attr = await inp.get_attribute("type") or "text"
                    id_attr = await inp.get_attribute("id") or ""
                    placeholder = await inp.get_attribute("placeholder") or ""
                    
                    print(f"\n   Input {i+1}:")
                    print(f"      type: {type_attr}")
                    if name: print(f"      name: {name}")
                    if id_attr: print(f"      id: {id_attr}")
                    if placeholder: print(f"      placeholder: {placeholder}")
                    
                    # Classify potential username/password fields
                    if type_attr == "password":
                        password_candidates.append((i+1, name or id_attr, f"input[name='{name}']" if name else f"#{id_attr}"))
                    elif type_attr in ["text", "email"] or "user" in name.lower() or "email" in name.lower():
                        username_candidates.append((i+1, name or id_attr, f"input[name='{name}']" if name else f"#{id_attr}"))
                        
                except Exception as e:
                    print(f"   Input {i+1}: Error reading - {e}")
            
            print(f"\n🎯 Analysis Results:")
            if username_candidates:
                print("📧 Potential Username Fields:")
                for idx, field_name, selector in username_candidates:
                    print(f"   Field {idx}: {field_name} → {selector}")
            
            if password_candidates:
                print("🔐 Potential Password Fields:")
                for idx, field_name, selector in password_candidates:
                    print(f"   Field {idx}: {field_name} → {selector}")
            
            # Test login if we have credentials and found fields
            if (username and username != 'your-actstrategic-username-here' and 
                username_candidates and password_candidates):
                
                print(f"\n🧪 Testing login with credentials...")
                
                # Use the fields with unique IDs (Field 19 and 20 from the analysis)
                username_selector = "#username"  # input with id="username"
                password_selector = "#password"  # input with id="password"
                
                print(f"✏️  Filling username field: {username_selector}")
                # Wait for the field to be visible and interactable
                await page.wait_for_selector(username_selector, state="visible", timeout=10000)
                await page.fill(username_selector, username)
                
                print(f"🔐 Filling password field: {password_selector}")
                await page.wait_for_selector(password_selector, state="visible", timeout=10000)
                await page.fill(password_selector, password)
                
                # Look for submit button
                print("🔍 Looking for submit button...")
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:has-text('Log in')",
                    "button:has-text('Login')", 
                    "button:has-text('Sign In')",
                    ".wp-block-button__link",
                    ".login-submit"
                ]
                
                submit_found = False
                for selector in submit_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            print(f"🚀 Found submit button: {selector}")
                            
                            # Get button text for confirmation
                            button_text = await page.locator(selector).text_content()
                            print(f"   Button text: '{button_text.strip()}'")
                            
                            print("🚀 Clicking submit button...")
                            await page.click(selector)
                            submit_found = True
                            break
                    except Exception as e:
                        continue
                
                if submit_found:
                    print("⏳ Waiting for login result...")
                    try:
                        await page.wait_for_load_state('networkidle', timeout=15000)
                        
                        new_url = page.url
                        new_title = await page.title()
                        
                        print(f"🔗 URL after login: {new_url}")
                        print(f"📄 Title after login: {new_title}")
                        
                        if new_url != url:
                            print("🎉 LOGIN SUCCESS! Page changed after login.")
                            
                            # Check if we're on a dashboard or account page
                            if any(keyword in new_url.lower() for keyword in ['dashboard', 'account', 'profile']):
                                print("✅ Successfully logged into account area!")
                        else:
                            print("⚠️  Still on login page. Checking for errors...")
                            
                            # Look for error messages
                            error_selectors = [
                                ".error", ".alert", ".message", ".notice", 
                                ".login-error", "[class*='error']"
                            ]
                            
                            for error_sel in error_selectors:
                                try:
                                    if await page.locator(error_sel).count() > 0:
                                        error_text = await page.locator(error_sel).text_content()
                                        if error_text and error_text.strip():
                                            print(f"❌ Error found: {error_text.strip()}")
                                except:
                                    pass
                    
                    except Exception as e:
                        print(f"⏳ Login process taking longer: {e}")
                        
                else:
                    print("❌ Could not find submit button")
                    
                    # Show all buttons for debugging
                    all_buttons = await page.locator("button, input[type='submit']").all()
                    print(f"\n🔘 All buttons found ({len(all_buttons)}):")
                    for i, btn in enumerate(all_buttons):
                        try:
                            text = await btn.text_content() or ""
                            type_attr = await btn.get_attribute("type") or ""
                            class_attr = await btn.get_attribute("class") or ""
                            print(f"   Button {i+1}: '{text.strip()}' type='{type_attr}' class='{class_attr}'")
                        except:
                            print(f"   Button {i+1}: Could not read attributes")
            
            else:
                if not username or username == 'your-actstrategic-username-here':
                    print("⚠️  No credentials provided - update .env file to test login")
                else:
                    print("⚠️  Could not identify username/password fields clearly")
        
        print(f"\n👀 Keeping browser open for 20 seconds for manual inspection...")
        print("💡 You can manually interact with the page now!")
        await page.wait_for_timeout(20000)
        
        # Clean up
        await context.close()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if playwright:
            await playwright.stop()
            
        print("🏁 All done!")

if __name__ == "__main__":
    asyncio.run(test_with_system_chrome())