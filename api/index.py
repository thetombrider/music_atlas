from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.main import app

# Export the app for Vercel
app = app
