#!/bin/bash

# Build script per deployment unificato
echo "🏗️  Building Music Atlas..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf static/
rm -rf frontend/dist/

# Build frontend
echo "⚛️  Building React frontend..."
cd frontend || { echo "❌ Frontend directory not found"; exit 1; }
npm install || { echo "❌ Frontend npm install failed"; exit 1; }
npm run build || { echo "❌ Frontend build failed"; exit 1; }
cd ..

# Copy frontend build to static directory
echo "📁 Copying frontend build..."
cp -r frontend/dist/ static/ || { echo "❌ Failed to copy frontend build"; exit 1; }

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt || { echo "❌ Python dependencies install failed"; exit 1; }

echo "✅ Build completed successfully!"
echo "🚀 Ready for deployment!"
echo ""
echo "📋 Build summary:"
echo "   - Frontend built: frontend/dist/ → static/"
echo "   - Python deps installed"
echo "   - Ready for Railway deployment"
echo ""

# Test locally (optional)
read -p "Test locally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Starting local server..."
    echo "🌐 Visit: http://localhost:8000"
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
fi
