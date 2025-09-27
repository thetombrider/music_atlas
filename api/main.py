import sys
import os
from mangum import Mangum

# Add backend to path  
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the complete FastAPI app from backend
from backend.main import app

# Wrap with Mangum for Vercel serverless
handler = Mangum(app)
