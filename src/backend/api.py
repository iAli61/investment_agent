"""
API endpoints for the Property Investment Analysis Application
"""
import logging
import json
import os
from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, BackgroundTasks, Query, Body, FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from datetime import datetime

from ..database.database import get_db
from ..database.models import User, Property, Scenario, AgentMemoryItem
from ..ai_agents.orchestrator.orchestrator import get_orchestrator
from ..ai_agents.agent_system import AIAgentSystem
from ..ai_agents.orchestrator.manager_agent import create_manager_agent
from ..ai_agents.specialized import (
    create_market_data_search_agent,
    create_rent_estimation_agent,
    create_document_analysis_agent,
    create_optimization_agent,
    create_risk_analysis_agent,
    create_strategy_agent
)
from ..utils.sse_updates import SSEManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Property Investment Analysis API", 
             description="API for property investment analysis with AI agents",
             version="1.0.0")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create SSE manager for real-time updates
sse_manager = SSEManager()

# Initialize AI Agent System
agent_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize the AI agent system on startup."""
    global agent_system
    try:
        # Disable OpenAI tracing to prevent 401 errors - ensure this is set before ANY OpenAI client creation
        os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
        
        # If the Agents SDK has a direct function to disable tracing, call it
        try:
            from agents import set_tracing_disabled
            set_tracing_disabled(True)
            logger.info("Tracing has been explicitly disabled for the Agents SDK")
        except ImportError:
            logger.info("Using environment variable method to disable tracing")
        
        # Initialize AI Agent System with Azure OpenAI integration
        agent_system = AIAgentSystem(
            use_azure=True,
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        agent_system.initialize()
        logger.info("AI Agent System initialized successfully")
        
        # Initialize orchestrator
        orchestrator = get_orchestrator()
        
        # If needed, register specialized agents directly
        if not orchestrator.specialized_agents:
            logger.info("Registering specialized agents with orchestrator")
            orchestrator.register_specialized_agent("market_data", create_market_data_search_agent())
            orchestrator.register_specialized_agent("rent_estimation", create_rent_estimation_agent())
            orchestrator.register_specialized_agent("document_analysis", create_document_analysis_agent())
            orchestrator.register_specialized_agent("optimization", create_optimization_agent())
            # Register the risk analysis and strategy agents that were missing
            logger.info("Registering risk analysis and strategy agents")
            orchestrator.register_specialized_agent("risk_analysis", create_risk_analysis_agent())
            orchestrator.register_specialized_agent("strategy", create_strategy_agent())
            
        # If manager agent is not initialized, create and register it
        if not orchestrator.manager_agent:
            logger.info("Creating and registering manager agent")
            manager_agent = create_manager_agent(orchestrator.specialized_agents)
            orchestrator.register_manager_agent(manager_agent)
            
        logger.info("API startup completed successfully")
    except Exception as e:
        logger.error(f"Error initializing AI Agent System: {str(e)}")
        # Continuing even with error, to allow other parts of the API to work

# Define routes directly in the app, not using a router
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint that provides basic API information"""
    return """
    <html>
        <head>
            <title>Property Investment Analysis API</title>
        </head>
        <body>
            <h1>Property Investment Analysis API</h1>
            <p>Welcome to the Property Investment Analysis API.</p>
            <p>This API provides endpoints for property investment analysis with AI agents.</p>
            <p>The frontend UI is available at <a href="http://localhost:8501">http://localhost:8501</a>.</p>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><code>/health</code> - Health check endpoint</li>
                <li><code>/ai/conversation/</code> - Converse with the AI assistant</li>
                <li><code>/ai/conversation/stream</code> - Stream conversation with AI assistant</li>
                <li><code>/properties/{property_id}/scenarios</code> - Get scenarios for a property</li>
                <li><code>/scenarios/{scenario_id}</code> - Get a specific scenario</li>
                <li><code>/scenarios/{scenario_id}/analyze</code> - Analyze a scenario</li>
                <li><code>/scenarios/compare</code> - Compare multiple scenarios</li>
            </ul>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is operational"}

@app.post("/ai/conversation/")
async def converse_with_ai(
    request: Request,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Converse with the AI assistant
    
    Args:
        request: The incoming request with JSON data
        background_tasks: Background tasks for async operations
        db: Database session
    
    Returns:
        Response from AI assistant with suggestions
    """
    try:
        # Get request body
        body = await request.json()
        message = body.get("message", "")
        context = body.get("context", {})
        
        # Log incoming request for debugging
        logger.info(f"Received conversation request - message: {message[:50]}...")
        
        # Disable OpenAI tracing to prevent 401 errors
        os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        # Check if manager agent is initialized and initialize it if needed
        if not orchestrator.manager_agent:
            logger.info("Manager agent not initialized. Initializing it now...")
            try:
                # Initialize specialized agents if needed
                if not orchestrator.specialized_agents:
                    logger.info("Registering specialized agents with orchestrator")
                    orchestrator.register_specialized_agent("market_data", create_market_data_search_agent())
                    orchestrator.register_specialized_agent("rent_estimation", create_rent_estimation_agent())
                    orchestrator.register_specialized_agent("document_analysis", create_document_analysis_agent())
                    orchestrator.register_specialized_agent("optimization", create_optimization_agent())
                    
                    # Register the risk analysis and strategy agents that were missing
                    logger.info("Registering risk analysis and strategy agents")
                    orchestrator.register_specialized_agent("risk_analysis", create_risk_analysis_agent())
                    orchestrator.register_specialized_agent("strategy", create_strategy_agent())
                
                # Create and register manager agent
                logger.info("Creating and registering manager agent")
                manager_agent = create_manager_agent(orchestrator.specialized_agents)
                orchestrator.register_manager_agent(manager_agent)
                logger.info("Manager agent initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize manager agent: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Could not initialize manager agent: {str(e)}")
        
        # Double-check that manager agent is now initialized
        if not orchestrator.manager_agent:
            logger.error("Manager agent initialization failed")
            raise HTTPException(status_code=500, detail="Manager agent not initialized and could not be initialized")
        
        # Enhance context with additional information if needed
        enhanced_context = {
            "user_id": context.get("user_id"),
            "property_id": context.get("property_id"),
            "scenario_id": context.get("scenario_id"),
            "session_id": context.get("session_id", "default"),
            **context
        }
        
        # Process the message through the manager agent
        # The _manager_converse method expects the first parameter to be the message and the second to be the context
        logger.info(f"Processing message with manager agent")
        response = await orchestrator._manager_converse(message, enhanced_context)
        
        # Return structured response
        result = {
            "response": response.get("response", "I'm sorry, I couldn't process that request."),
            "suggestions": response.get("suggestions", []),
            "context": response.get("context", {}),
        }
        logger.info(f"Returning conversation response: {result['response'][:50]}...")
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error in conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conversation error: {str(e)}")

@app.post("/ai/conversation/stream", response_class=StreamingResponse)
async def stream_conversation(request: Request, db: Session = Depends(get_db)):
    """
    Stream conversation with AI assistant
    
    Args:
        request: The incoming request with JSON data
        db: Database session
    
    Returns:
        Streaming response from AI assistant
    """
    try:
        # Get request body
        body = await request.json()
        message = body.get("message", "")
        context = body.get("context", {})
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        if not orchestrator or not orchestrator.manager_agent:
            raise HTTPException(status_code=500, detail="Manager agent not initialized")
        
        # Extract session information
        session_id = context.get("session_id", "default")
        
        # Create async generator for streaming
        async def event_generator():
            # Initialize response chunks
            async for chunk in orchestrator.manager_agent.stream_converse(
                message=message,
                context=context
            ):
                if chunk:
                    # Format chunk for SSE
                    yield json.dumps({
                        "data": chunk.get("content", ""),
                        "type": chunk.get("type", "content"),
                        "done": chunk.get("done", False)
                    })
            
            # Final message indicating completion
            yield json.dumps({"data": "", "type": "content", "done": True})
        
        # Return streaming response
        return EventSourceResponse(event_generator())
        
    except Exception as e:
        logger.error(f"Error in streaming conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Streaming error: {str(e)}")

@app.get("/properties/{property_id}/scenarios", response_model=List[Dict[str, Any]])
async def get_scenarios(
    property_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all scenarios for a property
    
    Args:
        property_id: ID of the property
        db: Database session
    
    Returns:
        List of scenarios
    """
    try:
        scenarios = db.query(Scenario).filter(Scenario.property_id == property_id).all()
        
        # Convert to dict with formatted results
        result = []
        for scenario in scenarios:
            scenario_dict = {
                "id": scenario.id,
                "name": scenario.name,
                "description": scenario.description,
                "is_baseline": scenario.is_baseline,
                "status": scenario.status,
                "created_at": scenario.created_at.isoformat(),
                "updated_at": scenario.updated_at.isoformat(),
                "financing_params": scenario.financing_params,
                "rental_params": scenario.rental_params,
                "expense_params": scenario.expense_params,
                "results": scenario.results,
                "warnings": scenario.warnings
            }
            result.append(scenario_dict)
            
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve scenarios: {str(e)}")

@app.post("/properties/{property_id}/scenarios", response_model=Dict[str, Any])
async def create_scenario(
    property_id: int,
    scenario_data: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Create a new scenario for a property
    
    Args:
        property_id: ID of the property
        scenario_data: Scenario data
        background_tasks: Background tasks for async operations
        db: Database session
    
    Returns:
        Created scenario
    """
    try:
        # Verify property exists
        property_obj = db.query(Property).filter(Property.id == property_id).first()
        if not property_obj:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Create new scenario
        new_scenario = Scenario(
            property_id=property_id,
            user_id=property_obj.user_id,
            name=scenario_data.get("name", "New Scenario"),
            description=scenario_data.get("description", ""),
            is_baseline=scenario_data.get("is_baseline", False),
            financing_params=scenario_data.get("financing_params", {}),
            rental_params=scenario_data.get("rental_params", {}),
            expense_params=scenario_data.get("expense_params", {})
        )
        
        # Add to database
        db.add(new_scenario)
        db.commit()
        db.refresh(new_scenario)
        
        # If this is set as baseline, update other scenarios
        if new_scenario.is_baseline:
            other_scenarios = db.query(Scenario).filter(
                Scenario.property_id == property_id,
                Scenario.id != new_scenario.id
            ).all()
            
            for scenario in other_scenarios:
                scenario.is_baseline = False
            
            db.commit()
        
        # Schedule analysis in background if needed
        if background_tasks and scenario_data.get("run_analysis", False):
            background_tasks.add_task(
                analyze_scenario_background,
                scenario_id=new_scenario.id,
                db=db
            )
        
        # Return created scenario
        return {
            "id": new_scenario.id,
            "name": new_scenario.name,
            "description": new_scenario.description,
            "is_baseline": new_scenario.is_baseline,
            "status": new_scenario.status,
            "created_at": new_scenario.created_at.isoformat(),
            "updated_at": new_scenario.updated_at.isoformat(),
            "financing_params": new_scenario.financing_params,
            "rental_params": new_scenario.rental_params,
            "expense_params": new_scenario.expense_params,
            "results": new_scenario.results,
            "warnings": new_scenario.warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not create scenario: {str(e)}")

@app.get("/scenarios/{scenario_id}", response_model=Dict[str, Any])
async def get_scenario(
    scenario_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scenario
    
    Args:
        scenario_id: ID of the scenario
        db: Database session
    
    Returns:
        Scenario details
    """
    try:
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Return scenario data
        return {
            "id": scenario.id,
            "property_id": scenario.property_id,
            "name": scenario.name,
            "description": scenario.description,
            "is_baseline": scenario.is_baseline,
            "status": scenario.status,
            "created_at": scenario.created_at.isoformat(),
            "updated_at": scenario.updated_at.isoformat(),
            "financing_params": scenario.financing_params,
            "rental_params": scenario.rental_params,
            "expense_params": scenario.expense_params,
            "results": scenario.results,
            "warnings": scenario.warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve scenario: {str(e)}")

@app.post("/scenarios/{scenario_id}/analyze", response_model=Dict[str, Any])
async def analyze_scenario(
    scenario_id: int,
    analysis_params: Dict[str, Any] = Body({}),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Analyze a scenario
    
    Args:
        scenario_id: ID of the scenario
        analysis_params: Analysis parameters
        background_tasks: Background tasks for async operations
        db: Database session
    
    Returns:
        Analysis results or status
    """
    try:
        # Verify scenario exists
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            raise HTTPException(status_code=404, detail="Scenario not found")
        
        # Check if running in background
        run_in_background = analysis_params.get("run_in_background", True)
        
        if run_in_background and background_tasks:
            # Schedule analysis in background
            background_tasks.add_task(
                analyze_scenario_background,
                scenario_id=scenario_id,
                db=db
            )
            
            return {
                "status": "analyzing",
                "message": "Analysis started in background",
                "scenario_id": scenario_id
            }
        else:
            # Run analysis synchronously
            orchestrator = get_orchestrator()
            if not orchestrator:
                raise HTTPException(status_code=500, detail="Agent orchestrator not initialized")
            
            # Get property details
            property_obj = db.query(Property).filter(Property.id == scenario.property_id).first()
            if not property_obj:
                raise HTTPException(status_code=404, detail="Property not found")
            
            # Prepare analysis context
            analysis_context = {
                "scenario_id": scenario_id,
                "property_id": scenario.property_id,
                "user_id": scenario.user_id,
                "financing_params": scenario.financing_params,
                "rental_params": scenario.rental_params,
                "expense_params": scenario.expense_params,
                "property_details": property_obj.property_details,
                **analysis_params
            }
            
            # Run analysis
            results = await orchestrator.run_analysis(analysis_context)
            
            # Update scenario with results
            scenario.results = results.get("results", {})
            scenario.warnings = results.get("warnings", [])
            scenario.updated_at = datetime.utcnow()
            db.commit()
            
            # Return results
            return {
                "status": "completed",
                "message": "Analysis completed",
                "scenario_id": scenario_id,
                "results": results.get("results", {}),
                "warnings": results.get("warnings", [])
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing scenario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not analyze scenario: {str(e)}")

@app.get("/scenarios/compare", response_model=Dict[str, Any])
async def compare_scenarios(
    scenario_ids: List[int] = Query(..., description="List of scenario IDs to compare"),
    db: Session = Depends(get_db)
):
    """
    Compare multiple scenarios
    
    Args:
        scenario_ids: List of scenario IDs to compare
        db: Database session
    
    Returns:
        Comparison results with metrics and AI-generated insights
    """
    try:
        # Verify scenarios exist and belong to the same property
        scenarios = db.query(Scenario).filter(Scenario.id.in_(scenario_ids)).all()
        
        if len(scenarios) != len(scenario_ids):
            raise HTTPException(status_code=404, detail="One or more scenarios not found")
        
        # Check if all scenarios belong to the same property
        property_ids = set(s.property_id for s in scenarios)
        if len(property_ids) > 1:
            raise HTTPException(
                status_code=400, 
                detail="Cannot compare scenarios from different properties"
            )
        
        # Get orchestrator for comparison
        orchestrator = get_orchestrator()
        if not orchestrator:
            raise HTTPException(status_code=500, detail="Agent orchestrator not initialized")
        
        # Prepare comparison context
        scenario_data = []
        for scenario in scenarios:
            scenario_data.append({
                "id": scenario.id,
                "name": scenario.name,
                "financing_params": scenario.financing_params,
                "rental_params": scenario.rental_params,
                "expense_params": scenario.expense_params,
                "results": scenario.results,
            })
        
        # Run comparison analysis
        comparison_results = await orchestrator.run_comparison({
            "scenarios": scenario_data,
            "property_id": scenarios[0].property_id,
            "user_id": scenarios[0].user_id
        })
        
        return comparison_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not compare scenarios: {str(e)}")

@app.get("/updates/{client_id}", response_class=EventSourceResponse)
async def sse_updates(
    client_id: str,
    user_id: Optional[int] = None,
    property_id: Optional[int] = None,
    scenario_id: Optional[int] = None
):
    """
    Server-Sent Events (SSE) endpoint for real-time updates
    
    Args:
        client_id: Unique client identifier
        user_id: Optional user ID to filter updates
        property_id: Optional property ID to filter updates
        scenario_id: Optional scenario ID to filter updates
    
    Returns:
        SSE stream with updates
    """
    try:
        return await sse_manager.subscribe(
            client_id=client_id,
            user_id=user_id,
            property_id=property_id,
            scenario_id=scenario_id
        )
    except Exception as e:
        logger.error(f"Error setting up SSE stream: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not setup update stream: {str(e)}")

async def analyze_scenario_background(scenario_id: int, db: Session):
    """
    Background task to analyze a scenario
    
    Args:
        scenario_id: ID of the scenario to analyze
        db: Database session
    """
    try:
        # Get orchestrator
        orchestrator = get_orchestrator()
        if not orchestrator:
            logger.error("Agent orchestrator not initialized")
            return
        
        # Get scenario
        scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
        if not scenario:
            logger.error(f"Scenario {scenario_id} not found")
            return
        
        # Get property details
        property_obj = db.query(Property).filter(Property.id == scenario.property_id).first()
        if not property_obj:
            logger.error(f"Property {scenario.property_id} not found")
            return
        
        # Update scenario status
        scenario.status = "analyzing"
        db.commit()
        
        # Send update that analysis has started
        await sse_manager.send_update(
            event_type="analysis_status",
            data={
                "scenario_id": scenario_id,
                "status": "analyzing",
                "message": "Analysis in progress"
            },
            user_id=scenario.user_id,
            property_id=scenario.property_id,
            scenario_id=scenario_id
        )
        
        # Prepare analysis context
        analysis_context = {
            "scenario_id": scenario_id,
            "property_id": scenario.property_id,
            "user_id": scenario.user_id,
            "financing_params": scenario.financing_params,
            "rental_params": scenario.rental_params,
            "expense_params": scenario.expense_params,
            "property_details": property_obj.property_details
        }
        
        # Run analysis
        results = await orchestrator.run_analysis(analysis_context)
        
        # Update scenario with results
        scenario.results = results.get("results", {})
        scenario.warnings = results.get("warnings", [])
        scenario.status = "completed"
        scenario.updated_at = datetime.utcnow()
        db.commit()
        
        # Send update that analysis is complete
        await sse_manager.send_update(
            event_type="analysis_complete",
            data={
                "scenario_id": scenario_id,
                "status": "completed",
                "message": "Analysis completed",
                "results_summary": results.get("results_summary", {})
            },
            user_id=scenario.user_id,
            property_id=scenario.property_id,
            scenario_id=scenario_id
        )
        
    except Exception as e:
        logger.error(f"Error in background analysis: {str(e)}")
        
        # Update scenario status
        if scenario:
            scenario.status = "error"
            db.commit()
            
            # Send error update
            await sse_manager.send_update(
                event_type="analysis_error",
                data={
                    "scenario_id": scenario_id,
                    "status": "error",
                    "message": f"Analysis failed: {str(e)}"
                },
                user_id=scenario.user_id if scenario else None,
                property_id=scenario.property_id if scenario else None,
                scenario_id=scenario_id
            )