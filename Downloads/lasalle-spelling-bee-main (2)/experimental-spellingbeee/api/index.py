# Vercel serverless function entry point
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app
from app import app

# Vercel serverless handler
def handler(request):
    return app(request.environ, lambda status, headers: None)
