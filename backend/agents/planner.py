from typing import Dict, Any
import httpx
import json
from agents.base import BaseAgent
from config import get_settings

settings = get_settings()

class PlannerAgent(BaseAgent):
    """Planner agent that breaks down complex tasks into executable steps"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate execution plan from user request"""
        user_query = input_data.get("query", "")
        context = input_data.get("context", "")
        
        # Generate initial plan
        plan = await self._generate_plan(f"User query: {user_query}\n\nContext: {context}")
        
        # Parse plan into structured steps
        steps = await self._parse_plan(plan)
        
        await self.log_execution("plan_generation", {
            "query": user_query,
            "plan": plan,
            "steps": steps
        })
        
        return {
            "agent_id": self.agent_id,
            "type": "plan",
            "plan": plan,
            "steps": steps,
            "num_steps": len(steps),
            "status": "success"
        }
    
    async def _generate_plan(self, context: str) -> str:
        """Generate plan using Ollama"""
        prompt = f"""{self.instructions}

User request:
{context}

Generate a detailed, step-by-step plan to accomplish this task. Format each step clearly:
Step 1: [action description]
Step 2: [action description]
..."""
        
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
            return f"Error generating plan: {str(e)}"
    
    async def _parse_plan(self, plan_text: str) -> list:
        """Parse plan text into structured steps"""
        steps = []
        for line in plan_text.split("\n"):
            line = line.strip()
            if line and (line.startswith("Step") or line.startswith("-")):
                steps.append(line)
        return steps if steps else ["Execute the planned task"]