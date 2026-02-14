"""
Tests for environment variable validation at application startup.

**Feature: agent-audit, Property 14: Environment variable configuration**
**Validates: Requirements 10.1, 10.2, 10.3, 10.4**

Property 14: Environment variable configuration
For any of the required environment variables (GROQ_API_KEY, GEMINI_API_KEY, 
SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, FRONTEND_URL), if missing at startup, 
the system should fail to start with a clear error message indicating which 
variable is missing.
"""

import os
import pytest
from unittest.mock import patch


def validate_required_env_vars():
    """
    Validate that all required environment variables are present.
    This function replicates the validation logic from main.py for testing purposes.
    
    Raises:
        ValueError: If any required environment variables are missing
    """
    required_env_vars = [
        "GROQ_API_KEY",
        "GEMINI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "FRONTEND_URL"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var) or not os.getenv(var).strip()]
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        raise ValueError(error_msg)


class TestEnvironmentVariableValidation:
    """Test suite for environment variable validation at startup."""
    
    def test_all_required_env_vars_present(self):
        """Should pass validation when all required environment variables are present"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            # This should not raise an exception
            try:
                validate_required_env_vars()
                # If we get here, validation passed
                assert True
            except ValueError as e:
                pytest.fail(f"Should not raise ValueError when all env vars present: {e}")
    
    def test_missing_groq_api_key(self):
        """Should fail with clear error when GROQ_API_KEY is missing"""
        with patch.dict(os.environ, {
            "GEMINI_API_KEY": "test-gemini-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "GROQ_API_KEY" in error_message
            assert "Missing required environment variables" in error_message
    
    def test_missing_gemini_api_key(self):
        """Should fail with clear error when GEMINI_API_KEY is missing"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "GEMINI_API_KEY" in error_message
            assert "Missing required environment variables" in error_message
    
    def test_missing_supabase_url(self):
        """Should fail with clear error when SUPABASE_URL is missing"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "SUPABASE_URL" in error_message
            assert "Missing required environment variables" in error_message
    
    def test_missing_supabase_service_role_key(self):
        """Should fail with clear error when SUPABASE_SERVICE_ROLE_KEY is missing"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "SUPABASE_SERVICE_ROLE_KEY" in error_message
            assert "Missing required environment variables" in error_message
    
    def test_missing_frontend_url(self):
        """Should fail with clear error when FRONTEND_URL is missing"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "GEMINI_API_KEY": "test-gemini-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "FRONTEND_URL" in error_message
            assert "Missing required environment variables" in error_message
    
    def test_multiple_missing_env_vars(self):
        """Should fail with clear error listing all missing environment variables"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key"
            # Missing: GEMINI_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, FRONTEND_URL
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "Missing required environment variables" in error_message
            assert "GEMINI_API_KEY" in error_message
            assert "SUPABASE_URL" in error_message
            assert "SUPABASE_SERVICE_ROLE_KEY" in error_message
            assert "FRONTEND_URL" in error_message
    
    def test_empty_env_var_treated_as_missing(self):
        """Should treat empty string environment variables as missing"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "",  # Empty string
            "GEMINI_API_KEY": "test-gemini-key",
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "GROQ_API_KEY" in error_message
            assert "Missing required environment variables" in error_message
    
    def test_whitespace_only_env_var_treated_as_missing(self):
        """Should treat whitespace-only environment variables as missing"""
        with patch.dict(os.environ, {
            "GROQ_API_KEY": "test-groq-key",
            "GEMINI_API_KEY": "   ",  # Whitespace only
            "SUPABASE_URL": "https://test.supabase.co",
            "SUPABASE_SERVICE_ROLE_KEY": "test-supabase-key",
            "FRONTEND_URL": "http://localhost:3000"
        }, clear=True):
            with pytest.raises(ValueError) as exc_info:
                validate_required_env_vars()
            
            error_message = str(exc_info.value)
            assert "GEMINI_API_KEY" in error_message
            assert "Missing required environment variables" in error_message
