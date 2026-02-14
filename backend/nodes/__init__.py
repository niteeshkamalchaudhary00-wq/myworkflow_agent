from typing import Dict, Any
from abc import ABC, abstractmethod
import json
import httpx
from datetime import datetime, timezone

class ManualNode(ABC):
    """Base class for manual workflow nodes (non-AI)"""
    
    def __init__(self, node_id: str, node_type: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type
        self.config = config
        self.execution_history = []
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute node with given input"""
        pass
    
    async def log_execution(self, action: str, result: Any):
        """Log execution step"""
        self.execution_history.append({
            "action": action,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

class HTTPRequestNode(ManualNode):
    """HTTP Request node for API calls"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make HTTP request"""
        method = self.config.get("method", "GET")
        url = self.config.get("url", "")
        headers = self.config.get("headers", {})
        body = self.config.get("body", {})
        timeout = self.config.get("timeout", 30)
        
        # Replace variables in URL and body with input data
        url = self._replace_variables(url, input_data)
        body = self._replace_variables_in_dict(body, input_data)
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=body)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=body)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                result = {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                }
                
                await self.log_execution("http_request", result)
                return {
                    "node_id": self.node_id,
                    "type": "http_request",
                    "success": response.status_code < 400,
                    "result": result
                }
        except Exception as e:
            return {
                "node_id": self.node_id,
                "type": "http_request",
                "success": False,
                "error": str(e)
            }
    
    def _replace_variables(self, text: str, data: Dict[str, Any]) -> str:
        """Replace {{variable}} with actual values"""
        if not isinstance(text, str):
            return text
        for key, value in data.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
        return text
    
    def _replace_variables_in_dict(self, obj: Any, data: Dict[str, Any]) -> Any:
        """Recursively replace variables in dict/list"""
        if isinstance(obj, dict):
            return {k: self._replace_variables_in_dict(v, data) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_variables_in_dict(item, data) for item in obj]
        elif isinstance(obj, str):
            return self._replace_variables(obj, data)
        return obj

class DataTransformNode(ManualNode):
    """Data transformation node"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data"""
        operation = self.config.get("operation", "map")
        
        try:
            if operation == "map":
                result = self._map_data(input_data)
            elif operation == "filter":
                result = self._filter_data(input_data)
            elif operation == "reduce":
                result = self._reduce_data(input_data)
            elif operation == "custom":
                result = self._custom_transform(input_data)
            else:
                result = input_data
            
            await self.log_execution("data_transform", result)
            return {
                "node_id": self.node_id,
                "type": "data_transform",
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "node_id": self.node_id,
                "type": "data_transform",
                "success": False,
                "error": str(e)
            }
    
    def _map_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map data fields"""
        mapping = self.config.get("mapping", {})
        result = {}
        for target_key, source_key in mapping.items():
            if source_key in data:
                result[target_key] = data[source_key]
        return result
    
    def _filter_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data based on conditions"""
        conditions = self.config.get("conditions", {})
        # Simple filtering logic
        return {k: v for k, v in data.items() if k in conditions}
    
    def _reduce_data(self, data: Dict[str, Any]) -> Any:
        """Reduce data to single value"""
        operation = self.config.get("reduce_operation", "sum")
        values = list(data.values()) if isinstance(data, dict) else data
        
        if operation == "sum":
            return sum(v for v in values if isinstance(v, (int, float)))
        elif operation == "avg":
            nums = [v for v in values if isinstance(v, (int, float))]
            return sum(nums) / len(nums) if nums else 0
        elif operation == "count":
            return len(values)
        return values
    
    def _custom_transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom transformation using provided code"""
        transform_code = self.config.get("transform_code", "")
        # For safety, only allow simple operations
        # In production, use a sandboxed execution environment
        return data

class ConditionalNode(ManualNode):
    """Conditional branching node"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate condition and return branch"""
        condition_type = self.config.get("condition_type", "equals")
        field = self.config.get("field", "")
        value = self.config.get("value", "")
        
        try:
            field_value = input_data.get(field)
            condition_met = False
            
            if condition_type == "equals":
                condition_met = field_value == value
            elif condition_type == "not_equals":
                condition_met = field_value != value
            elif condition_type == "greater_than":
                condition_met = float(field_value) > float(value)
            elif condition_type == "less_than":
                condition_met = float(field_value) < float(value)
            elif condition_type == "contains":
                condition_met = value in str(field_value)
            elif condition_type == "exists":
                condition_met = field in input_data
            
            result = {
                "condition_met": condition_met,
                "branch": "true_branch" if condition_met else "false_branch"
            }
            
            await self.log_execution("conditional", result)
            return {
                "node_id": self.node_id,
                "type": "conditional",
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "node_id": self.node_id,
                "type": "conditional",
                "success": False,
                "error": str(e)
            }

class WebhookNode(ManualNode):
    """Webhook trigger/receiver node"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook data"""
        webhook_url = self.config.get("webhook_url", "")
        method = self.config.get("method", "POST")
        
        result = {
            "webhook_url": webhook_url,
            "received_data": input_data,
            "processed": True
        }
        
        await self.log_execution("webhook", result)
        return {
            "node_id": self.node_id,
            "type": "webhook",
            "success": True,
            "result": result
        }

class DelayNode(ManualNode):
    """Delay/Wait node"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for specified time"""
        import asyncio
        delay_seconds = self.config.get("delay_seconds", 1)
        
        try:
            await asyncio.sleep(delay_seconds)
            
            result = {
                "delayed_seconds": delay_seconds,
                "data": input_data
            }
            
            await self.log_execution("delay", result)
            return {
                "node_id": self.node_id,
                "type": "delay",
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "node_id": self.node_id,
                "type": "delay",
                "success": False,
                "error": str(e)
            }