"""
Server-Sent Events (SSE) implementation for real-time updates
"""
import asyncio
import logging
import json
from typing import Dict, Any, Optional, Set, List
from datetime import datetime, timedelta
from fastapi import Request
from starlette.responses import StreamingResponse

logger = logging.getLogger(__name__)

class UpdateManager:
    """Singleton class to manage SSE connections and updates"""
    _instance = None
    
    def __new__(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super(UpdateManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the update manager"""
        if self._initialized:
            return
            
        # Store active connections by scenario_id
        self._connections: Dict[Optional[int], Set[asyncio.Queue]] = {}
        # Store connection timestamps for cleanup
        self._connection_timestamps: Dict[asyncio.Queue, datetime] = {}
        # Heartbeat interval in seconds
        self._heartbeat_interval = 15
        # Max connection idle time in seconds
        self._max_idle_time = 300
        # Cleanup task
        self._cleanup_task = None
        
        self._initialized = True
        logger.info("UpdateManager initialized")
    
    async def register_client(self, scenario_id: Optional[int] = None) -> asyncio.Queue:
        """
        Register a new client connection
        
        Args:
            scenario_id (Optional[int], optional): Scenario ID to filter updates.
                If None, client receives all updates. Defaults to None.
                
        Returns:
            asyncio.Queue: Queue for client updates
        """
        # Create a new queue for this connection
        queue = asyncio.Queue()
        
        # Register in the connections dict
        if scenario_id not in self._connections:
            self._connections[scenario_id] = set()
        
        self._connections[scenario_id].add(queue)
        self._connection_timestamps[queue] = datetime.utcnow()
        
        # Start cleanup task if not running
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())
        
        logger.info(f"Client registered for scenario_id: {scenario_id}")
        
        # Send initial connection event
        await queue.put(self._create_event(
            "connection_established", 
            {
                "status": "connected",
                "scenario_id": scenario_id,
                "timestamp": datetime.utcnow().isoformat(),
                "connection_id": id(queue)
            }
        ))
        
        return queue
    
    async def unregister_client(self, queue: asyncio.Queue, scenario_id: Optional[int] = None) -> None:
        """
        Unregister a client connection
        
        Args:
            queue (asyncio.Queue): Client queue to unregister
            scenario_id (Optional[int], optional): Scenario ID. Defaults to None.
        """
        # Remove from connections
        if scenario_id in self._connections and queue in self._connections[scenario_id]:
            self._connections[scenario_id].remove(queue)
            
            # Clean up empty scenario sets
            if not self._connections[scenario_id]:
                del self._connections[scenario_id]
        
        # Remove from timestamp tracking
        if queue in self._connection_timestamps:
            del self._connection_timestamps[queue]
            
        logger.info(f"Client unregistered for scenario_id: {scenario_id}")
    
    async def send_update(self, scenario_id: int, event_type: str, data: Dict[str, Any]) -> None:
        """
        Send an update to all registered clients for a scenario
        
        Args:
            scenario_id (int): Scenario ID
            event_type (str): Type of event (e.g., "metric_update", "calculation_complete")
            data (Dict[str, Any]): Event data
        """
        # Create event string
        event = self._create_event(event_type, data)
        
        # First, send to clients registered for this specific scenario
        if scenario_id in self._connections:
            for queue in self._connections[scenario_id]:
                await queue.put(event)
                self._connection_timestamps[queue] = datetime.utcnow()
        
        # Then, send to clients registered for all updates (scenario_id=None)
        if None in self._connections:
            for queue in self._connections[None]:
                await queue.put(event)
                self._connection_timestamps[queue] = datetime.utcnow()
        
        logger.debug(f"Update sent for scenario {scenario_id}, event: {event_type}")
    
    async def send_heartbeat(self) -> None:
        """Send heartbeat to all connected clients"""
        heartbeat = self._create_event("heartbeat", {"timestamp": datetime.utcnow().isoformat()})
        
        # Send to all connections
        for scenario_id, queues in self._connections.items():
            for queue in queues:
                await queue.put(heartbeat)
                self._connection_timestamps[queue] = datetime.utcnow()
        
        logger.debug("Heartbeat sent to all clients")
    
    async def _cleanup_inactive_connections(self) -> None:
        """Cleanup inactive connections and send periodic heartbeats"""
        try:
            while True:
                # Send heartbeat
                await self.send_heartbeat()
                
                # Identify inactive connections
                now = datetime.utcnow()
                inactive_queues = []
                
                for queue, timestamp in self._connection_timestamps.items():
                    if now - timestamp > timedelta(seconds=self._max_idle_time):
                        inactive_queues.append(queue)
                
                # Remove inactive connections
                for queue in inactive_queues:
                    for scenario_id in list(self._connections.keys()):
                        if queue in self._connections[scenario_id]:
                            await self.unregister_client(queue, scenario_id)
                            break
                
                # Sleep until next heartbeat
                await asyncio.sleep(self._heartbeat_interval)
        except asyncio.CancelledError:
            logger.info("Cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")
    
    def _create_event(self, event_type: str, data: Dict[str, Any]) -> str:
        """
        Create an SSE event string
        
        Args:
            event_type (str): Type of event
            data (Dict[str, Any]): Event data
            
        Returns:
            str: Formatted SSE event
        """
        json_data = json.dumps(data)
        return f"event: {event_type}\ndata: {json_data}\n\n"

# Create global singleton instance
update_manager = UpdateManager()

# Create an alias for UpdateManager for backward compatibility
SSEManager = UpdateManager

# Convenience function to send updates from anywhere in the code
async def send_update(scenario_id: int, event_type: str, data: Dict[str, Any]) -> None:
    """
    Send an update to all clients for a scenario
    
    Args:
        scenario_id (int): Scenario ID
        event_type (str): Type of event
        data (Dict[str, Any]): Event data
    """
    await update_manager.send_update(scenario_id, event_type, data)

# FastAPI SSE endpoint handler
async def sse_endpoint(request: Request, scenario_id: Optional[int] = None) -> StreamingResponse:
    """
    SSE endpoint for real-time updates
    
    Args:
        request (Request): FastAPI request
        scenario_id (Optional[int], optional): Scenario ID to filter updates. Defaults to None.
        
    Returns:
        StreamingResponse: Streaming response for SSE
    """
    # Register client
    queue = await update_manager.register_client(scenario_id)
    
    # Create async generator for streaming
    async def event_generator():
        try:
            while True:
                # Get message from queue
                message = await queue.get()
                yield message
                queue.task_done()
        except asyncio.CancelledError:
            # Client disconnected
            await update_manager.unregister_client(queue, scenario_id)
        finally:
            # Ensure cleanup on any other exception
            await update_manager.unregister_client(queue, scenario_id)
    
    # Return streaming response with text/event-stream media type
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for Nginx
        }
    )