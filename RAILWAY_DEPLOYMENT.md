# Railway Deployment Guide for ACT Strategic Service

## 📋 Files Overview

### Railway-Specific Files:
- ✅ `start_railway.py` - Railway-optimized server launcher
- ✅ `Dockerfile` - Railway container configuration
- ✅ `railway.json` - Railway deployment settings
- ✅ `Procfile` - Railway process configuration
- ✅ `requirements.txt` - Python dependencies

### Local Development Files:
- ✅ `start_server.py` - Local server launcher (visible browser)
- ✅ `unified_flow.py` - Core automation logic
- ✅ `.env` - Local environment variables

## 🚀 Railway Deployment Steps

### 1. Environment Variables (Required)
Set these in Railway dashboard:

```bash
# Authentication (Required)
SCHMICK_USER=amandeep.ai
SCHMICK_PASS=Byte#@123
PLAYWRIGHT_API_KEY=test-demo-key-12345

# Railway Configuration (Automatic)
HEADLESS=true
HOST=0.0.0.0
PORT=8000

# Optional (with sensible defaults)
MAX_CONCURRENCY=2
TIMEOUT_MS=30000
STORAGE_STATE_FILE=state.json
```

### 2. Deploy to Railway

**Option A: GitHub Integration (Recommended)**
1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Railway auto-deploys on push

**Option B: Railway CLI**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### 3. Expected Behavior

**After deployment:**
- ✅ Railway installs Firefox browsers automatically
- ✅ Service runs in headless mode (no visible browser)
- ✅ Health check at: `https://yourapp.railway.app/health`
- ✅ API endpoint at: `https://yourapp.railway.app/process`
- ✅ Returns: `{"result":"success","membership":"15"}`

## 🧪 Testing

### Local Testing:
```bash
# Local with visible browser
python start_server.py

# Test headless mode (Railway simulation)
HEADLESS=true python start_server.py
```

### Railway Testing:
```bash
# Health check
curl https://yourapp.railway.app/health

# API test
curl -X POST https://yourapp.railway.app/process \
  -H "x-api-key: test-demo-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "salesforceId": "SF-12345",
    "firstName": "John", 
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "dob": "1990-01-01"
  }'
```

## 🔧 Troubleshooting

### Common Issues:

1. **Healthcheck Fails**
   - Check Railway environment variables are set
   - Ensure PORT is not hardcoded to 8000
   - Verify Playwright browsers installed

2. **Browser Issues**
   - Ensure HEADLESS=true in Railway
   - Check Firefox installation in logs
   - Verify no display errors in headless mode

3. **Authentication Issues** 
   - Verify SCHMICK_USER and SCHMICK_PASS in Railway
   - Check credentials work in local testing first

### Logs:
```bash
railway logs
```

## 🌐 n8n Integration

Once deployed, update your n8n workflow:

```json
{
  "url": "https://yourapp.railway.app/process",
  "method": "POST",
  "headers": {
    "x-api-key": "test-demo-key-12345",
    "Content-Type": "application/json"
  }
}
```

Expected response: `{"result":"success","membership":"15"}`
Access in n8n: `{{ $json.membership }}` = "15"