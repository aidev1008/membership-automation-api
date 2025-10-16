#!/usr/bin/env python3
"""
Unified Schmick Club membership automation flow.
This function works identically on both localhost and Railway for:
1. Command line testing 
2. FastAPI server (for n8n integration)
"""

import asyncio
import os
import json
import uuid
from datetime import datetime
from playwright.async_api import async_playwright
from dotenv import load_dotenv
from website_selectors import selectors, FIELD_MAPPING


# Enhanced logging functions
def log_user_request(member_data, request_id=None):
    """Log user request data to requests.log"""
    if not request_id:
        request_id = str(uuid.uuid4())[:8]
    
    request_entry = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request_id,
        "user_data": member_data
    }
    
    try:
        with open("requests.log", "a") as f:
            f.write(f"\n[{request_entry['timestamp']}] REQUEST_ID: {request_id}\n")
            f.write(f"USER DATA: {json.dumps(member_data, indent=2)}\n")
            f.write("-" * 80 + "\n")
        
        print(f"   📝 Request logged with ID: {request_id}")
        return request_id
    except Exception as e:
        print(f"   ⚠️  Error logging request: {str(e)}")
        return request_id

def log_validation_errors_with_user_data(validation_errors, current_url, member_data, request_id):
    """Log validation errors with associated user data"""
    try:
        error_log_entry = f"\n[{datetime.now().isoformat()}] VALIDATION ERRORS\n"
        error_log_entry += f"REQUEST_ID: {request_id}\n"
        error_log_entry += f"URL: {current_url}\n"
        error_log_entry += f"USER_DATA: {json.dumps(member_data, indent=2)}\n"
        error_log_entry += "VALIDATION_ERRORS:\n"
        for error in validation_errors:
            error_log_entry += f"  - {error}\n"
        error_log_entry += "-" * 80 + "\n"
        
        with open("validation_errors.log", "a") as f:
            f.write(error_log_entry)
        
        print(f"   📝 Validation errors logged with user data (Request ID: {request_id})")
    except Exception as e:
        print(f"   ⚠️  Error logging validation errors: {str(e)}")


async def create_schmick_membership(member_data):
    """
    Complete Schmick Club membership creation workflow.
    
    Flow:
    1. Login to https://app.schmickclub.com/memberships/distributors
    2. Navigate to Add Member form  
    3. Fill membership form with provided data
    4. Submit form and handle validation
    5. Extract member ID from results
    6. Return member ID for n8n integration
    """
    
    # Generate request ID and log the incoming request
    request_id = str(uuid.uuid4())[:8]
    
    print("🧪 LOCAL TESTING MODE")
    print("=" * 50)
    print("📋 Using test data - this will be replaced by JSON from n8n")
    print()
    
    print("🔐 Schmick Club Membership Creation")
    print("=" * 45)
    print(f"👤 Creating membership for: {member_data.get('firstName', 'N/A')} {member_data.get('lastName', 'N/A')}")
    print(f"🆔 Request ID: {request_id}")
    
    # Log the user request
    log_user_request(member_data, request_id)
    
    # Determine environment mode
    is_railway = os.getenv("RAILWAY_ENVIRONMENT") == "true"
    headless_mode = is_railway
    
    # Load credentials
    load_dotenv()
    username = member_data["u"]
    password = member_data["p"]

    playwright = None
    browser = None
    context = None

    headless_env = os.getenv("HEADLESS", "true")
    headless_mode = str(headless_env).strip().lower() in ("1", "true", "yes", "on")
    print(f"🖥️ Headless mode: {headless_mode}")
    
    try:
        playwright = await async_playwright().start()
        
        # Configure Firefox for both local and cloud deployment
        browser = await playwright.firefox.launch(
            headless=headless_mode,  # False for local, True for Railway
            slow_mo=1000 if not headless_mode else 0,  # Slow down only for visible mode
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = await browser.new_context()
        page = await context.new_page()
        
        # STEP 1: LOGIN
        print("🔐 Step 1: Logging into Schmick Club...")
        login_url = selectors['login']['url']
        await page.goto(login_url, wait_until='networkidle', timeout=60000)
        
        # Fill login credentials
        await page.wait_for_selector(selectors['login']['username'], timeout=30000)
        await page.fill(selectors['login']['username'], username)
        print(f"   ✅ Filled username: {username}")
        
        await page.wait_for_selector(selectors['login']['password'], timeout=30000)  
        await page.fill(selectors['login']['password'], password)
        print("   ✅ Filled password")
        
        # Submit login
        await page.click(selectors['login']['submit'])
        print("   🚀 Clicked Login button")
        
        # Wait for login to complete
        await page.wait_for_timeout(10000)
        print(f"   🔗 URL after login: {page.url}")
        
        # STEP 2: NAVIGATE TO ADD MEMBER FORM
        print("\n� Step 2: Navigating to Add Member form...")
        add_member_url = selectors['new_membership']['url']
        await page.goto(add_member_url, wait_until='networkidle', timeout=60000)
        
        # Wait for form to be ready - wait for the first field to appear
        await page.wait_for_selector("#businessName", timeout=30000)
        print("   ✅ Add Member form loaded")
        
        # STEP 3: FILL FORM FIELDS
        print("\n✏️  Step 3: Filling membership form...")
        
        filled_fields = []
        
        # Fill text and email fields
        text_fields = [
            'businessName', 'firstName', 'lastName', 'email', 'address', 'city', 
            'postalAddress', 'startDate', 'postcode', 'mobile', 'phoneAH', 'distributorPONumber', 'distributorReference',
            'rego', 'colour', 'retailFee'
        ]
        
        for field in text_fields:
            if field in member_data and member_data[field]:
                selector_key = FIELD_MAPPING.get(field)
                if selector_key and selector_key in selectors['new_membership']:
                    try:
                        selector = selectors['new_membership'][selector_key]
                        await page.fill(selector, str(member_data[field]))
                        filled_fields.append(field)
                        print(f"   ✅ Filled {field}: {member_data[field]}")
                    except Exception as e:
                        print(f"   ⚠️ Failed to fill {field}: {e}")
        
        # Handle select dropdowns
        select_fields = ['state', 'carType', 'dealerId', 'prdId', 'vehPayOpt', 'year', 'make', 'model']
        
        for field in select_fields:
            if field in member_data and member_data[field]:
                selector_key = FIELD_MAPPING.get(field)
                if selector_key and selector_key in selectors['new_membership']:
                    try:
                        selector = selectors['new_membership'][selector_key]
                        await page.select_option(selector, str(member_data[field]))
                        filled_fields.append(field)
                        print(f"   ✅ Selected {field}: {member_data[field]}")
                    except Exception as e:
                        print(f"   ⚠️ Failed to select {field}: {e}")
        
        # Handle radio buttons for preExistingDamage
        if 'preExistingDamage' in member_data:
            try:
                if str(member_data['preExistingDamage']).lower() in ['true', 'yes', '1']:
                    await page.check(selectors['new_membership']['pre_existing_damage_yes'])
                    print("   ✅ Selected Pre-existing Damage: Yes")
                else:
                    await page.check(selectors['new_membership']['pre_existing_damage_no'])
                    print("   ✅ Selected Pre-existing Damage: No")
                filled_fields.append('preExistingDamage')
            except Exception as e:
                print(f"   ⚠️ Failed to set pre-existing damage: {e}")
        
        # Handle checkboxes
        checkbox_fields = ['alloyWheels', 'paintProtection']
        
        for field in checkbox_fields:
            if field in member_data and member_data[field]:
                selector_key = FIELD_MAPPING.get(field)
                if selector_key and selector_key in selectors['new_membership']:
                    try:
                        selector = selectors['new_membership'][selector_key]
                        if str(member_data[field]).lower() in ['true', 'yes', '1']:
                            await page.check(selector)
                            print(f"   ✅ Checked {field}")
                            filled_fields.append(field)
                    except Exception as e:
                        print(f"   ⚠️ Failed to check {field}: {e}")
        
        print(f"\n📊 Successfully filled {len(filled_fields)} fields")
        
        # STEP 4: SUBMIT FORM
        print("\n🚀 Step 4: Submitting membership form...")
        submit_selector = selectors['new_membership']['submit']
        await page.click(submit_selector)
        print("   🎯 Clicked 'Add Member' button")
        
        # Wait for form submission and check for validation errors
        await page.wait_for_timeout(5000)
        print(f"   🔗 URL after submission: {page.url}")
        
        # VALIDATION ERROR CHECKING
        try:
            validation_errors = []
            
            # Check if we're still on the add member form (indicates validation failure)
            current_url = page.url
            if "/add-member" in current_url or "distributors" in current_url:
                print("   ⚠️  Still on form page - checking for validation errors...")
                
                # Look for Kendo UI validation tooltips (primary method)
                kendo_validation_selector = ".k-widget.k-tooltip.k-tooltip-validation.k-invalid-msg"
                kendo_errors = page.locator(kendo_validation_selector)
                kendo_count = await kendo_errors.count()
                
                if kendo_count > 0:
                    print(f"   🔍 Found {kendo_count} Kendo validation errors")
                    for i in range(kendo_count):
                        error_element = kendo_errors.nth(i)
                        error_text = await error_element.text_content()
                        field_name = await error_element.get_attribute("data-for")
                        
                        if error_text and error_text.strip():
                            field_info = f" (Field: {field_name})" if field_name else ""
                            validation_errors.append(f"{error_text.strip()}{field_info}")
                
                # Also check for other common validation error patterns as backup
                backup_selectors = [
                    ".error",
                    ".field-error", 
                    ".validation-error",
                    ".alert-danger",
                    ".text-danger",
                    "[class*='error']",
                    "[class*='invalid']",
                    ".help-block.text-danger",
                    ".invalid-feedback"
                ]
                
                for error_selector in backup_selectors:
                    error_elements = page.locator(error_selector)
                    error_count = await error_elements.count()
                    
                    if error_count > 0:
                        for i in range(error_count):
                            error_text = await error_elements.nth(i).text_content()
                            if error_text and error_text.strip():
                                validation_errors.append(f"General error: {error_text.strip()}")
                
                # Check for any red text or required field indicators
                red_elements = page.locator("[style*='color: red'], [style*='color:red'], .text-red")
                red_count = await red_elements.count()
                
                for i in range(red_count):
                    red_text = await red_elements.nth(i).text_content()
                    if red_text and red_text.strip() and "required" in red_text.lower():
                        validation_errors.append(f"Required field error: {red_text.strip()}")
                
                # Look for HTML5 validation messages
                invalid_elements = page.locator(":invalid")
                invalid_count = await invalid_elements.count()
                
                if invalid_count > 0:
                    validation_errors.append(f"Found {invalid_count} invalid form fields")
                    for i in range(min(invalid_count, 5)):  # Limit to first 5
                        element = invalid_elements.nth(i)
                        field_name = await element.get_attribute("name") or await element.get_attribute("id") or "unknown"
                        validation_errors.append(f"Invalid field: {field_name}")
                
                if validation_errors:
                    print("   ❌ VALIDATION ERRORS DETECTED:")
                    for error in validation_errors:
                        print(f"      - {error}")
                    
                    # Log validation errors with user data
                    log_validation_errors_with_user_data(validation_errors, current_url, member_data, request_id)
                    
                    print("   🛑 STOPPING: Form submission failed due to validation errors")
                    return None
                else:
                    print("   ✅ No validation errors found on form page")
            else:
                print("   ✅ Successfully navigated away from form page")
        
        except Exception as e:
            print(f"   ⚠️  Error while checking for validation: {str(e)}")
        
        # Continue processing (wait a bit more for page to fully load)
        await page.wait_for_timeout(10000)
        print(f"   🔗 Final URL after validation check: {page.url}")
        
        # STEP 5: NAVIGATE TO VIEW MEMBERS
        print("\n📋 Step 5: Navigating to view members...")
        view_members_url = selectors['result']['url']
        await page.goto(view_members_url, wait_until='networkidle', timeout=60000)
        
        # STEP 6: EXTRACT MEMBER ID
        print("\n🔍 Step 6: Extracting member ID from table...")
        
        # Wait for table to load
        await page.wait_for_selector(selectors['result']['table_container'], timeout=30000)
        
        # Extract ID from first column, first row
        id_selector = selectors['result']['membership_selector']
        
        try:
            if await page.locator(id_selector).count() > 0:
                extracted_id = await page.locator(id_selector).first.text_content()
                if extracted_id and extracted_id.strip():
                    extracted_id = extracted_id.strip()
                    print(f"   ✅ EXTRACTED MEMBER ID: '{extracted_id}'")
                    
                    # Save to file for reference
                    with open("extracted_id.txt", "w") as f:
                        f.write(extracted_id)
                    print(f"   💾 ID saved to 'extracted_id.txt'")
                    
                    # Keep browser open briefly to see result
                    if not headless_mode:
                        print("   ⏳ Keeping browser open for 5 seconds...")
                        await page.wait_for_timeout(5000)
                    
                    return extracted_id
            
            print("   ❌ Could not find member ID in table")
            return None
            
        except Exception as e:
            print(f"   ❌ Error extracting ID: {e}")
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
    """Test function with sample data for local development"""
    # Test data for debugging
    test_member = {
        "businessName": "Test Business Ltd",
        "firstName": "John", 
        "lastName": "Doe",
        "email": "john.doe@test.com",
        "address": "123 Test Street",
        "city": "Test City",
        "postalAddress": "PO Box 456, Test City VIC 3000",
        "startDate": "06/10/2025",
        "state": "Victoria",
        "postcode": "3000",
        "mobile": "0412345678",
        "phoneAH": "0387654321",
        "preExistingDamage": "no",
        "distributorPONumber": "PO12345", 
        "distributorReference": "REF67811",
        "carType": "NEW",
        "dealerId": "3636152",
        "prdId": "24868",  # Will be selected from dropdown
        "vehPayOpt": "Cash",
        "year": "2023",
        "make": "Toyota", 
        "model": "Camry",
        "rego": "HR01AM4567",
        "colour": "White",
        "alloyWheels": True,
        "paintProtection": False,
        "retailFee": "299"
    }
    
    print("🧪 LOCAL TESTING MODE")
    print("=" * 50)
    print("📋 Using test data - this will be replaced by JSON from n8n")
    print()
    
    extracted_id = await create_schmick_membership(test_member)
    
    if extracted_id:
        print(f"\n🎯 FINAL RESULT: Member ID = '{extracted_id}'")
        print("🎉 Membership created successfully!")
        print("📋 You can now use this ID in your application!")
        return extracted_id
    else:
        print("\n❌ No member ID was extracted")
        return None


# if __name__ == "__main__":
#     # Run from command line for local testing
#     result = asyncio.run(main())
#     print(f"\nCommand line result: {result}")