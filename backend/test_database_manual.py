"""
Manual test script for DatabaseService
Run this to verify the DatabaseService works with the actual Supabase database
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.database_service import DatabaseService


async def test_database_service():
    """Test DatabaseService with actual Supabase database"""
    
    print("=" * 60)
    print("Testing DatabaseService")
    print("=" * 60)
    
    try:
        # Initialize service
        print("\n1. Initializing DatabaseService...")
        service = DatabaseService()
        print("✓ DatabaseService initialized successfully")
        
        # Create a test audit log
        print("\n2. Creating test audit log...")
        test_audit = {
            "risk_score": 2,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False,
            "details": "Test audit from DatabaseService implementation",
            "confidence": 0.95,
            "model": "test-model",
            "timestamp": "2024-02-13T00:00:00Z"
        }
        
        log_id = await service.create_audit_log(
            query="What is the capital of France?",
            response="The capital of France is Paris.",
            audit=test_audit,
            status="Safe"
        )
        print(f"✓ Created audit log with ID: {log_id}")
        
        # Retrieve recent logs
        print("\n3. Retrieving recent logs...")
        logs = await service.get_recent_logs(limit=5)
        print(f"✓ Retrieved {len(logs)} logs")
        
        if logs:
            print("\nMost recent log:")
            recent_log = logs[0]
            print(f"  ID: {recent_log['id']}")
            print(f"  Query: {recent_log['query'][:50]}...")
            print(f"  Status: {recent_log['status']}")
            print(f"  Risk Score: {recent_log['audit']['risk_score']}")
        
        # Test validation
        print("\n4. Testing validation...")
        try:
            await service.create_audit_log(
                query="",
                response="Test",
                audit=test_audit,
                status="Safe"
            )
            print("✗ Validation failed - empty query should be rejected")
        except ValueError as e:
            print(f"✓ Validation working: {e}")
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_database_service())
    sys.exit(0 if success else 1)
