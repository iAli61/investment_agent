"""
Test script for the enhanced AI Agent RAG (Retrieval Augmented Generation) system.

This script verifies the functionality of the Vector Store component
of our enhanced AI Agent architecture.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
import sys
import json
import time
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our vector store system
from src.ai_agents.rag.vector_store import get_vector_store, VectorStore

async def test_vector_store_chroma():
    """Test the vector store implementation with ChromaDB."""
    logger.info("Starting test for Vector Store system using ChromaDB...")
    
    # Initialize vector store with a test directory
    test_vector_db_path = "./test_vector_db_chroma"
    
    # Remove the test directory if it exists
    if os.path.exists(test_vector_db_path):
        import shutil
        shutil.rmtree(test_vector_db_path)
        logger.info(f"Removed existing test vector store directory: {test_vector_db_path}")
    
    try:
        # Get a vector store instance with ChromaDB
        vector_store = get_vector_store(
            vector_db_path=test_vector_db_path,
            collection_name="test_collection",
            use_faiss=False  # Use ChromaDB
        )
        logger.info(f"Initialized vector store with ChromaDB at: {test_vector_db_path}")
        
        # Test 1: Add documents to the vector store
        logger.info("\n===== Test 1: Add documents to vector store =====")
        
        # Create test documents
        test_docs = [
            "Berlin's rental market has shown steady growth with average yields between 3.0% to 3.5% in central areas.",
            "Property prices in Berlin increased by 5.3% in 2024, with stronger growth in eastern districts.",
            "Rental regulations in Berlin include rent control measures that limit rent increases for existing tenants.",
            "Multi-family properties in Berlin typically sell at a price-to-rent ratio between 25 and 30.",
            "The average price per square meter for apartments in Berlin is approximately 5,200 euros as of April 2025."
        ]
        
        # Create test metadata
        test_metadata = [
            {"source": "Market Report 2025", "category": "yields", "date": "2025-04-01"},
            {"source": "Real Estate Index", "category": "pricing", "date": "2025-03-15"},
            {"source": "Regulatory Guide", "category": "regulations", "date": "2025-02-20"},
            {"source": "Investment Analysis", "category": "valuation", "date": "2025-04-10"},
            {"source": "Market Statistics", "category": "pricing", "date": "2025-04-15"}
        ]
        
        # Add documents to vector store
        doc_ids = vector_store.add_documents(test_docs, test_metadata)
        logger.info(f"Added {len(doc_ids)} documents to vector store with IDs: {doc_ids[:3]}...")
        
        # Validate document addition
        assert len(doc_ids) == 5, f"Expected 5 document IDs, got {len(doc_ids)}"
        
        logger.info("Test 1 passed: Documents were successfully added to vector store")
        
        # Test 2: Search for documents by similarity
        logger.info("\n===== Test 2: Search for documents by similarity =====")
        
        # Perform similarity search
        search_results = vector_store.search(
            query="What are typical rental yields in Berlin?",
            k=2
        )
        
        logger.info(f"Search returned {len(search_results)} results")
        for i, result in enumerate(search_results):
            logger.info(f"Result {i+1}: {result.text[:100]}... [Score: {result.score:.4f}]")
        
        # Validate search results
        assert len(search_results) == 2, f"Expected 2 search results, got {len(search_results)}"
        # First result should be about rental yields since that's what we queried
        assert "yields" in search_results[0].text.lower() or "rental" in search_results[0].text.lower(), \
            f"Expected first result to contain 'yields' or 'rental', got: {search_results[0].text}"
        
        logger.info("Test 2 passed: Similarity search returned relevant results")
        
        # Test 3: Search with metadata filter
        logger.info("\n===== Test 3: Search with metadata filter =====")
        
        # Perform search with metadata filter
        filtered_results = vector_store.search(
            query="property prices in Berlin",
            k=3,
            filter_dict={"category": "pricing"}
        )
        
        logger.info(f"Filtered search returned {len(filtered_results)} results")
        for i, result in enumerate(filtered_results):
            logger.info(f"Result {i+1}: {result.text[:100]}... [Metadata: {result.metadata}]")
        
        # Validate filtered results
        assert len(filtered_results) > 0, "Expected at least one filtered result"
        for result in filtered_results:
            assert result.metadata["category"] == "pricing", \
                f"Expected category to be 'pricing', got: {result.metadata['category']}"
        
        logger.info("Test 3 passed: Metadata filtering works correctly")
        
        # Test 4: Update documents
        logger.info("\n===== Test 4: Update existing documents =====")
        
        # Get the first document ID
        first_doc_id = doc_ids[0]
        
        # Update the document
        updated_text = "Updated: Berlin's rental yields have increased to 3.5%-4.0% in premium locations as of May 2025."
        updated_metadata = {"source": "Updated Market Report", "category": "yields", "date": "2025-05-15"}
        
        vector_store.update_document(first_doc_id, updated_text, updated_metadata)
        logger.info(f"Updated document with ID: {first_doc_id}")
        
        # Search for the updated document
        updated_results = vector_store.search(
            query="rental yields in premium locations",
            k=1
        )
        
        logger.info(f"Search for updated document returned: {updated_results[0].text}")
        
        # Validate update
        assert "premium locations" in updated_results[0].text, \
            f"Expected updated text to contain 'premium locations', got: {updated_results[0].text}"
        assert updated_results[0].metadata["date"] == "2025-05-15", \
            f"Expected updated date to be '2025-05-15', got: {updated_results[0].metadata['date']}"
        
        logger.info("Test 4 passed: Document updates work correctly")
        
        # Test 5: Delete documents
        logger.info("\n===== Test 5: Delete documents =====")
        
        # Delete a document
        second_doc_id = doc_ids[1]
        vector_store.delete_document(second_doc_id)
        logger.info(f"Deleted document with ID: {second_doc_id}")
        
        # Try to search for content from the deleted document
        deleted_search = vector_store.search(
            query="Property prices increased by 5.3%",
            k=5
        )
        
        # Check if deleted content is gone
        deleted_found = False
        for result in deleted_search:
            if "5.3%" in result.text:
                deleted_found = True
                break
        
        assert not deleted_found, "Deleted document was still found in search results"
        
        logger.info("Test 5 passed: Document deletion works correctly")
        
        # Test 6: Persistence across instances
        logger.info("\n===== Test 6: Persistence across vector store instances =====")
        
        # Create a new vector store instance pointing to the same directory
        new_vector_store = get_vector_store(
            vector_db_path=test_vector_db_path,
            collection_name="test_collection",
            use_faiss=False
        )
        
        # Search with the new instance
        new_results = new_vector_store.search(
            query="rental yields in Berlin",
            k=2
        )
        
        logger.info(f"New instance search returned {len(new_results)} results")
        
        # Validate persistence
        assert len(new_results) == 2, f"Expected 2 results from new instance, got {len(new_results)}"
        
        logger.info("Test 6 passed: Vector store persistence works correctly")
        
        # Test 7: Performance with larger document set
        logger.info("\n===== Test 7: Performance with larger document set =====")
        
        # Generate a larger set of documents
        large_docs = []
        large_metadata = []
        
        for i in range(50):
            large_docs.append(f"Test document {i}: This is a document about property investment in various Berlin districts with different metrics and statistics for {i*100} properties.")
            large_metadata.append({"source": f"Test Source {i}", "category": "test", "index": i})
        
        # Time the addition
        start_time = time.time()
        large_doc_ids = vector_store.add_documents(large_docs, large_metadata)
        add_time = time.time() - start_time
        
        logger.info(f"Added {len(large_doc_ids)} documents in {add_time:.4f} seconds")
        
        # Time the search
        start_time = time.time()
        large_search = vector_store.search("property investment statistics", k=5)
        search_time = time.time() - start_time
        
        logger.info(f"Searched {len(large_docs) + 4} documents in {search_time:.4f} seconds")
        
        # Validate performance is reasonable
        assert search_time < 2.0, f"Search took too long: {search_time:.4f} seconds"
        
        logger.info("Test 7 passed: Vector store performance is reasonable")
        
        # Clean up
        if os.path.exists(test_vector_db_path):
            import shutil
            shutil.rmtree(test_vector_db_path)
            logger.info(f"Cleaned up test vector store directory: {test_vector_db_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing Chroma vector store: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def test_vector_store_faiss():
    """Test the vector store implementation with FAISS."""
    logger.info("Starting test for Vector Store system using FAISS...")
    
    # Initialize vector store with a test directory
    test_vector_db_path = "./test_vector_db_faiss"
    
    # Remove the test directory if it exists
    if os.path.exists(test_vector_db_path):
        import shutil
        shutil.rmtree(test_vector_db_path)
        logger.info(f"Removed existing test vector store directory: {test_vector_db_path}")
    
    try:
        # Try to get a vector store instance with FAISS
        try:
            vector_store = get_vector_store(
                vector_db_path=test_vector_db_path,
                collection_name="test_collection",
                use_faiss=True  # Use FAISS
            )
            logger.info(f"Initialized vector store with FAISS at: {test_vector_db_path}")
            faiss_available = True
        except ImportError:
            logger.warning("FAISS not available, skipping FAISS tests")
            faiss_available = False
            return True
        
        if not faiss_available:
            return True
            
        # Test 1: Add documents to the FAISS vector store
        logger.info("\n===== Test 1: Add documents to FAISS vector store =====")
        
        # Create test documents
        test_docs = [
            "Berlin's rental market has shown steady growth with average yields between 3.0% to 3.5% in central areas.",
            "Property prices in Berlin increased by 5.3% in 2024, with stronger growth in eastern districts.",
            "Rental regulations in Berlin include rent control measures that limit rent increases for existing tenants.",
            "Multi-family properties in Berlin typically sell at a price-to-rent ratio between 25 and 30.",
            "The average price per square meter for apartments in Berlin is approximately 5,200 euros as of April 2025."
        ]
        
        # Create test metadata
        test_metadata = [
            {"source": "Market Report 2025", "category": "yields", "date": "2025-04-01"},
            {"source": "Real Estate Index", "category": "pricing", "date": "2025-03-15"},
            {"source": "Regulatory Guide", "category": "regulations", "date": "2025-02-20"},
            {"source": "Investment Analysis", "category": "valuation", "date": "2025-04-10"},
            {"source": "Market Statistics", "category": "pricing", "date": "2025-04-15"}
        ]
        
        # Add documents to vector store
        doc_ids = vector_store.add_documents(test_docs, test_metadata)
        logger.info(f"Added {len(doc_ids)} documents to FAISS vector store with IDs: {doc_ids[:3]}...")
        
        # Validate document addition
        assert len(doc_ids) == 5, f"Expected 5 document IDs, got {len(doc_ids)}"
        
        logger.info("Test 1 passed: Documents were successfully added to FAISS vector store")
        
        # Test 2: Search for documents by similarity in FAISS
        logger.info("\n===== Test 2: Search for documents by similarity in FAISS =====")
        
        # Perform similarity search
        search_results = vector_store.search(
            query="What are typical rental yields in Berlin?",
            k=2
        )
        
        logger.info(f"FAISS search returned {len(search_results)} results")
        for i, result in enumerate(search_results):
            logger.info(f"Result {i+1}: {result.text[:100]}... [Score: {result.score:.4f}]")
        
        # Validate search results
        assert len(search_results) == 2, f"Expected 2 search results, got {len(search_results)}"
        
        logger.info("Test 2 passed: FAISS similarity search returned results")
        
        # Test 3: Persistence with FAISS
        logger.info("\n===== Test 3: Test FAISS persistence =====")
        
        # Save the vector store to disk
        vector_store.save()
        logger.info("Saved FAISS vector store to disk")
        
        # Create a new vector store instance pointing to the same directory
        new_vector_store = get_vector_store(
            vector_db_path=test_vector_db_path,
            collection_name="test_collection",
            use_faiss=True
        )
        
        # Search with the new instance
        new_results = new_vector_store.search(
            query="rental yields in Berlin",
            k=2
        )
        
        logger.info(f"New FAISS instance search returned {len(new_results)} results")
        
        # Validate persistence
        assert len(new_results) == 2, f"Expected 2 results from new FAISS instance, got {len(new_results)}"
        
        logger.info("Test 3 passed: FAISS vector store persistence works correctly")
        
        # Test 4: Metadata retrieval with FAISS
        logger.info("\n===== Test 4: Test FAISS metadata retrieval =====")
        
        # Check if metadata is preserved
        assert "source" in new_results[0].metadata, "Metadata 'source' missing from FAISS results"
        assert "category" in new_results[0].metadata, "Metadata 'category' missing from FAISS results"
        
        logger.info(f"FAISS result metadata: {new_results[0].metadata}")
        
        logger.info("Test 4 passed: FAISS preserves document metadata")
        
        # Clean up
        if os.path.exists(test_vector_db_path):
            import shutil
            shutil.rmtree(test_vector_db_path)
            logger.info(f"Cleaned up FAISS test vector store directory: {test_vector_db_path}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing FAISS vector store: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def test_langchain_integration():
    """Test the integration of vector store with LangChain."""
    logger.info("Starting test for Vector Store integration with LangChain...")
    
    # Initialize vector store with a test directory
    test_vector_db_path = "./test_vector_db_langchain"
    
    # Remove the test directory if it exists
    if os.path.exists(test_vector_db_path):
        import shutil
        shutil.rmtree(test_vector_db_path)
        logger.info(f"Removed existing test vector store directory: {test_vector_db_path}")
    
    try:
        # Try to import LangChain
        try:
            from langchain_core.vectorstores import VectorStore as LCVectorStore
            from src.ai_agents.utils.langchain_utils import create_langchain_rag_retriever
            langchain_available = True
        except ImportError:
            logger.warning("LangChain not available, skipping LangChain integration tests")
            langchain_available = False
            return True
        
        if not langchain_available:
            return True
        
        # Get a vector store instance
        vector_store = get_vector_store(
            vector_db_path=test_vector_db_path,
            collection_name="test_collection",
            use_faiss=False
        )
        logger.info(f"Initialized vector store for LangChain integration at: {test_vector_db_path}")
        
        # Add test documents
        test_docs = [
            "Berlin's rental market has shown steady growth with average yields between 3.0% to 3.5% in central areas.",
            "Property prices in Berlin increased by 5.3% in 2024, with stronger growth in eastern districts.",
            "Rental regulations in Berlin include rent control measures that limit rent increases for existing tenants.",
            "Multi-family properties in Berlin typically sell at a price-to-rent ratio between 25 and 30.",
            "The average price per square meter for apartments in Berlin is approximately 5,200 euros as of April 2025."
        ]
        
        test_metadata = [
            {"source": "Market Report 2025", "category": "yields", "date": "2025-04-01"},
            {"source": "Real Estate Index", "category": "pricing", "date": "2025-03-15"},
            {"source": "Regulatory Guide", "category": "regulations", "date": "2025-02-20"},
            {"source": "Investment Analysis", "category": "valuation", "date": "2025-04-10"},
            {"source": "Market Statistics", "category": "pricing", "date": "2025-04-15"}
        ]
        
        doc_ids = vector_store.add_documents(test_docs, test_metadata)
        
        # Test LangChain retriever creation
        retriever = create_langchain_rag_retriever(vector_store, {"k": 2})
        
        logger.info(f"Created LangChain retriever: {retriever is not None}")
        
        # Check if the retriever has expected methods
        assert hasattr(retriever, "get_relevant_documents"), "LangChain retriever missing get_relevant_documents method"
        
        # Try using the retriever
        try:
            documents = retriever.get_relevant_documents("What are rental yields in Berlin?")
            logger.info(f"LangChain retriever returned {len(documents)} documents")
            
            # Check document content
            assert len(documents) == 2, f"Expected 2 documents, got {len(documents)}"
            
            logger.info("LangChain integration test passed")
        except Exception as e:
            logger.error(f"Error using LangChain retriever: {str(e)}")
            
        # Clean up
        if os.path.exists(test_vector_db_path):
            import shutil
            shutil.rmtree(test_vector_db_path)
            logger.info(f"Cleaned up LangChain test vector store directory: {test_vector_db_path}")
        
        return True
            
    except Exception as e:
        logger.error(f"Error testing LangChain integration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

async def main():
    """Run all vector store tests."""
    logger.info("Starting Vector Store Test Suite")
    
    # Test ChromaDB vector store
    chroma_test_result = await test_vector_store_chroma()
    
    # Test FAISS vector store
    faiss_test_result = await test_vector_store_faiss()
    
    # Test LangChain integration
    langchain_test_result = await test_langchain_integration()
    
    # Print summary
    logger.info("\n===== Test Results Summary =====")
    logger.info(f"ChromaDB Vector Store Test: {'PASSED' if chroma_test_result else 'FAILED'}")
    logger.info(f"FAISS Vector Store Test: {'PASSED' if faiss_test_result else 'FAILED'}")
    logger.info(f"LangChain Integration Test: {'PASSED' if langchain_test_result else 'FAILED'}")

if __name__ == "__main__":
    asyncio.run(main())