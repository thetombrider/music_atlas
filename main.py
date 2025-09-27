import sys
import os

# Add backend to path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the complete FastAPI app from backend
from backend.main import app

# The app is already configured with all routes, CORS, etc.
# Vercel will serve this as the API
