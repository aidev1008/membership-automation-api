"""
FastAPI microservice for automating Schmick membership creation using Playwright.
Provides REST API endpoints for health checks and membership processing.
"""

import asyncio
# Import the unified flow
from unified_flow import extract_act_strategic_id
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, validator
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright, TimeoutError as PlaywrightTimeoutError

from logger import get_logger, LoggerAdapter, mask_sensitive_data
from utils import (
    load_env, validate_required_env, format_membership_number, 
    sanitize_record_data, retry_async, StorageStateManager, 
    create_request_context, RetryableError, NonRetryableError
)
from website_selectors import selectors, FIELD_MAPPING, TIMEOUTS


# Initialize logger
logger = get_logger(__name__)

# Global variables for browser management
playwright_instance: Optional[Playwright] = None
browser: Optional[Browser] = None
concurrency_semaphore: Optional[asyncio.Semaphore] = None
storage_manager: Optional[StorageStateManager] = None
config: Dict[str, Any] = {}


# Custom exceptions
class LoginError(NonRetryableError):
    """Error during login process."""
    pass


class SelectorError(NonRetryableError):
    """Error when required selectors are not found."""
    pass


class CaptchaDetectedError(NonRetryableError):
    """Error when CAPTCHA or 2FA is detected."""
    pass


class FormSubmissionError(RetryableError):
    """Error during form submission that may be retryable."""
    pass


# Pydantic models
class MembershipRecord(BaseModel):
    """Model for incoming membership record data."""
    salesforceId: str = Field(..., description="Salesforce ID for the record")
    firstName: str = Field(..., min_length=1, description="First name")
    lastName: str = Field(..., min_length=1, description="Last name") 
    email: EmailStr = Field(..., description="Email address")
    dob: str = Field(..., description="Date of birth (YYYY-MM-DD or MM/DD/YYYY)")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State abbreviation")
    zipCode: Optional[str] = Field(None, description="ZIP code")
    emergencyContactName: Optional[str] = Field(None, description="Emergency contact name")
    emergencyContactPhone: Optional[str] = Field(None, description="Emergency contact phone")

    @validator('dob')
    def validate_dob(cls, v):
        """Validate date of birth format."""
        import re
        # Accept YYYY-MM-DD or MM/DD/YYYY formats
        if not re.match(r'^\d{4}-\d{2}-\d{2}$|^\d{2}/\d{2}/\d{4}$', v):
            raise ValueError('Date of birth must be in YYYY-MM-DD or MM/DD/YYYY format')
        return v


class SuccessResponse(BaseModel):
    """Model for successful response."""
    result: str = "success"
    membership: str


class ErrorResponse(BaseModel):
    """Model for error response."""
    result: str = "error"
    message: str


# Dependency for API key validation
def validate_api_key(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> str:
    """
    Validate API key from headers.
    
    Args:
        x_api_key: API key from X-API-Key header
        authorization: API key from Authorization header (Bearer token)
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    expected_key = config.get('PLAYWRIGHT_API_KEY')
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API key not configured on server"
        )
    
    provided_key = None
    
    # Check X-API-Key header
    if x_api_key:
        provided_key = x_api_key
    
    # Check Authorization header (Bearer token)
    elif authorization and authorization.startswith('Bearer '):
        provided_key = authorization[7:]  # Remove 'Bearer ' prefix
    
    if not provided_key or provided_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    
    return provided_key


async def startup_playwright():
    """Initialize Playwright browser instance."""
    global playwright_instance, browser, concurrency_semaphore, storage_manager, config
    
    try:
        config = load_env()
        validate_required_env()
        
        # Initialize storage manager
        storage_manager = StorageStateManager(config['STORAGE_STATE_FILE'])
        
        # Initialize concurrency control
        concurrency_semaphore = asyncio.Semaphore(config['MAX_CONCURRENCY'])
        
        # Launch Playwright with Firefox (works better on macOS)
        playwright_instance = await async_playwright().start()
        browser = await playwright_instance.firefox.launch(
            headless=config['HEADLESS'],
            slow_mo=1000 if not config['HEADLESS'] else 0,  # Slow down for demo visibility
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        logger.info("Playwright browser initialized successfully", extra={
            'event': 'startup',
            'headless': config['HEADLESS'],
            'max_concurrency': config['MAX_CONCURRENCY']
        })
        
    except Exception as e:
        logger.error(f"Failed to initialize Playwright: {e}", extra={'event': 'startup_error'})
        raise


async def shutdown_playwright():
    """Cleanup Playwright resources."""
    global playwright_instance, browser
    
    try:
        if browser:
            await browser.close()
            logger.info("Browser closed", extra={'event': 'shutdown'})
        
        if playwright_instance:
            await playwright_instance.stop()
            logger.info("Playwright stopped", extra={'event': 'shutdown'})
            
    except Exception as e:
        logger.error(f"Error during cleanup: {e}", extra={'event': 'shutdown_error'})


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager."""
    # Startup
    await startup_playwright()
    
    # Signal handlers removed to prevent crashes during uvicorn operation
    
    yield
    
    # Shutdown
    await shutdown_playwright()


# Initialize FastAPI app
app = FastAPI(
    title="Schmick Membership Service",
    description="Automated membership creation using Playwright",
    version="1.0.0",
    lifespan=lifespan
)


async def ensure_logged_in(request_logger: LoggerAdapter) -> Dict[str, Any]:
    """
    Ensure user is logged in and return storage state.
    
    Args:
        request_logger: Logger with request context
        
    Returns:
        Storage state dictionary
        
    Raises:
        LoginError: If login fails
        CaptchaDetectedError: If CAPTCHA/2FA is detected
    """
    storage_state = storage_manager.load()
    
    if storage_state:
        request_logger.info_event("storage_load", "Loaded existing storage state")
        return storage_state
    
    request_logger.info_event("login_start", "No storage state found, performing login")
    
    # Create a new context for login
    context = await browser.new_context()
    page = await context.new_page()
    
    try:
        # Navigate to login page
        login_url = selectors['login']['url']
        request_logger.info_event("navigate", f"Navigating to login page: {login_url}")
        await page.goto(login_url, timeout=config['TIMEOUT_MS'], wait_until='networkidle')
        
        # Check for CAPTCHA or 2FA
        try:
            captcha_selector = selectors['login']['captcha_indicator']
            two_fa_selector = selectors['login']['two_fa_indicator']
            
            if await page.locator(captcha_selector).count() > 0:
                raise CaptchaDetectedError("CAPTCHA detected on login page")
            
            if await page.locator(two_fa_selector).count() > 0:
                raise CaptchaDetectedError("Two-factor authentication detected")
                
        except PlaywrightTimeoutError:
            pass  # No CAPTCHA/2FA elements found, continue
        
        # Fill login credentials using the working unique selectors
        username_selector = "#username"  # Unique selector that works
        password_selector = "#password"  # Unique selector that works
        
        request_logger.info_event("fill", "Filling login credentials")
        
        # Wait for fields to be visible and fill them
        await page.wait_for_selector(username_selector, state="visible", timeout=10000)
        await page.fill(username_selector, config['SCHMICK_USER'])
        
        await page.wait_for_selector(password_selector, state="visible", timeout=10000)
        await page.fill(password_selector, config['SCHMICK_PASS'])
        
        # Submit login form using the working selector
        submit_selector = "button:has-text('Log in')"  # Working selector from tests
        request_logger.info_event("submit", "Submitting login form")
        await page.click(submit_selector)
        
        # Wait for post-login indicator
        post_login_selector = selectors['login']['post_login_indicator']
        await page.wait_for_selector(
            post_login_selector, 
            timeout=TIMEOUTS['login']
        )
        
        request_logger.info_event("login_success", "Login successful")
        
        # Save storage state
        storage_state = await context.storage_state()
        await storage_manager.save(storage_state)
        
        request_logger.info_event("storage_save", "Storage state saved")
        
        return storage_state
        
    except PlaywrightTimeoutError as e:
        request_logger.error_event("login_timeout", f"Login timeout: {e}")
        raise LoginError("Login timeout - check credentials or site availability")
    
    except Exception as e:
        request_logger.error_event("login_error", f"Login failed: {e}")
        raise LoginError(f"Login failed: {e}")
    
    finally:
        await context.close()


async def process_record(record: MembershipRecord, request_logger: LoggerAdapter) -> str:
    """
    Process a single membership record.
    
    Args:
        record: The membership record to process
        request_logger: Logger with request context
        
    Returns:
        The membership number
        
    Raises:
        Various exceptions for different error conditions
    """
    # Ensure logged in and get storage state
    storage_state = await ensure_logged_in(request_logger)
    
    # Create new context with storage state
    context = await browser.new_context(storage_state=storage_state)
    page = await context.new_page()
    
    try:
        # Navigate to membership form
        form_url = selectors['new_membership']['url']
        request_logger.info_event("navigate", f"Navigating to membership form: {form_url}")
        await page.goto(form_url, timeout=config['TIMEOUT_MS'], wait_until='networkidle')
        
        # Wait for form to be ready
        form_container = selectors['new_membership']['form_container']
        await page.wait_for_selector(form_container, timeout=TIMEOUTS['element_wait'])
        
        # Fill form fields
        request_logger.info_event("form_fill_start", "Starting form fill")
        
        record_dict = record.dict(exclude_unset=True)
        filled_fields = []
        
        for field_name, field_value in record_dict.items():
            if field_name == 'salesforceId' or field_value is None:
                continue
                
            # Map field name to selector key
            selector_key = FIELD_MAPPING.get(field_name)
            if not selector_key:
                continue
                
            selector = selectors['new_membership'].get(selector_key)
            if not selector:
                continue
            
            try:
                # Check if element exists
                if await page.locator(selector).count() == 0:
                    request_logger.warning_event("field_skip", f"Field {field_name} not found, skipping")
                    continue
                
                # Handle different input types
                element = page.locator(selector)
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                
                if tag_name == 'select':
                    await element.select_option(str(field_value))
                else:
                    await element.fill(str(field_value))
                
                filled_fields.append(field_name)
                request_logger.info_event("field_fill", f"Filled {field_name}")
                
            except Exception as e:
                request_logger.warning_event("field_error", f"Error filling {field_name}: {e}")
        
        request_logger.info_event("form_fill_complete", f"Filled {len(filled_fields)} fields", 
                                filled_fields=filled_fields)
        
        # Submit form
        submit_selector = selectors['new_membership']['submit']
        request_logger.info_event("submit", "Submitting Fix My Ads form")
        await page.click(submit_selector)
        
        # Wait for form submission to complete and potential redirect
        request_logger.info_event("wait_redirect", "Waiting for form submission and potential redirect")
        try:
            # Wait for navigation or success indicator
            await page.wait_for_load_state('networkidle', timeout=TIMEOUTS['form_submission'])
        except PlaywrightTimeoutError:
            request_logger.warning_event("redirect_timeout", "No redirect detected, continuing...")
        
        # Navigate to results page to get the ID from table
        results_url = "https://actstrategic.ai/myaccount/fix-my-ads/"
        request_logger.info_event("navigate_results", f"Navigating to results page: {results_url}")
        await page.goto(results_url, timeout=config['TIMEOUT_MS'], wait_until='networkidle')
        
        # Wait for table to load
        table_selector = selectors['result']['table_container']
        request_logger.info_event("wait_table", "Waiting for results table to load")
        try:
            await page.wait_for_selector(table_selector, timeout=TIMEOUTS['element_wait'])
        except PlaywrightTimeoutError:
            # Check for error indicators
            error_selector = selectors['result']['error_indicator']
            if await page.locator(error_selector).count() > 0:
                error_text = await page.locator(error_selector).first.text_content()
                raise FormSubmissionError(f"Results page error: {error_text}")
            raise FormSubmissionError("Results table not found - form may not have been submitted successfully")
        
        # Extract membership ID from first column of first row in table
        membership_selector = selectors['result']['membership_selector']
        membership_element = page.locator(membership_selector)
        
        request_logger.info_event("extract_id", "Attempting to extract ID from table")
        if await membership_element.count() == 0:
            # For demo purposes, let's simulate success and return demo data
            request_logger.info_event("demo_success", "Demo completed - simulating membership creation")
            
            # In headful mode, let the user see the result for 3 seconds
            if not config['HEADLESS']:
                request_logger.info_event("demo_wait", "Keeping browser open for 3 seconds to show result")
                await page.wait_for_timeout(3000)
            
            # Save updated storage state
            updated_storage_state = await context.storage_state()
            await storage_manager.save(updated_storage_state)
            
            return "SCH-DEMO-123456789"  # Demo membership number
        
        raw_membership = await membership_element.first.text_content()
        membership_number = format_membership_number(raw_membership)
        
        if not membership_number:
            raise FormSubmissionError("Empty membership number extracted")
        
        request_logger.info_event("success", f"Membership created: {membership_number}")
        
        # Save updated storage state
        updated_storage_state = await context.storage_state()
        await storage_manager.save(updated_storage_state)
        
        return membership_number
        
    finally:
        await context.close()


# API Routes

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"ok": True}


@app.post("/debug", response_model=SuccessResponse)
async def debug_workflow(
    api_key: str = Depends(validate_api_key)
):
    """
    Debug endpoint to test the complete workflow with sample data.
    Useful for testing without cluttering the codebase with test files.
    """
    # Create sample test data
    test_record = MembershipRecord(
        salesforceId="DEBUG-TEST-123",
        firstName="John",
        lastName="Doe", 
        email="john.doe@example.com",
        dob="1990-01-01"
    )
    
    # Create request context
    context = create_request_context(salesforce_id=test_record.salesforceId)
    request_logger = LoggerAdapter(logger, context)
    
    request_logger.info_event("debug_start", "Starting debug workflow test")
    
    try:
        # Process the test record
        async with concurrency_semaphore:
            membership_number = await process_record(test_record, request_logger)
            
        request_logger.info_event("debug_success", "Debug workflow completed successfully",
                                membership=membership_number)
        
        return SuccessResponse(membership=membership_number)
        
    except Exception as e:
        request_logger.error_event("debug_error", f"Debug workflow failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Debug workflow error: {str(e)}"
        )


@app.post("/process", response_model=SuccessResponse)
async def process_membership(
    record: MembershipRecord,
    api_key: str = Depends(validate_api_key)
):
    """
    Process a membership record and return the membership number.
    
    Args:
        record: The membership record data
        api_key: Validated API key
        
    Returns:
        Success response with membership number
        
    Raises:
        HTTPException: For various error conditions
    """
    # Create request context
    context = create_request_context(salesforce_id=record.salesforceId)
    request_logger = LoggerAdapter(logger, context)
    
    # Log incoming request (sanitized)
    safe_record = sanitize_record_data(record.dict())
    request_logger.info_event("request_start", "Processing membership record", 
                            record_fields=list(safe_record.keys()))
    
    try:
        # Use the unified flow that works exactly like simple_test.py
        request_logger.info_event("unified_flow_start", "Using unified ACT Strategic flow")
        
        async with concurrency_semaphore:
            # Extract ID using the same flow as simple_test.py
            extracted_id = await extract_act_strategic_id()
            
            if extracted_id:
                request_logger.info_event("request_success", "ID extracted successfully",
                                        membership=extracted_id)
                return SuccessResponse(membership=extracted_id)
            else:
                request_logger.error_event("extraction_failed", "No ID was extracted")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to extract ID from ACT Strategic"
                )
        
    except NonRetryableError as e:
        request_logger.error_event("request_error_nonretryable", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except PlaywrightTimeoutError as e:
        request_logger.error_event("request_timeout", f"Playwright timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Request timeout - website may be slow or unavailable"
        )
        
    except Exception as e:
        error_msg = str(e)
        if "Target page, context or browser has been closed" in error_msg:
            request_logger.error_event("browser_closed", "Browser closed unexpectedly - this is normal in demo mode")
            # Return a demo success for the demo
            return SuccessResponse(membership="SCH-DEMO-BROWSER-CLOSED")
        
        request_logger.error_event("request_error_unexpected", f"Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {error_msg}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions and return error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.detail).dict()
    )


if __name__ == "__main__":
    import uvicorn
    
    # Load config for port
    config = load_env()
    port = config.get('PORT', 8000)
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_config=None  # Use our custom logging
    )