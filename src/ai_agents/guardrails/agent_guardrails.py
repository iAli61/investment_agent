"""
Guardrails for AI agents in the Property Investment Analysis Application.

This module implements safety measures to ensure agent behavior stays within defined boundaries.
"""

import logging
import json
import re
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, TResponseInputItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RelevanceCheckResult(BaseModel):
    """Result of a relevance check on user input."""
    is_relevant: bool
    reasoning: str
    confidence: float

class SafetyCheckResult(BaseModel):
    """Result of a safety check on user input."""
    is_safe: bool
    reasoning: str
    confidence: float
    blocked_categories: Optional[List[str]] = None

class PIICheckResult(BaseModel):
    """Result of a PII check on text."""
    contains_pii: bool
    pii_types: Optional[List[str]] = None
    redacted_text: Optional[str] = None

class JSONSchemaCheckResult(BaseModel):
    contains_invalid_json: bool
    error_message: Optional[str] = None
    model_config = {"extra": "forbid"}

async def output_schema_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: List[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Guardrail to ensure tool outputs are valid JSON.
    """
    # Check recent messages for tool outputs
    for msg in getattr(ctx.context, 'messages', []):
        if hasattr(msg, 'role') and msg.role == 'tool' and hasattr(msg, 'content'):
            content = msg.content
            try:
                json.loads(content)
            except Exception as e:
                result = JSONSchemaCheckResult(
                    contains_invalid_json=True,
                    error_message=str(e)
                )
                logger.warning(f"JSON schema guardrail triggered: invalid JSON from tool: {str(e)}")
                return GuardrailFunctionOutput(
                    output_info=result.dict(),
                    tripwire_triggered=True
                )
    # All tool outputs valid JSON
    result = JSONSchemaCheckResult(contains_invalid_json=False)
    return GuardrailFunctionOutput(
        output_info=result.dict(),
        tripwire_triggered=False
    )

async def create_guardrails() -> List[Callable]:
    """Create and return a list of guardrail functions."""
    return [
        relevance_check_guardrail,
        safety_check_guardrail,
        pii_filter_guardrail,
        output_schema_guardrail
    ]

async def relevance_check_guardrail(
    ctx: RunContextWrapper, 
    agent: Agent, 
    input: List[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Check if the user input is relevant to property investment analysis.
    
    Args:
        ctx: The run context
        agent: The agent instance
        input: The user input
        
    Returns:
        GuardrailFunctionOutput with result and whether tripwire was triggered
    """
    input_text = " ".join([item.content for item in input if hasattr(item, 'content')])
    
    # First perform a simple keyword-based check
    investment_keywords = [
        "property", "invest", "apartment", "house", "real estate", "mortgage", 
        "rent", "buy", "price", "market", "loan", "finance", "cash flow", 
        "closing cost", "ROI", "return", "rental", "tax", "depreciation"
    ]
    
    # Check if input contains any investment-related keywords
    contains_keywords = any(keyword.lower() in input_text.lower() for keyword in investment_keywords)
    
    # Perform more advanced analysis if needed
    # In production, this would use a classification model
    
    # For this implementation, we'll use a simple rule-based approach
    if contains_keywords:
        result = RelevanceCheckResult(
            is_relevant=True,
            reasoning="Input contains property investment related keywords",
            confidence=0.85
        )
    else:
        result = RelevanceCheckResult(
            is_relevant=False,
            reasoning="Input does not appear to be related to property investment analysis",
            confidence=0.75
        )
    
    # Log the result
    logger.info(f"Relevance check result: {result.is_relevant}, confidence: {result.confidence}")
    
    # Return the result
    return GuardrailFunctionOutput(
        output_info=result.dict(),
        tripwire_triggered=not result.is_relevant  # Tripwire triggers when content is not relevant
    )

async def safety_check_guardrail(
    ctx: RunContextWrapper, 
    agent: Agent, 
    input: List[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Check if the user input is safe (no harmful content, no prompt injection attempts).
    
    Args:
        ctx: The run context
        agent: The agent instance
        input: The user input
        
    Returns:
        GuardrailFunctionOutput with result and whether tripwire was triggered
    """
    input_text = " ".join([item.content for item in input if hasattr(item, 'content')])
    
    # Check for potential prompt injection patterns
    injection_patterns = [
        r"ignore previous instructions",
        r"disregard .*instructions",
        r"forget .*instructions",
        r"your instructions are",
        r"your prompt is",
        r"you are actually",
        r"system prompt"
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            result = SafetyCheckResult(
                is_safe=False,
                reasoning=f"Potential prompt injection attempt detected",
                confidence=0.9,
                blocked_categories=["prompt_injection"]
            )
            
            logger.warning(f"Safety check blocked potential prompt injection: {input_text}")
            
            return GuardrailFunctionOutput(
                output_info=result.dict(),
                tripwire_triggered=True
            )
    
    # In production, additional checks for harmful content would be performed
    
    # Return safe result
    result = SafetyCheckResult(
        is_safe=True,
        reasoning="No unsafe content detected",
        confidence=0.85,
        blocked_categories=[]
    )
    
    return GuardrailFunctionOutput(
        output_info=result.dict(),
        tripwire_triggered=False
    )

async def pii_filter_guardrail(
    ctx: RunContextWrapper, 
    agent: Agent, 
    input: List[TResponseInputItem]
) -> GuardrailFunctionOutput:
    """
    Check if the text contains personally identifiable information (PII).
    
    Args:
        ctx: The run context
        agent: The agent instance
        input: The text to check
        
    Returns:
        GuardrailFunctionOutput with result and whether tripwire was triggered
    """
    input_text = " ".join([item.content for item in input if hasattr(item, 'content')])
    
    # Check for common PII patterns
    pii_patterns = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone_number": r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b',
        "social_security": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
        "credit_card": r'\b(?:\d{4}[- ]?){3}\d{4}\b',
        "address": r'\b\d+\s+[A-Za-z]+\s+(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Drive|Dr)[.,]?\b'
    }
    
    found_pii = []
    redacted_text = input_text
    
    for pii_type, pattern in pii_patterns.items():
        if re.search(pattern, input_text, re.IGNORECASE):
            found_pii.append(pii_type)
            # Redact PII in the text
            redacted_text = re.sub(pattern, f"[REDACTED {pii_type.upper()}]", redacted_text, flags=re.IGNORECASE)
    
    if found_pii:
        result = PIICheckResult(
            contains_pii=True,
            pii_types=found_pii,
            redacted_text=redacted_text
        )
        
        logger.warning(f"PII detected: {found_pii}")
        
        # We don't necessarily want to block the input, just redact the PII
        # The context will be updated with the redacted text
        
        # Update the context with redacted text
        if hasattr(ctx, 'context') and hasattr(ctx.context, 'messages'):
            for i, message in enumerate(ctx.context.messages):
                if hasattr(message, 'content') and message.content == input_text:
                    ctx.context.messages[i].content = redacted_text
        
        return GuardrailFunctionOutput(
            output_info=result.dict(),
            tripwire_triggered=False  # Don't block, just redact
        )
    
    # No PII found
    result = PIICheckResult(
        contains_pii=False,
        pii_types=[],
        redacted_text=input_text
    )
    
    return GuardrailFunctionOutput(
        output_info=result.dict(),
        tripwire_triggered=False
    )