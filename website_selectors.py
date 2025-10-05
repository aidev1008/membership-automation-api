"""
CSS/XPath selectors for the Schmick Club web application.
Real Schmick website: app.schmickclub.com
"""

# Schmick Club website selectors - REAL WEBSITE
# Workflow:
# 1. Login at https://app.schmickclub.com/login
# 2. Fill form at https://app.schmickclub.com/memberships/distributors/add-member
# 3. Get ID from table at https://app.schmickclub.com/memberships/distributors/view-members

selectors = {
    # Login page selectors for Schmick Club
    "login": {
        "url": "https://app.schmickclub.com/memberships/distributors",
        "username": "#username, input[name='username'], input.form-control[type='text']",
        "password": "#password, input[name='password'], input.form-control[type='password']", 
        "submit": "#loginButton, button[type='button'].test, button:has-text('Login')",
        "post_login_indicator": "body, .dashboard, .user-menu, .container",
        # Error indicators
        "error_indicator": ".alert-danger, .error, .alert-error, .text-danger",
        "captcha_indicator": ".captcha, #captcha, [class*='captcha'], .recaptcha",
        "two_fa_indicator": ".two-factor, [class*='two-factor'], .mfa",
    },
    
    # Add member form selectors for Schmick Club
    "new_membership": {
        "url": "https://app.schmickclub.com/memberships/distributors/add-member",
        # Personal Information
        "business_name": "#businessName",
        "first_name": "#firstName", 
        "last_name": "#lastName",
        "email": "#email",
        "address": "#address",
        "city": "#city",
        "postal_address": "#postalAddress",
        "start_date": "#startDate",
        "state": "#state",
        "postcode": "#postcode",
        "mobile": "#mobile",
        "phone_ah": "#phoneAH",
        
        # Pre-existing damage radio buttons
        "pre_existing_damage_yes": "#yes",
        "pre_existing_damage_no": "#no",
        
        # Business Information
        "distributor_po_number": "#distributorPONumber",
        "distributor_reference": "#distributorReference",
        
        # Vehicle Information
        "car_type": "#car_type",
        "dealer_id": "#dealer_id", 
        "prd_id": "#prd_id",
        "veh_pay_opt": "#veh_pay_opt",
        "year": "#year",
        "make": "#make",
        "model": "#model",
        "rego": "#rego",
        "colour": "#colour",
        
        # Options
        "alloy_wheels": "#alloyWheels",
        "paint_protection": "#paintProtection", 
        "retail_fee": "#retailFee",
        
        # Form submission
        "submit": "button[type='submit'], input[type='submit'], .btn-primary, #addMember",
        "form_container": "#businessName, #firstName, form, .form-container, .add-member-form",
    },
    
    # Results page selectors - view members table
    "result": {
        "url": "https://app.schmickclub.com/memberships/distributors/view-members",
        # Get ID from first column, first row of table
        "membership_selector": "table tr:first-child td:first-child, table tbody tr:first-child td:first-child, .table tr:first-child td:first-child, .members-table tr:first-child td:first-child",
        "success_indicator": "table, .table, .members-table, .data-table",
        "error_indicator": ".alert-danger, .error, .alert-error, .text-danger",
        "loading_indicator": ".loading, .spinner, .processing, .loader",
        "table_container": "table, .table, .members-table, .data-table",
    },
    
    # Common navigation
    "navigation": {
        "home": "a[href='/'], .navbar-brand, .logo",
        "logout": "a[href*='logout'], button[class*='logout'], .logout",
        "view_members": "a[href*='view-members']",
        "add_member": "a[href*='add-member']",
    },
    
    # Wait indicators
    "wait_for": {
        "page_loaded": "body, .container, main, .content",
        "form_ready": "form, #addMember, .form-container",
        "table_ready": "table, .table, .members-table",
        "ajax_complete": ":not(.loading)",
    }
}

# Field mapping for dynamic form filling
# Maps record field names to selector keys for Schmick Club
FIELD_MAPPING = {
    "businessName": "business_name",
    "firstName": "first_name",
    "lastName": "last_name", 
    "email": "email",
    "address": "address",
    "city": "city",
    "postalAddress": "postal_address",
    "startDate": "start_date",
    "state": "state",
    "postcode": "postcode",
    "mobile": "mobile",
    "phoneAH": "phone_ah",
    "preExistingDamage": "pre_existing_damage",  # Special handling needed
    "distributorPONumber": "distributor_po_number",
    "distributorReference": "distributor_reference",
    "carType": "car_type",
    "dealerId": "dealer_id",
    "prdId": "prd_id",
    "vehPayOpt": "veh_pay_opt",
    "year": "year",
    "make": "make",
    "model": "model",
    "rego": "rego",
    "colour": "colour",
    "alloyWheels": "alloy_wheels",  # Checkbox
    "paintProtection": "paint_protection",  # Checkbox
    "retailFee": "retail_fee",
}

# Timeout configurations for different operations
TIMEOUTS = {
    "navigation": 60000,  # 60 seconds for page navigation
    "element_wait": 30000,  # 30 seconds for element to appear
    "form_submission": 45000,  # 45 seconds for form submission
    "login": 30000,  # 30 seconds for login process
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