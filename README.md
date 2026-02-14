# 🚀 Multi-Agent AI Workflow Builder

## Visual AI Workflow Platform powered by LangGraph & Ollama

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-19.0-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.110-green.svg)
![LangChain](https://img.shields.io/badge/langchain-latest-purple.svg)

</div>

## 🎯 Overview

A production-ready, open-source visual AI workflow platform that allows non-technical users to create, configure, and run multi-agent AI workflows using a drag-and-drop interface. Similar to n8n but specialized for LLM agents.

### ✨ Key Features

- **🎨 Visual Workflow Builder**: Drag-and-drop interface powered by React Flow
- **🤖 Multi-Agent Support**: Planner, Executor, and Reviewer agents
- **🔄 Multi-LLM Support**: Switch between Mistral, Llama3, and Qwen2 models
- **⚡ Real-time Execution**: Monitor workflow execution with live logs
- **💾 Persistent Storage**: MongoDB for workflow and execution history
- **🔧 Tool Integration**: Web search, file operations, API calls, calculations
- **🔀 Conditional Branching**: Build complex logic with decision nodes
- **🔁 Loop Support**: Retry mechanisms with LangGraph
- **🎯 No-Code Interface**: Natural language instructions for agents

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Workflow    │  │  Execution   │  │   React      │      │
│  │  Builder     │  │  Monitor     │  │   Flow       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Planner    │  │  Executor    │  │  Reviewer    │      │
│  │   Agent      │  │  Agent       │  │  Agent       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│              LangGraph Workflow Engine                       │
└─────────────────────────────────────────────────────────────┘
                ↓                              ↓
        ┌──────────────┐              ┌──────────────┐
        │   Ollama     │              │   MongoDB    │
        │  (Local LLM) │              │  (Database)  │
        └──────────────┘              └──────────────┘
```

### Technology Stack

**Frontend**
- React 19 + Vite
- React Flow (visual workflow canvas)
- Tailwind CSS + shadcn/ui
- Zustand (state management)
- Axios (API calls)

**Backend**
- Python 3.9+
- FastAPI
- LangChain & LangGraph
- Motor (async MongoDB driver)
- Ollama (local LLM runtime)

**Infrastructure**
- MongoDB (data persistence)
- Ollama (model runtime)
- Docker support (optional)

---

## 🚀 Quick Start

### Prerequisites

Before starting, ensure you have:

1. **Python 3.9+** installed
2. **Node.js 16+** and yarn installed
3. **MongoDB** running (locally or Atlas)
4. **Ollama** installed and running with models

### Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull mistral
ollama pull llama3
ollama pull qwen2

# Start Ollama server
ollama serve
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### Setup Instructions

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd agent-platform
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your settings

# Start backend server
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Start development server
yarn start
```

#### 4. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

---

## 📚 Usage Guide

### Creating a Workflow

1. **Navigate to Workflow Builder Tab**
2. **Add Nodes**:
   - Click "+ Planner Agent" to add a planning node
   - Click "+ Executor Agent" to add an execution node
   - Click "+ Reviewer Agent" to add a review node
3. **Connect Nodes**: Drag from one node's edge to another to create connections
4. **Configure Nodes**: Click on a node to:
   - Select agent type (Planner/Executor/Reviewer)
   - Choose LLM model (Mistral/Llama3/Qwen2)
   - Write natural language instructions
5. **Save Workflow**: Enter name and description, then click "Save Workflow"

### Executing a Workflow

1. **Navigate to Execution Monitor Tab**
2. **Select a Workflow** from the dropdown
3. **Enter Input**: Type your task or query in the input field
4. **Click "Run Workflow"**
5. **Monitor Execution**: Watch real-time progress in the execution history
6. **View Results**: Click on an execution to see detailed steps and output

### Example Workflows

#### Simple Research Workflow

```yaml
Workflow: Research Assistant
Nodes:
  1. Planner Agent (mistral)
     Instructions: "Break down the research topic into key questions"
  
  2. Executor Agent (llama3)
     Instructions: "Research each question and gather information"
  
  3. Reviewer Agent (qwen2)
     Instructions: "Review research quality and completeness"

Connections:
  Planner → Executor → Reviewer
```

#### Content Creation Workflow

```yaml
Workflow: Blog Writer
Nodes:
  1. Planner Agent
     Instructions: "Create outline with sections and key points"
  
  2. Executor Agent
     Instructions: "Write detailed content for each section"
  
  3. Reviewer Agent
     Instructions: "Check grammar, tone, and structure"
```

---

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL_PRIMARY=mistral
OLLAMA_MODEL_SECONDARY=llama3
OLLAMA_MODEL_TERTIARY=qwen2

# MongoDB Configuration
MONGO_URL=mongodb://localhost:27017
DB_NAME=workflow_engine

# API Security
API_SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000

# Application
DEBUG=false
LOG_LEVEL=INFO
```

### Frontend Environment Variables (.env)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

---

## 🎨 Agent Types

### Planner Agent

**Purpose**: Breaks down complex tasks into executable steps

**Capabilities**:
- Task decomposition
- Step-by-step planning
- Resource identification

**Example Instructions**:
```
Analyze the user's request and create a detailed execution plan.
Break it down into clear, actionable steps.
```

### Executor Agent

**Purpose**: Performs individual tasks and tool calls

**Capabilities**:
- Task execution
- Tool utilization
- Result generation

**Example Instructions**:
```
Execute the planned tasks using available tools.
Provide detailed results for each step.
```

### Reviewer Agent

**Purpose**: Evaluates quality and completeness

**Capabilities**:
- Quality assessment
- Completeness verification
- Approval/rejection decisions

**Example Instructions**:
```
Review the execution results. Verify completeness and accuracy.
Approve if satisfactory, otherwise suggest improvements.
```

---

## 🛠️ Adding New Agents

### Step 1: Create Agent Class

Create a new file in `backend/agents/`:

```python
# backend/agents/custom_agent.py
from typing import Dict, Any
from agents.base import BaseAgent

class CustomAgent(BaseAgent):
    """Your custom agent implementation"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Your agent logic here
        result = await self._process_task(input_data)
        return {
            "agent_id": self.agent_id,
            "type": "custom",
            "result": result,
            "status": "success"
        }
    
    async def _process_task(self, input_data: Dict[str, Any]) -> str:
        # Implement your custom logic
        return "Custom agent result"
```

### Step 2: Register in Backend

Add to `backend/server.py`:

```python
from agents.custom_agent import CustomAgent

# In execute_workflow endpoint
if agent_type == "custom":
    agents["custom"] = CustomAgent(
        agent_id=node["id"],
        agent_type="custom",
        model_name=model,
        instructions=instructions
    )
```

### Step 3: Add to Frontend

Update `frontend/src/components/WorkflowCanvas.js`:

```javascript
// Add to nodeColors
const nodeColors = {
  // ... existing colors
  custom: '#ff6b6b',
};

// Add button in Node Library
<Button onClick={() => addNode('custom')}>
  + Custom Agent
</Button>
```

---

## 🔌 Adding New Tools

### Step 1: Create Tool

Create a new file in `backend/tools/`:

```python
# backend/tools/my_tool.py
from langchain.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """
    Description of what your tool does.
    
    Args:
        input: Input parameter description
    
    Returns:
        Result description
    """
    # Your tool logic here
    result = process_input(input)
    return result
```

### Step 2: Register Tool

Update agent initialization to include your tool:

```python
from tools.my_tool import my_custom_tool

# When creating agents
tools = [my_custom_tool, web_search, calculator]
agent = ExecutorAgent(..., tools=tools)
```

---

## 🐳 Docker Deployment

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - OLLAMA_HOST=http://host.docker.internal:11434
    depends_on:
      - mongodb

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend

volumes:
  mongo_data:
```

### Run with Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 📊 API Reference

### Workflows

**Create Workflow**
```http
POST /api/workflows
Content-Type: application/json

{
  "name": "My Workflow",
  "description": "Description",
  "nodes": [...],
  "edges": [...]
}
```

**List Workflows**
```http
GET /api/workflows
```

**Get Workflow**
```http
GET /api/workflows/{workflow_id}
```

**Delete Workflow**
```http
DELETE /api/workflows/{workflow_id}
```

### Executions

**Execute Workflow**
```http
POST /api/workflows/execute
Content-Type: application/json

{
  "workflow_id": "uuid",
  "input": "Your task description",
  "context": {}
}
```

**Get Execution**
```http
GET /api/executions/{execution_id}
```

**List Workflow Executions**
```http
GET /api/executions/workflow/{workflow_id}
```

### Models

**List Available Models**
```http
GET /api/models
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
yarn test
```

### Integration Tests

```bash
# Test complete workflow
curl -X POST http://localhost:8001/api/workflows/execute \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_id": "your-workflow-id",
    "input": "Analyze this data"
  }'
```

---

## 🔍 Troubleshooting

### Ollama Connection Issues

**Problem**: Backend cannot connect to Ollama

**Solutions**:
1. Verify Ollama is running: `ollama serve`
2. Check correct port in `.env`: `OLLAMA_HOST=http://localhost:11434`
3. Test connectivity: `curl http://localhost:11434/api/tags`
4. On Docker: use `http://host.docker.internal:11434`

### MongoDB Connection Issues

**Problem**: Cannot connect to MongoDB

**Solutions**:
1. Start MongoDB: `mongod`
2. Check connection string in `.env`
3. Verify MongoDB is accessible: `mongosh`

### Frontend Not Loading

**Problem**: Blank page or errors

**Solutions**:
1. Check backend URL in frontend `.env`
2. Verify CORS settings in backend
3. Check browser console for errors
4. Clear browser cache and restart

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) - Framework for LLM applications
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Multi-agent orchestration
- [Ollama](https://ollama.com) - Local LLM runtime
- [React Flow](https://reactflow.dev) - Visual workflow builder
- [shadcn/ui](https://ui.shadcn.com) - UI components

---

## 📧 Support

For questions and support:
- Open an issue on GitHub
- Join our community discussions
- Check the documentation

---

**Built with ❤️ for the AI community**