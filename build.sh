#!/bin/bash

# Build script per deployment unificato
echo "🏗️  Building Music Atlas..."

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf static/
rm -rf frontend/dist/

# Build frontend
echo "⚛️  Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Copy frontend build to static directory
echo "📁 Copying frontend build..."
cp -r frontend/dist/ static/

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Build completed!"
echo "🚀 Ready for deployment!"

# Test locally (optional)
read -p "Test locally? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Starting local server..."
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
fi
