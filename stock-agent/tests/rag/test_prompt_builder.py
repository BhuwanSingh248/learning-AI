import pytest
import json
from pydantic import ValidationError
from src.llm.prompt_builder import PromptBuilder
from src.llm.models import RecommendationResponse

def test_load_system_prompt_success():
    """Verify that system prompt file is loaded correctly by version."""
    system_prompt = PromptBuilder.load_system_prompt("v1")
    assert "You are a professional financial analysis assistant" in system_prompt
    assert "recommendation" in system_prompt

def test_load_system_prompt_not_found():
    """Verify that loading an invalid version raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        PromptBuilder.load_system_prompt("invalid_v99")

def test_build_recommendation_prompt():
    """Verify build_recommendation_prompt formats system and user prompts correctly."""
    query = "Should I buy Apple stock?"
    symbol = "AAPL"
    context = "[1] Apple reports higher revenue."
    
    payload = PromptBuilder.build_recommendation_prompt(query, symbol, context, version="v1")
    
    assert "AAPL" in payload.user_prompt
    assert query in payload.user_prompt
    assert "--- START OF CONTEXT ---" in payload.user_prompt
    assert context in payload.user_prompt
    
    assert "You are a professional financial analysis assistant" in payload.system_prompt

def test_recommendation_response_validation_success():
    """Verify that RecommendationResponse parses valid JSON recommendation data successfully."""
    valid_json = {
        "recommendation": "BUY",
        "confidence": 0.85,
        "reasoning": "Solid financial growth beat expectations.",
        "citations": [1, 2]
    }
    
    response = RecommendationResponse(**valid_json)
    assert response.recommendation == "BUY"
    assert response.confidence == 0.85
    assert response.reasoning == "Solid financial growth beat expectations."
    assert response.citations == [1, 2]

def test_recommendation_response_validation_failure():
    """Verify that RecommendationResponse raises validation errors on bad datatypes or missing fields."""
    invalid_json = {
        "recommendation": "BUY",
        "confidence": "high",  # Should be float
        "citations": [1]
        # Missing reasoning
    }
    
    with pytest.raises(ValidationError):
        RecommendationResponse(**invalid_json)
