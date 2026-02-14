from typing import Dict, Any, List, Annotated, Literal
from typing_extensions import TypedDict
import operator
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.reviewer import ReviewerAgent

class WorkflowState(TypedDict):
    """State shared across all workflow nodes"""
    input: str
    plan: str
    executed_steps: Annotated[List[Dict], operator.add]
    current_results: Dict[str, Any]
    review_approved: bool
    final_output: str
    error: str
    iteration_count: int

class MultiAgentWorkflowBuilder:
    """Build and execute multi-agent workflows"""
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
    
    async def execute_workflow(self, user_input: str, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multi-agent workflow"""
        
        results = {
            "input": user_input,
            "steps": [],
            "final_output": "",
            "status": "running"
        }
        
        try:
            # Step 1: Planning
            if "planner" in self.agents:
                planner_result = await self.agents["planner"].execute({
                    "query": user_input,
                    "context": workflow_config.get("context", "")
                })
                results["steps"].append({
                    "step": "planning",
                    "agent": "planner",
                    "result": planner_result
                })
                plan = planner_result.get("plan", "")
            else:
                plan = "Execute task directly"
            
            # Step 2: Execution
            if "executor" in self.agents:
                executor_result = await self.agents["executor"].execute({
                    "task": user_input,
                    "previous_results": results["steps"]
                })
                results["steps"].append({
                    "step": "execution",
                    "agent": "executor",
                    "result": executor_result
                })
                execution_output = executor_result.get("result", "")
            else:
                execution_output = plan
            
            # Step 3: Review
            if "reviewer" in self.agents:
                reviewer_result = await self.agents["reviewer"].execute({
                    "task": user_input,
                    "results": results["steps"]
                })
                results["steps"].append({
                    "step": "review",
                    "agent": "reviewer",
                    "result": reviewer_result
                })
                approved = reviewer_result.get("approved", True)
            else:
                approved = True
            
            results["final_output"] = execution_output
            results["status"] = "completed" if approved else "needs_revision"
            results["approved"] = approved
            
        except Exception as e:
            results["error"] = str(e)
            results["status"] = "failed"
        
        return results