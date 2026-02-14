from typing import Dict, Any, List
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.reviewer import ReviewerAgent
from nodes import (
    HTTPRequestNode,
    DataTransformNode,
    ConditionalNode,
    WebhookNode,
    DelayNode
)

class EnhancedWorkflowBuilder:
    """Build and execute workflows with both AI agents and manual nodes"""
    
    def __init__(self, nodes_config: List[Dict[str, Any]]):
        self.nodes = {}
        self._initialize_nodes(nodes_config)
    
    def _initialize_nodes(self, nodes_config: List[Dict[str, Any]]):
        """Initialize all nodes from configuration"""
        for node_config in nodes_config:
            node_id = node_config.get("id")
            node_type = node_config.get("type")
            
            if node_type == "agent":
                agent_type = node_config.get("agent_type")
                model = node_config.get("model", "mistral")
                instructions = node_config.get("instructions", "")
                
                if agent_type == "planner":
                    self.nodes[node_id] = PlannerAgent(
                        agent_id=node_id,
                        agent_type="planner",
                        model_name=model,
                        instructions=instructions
                    )
                elif agent_type == "executor":
                    self.nodes[node_id] = ExecutorAgent(
                        agent_id=node_id,
                        agent_type="executor",
                        model_name=model,
                        instructions=instructions
                    )
                elif agent_type == "reviewer":
                    self.nodes[node_id] = ReviewerAgent(
                        agent_id=node_id,
                        agent_type="reviewer",
                        model_name=model,
                        instructions=instructions
                    )
            
            elif node_type == "http_request":
                self.nodes[node_id] = HTTPRequestNode(
                    node_id=node_id,
                    node_type="http_request",
                    config=node_config.get("config", {})
                )
            
            elif node_type == "data_transform":
                self.nodes[node_id] = DataTransformNode(
                    node_id=node_id,
                    node_type="data_transform",
                    config=node_config.get("config", {})
                )
            
            elif node_type == "conditional":
                self.nodes[node_id] = ConditionalNode(
                    node_id=node_id,
                    node_type="conditional",
                    config=node_config.get("config", {})
                )
            
            elif node_type == "webhook":
                self.nodes[node_id] = WebhookNode(
                    node_id=node_id,
                    node_type="webhook",
                    config=node_config.get("config", {})
                )
            
            elif node_type == "delay":
                self.nodes[node_id] = DelayNode(
                    node_id=node_id,
                    node_type="delay",
                    config=node_config.get("config", {})
                )
    
    async def execute_workflow(self, 
                             user_input: str, 
                             edges: List[Dict[str, Any]],
                             start_node_id: str = None) -> Dict[str, Any]:
        """Execute workflow following the edge connections"""
        results = {
            "input": user_input,
            "steps": [],
            "final_output": "",
            "status": "running"
        }
        
        # Build execution order from edges
        execution_order = self._build_execution_order(edges, start_node_id)
        
        # Execute nodes in order
        current_data = {"input": user_input}
        
        try:
            for node_id in execution_order:
                if node_id not in self.nodes:
                    continue
                
                node = self.nodes[node_id]
                
                # Execute node
                node_result = await node.execute(current_data)
                
                # Store result
                results["steps"].append({
                    "node_id": node_id,
                    "node_type": getattr(node, "node_type", "unknown"),
                    "result": node_result
                })
                
                # Update current data with node output
                if node_result.get("success"):
                    current_data.update(node_result.get("result", {}))
                else:
                    # Stop execution on error
                    results["status"] = "failed"
                    results["error"] = node_result.get("error", "Unknown error")
                    break
            
            if results["status"] != "failed":
                results["status"] = "completed"
                results["final_output"] = str(current_data)
        
        except Exception as e:
            results["error"] = str(e)
            results["status"] = "failed"
        
        return results
    
    def _build_execution_order(self, 
                              edges: List[Dict[str, Any]], 
                              start_node_id: str = None) -> List[str]:
        """Build execution order from edges (topological sort)"""
        # Build adjacency list
        graph = {}
        in_degree = {}
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            
            if source not in graph:
                graph[source] = []
            graph[source].append(target)
            
            in_degree[target] = in_degree.get(target, 0) + 1
            if source not in in_degree:
                in_degree[source] = 0
        
        # Find start nodes (no incoming edges)
        if start_node_id:
            queue = [start_node_id]
        else:
            queue = [node for node, degree in in_degree.items() if degree == 0]
        
        execution_order = []
        
        while queue:
            node = queue.pop(0)
            execution_order.append(node)
            
            if node in graph:
                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        return execution_order