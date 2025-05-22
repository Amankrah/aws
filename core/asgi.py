import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django ASGI application
django_app = get_asgi_application()

# Import FastAPI application
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.main import app as fastapi_app

# Create a combined application
app = FastAPI()

# Mount Django app for admin and web portal
app.mount("/django", WSGIMiddleware(django_app), name="django")

# Mount FastAPI app for API endpoints
app.mount("/api", fastapi_app, name="api")

# Root path redirects to API docs
@app.get("/")
async def root():
    return {"message": "Welcome to the Universal Agentic Web Scraper", "docs": "/api/docs"} 