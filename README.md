# Schmick Club Membership Automation Service

A robust Python FastAPI microservice that uses Playwright to automate Schmick Club membership form submissions. The service logs into app.schmickclub.com, fills out distributor membership forms with comprehensive validation, and provides detailed logging for request tracking.

## Features

- **Automated Form Filling**: Complete automation of Schmick Club distributor membership forms
- **Enhanced Logging**: Comprehensive request tracking and validation error logging with user data context
- **Session Management**: Persistent browser state for efficient login reuse
- **Field Validation**: Full support for all 26+ required membership fields including postal address and start date
- **Error Tracking**: Detailed validation error logging for debugging and troubleshooting
- **Railway Cloud Ready**: Configured for Railway.app cloud deployment
- **Security First**: Comprehensive gitignore protection for sensitive data

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.9+** (recommended: Python 3.11)
- **Git** for cloning the repository
- **Schmick Club credentials** (username and password)

### 1. Clone and Setup Repository

```bash
# Clone the repository
git clone https://github.com/aidev1008/service.git
cd service

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Install Playwright Firefox browser (required for Schmick Club)
playwright install firefox
```

### 2. Create Required Environment File

**⚠️ CRITICAL:** You must create a `.env` file with your credentials:

```bash
# Create .env file in the project root
touch .env

# Add the following content to .env (replace with your actual credentials):
SCHMICK_USER=your_schmick_username
SCHMICK_PASS=your_schmick_password
ENVIRONMENT=development
PORT=8000
HEADLESS=true
```

**Example `.env` file:**
```bash
SCHMICK_USER=your_email@example.com
SCHMICK_PASS=your_secure_password
ENVIRONMENT=development
PORT=8000
HEADLESS=true
```

### 3. Create Required Directories

```bash
# Create necessary directories that are ignored by git
mkdir -p logs
mkdir -p screenshots
mkdir -p browser-cache
mkdir -p .playwright

# Create empty state files
touch state.json
touch extracted_id.txt
```

### 4. Start the Service

```bash
# Option 1: Using the start script
chmod +x start.sh
./start.sh

# Option 2: Direct uvicorn command
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using Python directly
python start_server.py
```

### 5. Verify Installation

```bash
# Test the health endpoint
curl http://localhost:8000/

# You should see: {"message": "Schmick Club Automation Service", "status": "running"}
```

## 📋 Complete Setup Checklist

- [ ] Python 3.9+ installed
- [ ] Repository cloned
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright Firefox installed (`playwright install firefox`)
- [ ] `.env` file created with your credentials
- [ ] Required directories created (`logs/`, `screenshots/`, etc.)
- [ ] Service starts without errors
- [ ] Health endpoint responds correctly

## 🔧 Configuration

### Environment Variables (`.env` file)

```bash
# Schmick Club Credentials (REQUIRED)
SCHMICK_USER=your_email@example.com
SCHMICK_PASS=your_secure_password

# Application Configuration
ENVIRONMENT=development     # Options: development, production
PORT=8000                  # Port for the FastAPI server
HEADLESS=true             # Set to false to see browser during automation

# Browser Configuration (Optional)
TIMEOUT_MS=30000          # Browser timeout in milliseconds
MAX_RETRIES=3             # Number of retry attempts for failed operations
```

### Important Files and Directories

- `.env` - Your credentials (NEVER commit this to git)
- `logs/` - Application logs and request tracking
- `state.json` - Browser session state (auto-generated)
- `screenshots/` - Debug screenshots (auto-generated)
- `extracted_id.txt` - Extracted membership IDs (auto-generated)

## 📊 Logging and Monitoring

The service provides comprehensive logging:

- **Request Log** (`logs/requests.log`) - Every user request with timestamps
- **Validation Errors** (`logs/validation_errors.log`) - Detailed error context with user data
- **Application Log** (`logs/schmick_service.log`) - General application events

### Log File Examples:

```json
// Request Log Entry
{
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456",
  "endpoint": "/submit-membership",
  "business_name": "Test Business Ltd",
  "status": "started"
}

// Validation Error Entry
{
  "timestamp": "2024-01-15T10:30:15Z", 
  "request_id": "req_123456",
  "error_type": "validation_error",
  "field": "postalAddress",
  "user_data": {...},
  "error_message": "Field not found on page"
}
```

## 🔗 API Usage

### Health Check
```bash
curl -X GET http://localhost:8000/
```
**Response:**
```json
{
  "message": "Schmick Club Automation Service",
  "status": "running"
}
```

### Submit Membership Form
```bash
curl -X POST http://localhost:8000/submit-membership \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Test Business Ltd",
    "abn": "12345678901",
    "businessAddress": "123 Business Street, Sydney NSW 2000",
    "postalAddress": "PO Box 123, Sydney NSW 2000",
    "businessPhone": "0412345678",
    "businessEmail": "contact@testbusiness.com.au",
    "website": "https://testbusiness.com.au",
    "businessType": "Sole Trader",
    "industryType": "Technology",
    "businessDescription": "Technology consulting services",
    "yearsInBusiness": "5",
    "numberOfEmployees": "10",
    "annualTurnover": "$500,000 - $1M",
    "currentInsurer": "Insurance Company Ltd",
    "currentPremium": "$5000",
    "claimsHistory": "No claims in last 5 years",
    "contactPerson": "John Smith",
    "contactPhone": "0412345678",
    "contactEmail": "john@testbusiness.com.au",
    "startDate": "2024-02-01",
    "additionalInfo": "Additional business information",
    "hearAboutUs": "Online Search",
    "newsletter": true,
    "terms": true
  }'
```

**Success Response:**
```json
{
  "status": "success",
  "message": "Membership form submitted successfully",
  "request_id": "req_123456789",
  "extracted_id": "15",
  "submission_time": "2024-01-15T10:30:45Z"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Login failed - please check credentials",
  "request_id": "req_123456789",
  "error_details": "Invalid username or password"
}
```

### Required Fields

All membership submissions must include these **mandatory fields**:

- `businessName` - Name of the business
- `abn` - Australian Business Number
- `businessAddress` - Physical business address
- `postalAddress` - Postal address (can be same as business address)
- `businessPhone` - Business contact phone
- `businessEmail` - Business contact email
- `businessType` - Type of business entity
- `contactPerson` - Primary contact person name
- `contactPhone` - Contact person phone
- `contactEmail` - Contact person email
- `startDate` - Membership start date (YYYY-MM-DD format)
- `terms` - Must be `true` to accept terms and conditions

## 🔧 Development and Debugging

### Debugging Mode

Run with visible browser for debugging:
```bash
# Set in .env file
HEADLESS=false

# Or run with environment variable
HEADLESS=false uvicorn app:app --reload --port 8000
```

### Running Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio httpx

# Run specific test files
python simple_test.py
python tests/test_service.py

# Run all tests in tests directory
pytest tests/ -v

# Test the unified flow manually
python unified_flow.py
```

### Testing the Automation Flow Locally

**🎯 Direct Flow Testing (Recommended for Development)**

Test the complete Schmick Club automation flow without the API server:

```bash
# Method 1: Run the unified flow directly
python unified_flow.py

# Method 2: Test with visible browser (for debugging)
HEADLESS=false python unified_flow.py

# Method 3: Test specific scenarios
python simple_test.py
```

The `unified_flow.py` script will:
1. 🔐 Log into Schmick Club using your `.env` credentials
2. 📝 Fill out the membership form with test data
3. ✅ Submit the form and extract the membership ID
4. 📊 Generate comprehensive logs for analysis

**Sample Output:**
```
🚀 Starting Schmick Club membership automation...
   📝 Request logged with ID: req_1a2b3c4d
   🌐 Navigating to: https://app.schmickclub.com/memberships/distributors
   🔐 Attempting login...
   ✅ Login successful
   📝 Filling membership form...
   ✅ Form submitted successfully
   🆔 Extracted ID: 15
   ✅ Automation completed successfully
```

**🖥️ API Server Testing**

Test through the FastAPI server (useful for integration testing):

```bash
# Start the server first
uvicorn app:app --reload --port 8000

# In another terminal, test the API
curl -X GET http://localhost:8000/

# Test with minimal required fields
curl -X POST http://localhost:8000/submit-membership \
  -H "Content-Type: application/json" \
  -d '{
    "businessName": "Test Business",
    "abn": "12345678901",
    "businessAddress": "123 Test St, Sydney NSW 2000",
    "postalAddress": "123 Test St, Sydney NSW 2000", 
    "businessPhone": "0412345678",
    "businessEmail": "test@test.com",
    "businessType": "Sole Trader",
    "contactPerson": "Test User",
    "contactPhone": "0412345678",
    "contactEmail": "test@test.com",
    "startDate": "2024-02-01",
    "terms": true
  }'

# Test Railway deployment (if deployed)
./test_railway_curl.sh
```

**📊 Advanced Testing Options**

```bash
# Test with comprehensive data
python tests/test_service.py

# Test different business types
python tests/workflow_test.py

# Debug form filling issues
HEADLESS=false python tests/robust_test.py

# Quick validation test
python tests/quick_test.py
```

**🎯 Customizing Test Data**

The `unified_flow.py` script uses built-in test data. To customize it, edit the script or create your own test file:

```python
# Example: Create custom_test.py
import asyncio
from unified_flow import process_membership

# Your custom test data
test_data = {
    "businessName": "Your Test Business",
    "abn": "12345678901",
    "businessAddress": "Your Test Address",
    "postalAddress": "Your Test Postal Address", 
    "businessPhone": "0412345678",
    "businessEmail": "your-test@email.com",
    "businessType": "Company",  # Options: Sole Trader, Company, Partnership
    "contactPerson": "Your Name",
    "contactPhone": "0412345678", 
    "contactEmail": "your-test@email.com",
    "startDate": "2024-02-01",
    "terms": True
}

# Run the automation
result = asyncio.run(process_membership(test_data))
print(f"Result: {result}")
```

**🔍 Testing Different Scenarios**

```bash
# Test with invalid data (to see validation errors)
python tests/test_validation_errors.py

# Test with different business types
# Edit unified_flow.py and change businessType to:
# - "Sole Trader"
# - "Company" 
# - "Partnership"
# - "Trust"

# Test with minimal vs complete data
python tests/minimal_data_test.py
python tests/complete_data_test.py
```

### Log Analysis and Monitoring

Monitor logs in real-time during testing:
```bash
# Watch request logs (created by unified_flow.py)
tail -f requests.log

# Watch validation errors with user context
tail -f validation_errors.log

# Watch main application log (FastAPI server)
tail -f logs/schmick_service.log

# Watch all logs simultaneously
tail -f requests.log validation_errors.log logs/*.log
```

**Understanding Log Output:**

When you run `python unified_flow.py`, you'll see logs created in:
- `requests.log` - Every automation request with user data
- `validation_errors.log` - Form validation issues with full context
- Console output - Real-time progress and results

**Sample Log Entries:**
```bash
# requests.log
[2024-01-15T10:30:00] REQUEST_ID: req_1a2b3c4d
USER DATA: {
  "businessName": "Test Business Ltd",
  "abn": "12345678901",
  ...
}

# Console output during unified_flow.py execution
🚀 Starting Schmick Club membership automation...
   📝 Request logged with ID: req_1a2b3c4d
   🔐 Attempting login...
   ✅ Login successful
   📝 Filling membership form...
   ✅ Form submitted successfully
   🆔 Extracted ID: 15
```

## ☁️ Cloud Deployment

### Railway.app Deployment

The service is configured for Railway cloud deployment:

```bash
# Deploy to Railway (requires Railway CLI)
railway login
railway link
railway up

# Test Railway deployment
./test_railway_curl.sh
```

**Railway Environment Variables:**
Set these in your Railway dashboard:
- `SCHMICK_USER` - Your Schmick Club username
- `SCHMICK_PASS` - Your Schmick Club password  
- `ENVIRONMENT` - Set to `production`
- `HEADLESS` - Set to `true`

### Docker Deployment

```bash
# Build image
docker build -t schmick-service .

# Run container
docker run -d \
  --name schmick-service \
  -p 8000:8000 \
  -e SCHMICK_USER=your-username \
  -e SCHMICK_PASS=your-password \
  -e HEADLESS=true \
  -v $(pwd)/logs:/app/logs \
  schmick-service
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  schmick-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SCHMICK_USER=${SCHMICK_USER}
      - SCHMICK_PASS=${SCHMICK_PASS}
      - HEADLESS=true
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

### Important Notes for Cloud Deployment

⚠️ **Geo-blocking Consideration**: Schmick Club may have geo-blocking that prevents access from non-Australian IP addresses. If you encounter issues with cloud deployments, consider using an Australian-based hosting provider.

## Customization

### Updating Selectors

The service uses CSS/XPath selectors defined in `selectors.py`. Update these to match the actual Schmick website:

```python
# In selectors.py - update these placeholders
selectors = {
    "login": {
        "url": "https://actual-schmick-url.com/login",
        "username": "input[name='actual-username-field']",
        "password": "input[name='actual-password-field']",
        # ... more selectors
    }
}
```

### Adding Custom Fields

1. Add field to `MembershipRecord` model in `app.py`
2. Add selector to `selectors.py` 
3. Add field mapping in `FIELD_MAPPING`

### Error Handling

The service provides detailed error messages for common issues:
- **Login failures**: Check credentials and site availability
- **CAPTCHA detected**: Manual intervention required
- **Selector not found**: Website structure may have changed
- **Timeout errors**: Increase `TIMEOUT_MS` or check network

## Monitoring

### Structured Logging

All operations are logged in JSON format:
```json
{
  "timestamp": "2023-01-01T12:00:00Z",
  "level": "INFO", 
  "event": "form_fill",
  "message": "Filled firstName field",
  "request_id": "uuid-here",
  "salesforce_id": "SF123456"
}
```

### Health Monitoring

Monitor the `/health` endpoint and check for:
- Browser process health
- Storage state validity
- Environment configuration

### Performance Metrics

Key metrics to monitor:
- Request processing time
- Success/failure rates
- Concurrent request count
- Browser memory usage

## 🚨 Troubleshooting

### Setup Issues

1. **Missing `.env` file**
   ```bash
   # Error: "SCHMICK_USER environment variable not set"
   # Solution: Create .env file with your credentials
   touch .env
   echo "SCHMICK_USER=your_username" >> .env
   echo "SCHMICK_PASS=your_password" >> .env
   ```

2. **Missing directories**
   ```bash
   # Error: "Permission denied" or "Directory not found"
   # Solution: Create required directories
   mkdir -p logs screenshots browser-cache .playwright
   ```

3. **Playwright browser not installed**
   ```bash
   # Error: "firefox not found"
   # Solution: Install Firefox browser
   playwright install firefox
   ```

### Unified Flow Testing Issues

1. **unified_flow.py fails to start**
   ```bash
   # Error: "ModuleNotFoundError: No module named 'playwright'"
   # Solution: Ensure virtual environment is activated and dependencies installed
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Error: "SCHMICK_USER not found"
   # Solution: Check .env file exists and has correct format
   cat .env
   ```

2. **Browser automation issues**
   ```bash
   # Error: "Login failed" or "Timeout"
   # Solution: Run with visible browser to debug
   HEADLESS=false python unified_flow.py
   
   # Check if credentials are correct
   # Verify Schmick Club site is accessible manually
   ```

3. **Form filling failures**
   ```bash
   # Error: "Selector not found" or "Element not found"
   # Solution: Website structure may have changed
   # Run with visible browser and check the form
   HEADLESS=false python unified_flow.py
   
   # Check validation_errors.log for specific field issues
   tail validation_errors.log
   ```

4. **No output or logs**
   ```bash
   # Issue: Script runs but no visible results
   # Solution: Check console output and log files
   python unified_flow.py > test_output.log 2>&1
   cat test_output.log
   
   # Check if log files are created
   ls -la *.log
   ```

### Runtime Issues

1. **Login failures**
   - Verify credentials in `.env` file
   - Check if Schmick Club site is accessible
   - Delete `state.json` to force fresh login
   - Run with `HEADLESS=false` to see what's happening

2. **Form submission errors**
   - Check `logs/validation_errors.log` for detailed error context
   - Verify all required fields are provided
   - Ensure field values meet Schmick Club requirements

3. **Selector not found errors**
   - Website structure may have changed
   - Update selectors in `website_selectors.py`
   - Run in headful mode (`HEADLESS=false`) to debug

4. **Timeout errors**
   - Increase `TIMEOUT_MS` in `.env`
   - Check internet connection
   - Verify Schmick Club site is responsive

### Debug Steps

1. **Enable visible browser**: Set `HEADLESS=false` in `.env`
2. **Check logs**: Monitor `logs/` directory for detailed error information
3. **Test manually**: Navigate to Schmick Club site manually first
4. **Clear cache**: Delete `state.json`, `extracted_id.txt` and restart
5. **Verify selectors**: Use browser developer tools to check HTML elements

### Log Analysis

```bash
# Check recent errors
tail -20 logs/validation_errors.log

# Monitor real-time activity  
tail -f logs/schmick_service.log

# Search for specific errors
grep "ERROR" logs/*.log
```

## 🔐 Security Best Practices

- **Never commit `.env` files** - They contain sensitive credentials
- **Rotate credentials regularly** - Change passwords periodically
- **Monitor access logs** - Check for unusual activity patterns
- **Use HTTPS in production** - Ensure encrypted communication
- **Keep dependencies updated** - Regularly update Python packages
- **Implement rate limiting** - Prevent abuse in production environments
- **Use environment-specific configs** - Separate dev/staging/production settings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Standards

- Follow PEP 8 Python style guidelines
- Add docstrings to functions and classes
- Include tests for new features
- Update README.md for significant changes
- Ensure all tests pass before submitting PR

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

If you encounter issues during setup or deployment:

1. **Check this README** - Most common issues are covered here
2. **Review the logs** - Check `logs/` directory for detailed error information  
3. **Test manually** - Try accessing Schmick Club site manually first
4. **Create an issue** - If problems persist, create a GitHub issue with:
   - Error messages from logs
   - Steps to reproduce the issue  
   - Your environment details (OS, Python version, etc.)

**Remember**: Never include your actual credentials (usernames, passwords) in issue reports!