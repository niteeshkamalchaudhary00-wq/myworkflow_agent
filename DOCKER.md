# Docker Setup Guide

## Quick Start with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Ollama running on host machine

### Directory Structure

```
agent-platform/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── ...
└── README.md
```

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Run application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build application
RUN yarn build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: workflow-mongodb
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_DATABASE=workflow_engine
    networks:
      - workflow-network
    healthcheck:
      test: echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: workflow-backend
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=workflow_engine
      - OLLAMA_HOST=http://host.docker.internal:11434
      - CORS_ORIGINS=http://localhost:3000,http://localhost:80
      - API_SECRET_KEY=change-me-in-production
      - DEBUG=false
    depends_on:
      mongodb:
        condition: service_healthy
    networks:
      - workflow-network
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: workflow-frontend
    ports:
      - "3000:80"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend
    networks:
      - workflow-network
    restart: unless-stopped

volumes:
  mongo_data:
    driver: local

networks:
  workflow-network:
    driver: bridge
```

### Usage

#### Start All Services

```bash
# Build and start in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
```

#### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

#### Rebuild Services

```bash
# Rebuild specific service
docker-compose up -d --build backend

# Rebuild all services
docker-compose up -d --build
```

### Environment Configuration

Create `.env` file in project root:

```env
# Backend
MONGO_URL=mongodb://mongodb:27017
DB_NAME=workflow_engine
OLLAMA_HOST=http://host.docker.internal:11434
CORS_ORIGINS=http://localhost:3000

# Frontend
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Accessing Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **MongoDB**: localhost:27017

### Production Deployment

#### Using Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml workflow

# View services
docker service ls

# Scale services
docker service scale workflow_backend=3
```

#### Using Kubernetes

Create deployment files:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: workflow-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: workflow-backend
  template:
    metadata:
      labels:
        app: workflow-backend
    spec:
      containers:
      - name: backend
        image: your-registry/workflow-backend:latest
        ports:
        - containerPort: 8001
        env:
        - name: MONGO_URL
          value: "mongodb://mongodb-service:27017"
```

Apply:
```bash
kubectl apply -f k8s/
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8001/health

# Check MongoDB connection
docker exec -it workflow-mongodb mongosh --eval "db.adminCommand('ping')"

# Check Ollama connectivity from backend
docker exec -it workflow-backend curl http://host.docker.internal:11434/api/tags
```

### Troubleshooting

#### Backend Cannot Connect to Ollama

**Solution**: Ollama must run on host machine (not in container)

```bash
# On host machine
ollama serve

# Verify from container
docker exec -it workflow-backend curl http://host.docker.internal:11434/api/tags
```

#### MongoDB Connection Refused

**Solution**: Wait for MongoDB to be ready

```bash
# Check MongoDB status
docker-compose ps

# View MongoDB logs
docker-compose logs mongodb

# Restart services
docker-compose restart backend
```

#### Port Already in Use

**Solution**: Change port mappings

```yaml
# docker-compose.yml
services:
  frontend:
    ports:
      - "8080:80"  # Changed from 3000
```

### Maintenance

#### Backup MongoDB Data

```bash
# Create backup
docker exec workflow-mongodb mongodump --out /backup

# Copy to host
docker cp workflow-mongodb:/backup ./mongodb-backup
```

#### Restore MongoDB Data

```bash
# Copy backup to container
docker cp ./mongodb-backup workflow-mongodb:/backup

# Restore
docker exec workflow-mongodb mongorestore /backup
```

#### View Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```