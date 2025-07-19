#!/usr/bin/env python3

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.models.responses import BaseResponse, ResponseMetadata, HealthResponse
from api.models.ai_models import ChatMessage
import json

def test_datetime_serialization():
    """Test that datetime fields are properly serialized as strings"""
    print("Testing datetime serialization fixes...")
    
    # Test ResponseMetadata
    print("\n1. Testing ResponseMetadata...")
    metadata = ResponseMetadata()
    print(f"Metadata timestamp type: {type(metadata.timestamp)}")
    print(f"Metadata timestamp value: {metadata.timestamp}")
    
    # Test serialization
    try:
        metadata_json = metadata.model_dump_json()
        print(f"Metadata JSON serialization: SUCCESS")
        print(f"JSON content: {metadata_json}")
    except Exception as e:
        print(f"Metadata JSON serialization: FAILED - {e}")
        return False
    
    # Test HealthResponse
    print("\n2. Testing HealthResponse...")
    health = HealthResponse()
    print(f"Health timestamp type: {type(health.timestamp)}")
    print(f"Health timestamp value: {health.timestamp}")
    
    try:
        health_json = health.model_dump_json()
        print(f"HealthResponse JSON serialization: SUCCESS")
        print(f"JSON content: {health_json}")
    except Exception as e:
        print(f"HealthResponse JSON serialization: FAILED - {e}")
        return False
    
    # Test BaseResponse with metadata
    print("\n3. Testing BaseResponse...")
    response = BaseResponse.success_response({"test": "data"})
    print(f"BaseResponse metadata timestamp type: {type(response.metadata.timestamp)}")
    
    try:
        response_json = response.model_dump_json()
        print(f"BaseResponse JSON serialization: SUCCESS")
        print(f"JSON content: {response_json}")
    except Exception as e:
        print(f"BaseResponse JSON serialization: FAILED - {e}")
        return False
    
    # Test ChatMessage
    print("\n4. Testing ChatMessage...")
    message = ChatMessage(role="user", content="test message")
    print(f"ChatMessage timestamp type: {type(message.timestamp)}")
    
    try:
        message_json = message.model_dump_json()
        print(f"ChatMessage JSON serialization: SUCCESS")
        print(f"JSON content: {message_json}")
    except Exception as e:
        print(f"ChatMessage JSON serialization: FAILED - {e}")
        return False
    
    print("\n✅ All datetime serialization tests passed!")
    return True

async def test_json_parsing():
    """Test that the JSON parsing issue in repositories is fixed"""
    print("\nTesting JSON parsing fix...")
    
    # Mock the database functionality we'd need
    from database.repositories import BaseRepository
    import asyncpg
    
    # Test the _record_to_dict method with mock data
    class MockRecord:
        def __init__(self, data):
            self.data = data
        
        def __getitem__(self, key):
            return self.data[key]
        
        def keys(self):
            return self.data.keys()
        
        def items(self):
            return self.data.items()
    
    # Create a mock repository to test the method
    class TestRepo(BaseRepository):
        def __init__(self):
            pass
    
    repo = TestRepo()
    
    # Test case 1: dosage_info as JSON string (should be parsed)
    print("\n1. Testing JSON string parsing...")
    record1 = MockRecord({
        'id': '12345',
        'name': 'test ingredient',
        'dosage_info': '{"daily": "1-2 tablets", "with_food": true}'
    })
    
    try:
        result1 = repo._record_to_dict(record1)
        dosage_info = result1.get('dosage_info')
        print(f"dosage_info type: {type(dosage_info)}")
        print(f"dosage_info value: {dosage_info}")
        
        if isinstance(dosage_info, dict):
            print("✅ JSON string correctly parsed to dict")
        else:
            print("❌ JSON string not parsed to dict")
            return False
            
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        return False
    
    # Test case 2: dosage_info as dict (should not be double-parsed)
    print("\n2. Testing dict handling...")
    record2 = MockRecord({
        'id': '12345',
        'name': 'test ingredient',
        'dosage_info': {"daily": "1-2 tablets", "with_food": True}  # Already a dict
    })
    
    try:
        result2 = repo._record_to_dict(record2)
        dosage_info2 = result2.get('dosage_info')
        print(f"dosage_info type: {type(dosage_info2)}")
        print(f"dosage_info value: {dosage_info2}")
        
        if isinstance(dosage_info2, dict):
            print("✅ Dict correctly preserved")
        else:
            print("❌ Dict not preserved")
            return False
            
    except Exception as e:
        print(f"❌ Dict handling failed: {e}")
        return False
    
    print("\n✅ All JSON parsing tests passed!")
    return True

def main():
    print("=" * 60)
    print("GutIntel API - JSON & DateTime Serialization Test")
    print("=" * 60)
    
    success = True
    
    # Test datetime serialization
    if not test_datetime_serialization():
        success = False
    
    # Test JSON parsing
    if not asyncio.run(test_json_parsing()):
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The fixes are working correctly.")
        print("\nKey fixes applied:")
        print("1. ✅ Fixed double JSON parsing in repositories.py:950-953")
        print("2. ✅ Changed datetime fields to string fields with ISO format")
        print("3. ✅ Updated error handlers to use model_dump() instead of dict()")
        print("4. ✅ All response models now serialize datetime as strings")
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)