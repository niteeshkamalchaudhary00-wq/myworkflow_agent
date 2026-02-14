import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Toaster } from '@/components/ui/sonner';
import WorkflowCanvas from './components/WorkflowCanvas';
import ExecutionMonitor from './components/ExecutionMonitor';
import { Network, Play } from 'lucide-react';
import '@/App.css';

const MainApp = () => {
  const [activeTab, setActiveTab] = useState('builder');

  return (
    <div className="min-h-screen bg-zinc-950" style={{ fontFamily: 'Inter, sans-serif' }}>
      {/* Header */}
      <header className="bg-zinc-900/50 backdrop-blur-md border-b border-zinc-800 sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-violet-600 to-blue-600 rounded-lg flex items-center justify-center">
                <Network className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1
                  data-testid="app-title"
                  className="text-2xl font-bold text-white"
                  style={{ fontFamily: 'Manrope, sans-serif', letterSpacing: '-0.02em' }}
                >
                  Multi-Agent Workflow Builder
                </h1>
                <p className="text-sm text-zinc-400">Visual AI workflow platform powered by LangGraph</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-xs text-zinc-500">Ollama Connected</span>
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 bg-zinc-900/50 border border-zinc-800 p-1">
            <TabsTrigger
              data-testid="builder-tab"
              value="builder"
              className="data-[state=active]:bg-violet-600 data-[state=active]:text-white text-zinc-400 transition-all"
            >
              <Network className="w-4 h-4 mr-2" />
              Workflow Builder
            </TabsTrigger>
            <TabsTrigger
              data-testid="monitor-tab"
              value="monitor"
              className="data-[state=active]:bg-violet-600 data-[state=active]:text-white text-zinc-400 transition-all"
            >
              <Play className="w-4 h-4 mr-2" />
              Execution Monitor
            </TabsTrigger>
          </TabsList>

          <TabsContent value="builder" className="mt-6">
            <WorkflowCanvas />
          </TabsContent>

          <TabsContent value="monitor" className="mt-6">
            <ExecutionMonitor />
          </TabsContent>
        </Tabs>
      </main>

      <Toaster position="top-right" />
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainApp />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;