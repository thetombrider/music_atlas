#!/bin/bash

# Start script per Railway deployment
echo "🚀 Starting Music Atlas on Railway..."

# Check and set PORT variable
if [ -z "$PORT" ]; then
    echo "⚠️  PORT not set, using default 8000"
    export PORT=8000
else
    echo "✅ PORT set to: $PORT"
fi

# Validate PORT is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "❌ PORT is not numeric: $PORT, falling back to 8000"
    export PORT=8000
fi

echo "🌐 Starting FastAPI server on 0.0.0.0:$PORT"
echo "📁 Static files served from: /app/static"
echo "🔧 Environment: ${ENVIRONMENT:-development}"

# Start uvicorn with validated port
exec uvicorn backend.main:app --host 0.0.0.0 --port $PORT
