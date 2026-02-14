import { create } from 'zustand';

const useWorkflowStore = create((set, get) => ({
  workflows: [],
  selectedWorkflow: null,
  executions: [],
  
  addWorkflow: (workflow) => set((state) => ({
    workflows: [...state.workflows, workflow]
  })),
  
  setSelectedWorkflow: (workflow) => set({ selectedWorkflow: workflow }),
  
  updateWorkflows: (workflows) => set({ workflows }),
  
  addExecution: (execution) => set((state) => ({
    executions: [...state.executions, execution]
  })),
  
  updateExecutions: (executions) => set({ executions }),
}));

export default useWorkflowStore;