#!/bin/bash
# Metis - Local Environment Startup Script

echo "========================================================"
echo "          🚀 Starting Metis Local Environment 🚀          "
echo "========================================================"

# Check for Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment 'venv' not found."
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 1. Start Redis (Requirement for Celery)
if ! docker ps | grep -q "6379"; then
    echo "📦 Starting local Redis broker (Docker)..."
    docker run -d -p 6379:6379 --name metis_redis_local redis:7-alpine > /dev/null 2>&1
else
    echo "✅ Redis is already running on port 6379."
fi

# Set common environment variables
export SQLITE_FALLBACK=1
export PYTHONPATH=$(pwd)
source venv/bin/activate

# 2. Start Celery Worker
echo "⚙️ Starting Celery Worker..."
celery -A microservices.tasks.celery_app worker --loglevel=info > celery_worker.log 2>&1 &
CELERY_PID=$!

# 3. Start FastAPI Backend
echo "🌐 Starting FastAPI Backend on port 8001..."
uvicorn server.app:app --reload --port 8001 > backend.log 2>&1 &
BACKEND_PID=$!

# 4. Start React Frontend
echo "💻 Starting React Frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "========================================================"
echo "✨ Metis is now running natively! ✨"
echo ""
echo "📱 Frontend:    http://localhost:8080"
echo "🔌 Backend API: http://localhost:8001"
echo "📜 Logs are being written to: celery_worker.log, backend.log, frontend.log"
echo ""
echo "⚠️ Press [CTRL+C] to gracefully stop all services."
echo "========================================================"

# Trap Ctrl+C and kill child processes
trap "echo -e '\n🛑 Stopping all Metis services...'; kill $BACKEND_PID $CELERY_PID $FRONTEND_PID 2>/dev/null; echo '✅ Services stopped.'; exit 0" INT TERM

# Wait indefinitely until interrupted
wait
