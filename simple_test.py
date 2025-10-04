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
        
        print("🌐 Step 2: Launching Firefox browser...")
        browser = await playwright.firefox.launch(
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
        browser = await playwright.firefox.launch(
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
                
                # STEP 2: NAVIGATE TO RESULTS PAGE TO GET ID (Testing purpose)
                print("\n� Step 2: Navigating to results page to fetch existing ID...")
                await page.goto("https://actstrategic.ai/myaccount/fix-my-ads/", wait_until='networkidle', timeout=15000)
                
                results_title = await page.title()
                print(f"   📄 Results page title: {results_title}")
                
                # STEP 3: LOOK FOR TABLE AND EXTRACT ID
                print("\n🔍 Step 3: Looking for table with ID...")
                
                # Check for tables on this page
                table_count = await page.locator("table").count()
                print(f"   📋 Found {table_count} table(s) on the page")
                
                if table_count > 0:
                    # Extract ID from first row, first column
                    print("   🎯 Attempting to extract ID from table (first row, first column)...")
                    
                    # Try different selectors for the first cell using the specific table classes
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
                    
                    if not extracted_id:
                        print("   ❌ Could not extract ID from any selector")
                        print("   � Analyzing table structure...")
                        
                        # Debug: Look specifically for the target table first
                        target_table = page.locator(".widefat.striped.fixmyfunnel_submissions_lists")
                        if await target_table.count() > 0:
                            print("      ✅ Found target table with classes: widefat striped fixmyfunnel_submissions_lists")
                            
                            rows = await target_table.locator("tr").count()
                            print(f"         Rows in target table: {rows}")
                            
                            if rows > 0:
                                # Check first row cells
                                first_row_cells = await target_table.locator("tr:first-child td, tr:first-child th").count()
                                print(f"         First row cells: {first_row_cells}")
                                
                                if first_row_cells > 0:
                                    # Get all cells in first row
                                    for cell_idx in range(min(first_row_cells, 5)):  # Show first 5 cells max
                                        try:
                                            cell_text = await target_table.locator(f"tr:first-child td:nth-child({cell_idx + 1}), tr:first-child th:nth-child({cell_idx + 1})").first.text_content()
                                            print(f"         Cell {cell_idx + 1}: '{cell_text.strip() if cell_text else 'empty'}'")
                                        except:
                                            print(f"         Cell {cell_idx + 1}: Could not read")
                            else:
                                print("         ❌ Target table has no rows")
                        else:
                            print("      ❌ Target table not found, checking all tables...")
                            
                            # Fallback: Show all tables with their classes
                            all_tables = await page.locator("table").all()
                            for i, table in enumerate(all_tables):
                                try:
                                    class_attr = await table.get_attribute("class") or "no-class"
                                    rows = await table.locator("tr").count()
                                    print(f"      Table {i+1}: class='{class_attr}' rows={rows}")
                                except:
                                    print(f"      Table {i+1}: Could not analyze")
                    
                    else:
                        print(f"\n🎉 SUCCESS! ID extracted: {extracted_id}")
                        
                        # Return the extracted ID for programmatic use
                        return extracted_id
                
                else:
                    print("   ❌ No tables found on the results page")
                    print("   💡 The page might be empty or require form submission first")
                    
                    # Show what's actually on the page
                    page_content = await page.locator("body").text_content()
                    if page_content and len(page_content.strip()) > 0:
                        content_preview = page_content.strip()[:200] + "..." if len(page_content.strip()) > 200 else page_content.strip()
                        print(f"   📄 Page content preview: {content_preview}")
                    else:
                        print("   📄 Page appears to be empty")
                
                # STEP 4: ALSO NAVIGATE TO FORM FOR REFERENCE (keeping original flow)
                print(f"\n📝 Step 4: Also navigating to Fix My Ads form for reference...")
                await page.goto("https://actstrategic.ai/fixmyads/", wait_until='networkidle', timeout=15000)
                
                form_title = await page.title()
                print(f"   �📄 Form page title: {form_title}")
                
                # Check for forms on this page  
                form_count = await page.locator("form").count()
                form_inputs = await page.locator("input").count()
                print(f"   📋 Found {form_count} form(s) with {form_inputs} input(s)")
                
                if form_count > 0:
                    # STEP 5: FILL FORM (for reference)
                    print("\n🖊️  Step 5: Attempting to fill form with test data (reference only)...")
                    
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
                        print("\n🚀 Step 6: Ready to submit! (Not clicking in test mode)")
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
        extracted_id = await test_actstrategic_navigation()
        
        if extracted_id:
            print(f"\n🎯 FINAL RESULT: Extracted ID = '{extracted_id}'")
            return extracted_id
        else:
            print("\n❌ No ID was extracted")
            return None
    else:
        print("\n❌ Basic browser test failed. Fix browser issues before testing ACT Strategic.")
        return None
    
    print("\n🏁 Tests completed!")

if __name__ == "__main__":
    # Run the test and capture the extracted ID
    extracted_id = asyncio.run(main())
    
    if extracted_id:
        print(f"🎉 ID successfully extracted: {extracted_id}")
        print(f"📋 You can now use this ID in your application!")
        
        # Example: Save to file
        with open("extracted_id.txt", "w") as f:
            f.write(extracted_id)
        print(f"💾 ID saved to 'extracted_id.txt'")
        
    else:
        print("❌ No ID was extracted during the test")