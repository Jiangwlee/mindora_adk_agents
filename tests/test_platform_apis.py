#!/usr/bin/env python3
"""
Test script for platform API functionality.
"""
import asyncio
import json
import requests
import time
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_platform_apis():
    """Test all platform API endpoints."""
    print("🧪 Testing Platform APIs")
    print("=" * 50)
    
    # Test 1: Get platform apps
    print("\n1. Testing GET /platform/apps")
    try:
        response = requests.get(f"{BASE_URL}/platform/apps")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {data['totalCount']} apps")
            print(f"   Categories: {data['categories']}")
            if data['apps']:
                print(f"   Sample app: {data['apps'][0]['name']} ({data['apps'][0]['appType']})")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get specific app
    print("\n2. Testing GET /platform/apps/{name}")
    try:
        response = requests.get(f"{BASE_URL}/platform/apps/adk_demo")
        if response.status_code == 200:
            app = response.json()
            print(f"✅ Success: App '{app['name']}' loaded")
            print(f"   Type: {app['appType']}")
            print(f"   Description: {app['description']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Launch app session
    print("\n3. Testing POST /platform/apps/{name}/launch")
    try:
        launch_data = {
            "user_id": "test_user",
            "user_mode": "individual",
            "session_config": {
                "timeout": 3600,
                "persistent": False
            },
            "metadata": {
                "client": "test_script",
                "version": "1.0"
            }
        }
        response = requests.post(f"{BASE_URL}/platform/apps/adk_demo/launch", json=launch_data)
        if response.status_code == 200:
            session_data = response.json()
            print(f"✅ Success: App session launched")
            print(f"   Session ID: {session_data['sessionInfo']['sessionId']}")
            print(f"   User ID: {session_data['sessionInfo']['userId']}")
            print(f"   Status: {session_data['sessionInfo']['status']}")
            print(f"   WebSocket URL: {session_data['websocketUrl']}")
            
            # Save session ID for further tests
            session_id = session_data['sessionInfo']['sessionId']
            
            # Test 4: Get session info
            print("\n4. Testing GET /platform/sessions/{session_id}")
            response = requests.get(f"{BASE_URL}/platform/sessions/{session_id}")
            if response.status_code == 200:
                session = response.json()
                print(f"✅ Success: Session info retrieved")
                print(f"   Created: {session['createdAt']}")
                print(f"   Expires: {session['expiresAt']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
            
            # Test 5: List sessions
            print("\n5. Testing GET /platform/sessions")
            response = requests.get(f"{BASE_URL}/platform/sessions")
            if response.status_code == 200:
                sessions = response.json()
                print(f"✅ Success: Listed {sessions['totalCount']} sessions")
                print(f"   Active sessions: {sessions['activeCount']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
            
            # Test 6: Update session
            print("\n6. Testing PUT /platform/sessions/{session_id}")
            update_data = {
                "metadata": {
                    "updated_by": "test_script",
                    "last_action": "test_update"
                }
            }
            response = requests.put(f"{BASE_URL}/platform/sessions/{session_id}", json=update_data)
            if response.status_code == 200:
                print(f"✅ Success: Session updated")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
            
            # Test 7: Delete session
            print("\n7. Testing DELETE /platform/sessions/{session_id}")
            response = requests.delete(f"{BASE_URL}/platform/sessions/{session_id}")
            if response.status_code == 200:
                print(f"✅ Success: Session deleted")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 8: Cleanup expired sessions
    print("\n8. Testing POST /platform/cleanup")
    try:
        response = requests.post(f"{BASE_URL}/platform/cleanup")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Platform API testing completed!")

def test_backward_compatibility():
    """Test that existing APIs still work."""
    print("\n🔄 Testing Backward Compatibility")
    print("=" * 50)
    
    # Test existing list-apps endpoint
    print("\n1. Testing GET /list-apps (existing)")
    try:
        response = requests.get(f"{BASE_URL}/list-apps")
        if response.status_code == 200:
            apps = response.json()
            print(f"✅ Success: Found {len(apps)} apps")
            print(f"   Apps: {apps}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test health check
    print("\n2. Testing GET /health (existing)")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Success: Server is {health['status']}")
            print(f"   Version: {health['version']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Platform API Test Suite")
    print("Make sure the server is running on http://localhost:8000")
    print("Run: python run_server.py")
    print()
    
    # Test platform APIs
    test_platform_apis()
    
    # Test backward compatibility
    test_backward_compatibility()
    
    print("\n🎯 All tests completed!")