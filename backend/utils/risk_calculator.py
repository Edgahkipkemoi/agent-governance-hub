"""
Risk Calculator Utility

This module provides functions for calculating risk status and metrics
based on risk scores from the auditor agent.
"""

from typing import List, Dict, Any


def calculate_risk_status(risk_score: int) -> str:
    """
    Convert a risk score (0-10) to a risk status category.
    
    Args:
        risk_score: Integer from 0 to 10 indicating risk severity
        
    Returns:
        Risk status: "Safe" (0-3), "Warning" (4-6), or "Flagged" (7-10)
        
    Raises:
        ValueError: If risk_score is not between 0 and 10
    """
    if not isinstance(risk_score, int) or risk_score < 0 or risk_score > 10:
        raise ValueError(f"Risk score must be an integer between 0 and 10, got: {risk_score}")
    
    if risk_score <= 3:
        return "Safe"
    elif risk_score <= 6:
        return "Warning"
    else:
        return "Flagged"


def calculate_average_risk(logs: List[Dict[str, Any]]) -> float:
    """
    Calculate the average risk score across a list of audit logs.
    
    Args:
        logs: List of audit log dictionaries, each containing an 'audit' field
              with a 'risk_score' value
              
    Returns:
        Average risk score as a float. Returns 0.0 if logs list is empty.
        
    Raises:
        KeyError: If a log is missing the 'audit' or 'risk_score' field
        TypeError: If risk_score is not a number
    """
    if not logs:
        return 0.0
    
    total_score = 0
    for log in logs:
        if 'audit' not in log:
            raise KeyError(f"Log missing 'audit' field: {log}")
        
        audit = log['audit']
        if 'risk_score' not in audit:
            raise KeyError(f"Audit missing 'risk_score' field: {audit}")
        
        risk_score = audit['risk_score']
        if not isinstance(risk_score, (int, float)):
            raise TypeError(f"Risk score must be a number, got: {type(risk_score)}")
        
        total_score += risk_score
    
    return total_score / len(logs)
