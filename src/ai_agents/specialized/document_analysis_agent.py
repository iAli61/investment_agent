"""
Document Analysis Agent implementation for the Property Investment Analysis Application.

This specialized agent extracts and analyzes information from property documents.
"""

import logging
from typing import Dict, Any, List, Optional
import json

from agents import Agent, function_tool, OpenAIChatCompletionsModel
from pydantic import BaseModel

from ..tools.investment_tools import (
    extract_document_text,
    classify_document_type,
    parse_property_text,
    generate_section_explanation
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentAnalysisRequest(BaseModel):
    """Document analysis request parameters."""
    document_type: str
    document_text: str
    extraction_targets: Optional[List[str]] = None

class DocumentAnalysisResult(BaseModel):
    """Result from the Document Analysis Agent."""
    extracted_data: Dict[str, Any]
    structure_analysis: Optional[Dict[str, Any]] = None
    confidence_scores: Dict[str, float]
    key_insights: List[str]
    explanation: str

def create_document_analysis_agent() -> Agent:
    """Create and configure the Document Analysis Agent."""
    
    # Define agent instructions
    instructions = """
    You are a specialized Document Analysis Agent for property investment analysis.
    
    Your task is to extract, structure, and analyze information from property-related documents:
    1. Property listings
    2. Sales contracts
    3. Lease agreements
    4. Inspection reports
    5. Property management reports
    6. Financial documents
    
    Follow these steps when processing documents:
    1. Identify document type
    2. Extract key data points (dates, names, amounts, property details)
    3. Identify standard sections relevant to investment analysis
    4. Flag any unusual terms, conditions, or restrictions
    5. Structure information for further analysis
    
    Always include confidence scores for extracted data points and highlight any areas 
    of ambiguity or uncertainty.
    
    For property listings and inspection reports, extract:
    - Property details (size, rooms, features, conditions)
    - Noted issues or required repairs
    - Estimated costs of repairs
    
    For lease agreements, extract:
    - Rent amounts
    - Security deposits
    - Term duration
    - Renewal conditions
    - Tenant responsibilities
    - Special clauses
    
    For financial documents, extract:
    - Income figures
    - Expense categories
    - Profit calculations
    - Tax implications
    """
    
    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)

    # Create and return the agent
    return Agent(
        name="Document Analysis Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=[
            extract_document_text,
            classify_document_type,
            parse_property_text,
            generate_section_explanation
        ]
    )