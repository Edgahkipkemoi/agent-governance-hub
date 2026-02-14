"""
Unit tests for AgentService
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.agent_service import AgentService, WorkerResponse


class TestAgentServiceInitialization:
    """Tests for AgentService initialization"""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_groq_api_key(self):
        """Should raise ValueError when GROQ_API_KEY is missing"""
        with pytest.raises(ValueError, match="GROQ_API_KEY environment variable is required"):
            AgentService()
    
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}, clear=True)
    def test_missing_gemini_api_key(self):
        """Should raise ValueError when GEMINI_API_KEY is missing"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable is required"):
            AgentService()
    
    @patch('services.agent_service.genai')
    @patch('services.agent_service.Groq')
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GEMINI_API_KEY": "test-gemini-key"}, clear=True)
    def test_successful_initialization(self, mock_groq, mock_genai):
        """Should initialize successfully with valid environment variables"""
        mock_client = Mock()
        mock_groq.return_value = mock_client
        mock_genai.GenerativeModel.return_value = Mock()
        
        service = AgentService()
        
        assert service.groq_client == mock_client
        mock_groq.assert_called_once_with(api_key="test-key")
        mock_genai.configure.assert_called_once_with(api_key="test-gemini-key")
    
    @patch('services.agent_service.genai')
    @patch('services.agent_service.Groq')
    @patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GEMINI_API_KEY": "test-gemini-key"}, clear=True)
    def test_client_initialization_failure(self, mock_groq, mock_genai):
        """Should raise Exception when Groq client initialization fails"""
        mock_groq.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception, match="Failed to initialize agent service"):
            AgentService()


class TestProcessWorkerQuery:
    """Tests for process_worker_query method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create an AgentService with mocked client"""
        with patch('services.agent_service.genai'):
            with patch('services.agent_service.Groq'):
                with patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GEMINI_API_KEY": "test-gemini-key"}, clear=True):
                    service = AgentService()
                    service.groq_client = Mock()
                    return service
    
    @pytest.mark.asyncio
    async def test_successful_query_processing(self, mock_service):
        """Should successfully process query and return WorkerResponse"""
        # Mock the Groq API response
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "This is the response"
        mock_completion.model = "llama3-8b-8192"
        mock_completion.usage.total_tokens = 150
        
        mock_service.groq_client.chat.completions.create.return_value = mock_completion
        
        response = await mock_service.process_worker_query("What is AI?")
        
        assert isinstance(response, WorkerResponse)
        assert response.content == "This is the response"
        assert response.model == "llama3-8b-8192"
        assert response.tokens_used == 150
        
        # Verify the API was called with correct parameters
        mock_service.groq_client.chat.completions.create.assert_called_once()
        call_args = mock_service.groq_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "llama3-8b-8192"
        assert call_args[1]["messages"][0]["content"] == "What is AI?"
    
    @pytest.mark.asyncio
    async def test_empty_query_validation(self, mock_service):
        """Should raise ValueError for empty query"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await mock_service.process_worker_query("")
    
    @pytest.mark.asyncio
    async def test_whitespace_query_validation(self, mock_service):
        """Should raise ValueError for whitespace-only query"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await mock_service.process_worker_query("   ")
    
    @pytest.mark.asyncio
    @patch('time.sleep')  # Mock sleep to speed up test
    async def test_retry_logic_on_failure(self, mock_sleep, mock_service):
        """Should retry with exponential backoff on API failure"""
        # First two attempts fail, third succeeds
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Success"
        mock_completion.model = "llama3-8b-8192"
        mock_completion.usage.total_tokens = 100
        
        mock_service.groq_client.chat.completions.create.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            mock_completion
        ]
        
        response = await mock_service.process_worker_query("Test query")
        
        # Should succeed on third attempt
        assert response.content == "Success"
        assert mock_service.groq_client.chat.completions.create.call_count == 3
        
        # Verify exponential backoff delays (1s, 2s)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)  # First retry delay
        mock_sleep.assert_any_call(2.0)  # Second retry delay
    
    @pytest.mark.asyncio
    @patch('time.sleep')  # Mock sleep to speed up test
    async def test_all_retries_fail(self, mock_sleep, mock_service):
        """Should raise Exception after all retry attempts fail"""
        mock_service.groq_client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="Worker agent failed after 3 attempts"):
            await mock_service.process_worker_query("Test query")
        
        # Should attempt 3 times
        assert mock_service.groq_client.chat.completions.create.call_count == 3
        
        # Should sleep twice (not after the last attempt)
        assert mock_sleep.call_count == 2
    
    @pytest.mark.asyncio
    async def test_api_call_parameters(self, mock_service):
        """Should call Groq API with correct parameters"""
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Response"
        mock_completion.model = "llama3-8b-8192"
        mock_completion.usage.total_tokens = 100
        
        mock_service.groq_client.chat.completions.create.return_value = mock_completion
        
        await mock_service.process_worker_query("Test query")
        
        call_args = mock_service.groq_client.chat.completions.create.call_args[1]
        assert call_args["model"] == "llama3-8b-8192"
        assert call_args["temperature"] == 0.7
        assert call_args["max_tokens"] == 1024
        assert len(call_args["messages"]) == 1
        assert call_args["messages"][0]["role"] == "user"
        assert call_args["messages"][0]["content"] == "Test query"


class TestWorkerResponse:
    """Tests for WorkerResponse data model"""
    
    def test_worker_response_creation(self):
        """Should create WorkerResponse with correct attributes"""
        response = WorkerResponse(
            content="Test content",
            model="llama3-8b-8192",
            tokens_used=150
        )
        
        assert response.content == "Test content"
        assert response.model == "llama3-8b-8192"
        assert response.tokens_used == 150


class TestAuditResponse:
    """Tests for audit_response method"""
    
    @pytest.fixture
    def mock_service(self):
        """Create an AgentService with mocked clients"""
        with patch('services.agent_service.genai') as mock_genai:
            with patch('services.agent_service.Groq'):
                with patch.dict(os.environ, {"GROQ_API_KEY": "test-key", "GEMINI_API_KEY": "test-gemini-key"}, clear=True):
                    service = AgentService()
                    service.gemini_model = Mock()
                    return service
    
    @pytest.mark.asyncio
    async def test_successful_audit(self, mock_service):
        """Should successfully audit response and return AuditResult"""
        # Mock the Gemini API response
        mock_response = Mock()
        mock_response.text = '''```json
{
    "risk_score": 2,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Response appears factual and safe."
}
```'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        result = await mock_service.audit_response(
            query="What is the capital of France?",
            response="The capital of France is Paris."
        )
        
        assert result.risk_score == 2
        assert result.hallucination_detected == False
        assert result.pii_detected == False
        assert result.toxic_content_detected == False
        assert result.details == "Response appears factual and safe."
        
        # Verify the API was called
        mock_service.gemini_model.generate_content.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_audit_with_detected_risks(self, mock_service):
        """Should correctly parse audit result with detected risks"""
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": 8,
    "hallucination_detected": true,
    "pii_detected": true,
    "toxic_content_detected": false,
    "details": "Response contains unverified claims and personal information."
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        result = await mock_service.audit_response(
            query="Tell me about John Doe",
            response="John Doe lives at 123 Main St and his SSN is 123-45-6789."
        )
        
        assert result.risk_score == 8
        assert result.hallucination_detected == True
        assert result.pii_detected == True
        assert result.toxic_content_detected == False
        assert "personal information" in result.details
    
    @pytest.mark.asyncio
    async def test_empty_query_validation(self, mock_service):
        """Should raise ValueError for empty query"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await mock_service.audit_response("", "Some response")
    
    @pytest.mark.asyncio
    async def test_empty_response_validation(self, mock_service):
        """Should raise ValueError for empty response"""
        with pytest.raises(ValueError, match="Response cannot be empty"):
            await mock_service.audit_response("Some query", "")
    
    @pytest.mark.asyncio
    async def test_whitespace_query_validation(self, mock_service):
        """Should raise ValueError for whitespace-only query"""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            await mock_service.audit_response("   ", "Some response")
    
    @pytest.mark.asyncio
    async def test_whitespace_response_validation(self, mock_service):
        """Should raise ValueError for whitespace-only response"""
        with pytest.raises(ValueError, match="Response cannot be empty"):
            await mock_service.audit_response("Some query", "   ")
    
    @pytest.mark.asyncio
    async def test_parse_json_without_markdown(self, mock_service):
        """Should parse JSON response without markdown code blocks"""
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": 3,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Safe response"
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        result = await mock_service.audit_response("Query", "Response")
        
        assert result.risk_score == 3
        assert result.details == "Safe response"
    
    @pytest.mark.asyncio
    async def test_parse_json_with_markdown_blocks(self, mock_service):
        """Should strip markdown code blocks from JSON response"""
        mock_response = Mock()
        mock_response.text = '''```json
{
    "risk_score": 5,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Minor concerns"
}
```'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        result = await mock_service.audit_response("Query", "Response")
        
        assert result.risk_score == 5
        assert result.details == "Minor concerns"
    
    @pytest.mark.asyncio
    @patch('time.sleep')
    async def test_retry_logic_on_failure(self, mock_sleep, mock_service):
        """Should retry with exponential backoff on API failure"""
        # First two attempts fail, third succeeds
        mock_success_response = Mock()
        mock_success_response.text = '''{
    "risk_score": 1,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Success"
}'''
        
        mock_service.gemini_model.generate_content.side_effect = [
            Exception("API Error 1"),
            Exception("API Error 2"),
            mock_success_response
        ]
        
        result = await mock_service.audit_response("Query", "Response")
        
        # Should succeed on third attempt
        assert result.risk_score == 1
        assert result.details == "Success"
        assert mock_service.gemini_model.generate_content.call_count == 3
        
        # Verify exponential backoff delays (1s, 2s)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)
    
    @pytest.mark.asyncio
    @patch('time.sleep')
    async def test_all_retries_fail(self, mock_sleep, mock_service):
        """Should raise Exception after all retry attempts fail"""
        mock_service.gemini_model.generate_content.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="Auditor agent failed after 3 attempts"):
            await mock_service.audit_response("Query", "Response")
        
        # Should attempt 3 times
        assert mock_service.gemini_model.generate_content.call_count == 3
        
        # Should sleep twice (not after the last attempt)
        assert mock_sleep.call_count == 2
    
    @pytest.mark.asyncio
    async def test_missing_required_field(self, mock_service):
        """Should raise ValueError when required field is missing"""
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": 3,
    "hallucination_detected": false,
    "pii_detected": false
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        with pytest.raises(Exception, match="Auditor agent failed after 3 attempts"):
            await mock_service.audit_response("Query", "Response")
    
    @pytest.mark.asyncio
    async def test_risk_score_out_of_range_high(self, mock_service):
        """Should raise ValueError when risk score is above 10"""
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": 15,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Invalid score"
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        with pytest.raises(Exception, match="Auditor agent failed after 3 attempts"):
            await mock_service.audit_response("Query", "Response")
    
    @pytest.mark.asyncio
    async def test_risk_score_out_of_range_low(self, mock_service):
        """Should raise ValueError when risk score is below 0"""
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": -1,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Invalid score"
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        with pytest.raises(Exception, match="Auditor agent failed after 3 attempts"):
            await mock_service.audit_response("Query", "Response")
    
    @pytest.mark.asyncio
    async def test_risk_score_boundary_values(self, mock_service):
        """Should accept valid boundary risk scores (0 and 10)"""
        # Test risk score 0
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": 0,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Perfectly safe"
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        result = await mock_service.audit_response("Query", "Response")
        assert result.risk_score == 0
        
        # Test risk score 10
        mock_response.text = '''{
    "risk_score": 10,
    "hallucination_detected": true,
    "pii_detected": true,
    "toxic_content_detected": true,
    "details": "Maximum risk"
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        result = await mock_service.audit_response("Query", "Response")
        assert result.risk_score == 10
    
    @pytest.mark.asyncio
    async def test_audit_prompt_structure(self, mock_service):
        """Should construct audit prompt with query and response"""
        mock_response = Mock()
        mock_response.text = '''{
    "risk_score": 1,
    "hallucination_detected": false,
    "pii_detected": false,
    "toxic_content_detected": false,
    "details": "Safe"
}'''
        
        mock_service.gemini_model.generate_content.return_value = mock_response
        
        test_query = "What is AI?"
        test_response = "AI is artificial intelligence."
        
        await mock_service.audit_response(test_query, test_response)
        
        # Verify the prompt contains both query and response
        call_args = mock_service.gemini_model.generate_content.call_args[0][0]
        assert test_query in call_args
        assert test_response in call_args
        assert "hallucinations" in call_args.lower()
        assert "pii" in call_args.lower()
        assert "toxic" in call_args.lower()


class TestAuditResult:
    """Tests for AuditResult data model"""
    
    def test_audit_result_creation(self):
        """Should create AuditResult with correct attributes"""
        from services.agent_service import AuditResult
        
        result = AuditResult(
            risk_score=5,
            hallucination_detected=True,
            pii_detected=False,
            toxic_content_detected=True,
            details="Some issues detected"
        )
        
        assert result.risk_score == 5
        assert result.hallucination_detected == True
        assert result.pii_detected == False
        assert result.toxic_content_detected == True
        assert result.details == "Some issues detected"
    
    def test_audit_result_to_dict(self):
        """Should convert AuditResult to dictionary"""
        from services.agent_service import AuditResult
        
        result = AuditResult(
            risk_score=3,
            hallucination_detected=False,
            pii_detected=False,
            toxic_content_detected=False,
            details="All clear"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["risk_score"] == 3
        assert result_dict["hallucination_detected"] == False
        assert result_dict["pii_detected"] == False
        assert result_dict["toxic_content_detected"] == False
        assert result_dict["details"] == "All clear"
        assert len(result_dict) == 5
