#!/bin/bash

cd /home/runner/workspace/backend && python server.py &
BACKEND_PID=$!

cd /home/runner/workspace/frontend
PORT=5000 HOST=0.0.0.0 BROWSER=none npx craco start &
FRONTEND_PID=$!

wait $FRONTEND_PID $BACKEND_PID
