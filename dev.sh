#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "==> 启动后端 (port 8000)"
.venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "==> 启动前端 (port 5173)"
cd frontend && npx vite --host &
FRONTEND_PID=$!
echo "后端 PID=$BACKEND_PID  前端 PID=$FRONTEND_PID"
echo "访问 http://localhost:5173/calc/kaifa"
wait
