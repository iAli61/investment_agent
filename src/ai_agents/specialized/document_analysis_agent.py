"""
Document Analysis Agent implementation for the Property Investment Analysis Application.

This specialized agent extracts key information from property documents like leases and inspection reports.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from agents import Agent, function_tool
from pydantic import BaseModel

from ..tools.investment_tools import (
    extract_document_text,
    classify_document_type,
    parse_property_text
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentAnalysisRequest(BaseModel):
    """Document analysis request parameters."""
    document_content: str  # Base64 encoded or file path
    expected_document_type: Optional[str] = None

class DocumentAnalysisResult(BaseModel):
    """Result from the Document Analysis Agent."""
    document_type: str
    extracted_information: Dict[str, Any]
    potential_issues: Optional[List[Dict[str, Any]]] = None
    confidence_scores: Dict[str, float]
    missing_information: Optional[List[str]] = None

def create_document_analysis_agent() -> Agent:
    """Create and configure the Document Analysis Agent."""
    
    # Define agent instructions
    instructions = """
    You are a specialized Document Analysis Agent for property investment analysis.
    
    Your task is to extract relevant information from property documents such as:
    1. Lease agreements
    2. Inspection reports
    3. Title deeds
    4. Property listings
    5. Appraisal reports
    
    Follow these steps when processing documents:
    1. Process uploaded document and convert to text
    2. Classify document type (lease, inspection report, title)
    3. Extract key information based on document type
    4. Flag potential issues (lease violations, inspection concerns)
    5. Compare with user-entered data and highlight discrepancies
    6. Identify missing critical information
    
    For lease agreements, extract:
    - Monthly rent amount and payment terms
    - Lease duration and renewal options
    - Security deposit amount
    - Tenant and landlord responsibilities
    - Special clauses or conditions
    
    For inspection reports, extract:
    - Property condition assessments
    - Identified issues or defects
    - Recommended repairs and maintenance
    - Estimated costs for repairs
    - Safety concerns or code violations
    
    Always provide confidence scores for extracted information and highlight any
    information that may be missing or unclear in the document.
    """
    
    # Create and return the agent
    return Agent(
        name="Document Analysis Agent",
        instructions=instructions,
        tools=[
            extract_document_text,
            classify_document_type,
            parse_property_text
        ]
    )