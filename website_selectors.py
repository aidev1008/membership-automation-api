"""
CSS/XPath selectors for the Schmick web application.
These selectors need to be updated to match the actual Schmick website structure.
"""

# ACT Strategic website selectors - UPDATED for real website
# These selectors are configured for actstrategic.ai workflow:
# 1. Login at /myaccount/
# 2. Fill form at /fixmyads/ 
# 3. Get ID from table at /myaccount/fix-my-ads/

selectors = {
    # Login page selectors for ACT Strategic
    "login": {
        "url": "https://actstrategic.ai/myaccount/",
        # TODO: Update these selectors after inspecting the actual login form
        "username": "#username",  # Using unique ID to avoid multiple matches
        "password": "#password",  # Using unique ID to avoid multiple matches
        "submit": "button[type='submit'], button[name='login'], .login-button, .submit-btn",
        "post_login_indicator": ".dashboard, .account-dashboard, .user-menu, .logout, body:not(.login-page)",
        # Common selectors for potential issues
        "captcha_indicator": ".captcha, #captcha, [class*='captcha'], .recaptcha, .g-recaptcha",
        "two_fa_indicator": ".two-factor, [id='2fa'], [class*='two-factor'], .mfa, .authentication-code",
    },
    
    # Fix My Ads form selectors for ACT Strategic
    "new_membership": {
        "url": "https://actstrategic.ai/fixmyads/",
        # TODO: Update these selectors after inspecting the /fixmyads/ form
        # Common form field selectors - will need to be customized
        "first_name": "input[name='firstName'], input[name='first_name'], input[name='fname'], #firstName, #first_name",
        "last_name": "input[name='lastName'], input[name='last_name'], input[name='lname'], #lastName, #last_name",
        "email": "input[name='email'], input[type='email'], #email",
        "date_of_birth": "input[name='dob'], input[name='dateOfBirth'], input[name='birthdate'], #dob",
        "phone": "input[name='phone'], input[name='telephone'], input[type='tel'], #phone",
        "address": "input[name='address'], input[name='street'], #address",
        "city": "input[name='city'], #city",
        "state": "select[name='state'], select[name='province'], #state",
        "zip_code": "input[name='zip'], input[name='zipcode'], input[name='postal'], #zip",
        "emergency_contact_name": "input[name='emergency_contact'], input[name='emergencyName'], #emergency_contact",
        "emergency_contact_phone": "input[name='emergency_phone'], input[name='emergencyPhone'], #emergency_phone",
        # Form submission
        "submit": "button[type='submit'], input[type='submit'], .submit-btn, .btn-submit, button:has-text('Submit')",
        "form_container": "form, .form-container, .fixmyads-form, #fixmyads-form",
    },
    
    # Result page selectors for ACT Strategic table at /myaccount/fix-my-ads/
    "result": {
        # The ID should be in the first column of the table
        "membership_selector": ".widefat.striped.fixmyfunnel_submissions_lists tbody tr:first-child td:first-child, table.widefat.striped.fixmyfunnel_submissions_lists tr:first-child td:first-child, table tr:first-child td:first-child",
        "success_indicator": "table, .table, .fix-my-ads-table, .data-table",  # Table presence indicates success
        "error_indicator": ".error, .alert-danger, .error-message, .validation-error, .alert-error",
        "loading_indicator": ".loading, .spinner, .processing, .loader",
        # Alternative selectors in case the table structure is different
        "table_container": ".widefat.striped.fixmyfunnel_submissions_lists, table.widefat.striped.fixmyfunnel_submissions_lists, table, .table",
        "first_row": "tr:first-child, tbody tr:first-child, tr:not(:has(th))",
        "first_column": "td:first-child, td:first-of-type",
    },
    
    # Common navigation selectors
    "navigation": {
        "home": "a[href='/'], .logo",  # TODO: Update with actual home/logo link
        "logout": "a[href*='logout'], button[class*='logout']",  # TODO: Update with logout link selector
        "profile": "a[href*='profile'], .user-menu",  # TODO: Update with profile link selector
    },
    
    # Common wait selectors (elements that indicate page is fully loaded)
    "wait_for": {
        "page_loaded": "body.loaded, .page-content, main",  # TODO: Update with selectors that indicate page is ready
        "form_ready": "form input:not([disabled])",  # TODO: Update with selectors that indicate form is interactive
        "ajax_complete": ":not(.loading)",  # TODO: Update with selectors that indicate AJAX operations are complete
    }
}

# Field mapping for dynamic form filling
# Maps record field names to selector keys
FIELD_MAPPING = {
    "firstName": "first_name",
    "lastName": "last_name", 
    "email": "email",
    "dob": "date_of_birth",
    "phone": "phone",
    "address": "address",
    "city": "city",
    "state": "state",
    "zipCode": "zip_code",
    "emergencyContactName": "emergency_contact_name",
    "emergencyContactPhone": "emergency_contact_phone",
}

# Timeout configurations for different operations
TIMEOUTS = {
    "navigation": 30000,  # 30 seconds for page navigation
    "element_wait": 10000,  # 10 seconds for element to appear
    "form_submission": 20000,  # 20 seconds for form submission
    "login": 15000,  # 15 seconds for login process
}

# Expected values for dropdown fields (if any)
# TODO: Update these with actual values from the website
DROPDOWN_VALUES = {
    "state": {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming"
    }
}