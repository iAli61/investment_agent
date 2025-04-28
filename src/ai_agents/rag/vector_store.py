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
            self._initialize_vector_store()
    
    def _initialize_vector_store(self):
        """Initialize the vector database with the specified embedding model."""
        try:
            # Initialize embedding model
            self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
            
            # Initialize vector store
            if self.use_faiss:
                # Use FAISS for high-performance vector search
                if os.path.exists(f"{self.vector_db_path}/index.faiss"):
                    self.vector_db = FAISS.load_local(
                        self.vector_db_path, 
                        self.embeddings
                    )
                    logger.info(f"Loaded existing FAISS vector database from {self.vector_db_path}")
                else:
                    self.vector_db = FAISS.from_documents(
                        [Document(page_content="Investment initialization", metadata={"source": "init"})],
                        self.embeddings
                    )
                    self.vector_db.save_local(self.vector_db_path)
                    logger.info(f"Created new FAISS vector database at {self.vector_db_path}")
            else:
                # Use Chroma for ease of use and visualization
                self.vector_db = Chroma(
                    persist_directory=self.vector_db_path,
                    embedding_function=self.embeddings
                )
                logger.info(f"Initialized Chroma vector database at {self.vector_db_path}")
            
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}")
            self.initialized = False
    
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
            logger.error("Vector store not initialized")
            return []
        
        if not metadatas:
            metadatas = [{"source": "manual", "timestamp": datetime.now().isoformat()} for _ in texts]
        
        try:
            # Split texts into chunks
            docs = []
            for i, text in enumerate(texts):
                chunks = self.text_splitter.split_text(text)
                for j, chunk in enumerate(chunks):
                    chunk_metadata = metadatas[i].copy()
                    chunk_metadata["chunk_id"] = j
                    docs.append(Document(page_content=chunk, metadata=chunk_metadata))
            
            # Add documents to vector store
            ids = self.vector_db.add_documents(docs)
            
            # Save if using FAISS
            if self.use_faiss:
                self.vector_db.save_local(self.vector_db_path)
                
            logger.info(f"Added {len(docs)} document chunks to vector store")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {str(e)}")
            return []
    
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
            logger.error("Vector store not initialized")
            return []
        
        # Use filter_dict if provided, otherwise use filter_metadata
        filter_to_use = filter_dict if filter_dict is not None else filter_metadata
        
        try:
            # Search vector store
            if filter_to_use:
                docs_and_scores = self.vector_db.similarity_search_with_score(
                    query, k=k, filter=filter_to_use
                )
            else:
                docs_and_scores = self.vector_db.similarity_search_with_score(
                    query, k=k
                )
            
            # Convert to SearchResult objects
            results = []
            for doc, score in docs_and_scores:
                results.append(SearchResult(
                    text=doc.page_content,
                    metadata=doc.metadata,
                    score=float(score)
                ))
            
            logger.info(f"Found {len(results)} results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []

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
            logger.error("Vector store not initialized")
            return False
        
        try:
            # Delete from vector store
            self.vector_db.delete(filter=filter_metadata)
            
            # Save if using FAISS
            if self.use_faiss:
                self.vector_db.save_local(self.vector_db_path)
                
            logger.info(f"Deleted documents matching filter: {filter_metadata}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from vector store: {str(e)}")
            return False
    
    def save(self) -> bool:
        """
        Save the vector store to disk.
        
        Returns:
            Success indicator
        """
        if not self.initialized:
            logger.error("Vector store not initialized")
            return False
        
        try:
            if self.use_faiss:
                self.vector_db.save_local(self.vector_db_path)
                logger.info(f"Saved FAISS vector database to {self.vector_db_path}")
            else:
                # For Chroma, persistence is handled automatically
                pass
            return True
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
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
            logger.error("Vector store not initialized")
            return None
        
        if search_kwargs is None:
            search_kwargs = {"k": 4}
            
        try:
            return self.vector_db.as_retriever(search_kwargs=search_kwargs)
        except Exception as e:
            logger.error(f"Error creating retriever: {str(e)}")
            return None

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
        _vector_store = VectorStore(
            embedding_model=embedding_model,
            vector_db_path=vector_db_path,
            use_faiss=use_faiss
        )
    return _vector_store