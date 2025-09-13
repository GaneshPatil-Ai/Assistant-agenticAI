#!/usr/bin/env python3
"""
Demo script for LangGraph Supervisor-Worker System
Shows the workflow functionality without requiring the API
"""

import asyncio
import json
from workflow import LangGraphWorkflow
from config import Config

async def demo_workflow():
    """Demonstrate the workflow functionality"""
    print("🎭 LangGraph Supervisor-Worker System Demo")
    print("=" * 50)
    
    try:
        # Initialize workflow
        workflow = LangGraphWorkflow()
        print("✅ Workflow initialized successfully")
        
        # Show workflow info
        info = workflow.get_workflow_info()
        print(f"\n📋 Workflow Type: {info['workflow_type']}")
        print(f"Available Workers: {list(info['available_workers'].keys())}")
        print(f"Supervisor Capabilities: {info['supervisor_capabilities']}")
        
        # Demo 1: Query needing more information
        print("\n" + "="*50)
        print("🔍 Demo 1: Query needing more information")
        print("Query: 'Help me write something'")
        
        result1 = await workflow.process_query("Help me write something")
        print(f"Status: {result1['status']}")
        print(f"Action: {result1.get('action')}")
        
        if result1.get('follow_up_questions'):
            print("Follow-up questions:")
            for i, question in enumerate(result1['follow_up_questions'], 1):
                print(f"  {i}. {question}")
        
        # Demo 2: Specific query with sufficient information
        print("\n" + "="*50)
        print("🔍 Demo 2: Specific query with sufficient information")
        print("Query: 'Research quantum computing and create a creative summary'")
        
        result2 = await workflow.process_query("Research quantum computing and create a creative summary")
        print(f"Status: {result2['status']}")
        print(f"Action: {result2.get('action')}")
        
        if result2.get('worker_results'):
            print("Worker results:")
            for worker, result in result2['worker_results'].items():
                print(f"  {worker}: {result[:100]}...")
        
        if result2.get('final_response'):
            print(f"\nFinal Response: {result2['final_response'][:200]}...")
        
        # Demo 3: Research-focused query
        print("\n" + "="*50)
        print("🔍 Demo 3: Research-focused query")
        print("Query: 'Find information about renewable energy sources'")
        
        result3 = await workflow.process_query("Find information about renewable energy sources")
        print(f"Status: {result3['status']}")
        print(f"Action: {result3.get('action')}")
        
        if result3.get('worker_results'):
            print("Worker results:")
            for worker, result in result3['worker_results'].items():
                print(f"  {worker}: {result[:100]}...")
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\nMake sure you have:")
        print("1. Set your OpenAI API key in .env file")
        print("2. Installed all dependencies: pip install -r requirements.txt")

def main():
    """Main demo function"""
    # Check if .env exists
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please create a .env file with your OpenAI API key:")
        print("cp .env.example .env")
        print("Then edit .env and add: OPENAI_API_KEY=your_key_here")
        return
    
    # Run demo
    asyncio.run(demo_workflow())

if __name__ == "__main__":
    main()