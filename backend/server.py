from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import os
import uuid
import logging
from pathlib import Path
from dotenv import load_dotenv

from config import get_settings
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.reviewer import ReviewerAgent
from workflows.builder import MultiAgentWorkflowBuilder

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

settings = get_settings()

mongo_url = os.environ.get('MONGO_URL', '')
db = None
client = None
use_memory_store = True

if mongo_url:
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ.get('DB_NAME', 'test_database')]
        use_memory_store = False
    except Exception:
        pass

memory_workflows: Dict[str, Dict] = {}
memory_executions: Dict[str, Dict] = {}

app = FastAPI(
    title="Multi-Agent AI Workflow Engine",
    description="Build and execute multi-agent AI workflows",
    version="1.0.0"
)

api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NodeConfig(BaseModel):
    id: str
    type: str
    agent_type: Optional[str] = None
    model: Optional[str] = "mistral"
    instructions: Optional[str] = ""
    position: Optional[Dict[str, float]] = None

class EdgeConfig(BaseModel):
    id: str
    source: str
    target: str
    condition: Optional[str] = None

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]

class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str
    nodes: List[NodeConfig]
    edges: List[EdgeConfig]
    created_at: str
    updated_at: str

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    input: str
    context: Optional[Dict[str, Any]] = {}

class ExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    input: str
    steps: List[Dict[str, Any]]
    final_output: str
    created_at: str

class OllamaModelResponse(BaseModel):
    name: str
    available: bool

@api_router.get("/")
async def root():
    return {
        "service": "Multi-Agent AI Workflow Engine",
        "version": "1.0.0",
        "status": "running",
        "storage": "mongodb" if not use_memory_store else "in-memory"
    }

@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "workflow-engine",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/models", response_model=List[OllamaModelResponse])
async def list_models():
    models = [
        {"name": "mistral", "available": True},
        {"name": "llama3", "available": True},
        {"name": "qwen2", "available": True}
    ]
    return models

@api_router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(workflow: WorkflowCreate):
    try:
        workflow_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        workflow_doc = {
            "id": workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "nodes": [node.model_dump() for node in workflow.nodes],
            "edges": [edge.model_dump() for edge in workflow.edges],
            "created_at": now,
            "updated_at": now
        }

        if use_memory_store:
            memory_workflows[workflow_id] = workflow_doc
        else:
            await db.workflows.insert_one(workflow_doc)

        return WorkflowResponse(**workflow_doc)

    except Exception as e:
        logger.error(f"Error creating workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows():
    try:
        if use_memory_store:
            return list(memory_workflows.values())
        workflows = await db.workflows.find({}, {"_id": 0}).to_list(100)
        return workflows
    except Exception as e:
        logger.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: str):
    try:
        if use_memory_store:
            workflow = memory_workflows.get(workflow_id)
        else:
            workflow = await db.workflows.find_one({"id": workflow_id}, {"_id": 0})
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    try:
        if use_memory_store:
            if workflow_id not in memory_workflows:
                raise HTTPException(status_code=404, detail="Workflow not found")
            del memory_workflows[workflow_id]
        else:
            result = await db.workflows.delete_one({"id": workflow_id})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Workflow not found")
        return {"message": "Workflow deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/workflows/execute", response_model=ExecutionResponse)
async def execute_workflow(request: WorkflowExecuteRequest, background_tasks: BackgroundTasks):
    try:
        if use_memory_store:
            workflow = memory_workflows.get(request.workflow_id)
        else:
            workflow = await db.workflows.find_one({"id": request.workflow_id}, {"_id": 0})
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        agents = {}
        for node in workflow["nodes"]:
            if node["type"] == "agent":
                agent_type = node.get("agent_type", "executor")
                model = node.get("model", "mistral")
                instructions = node.get("instructions", f"You are a {agent_type} agent.")

                if agent_type == "planner":
                    agents["planner"] = PlannerAgent(
                        agent_id=node["id"],
                        agent_type="planner",
                        model_name=model,
                        instructions=instructions
                    )
                elif agent_type == "executor":
                    agents["executor"] = ExecutorAgent(
                        agent_id=node["id"],
                        agent_type="executor",
                        model_name=model,
                        instructions=instructions
                    )
                elif agent_type == "reviewer":
                    agents["reviewer"] = ReviewerAgent(
                        agent_id=node["id"],
                        agent_type="reviewer",
                        model_name=model,
                        instructions=instructions
                    )

        builder = MultiAgentWorkflowBuilder(agents=agents)
        result = await builder.execute_workflow(
            user_input=request.input,
            workflow_config=request.context
        )

        execution_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        execution_doc = {
            "execution_id": execution_id,
            "workflow_id": request.workflow_id,
            "status": result.get("status", "completed"),
            "input": request.input,
            "steps": result.get("steps", []),
            "final_output": result.get("final_output", ""),
            "created_at": now
        }

        if use_memory_store:
            memory_executions[execution_id] = execution_doc
        else:
            await db.executions.insert_one(execution_doc)

        return ExecutionResponse(**execution_doc)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str):
    try:
        if use_memory_store:
            execution = memory_executions.get(execution_id)
        else:
            execution = await db.executions.find_one({"execution_id": execution_id}, {"_id": 0})
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        return execution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/executions/workflow/{workflow_id}", response_model=List[ExecutionResponse])
async def list_workflow_executions(workflow_id: str):
    try:
        if use_memory_store:
            execs = [e for e in memory_executions.values() if e["workflow_id"] == workflow_id]
            execs.sort(key=lambda x: x["created_at"], reverse=True)
            return execs[:50]
        executions = await db.executions.find(
            {"workflow_id": workflow_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        return executions
    except Exception as e:
        logger.error(f"Error listing executions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
