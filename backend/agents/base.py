from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timezone

class BaseAgent(ABC):
    """Base class for all agent types in multi-agent system"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        model_name: str,
        instructions: str
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.model_name = model_name
        self.instructions = instructions
        self.execution_history = []
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with given input"""
        pass
    
    async def log_execution(self, action: str, result: Any):
        """Log execution step for debugging"""
        self.execution_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history