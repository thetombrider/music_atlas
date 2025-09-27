# Multi-stage build per ottimizzare dimensioni
FROM node:18-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/
COPY api/ ./api/

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./static

# Expose port
EXPOSE $PORT

# Start command
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
