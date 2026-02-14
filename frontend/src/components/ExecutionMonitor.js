import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Play, Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';
import useWorkflowStore from '../store/workflowStore';

const API = '/api';

const ExecutionMonitor = () => {
  const { workflows, executions, updateWorkflows, updateExecutions } = useWorkflowStore();
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [executionInput, setExecutionInput] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [workflowExecutions, setWorkflowExecutions] = useState([]);
  const [selectedExecution, setSelectedExecution] = useState(null);

  useEffect(() => {
    loadWorkflows();
  }, []);

  useEffect(() => {
    if (selectedWorkflow) {
      loadWorkflowExecutions(selectedWorkflow.id);
    }
  }, [selectedWorkflow]);

  const loadWorkflows = async () => {
    try {
      const response = await axios.get(`${API}/workflows`);
      updateWorkflows(response.data);
      if (response.data.length > 0 && !selectedWorkflow) {
        setSelectedWorkflow(response.data[0]);
      }
    } catch (error) {
      console.error('Error loading workflows:', error);
    }
  };

  const loadWorkflowExecutions = async (workflowId) => {
    try {
      const response = await axios.get(`${API}/executions/workflow/${workflowId}`);
      setWorkflowExecutions(response.data);
    } catch (error) {
      console.error('Error loading executions:', error);
    }
  };

  const executeWorkflow = async () => {
    if (!selectedWorkflow) {
      toast.error('Please select a workflow');
      return;
    }

    if (!executionInput.trim()) {
      toast.error('Please enter input for the workflow');
      return;
    }

    setIsExecuting(true);
    try {
      const response = await axios.post(`${API}/workflows/execute`, {
        workflow_id: selectedWorkflow.id,
        input: executionInput,
        context: {},
      });

      toast.success('Workflow executed successfully!');
      setSelectedExecution(response.data);
      loadWorkflowExecutions(selectedWorkflow.id);
      setExecutionInput('');
    } catch (error) {
      console.error('Error executing workflow:', error);
      toast.error('Failed to execute workflow');
    } finally {
      setIsExecuting(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-emerald-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'running':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-emerald-600/20 text-emerald-300';
      case 'failed':
        return 'bg-red-600/20 text-red-300';
      case 'running':
        return 'bg-blue-600/20 text-blue-300';
      default:
        return 'bg-yellow-600/20 text-yellow-300';
    }
  };

  return (
    <div className="grid grid-cols-12 gap-4 h-[calc(100vh-200px)]">
      {/* Left Sidebar - Workflow Selection */}
      <div className="col-span-3 space-y-4 overflow-y-auto">
        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="workflow-selector-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white">Select Workflow</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {workflows.length === 0 ? (
              <p className="text-zinc-500 text-sm text-center py-4">No workflows available</p>
            ) : (
              <Select
                value={selectedWorkflow?.id}
                onValueChange={(value) => {
                  const workflow = workflows.find((w) => w.id === value);
                  setSelectedWorkflow(workflow);
                }}
              >
                <SelectTrigger data-testid="workflow-select" className="bg-zinc-800 border-zinc-700 text-white">
                  <SelectValue placeholder="Choose a workflow" />
                </SelectTrigger>
                <SelectContent className="bg-zinc-800 border-zinc-700">
                  {workflows.map((workflow) => (
                    <SelectItem key={workflow.id} value={workflow.id}>
                      {workflow.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {selectedWorkflow && (
              <div className="mt-4 p-3 bg-zinc-800/50 rounded-lg">
                <h4 className="text-sm font-semibold text-white mb-1">{selectedWorkflow.name}</h4>
                <p className="text-xs text-zinc-400">{selectedWorkflow.description || 'No description'}</p>
                <div className="flex gap-2 mt-3">
                  <Badge variant="secondary" className="bg-violet-600/20 text-violet-300">
                    {selectedWorkflow.nodes?.length || 0} nodes
                  </Badge>
                  <Badge variant="secondary" className="bg-blue-600/20 text-blue-300">
                    {selectedWorkflow.edges?.length || 0} edges
                  </Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="execute-workflow-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white">Execute Workflow</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium text-zinc-300 uppercase tracking-wider">Input</label>
              <Textarea
                data-testid="execution-input-textarea"
                value={executionInput}
                onChange={(e) => setExecutionInput(e.target.value)}
                placeholder="Enter your task or query..."
                className="bg-zinc-800 border-zinc-700 text-white mt-1 min-h-[120px]"
                disabled={isExecuting}
              />
            </div>
            <Button
              data-testid="execute-workflow-btn"
              onClick={executeWorkflow}
              disabled={isExecuting || !selectedWorkflow}
              className="w-full bg-violet-600 hover:bg-violet-700 text-white font-semibold"
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Run Workflow
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Center - Execution History */}
      <div className="col-span-5 space-y-4 overflow-y-auto">
        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="execution-history-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white">Execution History</CardTitle>
            <CardDescription className="text-zinc-400">Recent workflow executions</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[calc(100vh-350px)]">
              {workflowExecutions.length === 0 ? (
                <div className="text-center text-zinc-500 py-8">
                  <p>No executions yet</p>
                  <p className="text-sm mt-2">Run a workflow to see results here</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {workflowExecutions.map((execution) => (
                    <div
                      key={execution.execution_id}
                      data-testid={`execution-item-${execution.execution_id}`}
                      onClick={() => setSelectedExecution(execution)}
                      className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 hover:-translate-y-0.5 ${
                        selectedExecution?.execution_id === execution.execution_id
                          ? 'bg-violet-600/10 border-violet-600/50'
                          : 'bg-zinc-800/50 border-zinc-700 hover:border-zinc-600'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <Badge className={getStatusColor(execution.status)}>
                          <span className="flex items-center gap-1">
                            {getStatusIcon(execution.status)}
                            {execution.status}
                          </span>
                        </Badge>
                        <span className="text-xs text-zinc-500">
                          {new Date(execution.created_at).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-white font-medium truncate">{execution.input}</p>
                      <p className="text-xs text-zinc-400 mt-1">{execution.steps?.length || 0} steps completed</p>
                    </div>
                  ))}
                </div>
              )}
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Right Sidebar - Execution Details */}
      <div className="col-span-4 space-y-4 overflow-y-auto">
        <Card className="bg-zinc-900/80 backdrop-blur-md border-zinc-800" data-testid="execution-details-card">
          <CardHeader>
            <CardTitle className="text-lg font-bold text-white">Execution Details</CardTitle>
          </CardHeader>
          <CardContent>
            {selectedExecution ? (
              <ScrollArea className="h-[calc(100vh-300px)]">
                <div className="space-y-4">
                  <div>
                    <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Status</label>
                    <Badge className={`mt-1 ${getStatusColor(selectedExecution.status)}`}>
                      {selectedExecution.status}
                    </Badge>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Input</label>
                    <div className="mt-1 p-3 bg-zinc-800/50 rounded-lg">
                      <p className="text-sm text-white">{selectedExecution.input}</p>
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-2 block">
                      Execution Steps ({selectedExecution.steps?.length || 0})
                    </label>
                    <div className="space-y-3">
                      {selectedExecution.steps?.map((step, index) => (
                        <div
                          key={index}
                          data-testid={`step-${index}`}
                          className="p-3 bg-zinc-800/50 rounded-lg border border-zinc-700"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-semibold text-white capitalize">{step.step}</span>
                            <Badge variant="secondary" className="bg-blue-600/20 text-blue-300 text-xs">
                              {step.agent}
                            </Badge>
                          </div>
                          <div className="text-xs text-zinc-400 font-mono bg-black/30 p-2 rounded overflow-auto max-h-32">
                            {JSON.stringify(step.result, null, 2)}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Final Output</label>
                    <div className="mt-1 p-3 bg-zinc-800/50 rounded-lg">
                      <p className="text-sm text-white whitespace-pre-wrap">
                        {selectedExecution.final_output || 'No output available'}
                      </p>
                    </div>
                  </div>
                </div>
              </ScrollArea>
            ) : (
              <div className="text-center text-zinc-500 py-8">
                <p>Select an execution to view details</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ExecutionMonitor;