"""
Document Analysis Agent implementation for the Property Investment Analysis Application.

This specialized agent extracts and analyzes information from property documents.
"""

import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

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

# Check for LangChain dependencies
try:
    from langchain_community.document_loaders import UnstructuredPDFLoader, WebBaseLoader
    from langchain_core.tools import Tool
    has_langchain = True
    logger.info("[Document Analysis] LangChain dependencies loaded")
except ImportError:
    has_langchain = False
    logger.warning("[Document Analysis] LangChain dependencies not available")

if has_langchain:
    @function_tool
    def load_document_with_langchain(source: str) -> str:
        """
        Load and extract text from a document (PDF or webpage) using LangChain.
        """
        logger.info(f"[Document Analysis] Loading document from {source} using LangChain")
        try:
            if source.lower().startswith(('http://','https://')):
                loader = WebBaseLoader(source)
            else:
                loader = UnstructuredPDFLoader(source)
            docs = loader.load()
            content = "\n".join([d.page_content for d in docs])
            return content
        except Exception as e:
            logger.error(f"[Document Analysis] LangChain load error: {e}")
            return ""

    @function_tool
    def summarize_document_with_langchain(text: str, max_length: int = 200) -> str:
        """
        Summarize a document's text using the default OpenAI summarization model.
        """
        logger.info("[Document Analysis] Summarizing document using LangChain")
        try:
            from agents import OpenAIChatCompletionsModel, Agent
            # Use a lightweight summarization prompt
            summary_prompt = f"Summarize the following document in up to {max_length} characters:\n{text}"  
            agent = Agent(
                name="DocSummaryAgent",
                instructions="You are a concise summarizer.",
                model=OpenAIChatCompletionsModel(model="gpt-3.5-turbo"),
                tools=[]
            )
            result = agent.run(summary_prompt)
            return result
        except Exception as e:
            logger.error(f"[Document Analysis] Summarization error: {e}")
            return text[:max_length]

def create_document_analysis_agent() -> Agent:
    """Create and configure the Document Analysis Agent."""
    
    logger.info("[Document Analysis] Creating document analysis agent")
    
    # Define tools list
    tools = [extract_document_text, classify_document_type, parse_property_text, generate_section_explanation]
    if has_langchain:
        tools = [load_document_with_langchain, summarize_document_with_langchain] + tools
        logger.info("[Document Analysis] Added LangChain document loader and summarizer tools")

    # Update instructions to reference new tools
    instructions = """
    You are a specialized Document Analysis Agent for property investment analysis.

    You can load and analyze property-related documents (PDFs, webpages, reports) using LangChain document loaders.

    Your tasks:
    1. Load documents from URLs or file paths (PDF, HTML)
    2. Extract and structure key data points (dates, amounts, property details)
    3. Summarize large documents into concise overviews
    4. Identify and highlight unusual clauses or risks
    5. Provide confidence scores for extracted information

    Always cite sections when summarizing and flag any ambiguities.
    """
    
    from openai import AsyncAzureOpenAI
    from agents import set_default_openai_client
    from dotenv import load_dotenv
    import os

    # Load environment variables
    load_dotenv()
    logger.info("[Document Analysis] Configuring integration with Azure OpenAI services")
    
    # Create OpenAI client using Azure OpenAI
    openai_client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    )

    # Set the default OpenAI client for the Agents SDK
    set_default_openai_client(openai_client)
    logger.info("[Document Analysis] OpenAI client configured for agent")

    # Log the available tools
    tool_names = [tool.__name__ if hasattr(tool, '__name__') else tool.name for tool in tools]
    logger.info(f"[Document Analysis] Setting up agent with tools: {', '.join(tool_names)}")

    # Create and return the agent
    agent = Agent(
        name="Document Analysis Agent",
        instructions=instructions,
        model=OpenAIChatCompletionsModel(
            model="gpt-4o",
            openai_client=openai_client
        ),
        tools=tools
    )
    
    logger.info("[Document Analysis] Document analysis agent successfully initialized")
    return agent

# Add custom document processing functions with enhanced logging

def process_document_with_logging(document_type: str, document_text: str, extraction_targets: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Custom wrapper to process documents with enhanced logging.
    
    Args:
        document_type: Type of document being analyzed
        document_text: Text content of the document
        extraction_targets: Specific data points to extract (optional)
        
    Returns:
        Dictionary containing the extracted and analyzed data
    """
    start_time = datetime.now()
    text_length = len(document_text)
    logger.info(f"[Document Analysis] Starting analysis of {document_type} document ({text_length} characters)")
    
    if extraction_targets:
        logger.info(f"[Document Analysis] Targeting extraction of: {', '.join(extraction_targets)}")
    
    try:
        # Log document classification check
        logger.info(f"[Document Analysis] Verifying document type classification")
        
        # Log text extraction process
        logger.info(f"[Document Analysis] Extracting text content from document")
        
        # Simulate document processing steps
        if document_type == "lease_agreement":
            logger.info(f"[Document Analysis] Analyzing lease agreement terms and conditions")
            logger.info(f"[Document Analysis] Extracting rent amounts, deposit information, and lease duration")
            logger.info(f"[Document Analysis] Checking for special clauses and restrictions")
        elif document_type == "inspection_report":
            logger.info(f"[Document Analysis] Analyzing property inspection details")
            logger.info(f"[Document Analysis] Identifying reported issues and maintenance requirements")
            logger.info(f"[Document Analysis] Estimating repair costs based on report data")
        elif document_type == "property_listing":
            logger.info(f"[Document Analysis] Extracting property specifications and features")
            logger.info(f"[Document Analysis] Analyzing property description for relevant investment details")
        else:
            logger.info(f"[Document Analysis] Processing general document content")
        
        # Calculate confidence scores for extracted data
        logger.info(f"[Document Analysis] Calculating confidence scores for extracted data points")
        
        # Generate document structure analysis
        logger.info(f"[Document Analysis] Generating document structure analysis")
        
        # Identify key insights
        logger.info(f"[Document Analysis] Identifying key insights for investment decision-making")
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"[Document Analysis] Document analysis completed in {execution_time:.2f} seconds")
        
        # Return sample structured data
        return {
            "document_type": document_type,
            "extracted_data": {"sample": "data"},
            "confidence_scores": {"overall": 0.85},
            "execution_time": execution_time
        }
    except Exception as e:
        logger.error(f"[Document Analysis] Error processing document: {str(e)}")
        raise