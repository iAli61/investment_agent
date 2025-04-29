"""
Vector Database Integration for Property Investment Knowledge Retrieval.

This module provides vector database operations for storing and retrieving
property investment knowledge to enhance AI agent capabilities with RAG.
"""

import logging
import os
from typing import List, Dict, Any, Optional, Union
import numpy as np
from pydantic import BaseModel, Field
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorRecord(BaseModel):
    """A record stored in the vector database."""
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    id: Optional[str] = None

class DocumentChunk(BaseModel):
    """A chunk of text from a document with metadata."""
    text: str
    metadata: Dict[str, Any]
    
class SearchResult(BaseModel):
    """Result from a vector search operation."""
    text: str
    metadata: Dict[str, Any]
    score: float

try:
    # Import vector database libraries using the updated import paths
    from langchain_community.vectorstores import Chroma, FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_core.documents import Document
    HAS_VECTOR_DEPENDENCIES = True
except ImportError:
    logger.warning("Vector database dependencies not installed. RAG capabilities will be limited.")
    HAS_VECTOR_DEPENDENCIES = False

class VectorStore:
    """Vector database for property investment knowledge storage and retrieval."""
    
    def __init__(self, 
                 embedding_model: str = "all-MiniLM-L6-v2",
                 vector_db_path: str = "./vector_db",
                 use_faiss: bool = False):
        """
        Initialize the vector database.
        
        Args:
            embedding_model: Name of the embedding model to use
            vector_db_path: Path to store the vector database
            use_faiss: Whether to use FAISS (True) or Chroma (False)
        """
        self.vector_db_path = vector_db_path
        self.use_faiss = use_faiss
        self.embedding_model = embedding_model
        self.initialized = False
        self.vector_db = None
        self.embeddings = None
        self.text_splitter = None
        
        if HAS_VECTOR_DEPENDENCIES:
            # Initialize vector store on creation
            self._initialize_vector_store()

    def _initialize_vector_store(self):
        """Initialize the vector database with the specified embedding model."""
        try:
            # Setup embeddings and text splitter
            self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            # Initialize vector DB
            if self.use_faiss:
                self.vector_db = FAISS(self.embeddings, persist_directory=self.vector_db_path)
            else:
                self.vector_db = Chroma(embedding_function=self.embeddings, persist_directory=self.vector_db_path)
            self.initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def add_documents(self, 
                      texts: List[str], 
                      metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of document texts to add
            metadatas: Metadata for each document
            
        Returns:
            List of document IDs
        """
        if not self.initialized:
            self._initialize_vector_store()
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        try:
            # Split texts into documents and add
            docs = []
            for text, meta in zip(texts, metadatas):
                for chunk in self.text_splitter.split_text(text):
                    docs.append(Document(page_content=chunk, metadata=meta))
            # Add to DB and persist
            self.vector_db.add_documents(docs)
            if hasattr(self.vector_db, 'persist'): self.vector_db.persist()
            # Return generated ids if available
            return [d.metadata.get('id', '') for d in docs]
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def search(self, 
               query: str, 
               k: int = 5, 
               filter_dict: Optional[Dict[str, Any]] = None,
               filter_metadata: Optional[Dict[str, Any]] = None) -> List[SearchResult]:
        """
        Search the vector store for relevant documents.
        
        Args:
            query: The search query
            k: Number of results to return
            filter_dict: Optional metadata filter (alias for filter_metadata)
            filter_metadata: Optional metadata filter
            
        Returns:
            List of search results
        """
        if not self.initialized:
            self._initialize_vector_store()
        
        filter_to_use = filter_dict or filter_metadata
        try:
            results = self.vector_db.similarity_search(query, k=k, filter=filter_to_use)
            return [SearchResult(text=res.page_content, metadata=res.metadata, score=res.score) for res in results]
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    def delete(self, 
               filter_metadata: Dict[str, Any]) -> bool:
        """
        Delete documents from the vector store based on metadata filter.
        
        Args:
            filter_metadata: Metadata filter for documents to delete
            
        Returns:
            Success indicator
        """
        if not self.initialized:
            self._initialize_vector_store()
        
        try:
            # Remove by metadata filter
            self.vector_db.delete(filter_metadata)
            if hasattr(self.vector_db, 'persist'): self.vector_db.persist()
            return True
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False

    def save(self) -> bool:
        """
        Save the vector store to disk.
        
        Returns:
            Success indicator
        """
        if not self.initialized:
            return False
        
        try:
            # Persist the vector store
            if hasattr(self.vector_db, 'persist'):
                self.vector_db.persist()
                return True
            return False
        except Exception as e:
            logger.error(f"Save error: {e}")
            return False

    def get_retriever(self, search_kwargs=None):
        """
        Get a LangChain retriever from this vector store.
        
        Args:
            search_kwargs: Optional search parameters
            
        Returns:
            A LangChain retriever
        """
        if not self.initialized:
            self._initialize_vector_store()
        # Return a LangChain retriever
        return self.vector_db.as_retriever(search_kwargs=search_kwargs)

# Create singleton instance
_vector_store = None

def get_vector_store(
    embedding_model: str = "all-MiniLM-L6-v2",
    vector_db_path: str = "./vector_db",
    use_faiss: bool = False,
    collection_name: Optional[str] = None
) -> VectorStore:
    """
    Get or create a vector store instance.
    
    Args:
        embedding_model: Name of the embedding model to use
        vector_db_path: Path to store the vector database
        use_faiss: Whether to use FAISS (True) or Chroma (False)
        collection_name: Optional collection name for Chroma DB
        
    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        # Instantiate singleton
        _vector_store = VectorStore(embedding_model=embedding_model, vector_db_path=vector_db_path, use_faiss=use_faiss)
    return _vector_store