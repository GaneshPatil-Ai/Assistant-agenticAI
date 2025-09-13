#!/usr/bin/env python3
"""
Test client for LangGraph Supervisor-Worker API
Demonstrates the workflow functionality
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_workflow_info():
    """Test workflow info endpoint"""
    print("\n📋 Testing workflow info...")
    try:
        response = requests.get(f"{BASE_URL}/info")
        print(f"Status: {response.status_code}")
        info = response.json()
        print(f"Workflow Type: {info.get('workflow_type')}")
        print(f"Available Workers: {list(info.get('available_workers', {}).keys())}")
        print(f"Supervisor Capabilities: {info.get('supervisor_capabilities')}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Workflow info failed: {e}")
        return False

def test_query_processing():
    """Test query processing with different types of queries"""
    print("\n🔍 Testing query processing...")
    
    # Test 1: Simple query that might need more info
    print("\n--- Test 1: Simple query ---")
    query1 = "Help me write something"
    result1 = process_query(query1)
    
    if result1 and result1.get('action') == 'gather_info':
        print("✅ Query correctly identified as needing more information")
        print(f"Follow-up questions: {result1.get('follow_up_questions')}")
        
        # Test follow-up response
        print("\n--- Test 1.1: Follow-up response ---")
        follow_up_query = f"{query1} about artificial intelligence for beginners"
        result1_followup = process_query(follow_up_query)
        print(f"Follow-up result: {result1_followup.get('action')}")
    
    # Test 2: Specific query that should have sufficient info
    print("\n--- Test 2: Specific query ---")
    query2 = "Research the latest developments in quantum computing and create a creative summary"
    result2 = process_query(query2)
    
    if result2 and result2.get('action') == 'completed':
        print("✅ Query processed successfully with workers")
        print(f"Final response length: {len(result2.get('final_response', ''))}")
        print(f"Workers used: {list(result2.get('worker_results', {}).keys())}")
    
    # Test 3: Research-focused query
    print("\n--- Test 3: Research query ---")
    query3 = "Find information about renewable energy sources and their efficiency rates"
    result3 = process_query(query3)
    
    if result3:
        print(f"Query 3 result: {result3.get('action')}")
        if result3.get('worker_results'):
            print(f"Research worker output: {result3.get('worker_results', {}).get('research_worker', '')[:200]}...")

def process_query(query):
    """Process a query through the API"""
    try:
        payload = {"query": query}
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Query failed with status {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error processing query: {e}")
        return None

def main():
    """Main test function"""
    print("🧪 LangGraph Supervisor-Worker API Test Client")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("\n❌ Server is not running. Please start the server first:")
        print("   python run.py")
        print("   or")
        print("   gunicorn -c gunicorn.conf.py api:app")
        sys.exit(1)
    
    # Test workflow info
    if not test_workflow_info():
        print("\n❌ Workflow info test failed")
        sys.exit(1)
    
    # Test query processing
    test_query_processing()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()