"""
Basic integration tests for the Schmick Membership Service.
Run with: pytest tests/ -v
"""

import asyncio
import pytest
import httpx
from unittest.mock import patch, MagicMock


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test that health endpoint returns ok."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"ok": True}


class TestProcessEndpoint:
    """Test the membership processing endpoint."""
    
    def setup_method(self):
        """Setup test data."""
        self.valid_record = {
            "salesforceId": "SF123456",
            "firstName": "John",
            "lastName": "Doe", 
            "email": "john.doe@example.com",
            "dob": "1990-01-01",
            "phone": "555-0123",
            "address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zipCode": "12345"
        }
        
        self.headers = {
            "x-api-key": "test-api-key",
            "Content-Type": "application/json"
        }
    
    @pytest.mark.asyncio
    async def test_process_missing_api_key(self):
        """Test that missing API key returns 401."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/process", json=self.valid_record)
            assert response.status_code == 401
            assert "Invalid or missing API key" in response.json()["message"]
    
    @pytest.mark.asyncio
    async def test_process_invalid_api_key(self):
        """Test that invalid API key returns 401."""
        headers = {"x-api-key": "invalid-key", "Content-Type": "application/json"}
        
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/process", json=self.valid_record, headers=headers)
            assert response.status_code == 401
            assert "Invalid or missing API key" in response.json()["message"]
    
    @pytest.mark.asyncio 
    async def test_process_invalid_record_data(self):
        """Test that invalid record data returns 422."""
        invalid_record = {
            "salesforceId": "SF123456",
            # Missing required fields
            "email": "invalid-email"  # Invalid email format
        }
        
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/process", json=invalid_record, headers=self.headers)
            assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_process_valid_record_structure(self):
        """Test that valid record structure is accepted (may fail due to missing Schmick site)."""
        # Note: This test will likely fail in CI/CD without actual Schmick credentials
        # but verifies the request structure is correct
        
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.post("/process", json=self.valid_record, headers=self.headers)
            
            # We expect either success or a specific error (not validation error)
            # Status should not be 422 (validation error)
            assert response.status_code != 422
            
            # Response should have proper structure
            json_response = response.json()
            assert "result" in json_response
            
            if response.status_code == 200:
                assert json_response["result"] == "success"
                assert "membership" in json_response
            else:
                assert json_response["result"] == "error"
                assert "message" in json_response


def test_example_curl_commands():
    """
    Example curl commands for manual testing.
    This is not a real test, just documentation.
    """
    commands = [
        # Health check
        "curl -X GET http://localhost:8000/health",
        
        # Process membership (replace API key with actual value)
        '''curl -X POST http://localhost:8000/process \\
  -H "x-api-key: your-api-key-here" \\
  -H "Content-Type: application/json" \\
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
    "zipCode": "12345"
  }' ''',
        
        # Alternative using Bearer token
        '''curl -X POST http://localhost:8000/process \\
  -H "Authorization: Bearer your-api-key-here" \\
  -H "Content-Type: application/json" \\
  -d '{
    "salesforceId": "SF789012", 
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@example.com",
    "dob": "1985-05-15"
  }' '''
    ]
    
    # This is just for documentation, not actual execution
    assert len(commands) == 3


if __name__ == "__main__":
    print("Example curl commands for testing:")
    print("\n1. Health check:")
    print("curl -X GET http://localhost:8000/health")
    
    print("\n2. Process membership:")
    print("""curl -X POST http://localhost:8000/process \\
  -H "x-api-key: your-api-key-here" \\
  -H "Content-Type: application/json" \\
  -d '{
    "salesforceId": "SF123456",
    "firstName": "John", 
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "dob": "1990-01-01"
  }' """)
    
    print("\n3. Run tests:")
    print("pytest tests/ -v")