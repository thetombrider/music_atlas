from fastapi import FastAPI
from mangum import Mangum
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from backend.main import app
except ImportError:
    # Fallback for Vercel deployment
    from main import app

# Wrap FastAPI app with Mangum for serverless
handler = Mangum(app)
