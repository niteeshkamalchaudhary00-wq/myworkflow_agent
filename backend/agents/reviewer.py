from typing import Dict, Any
import httpx
import re
import json
from agents.base import BaseAgent
from config import get_settings

settings = get_settings()

class ReviewerAgent(BaseAgent):
    """Reviewer agent that evaluates task completion and results quality"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review task results and determine if acceptable"""
        task_description = input_data.get("task", "")
        execution_results = input_data.get("results", [])
        
        # Evaluate results
        review = await self._evaluate_results(
            f"Task: {task_description}\n\nExecution results:\n{json.dumps(execution_results, indent=2)}"
        )
        
        # Parse review decision
        decision = await self._parse_review(review)
        
        await self.log_execution("review", {
            "task": task_description,
            "decision": decision,
            "review": review
        })
        
        return {
            "agent_id": self.agent_id,
            "type": "review",
            "approved": decision.get("approved", False),
            "feedback": decision.get("feedback", ""),
            "confidence": decision.get("confidence", 0.8),
            "status": "completed"
        }
    
    async def _evaluate_results(self, context: str) -> str:
        """Evaluate task completion and quality"""
        prompt = f"""{self.instructions}

Review context:
{context}

Provide a detailed review. Is the task completed successfully? Answer YES or NO, then provide feedback."""
        
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
            return f"Error evaluating results: {str(e)}"
    
    async def _parse_review(self, review_text: str) -> Dict[str, Any]:
        """Parse review decision from LLM output"""
        approved = "yes" in review_text.lower()[:100]
        
        return {
            "approved": approved,
            "feedback": review_text,
            "confidence": 0.8
        }