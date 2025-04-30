"""
Memory management system for AI agents, providing context storage and retrieval.

This module provides a memory system for the Property Investment Analysis Application
to maintain conversation history and context across interactions.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import os
import time
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryRecord(BaseModel):
    """A memory record representing an interaction or piece of context."""
    content: Dict[str, Any]
    memory_type: str  # 'conversation', 'user_preference', 'fact', 'decision'
    timestamp: str
    source: str  # 'user', 'agent', 'system'
    importance: float = 1.0  # higher = more important

class AgentMemory:
    """Memory system for AI agents to store and retrieve contextual information."""
    
    def __init__(self, memory_file: Optional[str] = None):
        """
        Initialize the memory system.
        
        Args:
            memory_file: Optional path to a file for persisting memory
        """
        self.memories: List[MemoryRecord] = []
        self.memory_file = memory_file
        self.max_memory_items = 100  # Default, can be adjusted based on token limits
        
        # Load memories from file if it exists
        if memory_file and os.path.exists(memory_file):
            self._load_memories()
    
    def _load_memories(self):
        """Load memories from the memory file."""
        try:
            with open(self.memory_file, 'r') as f:
                memory_data = json.load(f)
                
            self.memories = []
            
            # Load conversation history
            if 'conversation_history' in memory_data:
                for conversation in memory_data['conversation_history']:
                    memory = MemoryRecord(
                        content={"message": conversation.get('content', '')},
                        memory_type="conversation",
                        timestamp=conversation.get('timestamp', datetime.now().isoformat()),
                        source=conversation.get('role', 'user'),
                        importance=1.0
                    )
                    self.memories.append(memory)
            
            # Load user preferences
            if 'user_preferences' in memory_data:
                for key, value in memory_data['user_preferences'].items():
                    memory = MemoryRecord(
                        content={"key": key, "value": value},
                        memory_type="user_preference",
                        timestamp=datetime.now().isoformat(),
                        source="user",
                        importance=2.0
                    )
                    self.memories.append(memory)
            
            # Load facts
            if 'facts' in memory_data:
                for fact in memory_data['facts']:
                    memory = MemoryRecord(
                        content={"fact": fact.get('text', ''), "source": fact.get('source', '')},
                        memory_type="fact",
                        timestamp=fact.get('timestamp', datetime.now().isoformat()),
                        source="system",
                        importance=1.5
                    )
                    self.memories.append(memory)
            
            # Load decisions
            if 'decisions' in memory_data:
                for decision in memory_data['decisions']:
                    memory = MemoryRecord(
                        content={
                            "decision": decision.get('decision', ''),
                            "reasoning": decision.get('reasoning', ''),
                            "confidence": decision.get('confidence')
                        },
                        memory_type="decision",
                        timestamp=decision.get('timestamp', datetime.now().isoformat()),
                        source="agent",
                        importance=1.8
                    )
                    self.memories.append(memory)
            
            logger.info(f"Loaded {len(self.memories)} memories from {self.memory_file}")
        except Exception as e:
            logger.error(f"Error loading memories: {str(e)}")
            self.memories = []
    
    def _save_memories(self):
        """Save memories to the memory file."""
        if not self.memory_file:
            return
        
        try:
            # Organize memories by type
            organized_data = {
                'conversation_history': [],
                'user_preferences': {},
                'facts': [],
                'decisions': []
            }
            
            # Fill in the data structures
            for memory in self.memories:
                if memory.memory_type == "conversation":
                    organized_data['conversation_history'].append({
                        'role': memory.source,
                        'content': memory.content.get('message', ''),
                        'timestamp': memory.timestamp
                    })
                elif memory.memory_type == "user_preference":
                    key = memory.content.get('key')
                    value = memory.content.get('value')
                    if key and value is not None:
                        organized_data['user_preferences'][key] = value
                elif memory.memory_type == "fact":
                    organized_data['facts'].append({
                        'text': memory.content.get('fact', ''),
                        'source': memory.content.get('source', ''),
                        'timestamp': memory.timestamp
                    })
                elif memory.memory_type == "decision":
                    organized_data['decisions'].append({
                        'decision': memory.content.get('decision', ''),
                        'reasoning': memory.content.get('reasoning', ''),
                        'confidence': memory.content.get('confidence'),
                        'timestamp': memory.timestamp
                    })
            
            # Write the organized data to the file
            with open(self.memory_file, 'w') as f:
                json.dump(organized_data, f, indent=2)
            
            logger.info(f"Saved {len(self.memories)} memories to {self.memory_file}")
        except Exception as e:
            logger.error(f"Error saving memories: {str(e)}")
    
    def add(self, 
            content: Dict[str, Any], 
            memory_type: str,
            source: str,
            importance: float = 1.0) -> MemoryRecord:
        """
        Add a new memory.
        
        Args:
            content: The content of the memory
            memory_type: Type of memory (conversation, user_preference, fact, decision)
            source: Source of the memory (user, agent, system)
            importance: Importance score (higher = more important)
            
        Returns:
            The created memory record
        """
        memory = MemoryRecord(
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now().isoformat(),
            source=source,
            importance=importance
        )
        
        # Add to memories list
        self.memories.append(memory)
        
        # Trim memories if needed
        if len(self.memories) > self.max_memory_items:
            # Remove least important memories first
            self.memories.sort(key=lambda x: x.importance, reverse=True)
            self.memories = self.memories[:self.max_memory_items]
        
        # Save to file if configured
        if self.memory_file:
            self._save_memories()
        
        return memory
    
    def add_user_message(self, 
                         message: str, 
                         importance: float = 1.0) -> MemoryRecord:
        """
        Add a user message to memory.
        
        Args:
            message: The user's message
            importance: Importance score
            
        Returns:
            The created memory record
        """
        return self.add(
            content={"message": message},
            memory_type="conversation",
            source="user",
            importance=importance
        )
    
    def add_agent_message(self, 
                          message: str, 
                          importance: float = 1.0) -> MemoryRecord:
        """
        Add an agent message to memory.
        
        Args:
            message: The agent's message
            importance: Importance score
            
        Returns:
            The created memory record
        """
        return self.add(
            content={"message": message},
            memory_type="conversation",
            source="agent",
            importance=importance
        )
    
    def add_user_preference(self, 
                            preference_key: str, 
                            preference_value: Any,
                            importance: float = 2.0) -> MemoryRecord:
        """
        Add a user preference to memory.
        
        Args:
            preference_key: The key for the preference
            preference_value: The value of the preference
            importance: Importance score
            
        Returns:
            The created memory record
        """
        return self.add(
            content={"key": preference_key, "value": preference_value},
            memory_type="user_preference",
            source="user",
            importance=importance
        )
    
    def add_fact(self, 
                 fact: str, 
                 source_reference: Optional[str] = None,
                 importance: float = 1.5) -> MemoryRecord:
        """
        Add a factual record to memory.
        
        Args:
            fact: The factual information
            source_reference: Reference to the source of the fact
            importance: Importance score
            
        Returns:
            The created memory record
        """
        return self.add(
            content={"fact": fact, "source": source_reference},
            memory_type="fact",
            source="system",
            importance=importance
        )
    
    def add_decision(self, 
                     decision: str, 
                     reasoning: Optional[str] = None,
                     confidence: Optional[float] = None,
                     importance: float = 1.8) -> MemoryRecord:
        """
        Add a decision record to memory.
        
        Args:
            decision: The decision made
            reasoning: The reasoning behind the decision
            confidence: Confidence level in the decision (0.0 to 1.0)
            importance: Importance score
            
        Returns:
            The created memory record
        """
        return self.add(
            content={"decision": decision, "reasoning": reasoning, "confidence": confidence},
            memory_type="decision",
            source="agent",
            importance=importance
        )
    
    def get_recent_memories(self, 
                           limit: int = 10) -> List[MemoryRecord]:
        """
        Get the most recent memories.
        
        Args:
            limit: Maximum number of memories to return
            
        Returns:
            List of memory records
        """
        # Sort by timestamp (most recent first)
        sorted_memories = sorted(
            self.memories, 
            key=lambda x: x.timestamp, 
            reverse=True
        )
        return sorted_memories[:limit]
    
    def get_memories_by_type(self, 
                            memory_type: str, 
                            limit: Optional[int] = None) -> List[MemoryRecord]:
        """
        Get memories of a specific type.
        
        Args:
            memory_type: Type of memories to retrieve
            limit: Maximum number of memories to return
            
        Returns:
            List of memory records
        """
        memories = [m for m in self.memories if m.memory_type == memory_type]
        
        # Sort by timestamp (most recent first)
        memories = sorted(
            memories, 
            key=lambda x: x.timestamp, 
            reverse=True
        )
        
        if limit:
            memories = memories[:limit]
            
        return memories
    
    def get_conversation_history(self, 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent conversation history in a format suitable for LLM context.
        
        Args:
            limit: Maximum number of conversation turns to return
            
        Returns:
            List of conversation turns in LangChain message format
        """
        # Get only the conversation type memories
        conversations = self.get_memories_by_type("conversation")
        
        # Sort conversations by timestamp (newest first, so we get the most recent conversations)
        conversations = sorted(
            conversations,
            key=lambda x: x.timestamp,
            reverse=True
        )
        
        # Limit to the requested number (or fewer if we don't have that many)
        conversations = conversations[:limit]
        
        # Convert to the format expected by LLMs (and reverse to get chronological order)
        return [
            {"role": m.source, "content": m.content["message"]} 
            for m in reversed(conversations)  # Reverse to get oldest first (chronological order)
        ]
    
    def get_user_preferences(self) -> dict:
        """
        Get all current user preferences.
        
        Returns:
            dict: A dictionary containing all user preferences
        """
        preferences = {}
        
        # Get memories of type user_preference
        preference_memories = self.get_memories_by_type("user_preference")
        
        # Extract key-value pairs from preference memories
        for memory in preference_memories:
            if memory.memory_type == "user_preference":
                key = memory.content.get("key")
                value = memory.content.get("value")
                if key and value is not None:
                    preferences[key] = value
        
        return preferences

    def get_facts(self, filter_dict: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve facts from memory, optionally filtered by criteria.
        
        Args:
            filter_dict: Optional dictionary of key-value pairs to filter facts
                         Example: {"category": "property_data"}
        
        Returns:
            List of fact dictionaries with text and metadata
        """
        facts = []
        
        # Get memories of type fact
        fact_memories = self.get_memories_by_type("fact")
        
        for memory in fact_memories:
            # If filter is provided, check if memory matches all filter criteria
            if filter_dict:
                matches_filter = True
                
                # Check each filter key-value pair against memory content
                for filter_key, filter_value in filter_dict.items():
                    if memory.content.get(filter_key) != filter_value:
                        matches_filter = False
                        break
                
                if not matches_filter:
                    continue
            
            # Add the fact to our results
            facts.append({
                "text": memory.content.get("fact", ""),
                "source": memory.content.get("source", ""),
                "timestamp": memory.timestamp
            })
        
        return facts
    
    def get_decisions(self, filter_dict: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve past decisions from memory, optionally filtered by criteria.
        
        Args:
            filter_dict: Optional dictionary of key-value pairs to filter decisions
                         Example: {"category": "investment_decision"}
        
        Returns:
            List of decision dictionaries with text and metadata
        """
        decisions = []
        
        # Get memories of type decision
        decision_memories = self.get_memories_by_type("decision")
        
        for memory in decision_memories:
            # If filter is provided, check if memory matches all filter criteria
            if filter_dict:
                matches_filter = True
                
                # Check each filter key-value pair against memory content
                for filter_key, filter_value in filter_dict.items():
                    if memory.content.get(filter_key) != filter_value:
                        matches_filter = False
                        break
                
                if not matches_filter:
                    continue
            
            # Add the decision to our results
            decisions.append({
                "decision": memory.content.get("decision", ""),
                "reasoning": memory.content.get("reasoning", ""),
                "confidence": memory.content.get("confidence"),
                "timestamp": memory.timestamp
            })
        
        return decisions
    
    def save_memory(self):
        """
        Force saving the memory to file.
        This is typically only needed for testing as memories are saved automatically when added.
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.memory_file) if os.path.dirname(self.memory_file) else '.', exist_ok=True)
        
        # Save the memories
        self._save_memories()
        
        # Verify the file was created
        if not os.path.exists(self.memory_file):
            logger.warning(f"Failed to create memory file at {self.memory_file}")
            return False
        
        return True
    
    def create_langchain_memory(self):
        """
        Create a LangChain memory object from this memory system.
        
        This allows the memory system to be used with LangChain-based agents.
        
        Returns:
            LangChain memory object
        """
        try:
            from langchain.memory import ConversationBufferMemory
            
            # Create a LangChain memory object
            langchain_memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
            
            # Get conversation history
            conversation_history = self.get_conversation_history()
            
            # Add existing messages to LangChain memory
            # LangChain expects format: [{"role": "human", "content": "..."}, {"role": "ai", "content": "..."}]
            for message in conversation_history:
                if message["role"] == "user":
                    langchain_memory.chat_memory.add_user_message(message["content"])
                elif message["role"] == "agent":
                    langchain_memory.chat_memory.add_ai_message(message["content"])
            
            return langchain_memory
            
        except ImportError:
            logger.warning("LangChain not installed. Cannot create LangChain memory.")
            # Return a mock memory object 
            return {"chat_history": self.get_conversation_history()}

# Create singleton instance
_agent_memory = None

def get_agent_memory(memory_file: Optional[str] = "./agent_memory.json") -> AgentMemory:
    """
    Get or create an agent memory instance.
    
    Args:
        memory_file: Path to memory file
        
    Returns:
        AgentMemory instance
    """
    global _agent_memory
    
    # Create a new instance if none exists or if memory_file is different
    if _agent_memory is None or (_agent_memory.memory_file != memory_file and memory_file is not None):
        _agent_memory = AgentMemory(memory_file=memory_file)
    
    return _agent_memory

class AgentMemoryService:
    """Service wrapper for AgentMemory to provide additional functionality for API usage."""
    
    def __init__(self, memory_file: Optional[str] = "./agent_memory.json"):
        """
        Initialize the memory service.
        
        Args:
            memory_file: Optional path to a file for persisting memory
        """
        self.memory = get_agent_memory(memory_file)
        
    def add_user_message(self, message: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a user message to memory.
        
        Args:
            message: The user's message
            user_id: Optional user ID for tracking
            
        Returns:
            Dictionary with status and memory info
        """
        memory_record = self.memory.add_user_message(message)
        return {
            "status": "success",
            "memory_id": id(memory_record),
            "timestamp": memory_record.timestamp
        }
        
    def add_agent_message(self, message: str) -> Dict[str, Any]:
        """
        Add an agent message to memory.
        
        Args:
            message: The agent's message
            
        Returns:
            Dictionary with status and memory info
        """
        memory_record = self.memory.add_agent_message(message)
        return {
            "status": "success",
            "memory_id": id(memory_record),
            "timestamp": memory_record.timestamp
        }
        
    def get_conversation_history(self, limit: int = 10, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            limit: Maximum number of turns to retrieve
            user_id: Optional user ID for filtering
            
        Returns:
            List of conversation turns
        """
        return self.memory.get_conversation_history(limit=limit)
        
    def get_user_preferences(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get user preferences.
        
        Args:
            user_id: Optional user ID for filtering
            
        Returns:
            Dictionary of user preferences
        """
        return self.memory.get_user_preferences()
        
    def add_user_preference(self, key: str, value: Any, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Add or update a user preference.
        
        Args:
            key: Preference key
            value: Preference value
            user_id: Optional user ID
            
        Returns:
            Dictionary with status and preference info
        """
        memory_record = self.memory.add_user_preference(key, value)
        return {
            "status": "success",
            "preference_key": key,
            "timestamp": memory_record.timestamp
        }