import sys
import os

# Ensure parent directory is in Python path for Vercel Serverless Function
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Export app instance for Vercel Serverless Function execution
app = app
