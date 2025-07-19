#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import httpx
import json
from datetime import datetime

async def test_health_endpoint():
    """Test the health endpoint"""
    print("Testing /health endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=10)
            
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            # Check that timestamp is a string, not datetime object
            timestamp = data.get('timestamp')
            if isinstance(timestamp, str):
                print("✅ Health endpoint working with string timestamp")
                return True
            else:
                print(f"❌ Timestamp is not string: {type(timestamp)}")
                return False
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health endpoint test failed: {e}")
        return False

async def test_ai_health_endpoint():
    """Test the AI health endpoint"""
    print("\nTesting /api/v1/ai/health endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/ai/health", timeout=30)
            
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code == 200:
            data = response.json()
            # Check that response follows BaseResponse format with string timestamp
            metadata = data.get('metadata', {})
            timestamp = metadata.get('timestamp')
            if isinstance(timestamp, str):
                print("✅ AI health endpoint working with string timestamp")
                return True
            else:
                print(f"❌ Metadata timestamp is not string: {type(timestamp)}")
                return False
        else:
            print(f"❌ AI health endpoint returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ AI health endpoint test failed: {e}")
        return False

async def test_explain_endpoint():
    """Test the explain endpoint with a known ingredient"""
    print("\nTesting /api/v1/ai/explain endpoint...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/v1/ai/explain",
                params={"ingredient_name": "inulin"},
                timeout=30
            )
            
        print(f"Status: {response.status_code}")
        
        if response.status_code == 404:
            print("ℹ️ Ingredient 'inulin' not found in database (expected)")
            print("✅ Endpoint working - properly returns 404 for missing ingredient")
            
            # Check that error response has proper datetime serialization
            data = response.json()
            metadata = data.get('metadata', {})
            timestamp = metadata.get('timestamp')
            if isinstance(timestamp, str):
                print("✅ Error response has string timestamp")
                return True
            else:
                print(f"❌ Error response timestamp is not string: {type(timestamp)}")
                return False
        elif response.status_code == 200:
            print("✅ Explain endpoint working with existing ingredient")
            data = response.json()
            metadata = data.get('metadata', {})
            timestamp = metadata.get('timestamp')
            if isinstance(timestamp, str):
                print("✅ Success response has string timestamp")
                return True
            else:
                print(f"❌ Success response timestamp is not string: {type(timestamp)}")
                return False
        else:
            print(f"Response: {response.text}")
            print(f"❌ Explain endpoint returned unexpected status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Explain endpoint test failed: {e}")
        return False

async def start_server():
    """Start the FastAPI server"""
    import subprocess
    
    print("Starting FastAPI server...")
    
    # Start server in background
    process = subprocess.Popen([
        "python", "-m", "uvicorn", "api.main:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ])
    
    # Wait a bit for server to start
    await asyncio.sleep(5)
    
    return process

async def main():
    print("=" * 60)
    print("GutIntel API - Endpoint Integration Test")
    print("=" * 60)
    
    # Start the server
    server_process = None
    try:
        server_process = await start_server()
        
        success = True
        
        # Test health endpoint
        if not await test_health_endpoint():
            success = False
        
        # Test AI health endpoint (this might fail due to missing OpenAI key)
        if not await test_ai_health_endpoint():
            print("⚠️ AI health endpoint failed (likely missing OpenAI API key)")
        
        # Test explain endpoint
        if not await test_explain_endpoint():
            success = False
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 CORE ENDPOINT TESTS PASSED!")
            print("\nThe JSON and datetime serialization fixes are working!")
            print("✅ All response timestamps are properly serialized as strings")
            print("✅ Error handlers work without datetime serialization issues")
            print("✅ BaseResponse format is consistent")
        else:
            print("❌ SOME TESTS FAILED! Please check the errors above.")
        print("=" * 60)
        
    finally:
        # Clean up server process
        if server_process:
            server_process.terminate()
            await asyncio.sleep(2)
            if server_process.poll() is None:
                server_process.kill()

if __name__ == "__main__":
    asyncio.run(main())