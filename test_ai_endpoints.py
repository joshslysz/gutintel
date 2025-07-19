"""
Test script for AI endpoints in GutIntel API.

This script tests the new AI-powered endpoints to ensure they work correctly.
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

async def test_ai_endpoints():
    """Test all AI endpoints."""
    
    print("🧪 Testing GutIntel AI Endpoints\n")
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: AI Capabilities
        print("1. Testing AI Capabilities...")
        try:
            response = await client.get(f"{BASE_URL}/ai/capabilities")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Features: {len(data['data']['features'])} available")
                print(f"   ✅ Model: {data['data']['models']['primary']}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Ingredient Explanation
        print("\n2. Testing Ingredient Explanation...")
        try:
            response = await client.post(
                f"{BASE_URL}/ai/explain",
                params={"ingredient_name": "inulin", "user_level": "general"}
            )
            if response.status_code == 200:
                data = response.json()
                explanation = data['data']['explanation']
                print(f"   ✅ Generated explanation ({len(explanation)} characters)")
                print(f"   ✅ Key benefits: {len(data['data']['key_benefits'])}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Personalized Recommendations
        print("\n3. Testing Personalized Recommendations...")
        try:
            user_profile = {
                "symptoms": ["bloating", "irregular_bowel"],
                "goals": ["improve_digestion", "boost_immunity"],
                "dietary_restrictions": ["vegetarian"],
                "current_supplements": ["multivitamin"],
                "age": 35,
                "gender": "female"
            }
            
            response = await client.post(
                f"{BASE_URL}/ai/recommend",
                json={
                    "user_profile": user_profile,
                    "max_recommendations": 3
                }
            )
            if response.status_code == 200:
                data = response.json()
                recommendations = data['data']['recommendations']
                print(f"   ✅ Generated {len(recommendations)} recommendations")
                print(f"   ✅ Confidence: {data['data']['confidence_score']}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: Meal Analysis
        print("\n4. Testing Meal Analysis...")
        try:
            response = await client.post(
                f"{BASE_URL}/ai/analyze-meal",
                json={
                    "ingredients": ["inulin", "lactobacillus", "psyllium husk"],
                    "meal_type": "supplement"
                }
            )
            if response.status_code == 200:
                data = response.json()
                gut_score = data['data']['gut_score']
                print(f"   ✅ Gut score: {gut_score}/10")
                print(f"   ✅ Synergies: {len(data['data']['synergistic_effects'])}")
                print(f"   ✅ Suggestions: {len(data['data']['optimization_suggestions'])}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Chat Interface
        print("\n5. Testing Chat Interface...")
        try:
            response = await client.post(
                f"{BASE_URL}/ai/chat",
                json={
                    "messages": [
                        {
                            "role": "user",
                            "content": "What are the best probiotics for digestive health?",
                            "timestamp": datetime.now().isoformat()
                        }
                    ]
                }
            )
            if response.status_code == 200:
                data = response.json()
                ai_response = data['data']['response']
                print(f"   ✅ Generated response ({len(ai_response)} characters)")
                print(f"   ✅ Suggestions: {len(data['data']['suggestions'])}")
                print(f"   ✅ Confidence: {data['data']['confidence_score']}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 6: Batch Analysis
        print("\n6. Testing Batch Analysis...")
        try:
            response = await client.post(
                f"{BASE_URL}/ai/batch-analyze",
                json={
                    "ingredients": ["inulin", "berberine", "omega-3", "vitamin-d"],
                    "analysis_type": "summary"
                }
            )
            if response.status_code == 200:
                data = response.json()
                combined_score = data['data']['combined_score']
                print(f"   ✅ Combined score: {combined_score}/10")
                print(f"   ✅ Individual scores: {len(data['data']['individual_scores'])}")
                print(f"   ✅ Synergies: {len(data['data']['top_synergies'])}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 7: AI Health Check
        print("\n7. Testing AI Health Check...")
        try:
            response = await client.get(f"{BASE_URL}/ai/health")
            if response.status_code == 200:
                data = response.json()
                status = data['data']['status']
                response_time = data['data']['response_time_ms']
                print(f"   ✅ Status: {status}")
                print(f"   ✅ Response time: {response_time:.2f}ms")
                if data['data'].get('error_message'):
                    print(f"   ⚠️  Error: {data['data']['error_message']}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n🎉 AI Endpoint Testing Complete!")

if __name__ == "__main__":
    print("Note: Make sure to set OPENAI_API_KEY environment variable")
    print("Starting in 3 seconds...")
    asyncio.run(test_ai_endpoints())