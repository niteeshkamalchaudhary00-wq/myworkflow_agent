from typing import Dict, Any
import httpx
from agents.base import BaseAgent
from config import get_settings

settings = get_settings()

class ExecutorAgent(BaseAgent):
    """Executor agent that performs individual tasks"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task"""
        task = input_data.get("task", "")
        previous_results = input_data.get("previous_results", [])
        
        # Execute task
        result = await self._execute_task(
            f"Task: {task}\n\nPrevious results:\n{previous_results}"
        )
        
        await self.log_execution("task_execution", {
            "task": task,
            "result": result
        })
        
        return {
            "agent_id": self.agent_id,
            "type": "execution",
            "task": task,
            "result": result,
            "success": True,
            "status": "completed"
        }
    
    async def _execute_task(self, context: str) -> str:
        """Execute task using Ollama"""
        prompt = f"""{self.instructions}

Task context:
{context}

Provide a detailed execution of the task."""
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ollama_host}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                return response.json()["response"]
        except Exception as e:
            return f"Error executing task: {str(e)}"