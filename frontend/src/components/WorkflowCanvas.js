import React, { useState, useCallback, useRef, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Play, Plus, Save, Trash2 } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';
import useWorkflowStore from '../store/workflowStore';

const API = '/api';

const nodeColors = {
  planner: '#7c3aed',
  executor: '#3b82f6',
  reviewer: '#10b981',
  start: '#10b981',
  end: '#ef4444',
};

const WorkflowCanvas = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [workflowName, setWorkflowName] = useState('');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedAgentType, setSelectedAgentType] = useState('planner');
  const [selectedModel, setSelectedModel] = useState('mistral');
  const [nodeInstructions, setNodeInstructions] = useState('');
  const reactFlowWrapper = useRef(null);
  const { addWorkflow } = useWorkflowStore();

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: '#7c3aed' } }, eds)),
    [setEdges]
  );

  const addNode = (type) => {
    const newNode = {
      id: `node-${Date.now()}`,
      type: 'default',
      position: {
        x: Math.random() * 400 + 100,
        y: Math.random() * 300 + 100,
      },
      data: {
        label: (
          <div className="px-3 py-2 text-center">
            <div className="font-semibold text-sm">{type.toUpperCase()}</div>
            <div className="text-xs text-gray-300 mt-1">Click to configure</div>
          </div>
        ),
        agentType: type,
        model: selectedModel,
        instructions: 'Default agent instructions',
      },
      style: {
        background: nodeColors[type] || '#3b82f6',
        color: '#ffffff',
        border: '2px solid rgba(255,255,255,0.2)',
        borderRadius: '8px',
        padding: '0',
        minWidth: '150px',
        boxShadow: `0 0 20px ${nodeColors[type]}33`,
      },
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const onNodeClick = useCallback((event, node) => {
    setSelectedNode(node);
    setSelectedAgentType(node.data.agentType || 'executor');
    setSelectedModel(node.data.model || 'mistral');
    setNodeInstructions(node.data.instructions || '');
  }, []);

  const updateSelectedNode = () => {
    if (!selectedNode) return;

    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedNode.id) {
          return {
            ...node,
            data: {
              ...node.data,
              label: (
                <div className="px-3 py-2 text-center">
                  <div className="font-semibold text-sm">{selectedAgentType.toUpperCase()}</div>
                  <div className="text-xs text-gray-300 mt-1">{selectedModel}</div>
                </div>
              ),
              agentType: selectedAgentType,
              model: selectedModel,
              instructions: nodeInstructions,
            },
            style: {
              ...node.style,
              background: nodeColors[selectedAgentType] || '#3b82f6',
              boxShadow: `0 0 20px ${nodeColors[selectedAgentType]}33`,
            },
          };
        }
        return node;
      })
    );
    toast.success('Node updated successfully');
  };

  const deleteSelectedNode = () => {
    if (!selectedNode) return;
    setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
    setEdges((eds) => eds.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id));
    setSelectedNode(null);
    toast.success('Node deleted');
  };

  const saveWorkflow = async () => {
    if (!workflowName.trim()) {
      toast.error('Please enter a workflow name');
      return;
    }

    if (nodes.length === 0) {
      toast.error('Add at least one node to the workflow');
      return;
    }

    try {
      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        nodes: nodes.map((node) => ({
          id: node.id,
          type: 'agent',
          agent_type: node.data.agentType,
          model: node.data.model,
          instructions: node.data.instructions,
          position: node.position,
        })),
        edges: edges.map((edge) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          condition: null,
        })),
      };

      const response = await axios.post(`${API}/workflows`, workflowData);
      addWorkflow(response.data);
      toast.success('Workflow saved successfully!');
      
      // Reset form
      setWorkflowName('');
      setWorkflowDescription('');
      setNodes([]);
      setEdges([]);
      setSelectedNode(null);
    } catch (error) {
      console.error('Error saving workflow:', error);
      toast.error('Failed to save workflow');
    }
  };

  return (
    <div className="grid grid-cols-12 gap-4 h-[calc(100vh-200px)]">
      {/* Left Sidebar - Node Library */}
      <div className="col-span-3 space-y-4 overflow-y-auto">
        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="node-library-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Node Library
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              data-testid="add-planner-node-btn"
              onClick={() => addNode('planner')}
              className="w-full bg-violet-600 hover:bg-violet-700 text-white transition-all duration-200 hover:-translate-y-0.5"
            >
              + Planner Agent
            </Button>
            <Button
              data-testid="add-executor-node-btn"
              onClick={() => addNode('executor')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white transition-all duration-200 hover:-translate-y-0.5"
            >
              + Executor Agent
            </Button>
            <Button
              data-testid="add-reviewer-node-btn"
              onClick={() => addNode('reviewer')}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white transition-all duration-200 hover:-translate-y-0.5"
            >
              + Reviewer Agent
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="workflow-config-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white">Workflow Config</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-zinc-300 uppercase tracking-wider">Name</label>
              <Input
                data-testid="workflow-name-input"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                placeholder="My Workflow"
                className="bg-zinc-800 border-zinc-700 text-white mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium text-zinc-300 uppercase tracking-wider">Description</label>
              <Textarea
                data-testid="workflow-description-input"
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
                placeholder="Describe your workflow..."
                className="bg-zinc-800 border-zinc-700 text-white mt-1 min-h-[80px]"
              />
            </div>
            <Button
              data-testid="save-workflow-btn"
              onClick={saveWorkflow}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-semibold"
            >
              <Save className="w-4 h-4 mr-2" />
              Save Workflow
            </Button>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800">
          <CardHeader>
            <CardTitle className="text-sm text-zinc-400">Canvas Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Nodes:</span>
              <Badge variant="secondary" className="bg-violet-600/20 text-violet-300">
                {nodes.length}
              </Badge>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-zinc-400">Connections:</span>
              <Badge variant="secondary" className="bg-blue-600/20 text-blue-300">
                {edges.length}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Center - Canvas */}
      <div className="col-span-6" ref={reactFlowWrapper}>
        <Card className="h-full bg-black/40 backdrop-blur-md border-zinc-800" data-testid="workflow-canvas">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            fitView
            style={{ background: '#09090b' }}
          >
            <Background color="#27272a" gap={20} size={1} />
            <Controls className="bg-zinc-900 border-zinc-800" />
            <MiniMap
              className="bg-zinc-900 border-zinc-800"
              nodeColor={(node) => node.style.background}
            />
            <Panel position="top-center" className="bg-zinc-900/90 backdrop-blur-md px-4 py-2 rounded-lg border border-zinc-800">
              <div className="text-white font-semibold text-sm">
                Drag nodes to arrange • Connect nodes to create workflow
              </div>
            </Panel>
          </ReactFlow>
        </Card>
      </div>

      {/* Right Sidebar - Node Configuration */}
      <div className="col-span-3 space-y-4 overflow-y-auto">
        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="node-config-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white">
              {selectedNode ? 'Configure Node' : 'Select a Node'}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedNode ? (
              <>
                <div>
                  <label className="text-sm font-medium text-zinc-300 uppercase tracking-wider">Agent Type</label>
                  <Select value={selectedAgentType} onValueChange={setSelectedAgentType}>
                    <SelectTrigger data-testid="agent-type-select" className="bg-zinc-800 border-zinc-700 text-white mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      <SelectItem value="planner">Planner</SelectItem>
                      <SelectItem value="executor">Executor</SelectItem>
                      <SelectItem value="reviewer">Reviewer</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-zinc-300 uppercase tracking-wider">LLM Model</label>
                  <Select value={selectedModel} onValueChange={setSelectedModel}>
                    <SelectTrigger data-testid="model-select" className="bg-zinc-800 border-zinc-700 text-white mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-zinc-800 border-zinc-700">
                      <SelectItem value="mistral">Mistral</SelectItem>
                      <SelectItem value="llama3">Llama 3</SelectItem>
                      <SelectItem value="qwen2">Qwen 2</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium text-zinc-300 uppercase tracking-wider">Instructions</label>
                  <Textarea
                    data-testid="node-instructions-input"
                    value={nodeInstructions}
                    onChange={(e) => setNodeInstructions(e.target.value)}
                    placeholder="Enter agent instructions in natural language..."
                    className="bg-zinc-800 border-zinc-700 text-white mt-1 min-h-[120px] font-mono text-xs"
                  />
                </div>

                <div className="flex gap-2">
                  <Button
                    data-testid="update-node-btn"
                    onClick={updateSelectedNode}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    Update Node
                  </Button>
                  <Button
                    data-testid="delete-node-btn"
                    onClick={deleteSelectedNode}
                    variant="destructive"
                    className="bg-red-600 hover:bg-red-700"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </>
            ) : (
              <div className="text-center text-zinc-500 py-8">
                <p>Click on a node to configure it</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default WorkflowCanvas;