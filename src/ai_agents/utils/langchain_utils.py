"""
Utility functions for integrating LangChain components with the agent system.

This module provides helper functions for creating LangChain-compatible objects
and converting between different formats used in the system.
"""

import logging
from typing import Dict, List, Any, Optional, Union
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_langchain_prompt_context(
    user_query: str,
    knowledge_snippets: Optional[List[str]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prepare a context dictionary for use in LangChain prompts.
    
    Args:
        user_query: The current user query
        knowledge_snippets: Optional list of knowledge snippets from RAG
        conversation_history: Optional conversation history
        user_preferences: Optional user preferences
        
    Returns:
        A context dictionary for use in LangChain prompts
    """
    context = {
        "query": user_query,
    }
    
    # Add knowledge if available
    if knowledge_snippets and len(knowledge_snippets) > 0:
        knowledge_text = "\n\n".join([f"- {k}" for k in knowledge_snippets])
        context["knowledge"] = knowledge_text
    
    # Add conversation history if available
    if conversation_history and len(conversation_history) > 0:
        history_text = "\n".join([
            f"{turn['role']}: {turn['content']}" 
            for turn in conversation_history
        ])
        context["conversation_history"] = history_text
    
    # Add user preferences if available
    if user_preferences and len(user_preferences) > 0:
        preferences_text = "\n".join([
            f"- {key}: {value}" 
            for key, value in user_preferences.items()
        ])
        context["user_preferences"] = preferences_text
    
    return context

def create_langchain_chat_messages(
    conversation_history: List[Dict[str, str]],
    include_system_message: bool = True,
    system_message: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Convert our conversation history format to LangChain chat messages.
    
    Args:
        conversation_history: List of conversation turns
        include_system_message: Whether to include a system message
        system_message: Optional custom system message
        
    Returns:
        List of LangChain-compatible chat messages
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
        
        messages = []
        
        # Add system message if requested
        if include_system_message:
            if not system_message:
                system_message = (
                    "You are an AI assistant helping with property investment analysis. "
                    "Provide accurate, helpful information based on your knowledge and the conversation context."
                )
            messages.append(SystemMessage(content=system_message))
        
        # Add conversation history
        for turn in conversation_history:
            role = turn.get("role", "")
            content = turn.get("content", "")
            
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "agent":
                messages.append(AIMessage(content=content))
            # Skip other roles
        
        return messages
    
    except ImportError:
        logger.warning("LangChain not installed. Returning raw messages.")
        return conversation_history

def convert_agent_context_to_memory(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert agent context dictionary to memory.
    
    Args:
        context: Agent context dictionary
        
    Returns:
        Memory-compatible dictionary
    """
    memory_data = {}
    
    # Extract conversation history if available
    if "conversation_history" in context:
        memory_data["conversation_history"] = context["conversation_history"]
    
    # Extract user preferences if available
    if "user_preferences" in context:
        memory_data["user_preferences"] = context["user_preferences"]
    
    # Extract parameters if available
    if "parameters" in context:
        memory_data["parameters"] = context["parameters"]
    
    return memory_data

def get_azure_langchain_credentials():
    """
    Get Azure OpenAI credentials for LangChain from environment variables.
    
    Returns:
        Dictionary with Azure OpenAI credentials
    """
    credentials = {}
    
    # Check for Azure OpenAI credentials
    if os.environ.get("AZURE_OPENAI_API_KEY"):
        credentials["api_key"] = os.environ["AZURE_OPENAI_API_KEY"]
    
    if os.environ.get("AZURE_OPENAI_ENDPOINT"):
        credentials["azure_endpoint"] = os.environ["AZURE_OPENAI_ENDPOINT"]
    
    if os.environ.get("AZURE_OPENAI_API_VERSION"):
        credentials["api_version"] = os.environ["AZURE_OPENAI_API_VERSION"]
    else:
        credentials["api_version"] = "2023-12-01-preview"  # Default version
    
    if os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"):
        credentials["azure_deployment"] = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]
    
    return credentials

def create_langchain_rag_retriever(vector_store, search_kwargs=None):
    """
    Create a LangChain retriever from our vector store.
    
    Args:
        vector_store: Our vector store implementation
        search_kwargs: Optional search parameters
        
    Returns:
        A LangChain-compatible retriever
    """
    try:
        from langchain_core.vectorstores import VectorStoreRetriever
        from ..rag.vector_store import VectorStore
        
        if not search_kwargs:
            search_kwargs = {"k": 3}
        
        # Create a LangChain-compatible retriever
        retriever = VectorStoreRetriever(
            vectorstore=vector_store.vector_db,
            search_kwargs=search_kwargs,
            search_type="similarity"
        )
        
        return retriever
    
    except ImportError:
        logger.warning("LangChain not installed. Returning None for retriever.")
        return None