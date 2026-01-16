#!/usr/bin/env python3
"""
Simple test script for EcoTravel API
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_plan_api():
    """Test the travel plan creation API"""
    print("Testing /api/plan endpoint...")
    
    data = {
        "start_location": {"lat": 39.9334, "lng": 32.8597},
        "end_location": {"lat": 41.0082, "lng": 28.9784},
        "days": 5,
        "budget": 5000,
        "preferences": ["nature", "culture"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/plan", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✓ Plan API test passed!")
            print(f"  - Generated {len(result['plans'])} plan tiers")
            for tier, plan in result['plans'].items():
                print(f"  - {tier}: {plan['tier_name']} - {plan['estimated_cost']} TL")
            return True
        else:
            print(f"✗ Plan API test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Plan API test failed: {e}")
        return False

def test_pois_api():
    """Test the POIs listing API"""
    print("\nTesting /api/pois endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/pois")
        if response.status_code == 200:
            result = response.json()
            print("✓ POIs API test passed!")
            print(f"  - Found {len(result['pois'])} POIs")
            return True
        else:
            print(f"✗ POIs API test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ POIs API test failed: {e}")
        return False

def test_review_api():
    """Test the review submission API"""
    print("\nTesting /api/review endpoint...")
    
    data = {
        "poi_id": 1,
        "rating": 5,
        "comment": "Test comment"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/review", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✓ Review API test passed!")
            print(f"  - {result['message']}")
            return True
        else:
            print(f"✗ Review API test failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Review API test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("EcoTravel API Test Suite")
    print("=" * 60)
    print("\nNote: Make sure the Flask app is running on localhost:5000")
    print("\nStarting tests...\n")
    
    # Run tests
    results = []
    results.append(test_plan_api())
    results.append(test_pois_api())
    results.append(test_review_api())
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print(f"\n✗ {total - passed} test(s) failed")
