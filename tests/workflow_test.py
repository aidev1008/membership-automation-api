#!/usr/bin/env python3
"""
Complete workflow test: Login + Navigate to Fix My Ads + Fill Form
Tests the full automation process from login to form submission.
"""

import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

async def test_complete_workflow():
    """Test the complete workflow: login -> navigate -> fill form -> submit."""
    
    load_dotenv()
    username = os.getenv('SCHMICK_USER', '')
    password = os.getenv('SCHMICK_PASS', '')
    
    print("🎯 Complete ACT Strategic Workflow Test")
    print("=" * 50)
    print("Testing: Login → Fix My Ads Form → Submit")
    print(f"📧 Username: {username}")
    print(f"🔐 Password: {'*' * len(password) if password else 'NOT SET'}")
    print("=" * 50)
    
    # Sample data to fill in the form
    test_data = {
        "firstName": "John",
        "lastName": "Doe", 
        "email": "john.doe@example.com",
        "dob": "1990-01-01",
        "phone": "555-123-4567",
        "address": "123 Main St",
        "city": "Anytown",
        "state": "CA", 
        "zipCode": "12345"
    }
    
    async with async_playwright() as playwright:
        try:
            # Launch browser
            browser = await playwright.chromium.launch(
                headless=False,
                slow_mo=2000,  # 2 second delays to see what's happening
                args=['--start-maximized']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # ==========================================
            # STEP 1: LOGIN 
            # ==========================================
            print("\n🔐 STEP 1: Logging into ACT Strategic...")
            await page.goto("https://actstrategic.ai/myaccount/", timeout=30000)
            
            print("✅ Login page loaded")
            print(f"📄 Title: {await page.title()}")
            
            # Wait for and fill login form using the working selectors
            print("📝 Filling login credentials...")
            await page.wait_for_selector("#username", state="visible", timeout=10000)
            await page.fill("#username", username)
            
            await page.wait_for_selector("#password", state="visible", timeout=10000)
            await page.fill("#password", password)
            
            # Submit login form
            print("🚀 Submitting login...")
            await page.click("button:has-text('Log in')")
            
            # Wait for login to complete - check for page change or dashboard elements
            print("⏳ Waiting for login to complete...")
            try:
                # Wait for either URL change or dashboard elements to appear
                await page.wait_for_function(
                    "window.location.pathname !== '/myaccount/' || document.querySelector('.dashboard, .account-dashboard, .woocommerce-MyAccount-navigation')",
                    timeout=15000
                )
                print("✅ Login successful!")
            except:
                print("⚠️  Login might have taken longer, but continuing...")
            
            current_url = page.url
            print(f"🔗 Current URL after login: {current_url}")
            
            # ==========================================
            # STEP 2: NAVIGATE TO FIX MY ADS
            # ==========================================
            print("\n🌐 STEP 2: Navigating to Fix My Ads page...")
            await page.goto("https://actstrategic.ai/fixmyads/", timeout=30000)
            
            # Wait for page to load
            await page.wait_for_load_state('networkidle', timeout=15000)
            
            print("✅ Fix My Ads page loaded")
            print(f"📄 Title: {await page.title()}")
            print(f"🔗 URL: {page.url}")
            
            # ==========================================
            # STEP 3: ANALYZE THE FORM
            # ==========================================
            print("\n🔍 STEP 3: Analyzing Fix My Ads form...")
            
            # Look for forms and inputs
            forms = await page.locator("form").count()
            inputs = await page.locator("input").count()
            textareas = await page.locator("textarea").count()
            selects = await page.locator("select").count()
            
            print(f"📋 Found {forms} form(s)")
            print(f"📝 Found {inputs} input field(s)")
            print(f"📄 Found {textareas} textarea(s)")
            print(f"📋 Found {selects} select dropdown(s)")
            
            if forms == 0:
                print("❌ No forms found on the page!")
                print("📸 Taking screenshot for debugging...")
                await page.screenshot(path="fixmyads_no_form.png", full_page=True)
                return
            
            # Analyze input fields
            print("\n📝 Input Field Analysis:")
            all_inputs = await page.locator("input, textarea, select").all()
            
            form_fields = {}
            
            for i, field in enumerate(all_inputs):
                try:
                    tag_name = await field.evaluate("el => el.tagName.toLowerCase()")
                    name = await field.get_attribute("name") or ""
                    type_attr = await field.get_attribute("type") or "text"
                    id_attr = await field.get_attribute("id") or ""
                    placeholder = await field.get_attribute("placeholder") or ""
                    label_text = ""
                    
                    # Try to find associated label
                    if id_attr:
                        try:
                            label = await page.locator(f"label[for='{id_attr}']").first
                            if await label.count() > 0:
                                label_text = await label.text_content() or ""
                        except:
                            pass
                    
                    print(f"\n   Field {i+1} ({tag_name}):")
                    if name: print(f"      name: {name}")
                    if id_attr: print(f"      id: {id_attr}")
                    if type_attr: print(f"      type: {type_attr}")
                    if placeholder: print(f"      placeholder: {placeholder}")
                    if label_text: print(f"      label: {label_text}")
                    
                    # Store field info for potential matching
                    field_info = {
                        'element': field,
                        'name': name,
                        'id': id_attr,
                        'type': type_attr,
                        'placeholder': placeholder,
                        'label': label_text,
                        'selector': f"#{id_attr}" if id_attr else f"input[name='{name}']" if name else f"input:nth-of-type({i+1})"
                    }
                    
                    form_fields[i] = field_info
                    
                except Exception as e:
                    print(f"   Field {i+1}: Error reading - {e}")
            
            # ==========================================
            # STEP 4: ATTEMPT TO FILL FORM
            # ==========================================
            print(f"\n📝 STEP 4: Attempting to fill form with test data...")
            
            # Common field name patterns to look for
            field_patterns = {
                'firstName': ['first_name', 'fname', 'firstname', 'first-name'],
                'lastName': ['last_name', 'lname', 'lastname', 'last-name'],
                'email': ['email', 'email_address', 'mail'],
                'phone': ['phone', 'telephone', 'mobile', 'tel'],
                'dob': ['dob', 'date_of_birth', 'birthdate', 'birth_date'],
                'address': ['address', 'street', 'address1'],
                'city': ['city', 'town'],
                'state': ['state', 'province', 'region'],
                'zipCode': ['zip', 'zipcode', 'postal_code', 'postcode']
            }
            
            filled_fields = 0
            
            for data_key, data_value in test_data.items():
                print(f"\n🔍 Looking for field: {data_key} = '{data_value}'")
                
                # Get possible field names for this data
                possible_names = field_patterns.get(data_key, [data_key.lower()])
                possible_names.append(data_key.lower())
                
                field_found = False
                
                # Try to find matching field
                for field_info in form_fields.values():
                    field_name = field_info['name'].lower()
                    field_id = field_info['id'].lower()
                    field_placeholder = field_info['placeholder'].lower()
                    field_label = field_info['label'].lower()
                    
                    # Check if this field matches any of our patterns
                    if any(pattern in field_name or pattern in field_id or 
                           pattern in field_placeholder or pattern in field_label 
                           for pattern in possible_names):
                        
                        try:
                            print(f"   ✅ Found match: {field_info['selector']}")
                            
                            # Fill the field
                            if field_info['type'] == 'select':
                                # Handle dropdown
                                print(f"   📋 Dropdown field - checking options...")
                                options = await field_info['element'].locator('option').all_text_contents()
                                print(f"   📋 Available options: {options}")
                                
                                # For state, try to find matching option
                                if data_key == 'state':
                                    for option_text in options:
                                        if data_value.upper() in option_text.upper() or option_text.upper() == data_value.upper():
                                            await field_info['element'].select_option(label=option_text)
                                            print(f"   ✅ Selected option: {option_text}")
                                            filled_fields += 1
                                            field_found = True
                                            break
                            else:
                                # Handle text input
                                await field_info['element'].fill(str(data_value))
                                print(f"   ✅ Filled with: {data_value}")
                                filled_fields += 1
                                field_found = True
                            
                            break
                            
                        except Exception as e:
                            print(f"   ❌ Error filling field: {e}")
                
                if not field_found:
                    print(f"   ❌ No matching field found for {data_key}")
            
            print(f"\n📊 Form filling summary: {filled_fields}/{len(test_data)} fields filled")
            
            # ==========================================
            # STEP 5: SUBMIT FORM
            # ==========================================
            if filled_fields > 0:
                print(f"\n🚀 STEP 5: Looking for submit button...")
                
                # Common submit button selectors
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']", 
                    "button:has-text('Submit')",
                    "button:has-text('Send')",
                    "button:has-text('Apply')",
                    ".submit-btn",
                    ".btn-submit",
                    "form button:last-of-type"
                ]
                
                submit_found = False
                for selector in submit_selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            button_text = await page.locator(selector).first.text_content()
                            print(f"   🎯 Found submit button: '{button_text}' ({selector})")
                            
                            print("   ⏳ Clicking submit button...")
                            await page.click(selector)
                            
                            # Wait for form submission
                            print("   ⏳ Waiting for form submission...")
                            await page.wait_for_load_state('networkidle', timeout=15000)
                            
                            final_url = page.url
                            final_title = await page.title()
                            
                            print(f"   🔗 URL after submission: {final_url}")
                            print(f"   📄 Title after submission: {final_title}")
                            
                            if final_url != "https://actstrategic.ai/fixmyads/":
                                print("   🎉 SUCCESS! Form submitted - page changed!")
                            else:
                                print("   ⚠️  Still on same page - checking for success/error messages...")
                                
                                # Look for success/error messages
                                success_indicators = [".success", ".alert-success", ".message", ".confirmation"]
                                error_indicators = [".error", ".alert-danger", ".validation-error"]
                                
                                for sel in success_indicators:
                                    try:
                                        if await page.locator(sel).count() > 0:
                                            msg = await page.locator(sel).text_content()
                                            print(f"   ✅ Success message: {msg}")
                                    except:
                                        pass
                                
                                for sel in error_indicators:
                                    try:
                                        if await page.locator(sel).count() > 0:
                                            msg = await page.locator(sel).text_content()
                                            print(f"   ❌ Error message: {msg}")
                                    except:
                                        pass
                            
                            submit_found = True
                            break
                            
                    except Exception as e:
                        continue
                
                if not submit_found:
                    print("   ❌ No submit button found")
                    
                    # Show all buttons for debugging
                    all_buttons = await page.locator("button, input[type='submit']").all()
                    print(f"\n   🔘 All buttons found ({len(all_buttons)}):")
                    for i, btn in enumerate(all_buttons):
                        try:
                            text = await btn.text_content() or ""
                            type_attr = await btn.get_attribute("type") or ""
                            print(f"      Button {i+1}: '{text.strip()}' type='{type_attr}'")
                        except:
                            print(f"      Button {i+1}: Could not read")
            
            # Keep browser open for inspection
            print(f"\n👀 Keeping browser open for 30 seconds for inspection...")
            await page.wait_for_timeout(30000)
            
        except Exception as e:
            print(f"❌ Error during workflow: {e}")
            import traceback
            traceback.print_exc()
        
        print("🏁 Workflow test completed!")

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())