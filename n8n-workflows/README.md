# n8n Integration Guide for ACT Strategic Service

## 🚀 Quick Setup

### 1. Service Configuration
- **Service URL**: `http://localhost:8000`
- **API Key**: `test-demo-key-12345`
- **Endpoints**: 
  - `/health` - Health check
  - `/process` - Main automation (requires form data)
  - `/debug` - Test with sample data

### 2. n8n HTTP Request Node Settings

#### Method: POST
#### URL: `http://localhost:8000/process`

#### Headers:
```
x-api-key: test-demo-key-12345
Content-Type: application/json
```

#### Request Body (JSON):
```json
{
  "salesforceId": "{{ $json.salesforceId }}",
  "firstName": "{{ $json.firstName }}",
  "lastName": "{{ $json.lastName }}",
  "email": "{{ $json.email }}",
  "dob": "{{ $json.dob }}"
}
```

#### Expected Response:
```json
{
  "membership": "SCH-EXTRACTED-ID"
}
```

## 📋 Workflow Templates

### Template 1: Manual Trigger Workflow
1. **Manual Trigger** - Start workflow manually
2. **Set Node** - Sample data for testing
3. **HTTP Request** - Call ACT Strategic service
4. **Set Node** - Process the returned membership ID

### Template 2: Webhook Workflow  
1. **Webhook Trigger** - Receive data from external systems
2. **IF Node** - Validate required fields
3. **HTTP Request** - Call ACT Strategic service
4. **Respond to Webhook** - Return success/error response

## 🔧 Integration Examples

### From Salesforce (via webhook):
```
Salesforce → n8n Webhook → ACT Strategic Service → Response
```

### From Form Submission:
```
Web Form → n8n Webhook → Validation → ACT Strategic Service → Database
```

### From Spreadsheet:
```
Google Sheets → n8n Trigger → ACT Strategic Service → Update Sheet
```

## 🛠️ Testing

### Test with cURL:
```bash
curl -X POST http://localhost:8000/process \
  -H "x-api-key: test-demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "salesforceId": "TEST-123",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "dob": "1990-01-01"
  }'
```

### Test Debug Endpoint:
```bash
curl -X POST http://localhost:8000/debug \
  -H "x-api-key: test-demo-key-12345"
```

## 📝 Field Mapping

| n8n Field | Service Field | Required | Example |
|-----------|---------------|----------|---------|
| salesforceId | salesforceId | Yes | "SF-12345" |
| firstName | firstName | Yes | "John" |
| lastName | lastName | Yes | "Doe" |
| email | email | Yes | "john@example.com" |
| dob | dob | Yes | "1990-01-01" |

## ⚠️ Important Notes

1. **Service Must Be Running**: Ensure your FastAPI service is running on port 8000
2. **API Key**: Use the correct API key in headers
3. **Browser Visibility**: Set `HEADLESS=false` in .env to see browser automation
4. **Timeout**: Set appropriate timeout in n8n (60+ seconds for browser automation)
5. **Error Handling**: Add error handling nodes for failed requests

## 🔄 Error Handling

Common errors and solutions:

### Connection Refused
- Check if service is running: `curl http://localhost:8000/health`
- Verify port 8000 is available

### Authentication Error  
- Verify API key: `x-api-key: test-demo-key-12345`

### Browser Issues
- Check browser automation logs
- Set `HEADLESS=false` for debugging

### Timeout Errors
- Increase timeout in n8n HTTP Request node
- Check ACT Strategic website availability

## 🎯 Production Deployment

For production use:
1. Deploy service to cloud (AWS, Azure, etc.)
2. Update n8n URLs to production endpoints
3. Use secure API keys
4. Set up monitoring and logging
5. Configure proper error handling and retries