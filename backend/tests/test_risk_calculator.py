"""
Unit tests for risk calculator utility
"""

import pytest
from hypothesis import given, strategies as st, settings
from backend.utils.risk_calculator import calculate_risk_status, calculate_average_risk


class TestCalculateRiskStatus:
    """Tests for calculate_risk_status function"""
    
    def test_safe_status_lower_bound(self):
        """Risk score 0 should return Safe"""
        assert calculate_risk_status(0) == "Safe"
    
    def test_safe_status_upper_bound(self):
        """Risk score 3 should return Safe"""
        assert calculate_risk_status(3) == "Safe"
    
    def test_safe_status_middle(self):
        """Risk score 1-2 should return Safe"""
        assert calculate_risk_status(1) == "Safe"
        assert calculate_risk_status(2) == "Safe"
    
    def test_warning_status_lower_bound(self):
        """Risk score 4 should return Warning"""
        assert calculate_risk_status(4) == "Warning"
    
    def test_warning_status_upper_bound(self):
        """Risk score 6 should return Warning"""
        assert calculate_risk_status(6) == "Warning"
    
    def test_warning_status_middle(self):
        """Risk score 5 should return Warning"""
        assert calculate_risk_status(5) == "Warning"
    
    def test_flagged_status_lower_bound(self):
        """Risk score 7 should return Flagged"""
        assert calculate_risk_status(7) == "Flagged"
    
    def test_flagged_status_upper_bound(self):
        """Risk score 10 should return Flagged"""
        assert calculate_risk_status(10) == "Flagged"
    
    def test_flagged_status_middle(self):
        """Risk score 8-9 should return Flagged"""
        assert calculate_risk_status(8) == "Flagged"
        assert calculate_risk_status(9) == "Flagged"
    
    def test_invalid_negative_score(self):
        """Negative risk score should raise ValueError"""
        with pytest.raises(ValueError, match="Risk score must be an integer between 0 and 10"):
            calculate_risk_status(-1)
    
    def test_invalid_too_high_score(self):
        """Risk score above 10 should raise ValueError"""
        with pytest.raises(ValueError, match="Risk score must be an integer between 0 and 10"):
            calculate_risk_status(11)
    
    def test_invalid_non_integer(self):
        """Non-integer risk score should raise ValueError"""
        with pytest.raises(ValueError, match="Risk score must be an integer between 0 and 10"):
            calculate_risk_status(5.5)


class TestCalculateAverageRisk:
    """Tests for calculate_average_risk function"""
    
    def test_empty_logs_list(self):
        """Empty logs list should return 0.0"""
        assert calculate_average_risk([]) == 0.0
    
    def test_single_log(self):
        """Single log should return its risk score"""
        logs = [{"audit": {"risk_score": 5}}]
        assert calculate_average_risk(logs) == 5.0
    
    def test_multiple_logs_same_score(self):
        """Multiple logs with same score should return that score"""
        logs = [
            {"audit": {"risk_score": 3}},
            {"audit": {"risk_score": 3}},
            {"audit": {"risk_score": 3}}
        ]
        assert calculate_average_risk(logs) == 3.0
    
    def test_multiple_logs_different_scores(self):
        """Multiple logs with different scores should return correct average"""
        logs = [
            {"audit": {"risk_score": 0}},
            {"audit": {"risk_score": 5}},
            {"audit": {"risk_score": 10}}
        ]
        assert calculate_average_risk(logs) == 5.0
    
    def test_average_with_decimal_result(self):
        """Average calculation should handle decimal results"""
        logs = [
            {"audit": {"risk_score": 1}},
            {"audit": {"risk_score": 2}},
            {"audit": {"risk_score": 3}}
        ]
        assert calculate_average_risk(logs) == 2.0
    
    def test_float_risk_scores(self):
        """Should handle float risk scores"""
        logs = [
            {"audit": {"risk_score": 2.5}},
            {"audit": {"risk_score": 3.5}}
        ]
        assert calculate_average_risk(logs) == 3.0
    
    def test_missing_audit_field(self):
        """Missing audit field should raise KeyError"""
        logs = [{"query": "test"}]
        with pytest.raises(KeyError, match="Log missing 'audit' field"):
            calculate_average_risk(logs)
    
    def test_missing_risk_score_field(self):
        """Missing risk_score field should raise KeyError"""
        logs = [{"audit": {"other_field": "value"}}]
        with pytest.raises(KeyError, match="Audit missing 'risk_score' field"):
            calculate_average_risk(logs)
    
    def test_invalid_risk_score_type(self):
        """Non-numeric risk score should raise TypeError"""
        logs = [{"audit": {"risk_score": "invalid"}}]
        with pytest.raises(TypeError, match="Risk score must be a number"):
            calculate_average_risk(logs)



# Property-Based Tests
class TestRiskCalculatorPropertyTests:
    """Property-based tests for risk calculator"""
    
    @given(st.integers(min_value=0, max_value=10))
    @settings(max_examples=100, deadline=None)
    def test_property_5_risk_status_classification(self, risk_score):
        """
        **Feature: agent-audit, Property 5: Risk status classification**
        
        For any risk score value from 0-10, the calculated status should be 
        "Safe" for scores 0-3, "Warning" for scores 4-6, and "Flagged" for 
        scores 7-10.
        
        **Validates: Requirements 2.4**
        """
        status = calculate_risk_status(risk_score)
        
        # Property: Status must be one of the three valid values
        assert status in ["Safe", "Warning", "Flagged"], \
            f"Status must be Safe, Warning, or Flagged, got: {status}"
        
        # Property: Correct classification based on score ranges
        if 0 <= risk_score <= 3:
            assert status == "Safe", \
                f"Risk score {risk_score} should be classified as Safe, got: {status}"
        elif 4 <= risk_score <= 6:
            assert status == "Warning", \
                f"Risk score {risk_score} should be classified as Warning, got: {status}"
        elif 7 <= risk_score <= 10:
            assert status == "Flagged", \
                f"Risk score {risk_score} should be classified as Flagged, got: {status}"
