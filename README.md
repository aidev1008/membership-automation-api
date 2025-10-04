# ACT Strategic Fix My Ads Service

A robust Python FastAPI microservice that uses Playwright to automate the ACT Strategic "Fix My Ads" workflow. The service logs into actstrategic.ai, fills out forms, and extracts submission IDs from result tables.

## Features

- **Asynchronous Processing**: Uses Playwright async API for efficient browser automation
- **Concurrent Request Handling**: Configurable concurrency limits with semaphore-based queuing
- **Session Persistence**: Saves browser cookies/localStorage to `state.json` for login reuse
- **Structured Logging**: JSON-formatted logs for production monitoring
- **Robust Error Handling**: Comprehensive error handling with retry logic
- **Security**: API key authentication and input validation
- **Docker Support**: Production-ready containerization

## Quick Start

### Local Development Setup

1. **Clone and setup environment**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install Playwright browsers
   python -m playwright install chromium
   ```

2. **Configure environment**:
   ```bash
   # Copy example configuration
   cp .env.example .env
   
   # Edit .env with your actual values
   nano .env
   ```

3. **Start the service**:
   ```bash
   # Using the convenience script
   ./start.sh
   
   # Or manually
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Verify it's running**:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"ok": true}
   ```

## Configuration

Configure the service using environment variables in your `.env` file:

```bash
# API Security
PLAYWRIGHT_API_KEY=your-secret-api-key-here

# ACT Strategic Login Credentials
SCHMICK_USER=amandeep.ai
SCHMICK_PASS=Byte#@123

# Browser Configuration
HEADLESS=true          # Set to false to see browser in action
TIMEOUT_MS=30000       # Request timeout in milliseconds

# Server Configuration
PORT=8000
MAX_CONCURRENCY=2      # Number of concurrent browser sessions

# Storage Configuration
STORAGE_STATE_FILE=state.json
```

## API Usage

### Health Check
```bash
curl -X GET http://localhost:8000/health
```

### Process Membership
```bash
curl -X POST http://localhost:8000/process \
  -H "x-api-key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "salesforceId": "SF123456",
    "firstName": "John",
    "lastName": "Doe", 
    "email": "john.doe@example.com",
    "dob": "1990-01-01",
    "phone": "555-0123",
    "address": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zipCode": "12345",
    "emergencyContactName": "Jane Doe",
    "emergencyContactPhone": "555-0124"
  }'
```

**Success Response**:
```json
{
  "result": "success",
  "membership": "SCH-123456789"
}
```

**Error Response**:
```json
{
  "result": "error", 
  "message": "Login failed - check credentials"
}
```

### Authentication

Use either header format:
- `x-api-key: your-api-key`
- `Authorization: Bearer your-api-key`

## Development

### Debugging Mode

Run with visible browser for debugging:
```bash
# Set in .env
HEADLESS=false

# Or set inline
HEADLESS=false uvicorn app:app --reload
```

### Running Tests

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app
```

### Manual Testing Commands

```bash
# Health check
curl -X GET http://localhost:8000/health

# Minimal membership record
curl -X POST http://localhost:8000/process \
  -H "x-api-key: test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "salesforceId": "SF123",
    "firstName": "Test",
    "lastName": "User",
    "email": "test@example.com",
    "dob": "1990-01-01"
  }'

# Full membership record
curl -X POST http://localhost:8000/process \
  -H "Authorization: Bearer test-key" \
  -H "Content-Type: application/json" \
  -d @test-record.json  # Use a JSON file for complex records
```

## Docker Deployment

### Build and Run

```bash
# Build image
docker build -t schmick-service .

# Run container
docker run -d \
  --name schmick-service \
  -p 8000:8000 \
  -e PLAYWRIGHT_API_KEY=your-api-key \
  -e SCHMICK_USER=your-username \
  -e SCHMICK_PASS=your-password \
  -v $(pwd)/data:/app/data \
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
      - PLAYWRIGHT_API_KEY=${PLAYWRIGHT_API_KEY}
      - SCHMICK_USER=${SCHMICK_USER}
      - SCHMICK_PASS=${SCHMICK_PASS}
      - HEADLESS=true
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

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

## Troubleshooting

### Common Issues

1. **"API key not configured"**
   - Check `PLAYWRIGHT_API_KEY` in environment

2. **"Login timeout"**
   - Verify `SCHMICK_USER` and `SCHMICK_PASS`
   - Check if Schmick site is accessible
   - Increase `TIMEOUT_MS`

3. **"Selector not found"**
   - Website structure changed
   - Update selectors in `selectors.py`
   - Run in headful mode to debug

4. **"CAPTCHA detected"**
   - Manual login required
   - Delete `state.json` and retry
   - Consider using different credentials

### Debug Steps

1. **Enable headful mode**: `HEADLESS=false`
2. **Check logs**: Look for structured log events
3. **Verify selectors**: Use browser dev tools
4. **Test manually**: Navigate the site manually first
5. **Clear state**: Delete `state.json` to force fresh login

## Security Considerations

- Store API keys securely (use secrets management in production)
- Rotate credentials regularly
- Monitor for unusual activity
- Use HTTPS in production
- Implement rate limiting if needed
- Keep Playwright and dependencies updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Update documentation
5. Submit a pull request

## License

[Add your license information here]