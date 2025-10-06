#!/bin/bash

# Test Railway Deployment with Curl
# Railway URL: https://service-production-0645.up.railway.app/

echo "Testing Railway deployment..."
echo "URL: https://service-production-0645.up.railway.app/"
echo ""

# Test 1: Health check endpoint
echo "=== Test 1: Health Check ==="
curl -X GET "https://service-production-0645.up.railway.app/" \
  -H "Accept: application/json" \
  -v

echo ""
echo ""

# Test 2: Submit membership form
echo "=== Test 2: Submit Membership Form ==="
curl -X POST "https://service-production-0645.up.railway.app/submit-membership" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "businessName": "Test Business Ltd",
    "abn": "12345678901",
    "businessAddress": "123 Test Street, Test City NSW 2000",
    "postalAddress": "PO Box 123, Test City NSW 2000",
    "businessPhone": "0412345678",
    "businessEmail": "test@testbusiness.com.au",
    "website": "https://testbusiness.com.au",
    "businessType": "Sole Trader",
    "industryType": "Technology",
    "businessDescription": "Test technology business for Railway deployment",
    "yearsInBusiness": "5",
    "numberOfEmployees": "10",
    "annualTurnover": "$500,000 - $1M",
    "currentInsurer": "Test Insurance Co",
    "currentPremium": "$5000",
    "claimsHistory": "No claims in last 5 years",
    "contactPerson": "John Test",
    "contactPhone": "0412345678",
    "contactEmail": "john@testbusiness.com.au",
    "startDate": "2024-02-01",
    "additionalInfo": "Testing Railway deployment with curl",
    "hearAboutUs": "Online Search",
    "newsletter": true,
    "terms": true
  }' \
  -v

echo ""
echo ""
echo "=== Railway Deployment Test Complete ==="
echo ""
echo "Note: If you see connection errors, this may be due to:"
echo "1. Railway deployment not active"
echo "2. Geo-blocking (Railway servers may not have Australian IPs)"
echo "3. Service configuration issues"