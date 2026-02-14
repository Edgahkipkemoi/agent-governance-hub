"""
Unit tests for DatabaseService
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.database_service import DatabaseService


class TestDatabaseServiceInitialization:
    """Tests for DatabaseService initialization"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_supabase_url(self):
        """Should raise ValueError when SUPABASE_URL is missing"""
        with pytest.raises(ValueError, match="SUPABASE_URL environment variable is required"):
            DatabaseService()
    
    @patch.dict(os.environ, {"SUPABASE_URL": "https://test.supabase.co"}, clear=True)
    def test_missing_supabase_key(self):
        """Should raise ValueError when SUPABASE_SERVICE_ROLE_KEY is missing"""
        with pytest.raises(ValueError, match="SUPABASE_SERVICE_ROLE_KEY environment variable is required"):
            DatabaseService()
    
    @patch('services.database_service.create_client')
    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key"
    }, clear=True)
    def test_successful_initialization(self, mock_create_client):
        """Should initialize successfully with valid environment variables"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        service = DatabaseService()
        
        assert service.client == mock_client
        mock_create_client.assert_called_once_with("https://test.supabase.co", "test-key")
    
    @patch('services.database_service.create_client')
    @patch.dict(os.environ, {
        "SUPABASE_URL": "https://test.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "test-key"
    }, clear=True)
    def test_client_initialization_failure(self, mock_create_client):
        """Should raise Exception when Supabase client initialization fails"""
        mock_create_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Failed to initialize database connection"):
            DatabaseService()


class TestCreateAuditLog:
    """Tests for create_audit_log method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a DatabaseService with mocked client"""
        with patch('services.database_service.create_client'):
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "test-key"
            }, clear=True):
                service = DatabaseService()
                service.client = Mock()
                return service
    
    @pytest.mark.asyncio
    async def test_successful_log_creation(self, mock_service):
        """Should successfully create audit log and return UUID"""
        # Mock the database response
        mock_result = Mock()
        mock_result.data = [{"id": "test-uuid-123"}]
        mock_service.client.table.return_value.insert.return_value.execute.return_value = mock_result
        
        audit_data = {
            "risk_score": 5,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False,
            "details": "Test audit"
        }
        
        log_id = await mock_service.create_audit_log(
            query="Test query",
            response="Test response",
            audit=audit_data,
            status="Warning"
        )
        
        assert log_id == "test-uuid-123"
        mock_service.client.table.assert_called_once_with("logs")
    
    @pytest.mark.asyncio
    async def test_empty_query_validation(self, mock_service):
        """Should raise ValueError for empty query"""
        audit_data = {
            "risk_score": 5,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False
        }
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await mock_service.create_audit_log(
                query="",
                response="Test response",
                audit=audit_data,
                status="Safe"
            )
    
    @pytest.mark.asyncio
    async def test_whitespace_query_validation(self, mock_service):
        """Should raise ValueError for whitespace-only query"""
        audit_data = {
            "risk_score": 5,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False
        }
        
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await mock_service.create_audit_log(
                query="   ",
                response="Test response",
                audit=audit_data,
                status="Safe"
            )
    
    @pytest.mark.asyncio
    async def test_empty_response_validation(self, mock_service):
        """Should raise ValueError for empty response"""
        audit_data = {
            "risk_score": 5,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False
        }
        
        with pytest.raises(ValueError, match="Response cannot be empty"):
            await mock_service.create_audit_log(
                query="Test query",
                response="",
                audit=audit_data,
                status="Safe"
            )
    
    @pytest.mark.asyncio
    async def test_invalid_status_validation(self, mock_service):
        """Should raise ValueError for invalid status"""
        audit_data = {
            "risk_score": 5,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False
        }
        
        with pytest.raises(ValueError, match="Invalid status"):
            await mock_service.create_audit_log(
                query="Test query",
                response="Test response",
                audit=audit_data,
                status="Invalid"
            )
    
    @pytest.mark.asyncio
    async def test_missing_audit_field_validation(self, mock_service):
        """Should raise ValueError for missing required audit fields"""
        incomplete_audit = {
            "risk_score": 5,
            "hallucination_detected": False
            # Missing pii_detected and toxic_content_detected
        }
        
        with pytest.raises(ValueError, match="Audit data missing required field"):
            await mock_service.create_audit_log(
                query="Test query",
                response="Test response",
                audit=incomplete_audit,
                status="Safe"
            )
    
    @pytest.mark.asyncio
    async def test_database_insertion_failure(self, mock_service):
        """Should raise Exception when database insertion fails"""
        mock_service.client.table.return_value.insert.return_value.execute.side_effect = Exception("DB Error")
        
        audit_data = {
            "risk_score": 5,
            "hallucination_detected": False,
            "pii_detected": False,
            "toxic_content_detected": False
        }
        
        with pytest.raises(Exception, match="Database error: Failed to create audit log"):
            await mock_service.create_audit_log(
                query="Test query",
                response="Test response",
                audit=audit_data,
                status="Safe"
            )


class TestGetRecentLogs:
    """Tests for get_recent_logs method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create a DatabaseService with mocked client"""
        with patch('services.database_service.create_client'):
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "test-key"
            }, clear=True):
                service = DatabaseService()
                service.client = Mock()
                return service
    
    @pytest.mark.asyncio
    async def test_successful_log_retrieval(self, mock_service):
        """Should successfully retrieve logs"""
        # Mock the database response
        mock_result = Mock()
        mock_result.data = [
            {
                "id": "uuid-1",
                "query": "Test query 1",
                "response": "Test response 1",
                "audit": {"risk_score": 3},
                "status": "Safe"
            },
            {
                "id": "uuid-2",
                "query": "Test query 2",
                "response": "Test response 2",
                "audit": {"risk_score": 7},
                "status": "Flagged"
            }
        ]
        
        mock_chain = Mock()
        mock_chain.order.return_value.limit.return_value.execute.return_value = mock_result
        mock_service.client.table.return_value.select.return_value = mock_chain
        
        logs = await mock_service.get_recent_logs(limit=50)
        
        assert len(logs) == 2
        assert logs[0]["id"] == "uuid-1"
        assert logs[1]["id"] == "uuid-2"
        mock_service.client.table.assert_called_once_with("logs")
    
    @pytest.mark.asyncio
    async def test_empty_logs_retrieval(self, mock_service):
        """Should return empty list when no logs exist"""
        mock_result = Mock()
        mock_result.data = []
        
        mock_chain = Mock()
        mock_chain.order.return_value.limit.return_value.execute.return_value = mock_result
        mock_service.client.table.return_value.select.return_value = mock_chain
        
        logs = await mock_service.get_recent_logs()
        
        assert logs == []
    
    @pytest.mark.asyncio
    async def test_custom_limit(self, mock_service):
        """Should respect custom limit parameter"""
        mock_result = Mock()
        mock_result.data = []
        
        mock_chain = Mock()
        mock_limit = Mock()
        mock_chain.order.return_value = mock_limit
        mock_limit.limit.return_value.execute.return_value = mock_result
        mock_service.client.table.return_value.select.return_value = mock_chain
        
        await mock_service.get_recent_logs(limit=10)
        
        mock_limit.limit.assert_called_once_with(10)
    
    @pytest.mark.asyncio
    async def test_invalid_limit_validation(self, mock_service):
        """Should raise ValueError for invalid limit"""
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            await mock_service.get_recent_logs(limit=0)
        
        with pytest.raises(ValueError, match="Limit must be a positive integer"):
            await mock_service.get_recent_logs(limit=-5)
    
    @pytest.mark.asyncio
    async def test_database_query_failure(self, mock_service):
        """Should raise Exception when database query fails"""
        mock_service.client.table.return_value.select.side_effect = Exception("Query failed")
        
        with pytest.raises(Exception, match="Database error: Failed to retrieve audit logs"):
            await mock_service.get_recent_logs()


# Property-Based Tests
from hypothesis import given, strategies as st, settings
import uuid


class TestDatabasePropertyTests:
    """Property-based tests for database operations"""
    
    @pytest.fixture
    def mock_service_with_real_uuids(self):
        """Create a DatabaseService that generates real UUIDs"""
        with patch('backend.services.database_service.create_client'):
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "test-key"
            }, clear=True):
                service = DatabaseService()
                service.client = Mock()
                
                # Mock to return different UUIDs for each call
                def mock_insert_with_uuid(*args, **kwargs):
                    mock_result = Mock()
                    mock_result.data = [{"id": str(uuid.uuid4())}]
                    return Mock(execute=Mock(return_value=mock_result))
                
                service.client.table.return_value.insert = mock_insert_with_uuid
                return service
    
    @pytest.mark.asyncio
    @given(st.integers(min_value=2, max_value=20))
    @settings(max_examples=100, deadline=None)
    async def test_property_8_uuid_uniqueness(self, num_logs):
        """
        **Feature: agent-audit, Property 8: Unique log identifiers**
        
        For any two audit logs created by the system, their id values should be 
        different valid UUIDs.
        
        **Validates: Requirements 3.2, 9.2**
        """
        with patch('services.database_service.create_client'):
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "test-key"
            }, clear=True):
                service = DatabaseService()
                service.client = Mock()
                
                generated_uuids = []
                
                # Mock to return different UUIDs for each call
                def mock_insert_with_uuid(*args, **kwargs):
                    new_uuid = str(uuid.uuid4())
                    generated_uuids.append(new_uuid)
                    mock_result = Mock()
                    mock_result.data = [{"id": new_uuid}]
                    return Mock(execute=Mock(return_value=mock_result))
                
                service.client.table.return_value.insert = mock_insert_with_uuid
                
                # Create multiple audit logs
                audit_data = {
                    "risk_score": 3,
                    "hallucination_detected": False,
                    "pii_detected": False,
                    "toxic_content_detected": False,
                    "details": "Test"
                }
                
                log_ids = []
                for i in range(num_logs):
                    log_id = await service.create_audit_log(
                        query=f"Test query {i}",
                        response=f"Test response {i}",
                        audit=audit_data,
                        status="Safe"
                    )
                    log_ids.append(log_id)
                
                # Property: All UUIDs should be unique
                assert len(log_ids) == len(set(log_ids)), "All log IDs should be unique"
                
                # Property: All IDs should be valid UUIDs
                for log_id in log_ids:
                    try:
                        uuid.UUID(log_id)
                    except ValueError:
                        pytest.fail(f"Invalid UUID format: {log_id}")
    
    @pytest.mark.asyncio
    @given(
        query=st.text(min_size=1, max_size=100),
        response=st.text(min_size=1, max_size=100),
        risk_score=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    async def test_property_9_automatic_timestamp_generation(self, query, response, risk_score):
        """
        **Feature: agent-audit, Property 9: Automatic timestamp generation**
        
        For any newly created audit log, the created_at timestamp should be within 
        5 seconds of the current time.
        
        **Validates: Requirements 3.3, 9.3**
        """
        from datetime import datetime, timezone, timedelta
        
        with patch('services.database_service.create_client'):
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "test-key"
            }, clear=True):
                service = DatabaseService()
                service.client = Mock()
                
                # Record the time before creating the log
                before_time = datetime.now(timezone.utc)
                
                # Mock to return a timestamp close to current time
                current_timestamp = datetime.now(timezone.utc).isoformat()
                mock_result = Mock()
                mock_result.data = [{
                    "id": str(uuid.uuid4()),
                    "created_at": current_timestamp
                }]
                service.client.table.return_value.insert.return_value.execute.return_value = mock_result
                
                # Create audit log
                audit_data = {
                    "risk_score": risk_score,
                    "hallucination_detected": False,
                    "pii_detected": False,
                    "toxic_content_detected": False,
                    "details": "Test"
                }
                
                # Determine status based on risk score
                if risk_score <= 3:
                    status = "Safe"
                elif risk_score <= 6:
                    status = "Warning"
                else:
                    status = "Flagged"
                
                await service.create_audit_log(
                    query=query,
                    response=response,
                    audit=audit_data,
                    status=status
                )
                
                # Record the time after creating the log
                after_time = datetime.now(timezone.utc)
                
                # Parse the returned timestamp
                returned_timestamp = datetime.fromisoformat(current_timestamp.replace('Z', '+00:00'))
                
                # Property: Timestamp should be within 5 seconds of current time
                time_diff = abs((returned_timestamp - before_time).total_seconds())
                assert time_diff <= 5, f"Timestamp should be within 5 seconds, but was {time_diff} seconds"
                
                # Also check it's not in the future
                assert returned_timestamp <= after_time, "Timestamp should not be in the future"
    
    @pytest.mark.asyncio
    @given(
        query=st.text(min_size=1, max_size=100),
        response=st.text(min_size=1, max_size=100),
        risk_score=st.integers(min_value=0, max_value=10),
        hallucination=st.booleans(),
        pii=st.booleans(),
        toxic=st.booleans(),
        confidence=st.floats(min_value=0.0, max_value=1.0)
    )
    @settings(max_examples=100, deadline=None)
    async def test_property_11_audit_json_structure(
        self, query, response, risk_score, hallucination, pii, toxic, confidence
    ):
        """
        **Feature: agent-audit, Property 11: Audit JSON structure**
        
        For any stored audit log, the audit field should be valid JSON containing 
        at minimum the fields: risk_score, hallucination_detected, pii_detected, 
        and toxic_content_detected.
        
        **Validates: Requirements 2.2, 9.4**
        """
        import json
        
        with patch('services.database_service.create_client'):
            with patch.dict(os.environ, {
                "SUPABASE_URL": "https://test.supabase.co",
                "SUPABASE_SERVICE_ROLE_KEY": "test-key"
            }, clear=True):
                service = DatabaseService()
                service.client = Mock()
                
                # Track what was inserted
                inserted_data = None
                
                def capture_insert(data):
                    nonlocal inserted_data
                    inserted_data = data
                    mock_result = Mock()
                    mock_result.data = [{"id": str(uuid.uuid4())}]
                    return Mock(execute=Mock(return_value=mock_result))
                
                service.client.table.return_value.insert = capture_insert
                
                # Create audit log with all required fields
                audit_data = {
                    "risk_score": risk_score,
                    "hallucination_detected": hallucination,
                    "pii_detected": pii,
                    "toxic_content_detected": toxic,
                    "confidence": confidence,
                    "details": "Test audit"
                }
                
                # Determine status based on risk score
                if risk_score <= 3:
                    status = "Safe"
                elif risk_score <= 6:
                    status = "Warning"
                else:
                    status = "Flagged"
                
                await service.create_audit_log(
                    query=query,
                    response=response,
                    audit=audit_data,
                    status=status
                )
                
                # Property: Audit data should be JSON-serializable
                assert inserted_data is not None, "Data should have been inserted"
                audit_field = inserted_data["audit"]
                
                # Should be serializable to JSON
                json_str = json.dumps(audit_field)
                parsed = json.loads(json_str)
                
                # Property: Must contain required fields
                required_fields = ["risk_score", "hallucination_detected", "pii_detected", "toxic_content_detected"]
                for field in required_fields:
                    assert field in parsed, f"Audit JSON must contain field: {field}"
                
                # Property: risk_score should be an integer 0-10
                assert isinstance(parsed["risk_score"], int), "risk_score must be an integer"
                assert 0 <= parsed["risk_score"] <= 10, "risk_score must be between 0 and 10"
                
                # Property: Boolean fields should be booleans
                assert isinstance(parsed["hallucination_detected"], bool), "hallucination_detected must be boolean"
                assert isinstance(parsed["pii_detected"], bool), "pii_detected must be boolean"
                assert isinstance(parsed["toxic_content_detected"], bool), "toxic_content_detected must be boolean"
