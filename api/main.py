from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.routers import auth, scraper, scratchpad, jobs
from api.dependencies import get_current_user

app = FastAPI(
    title="Universal Agentic Web Scraper API",
    description="API for intelligent web scraping with Claude 3.7 and Firecrawl",
    version="1.0.0",
    root_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include router modules
app.include_router(auth.router, tags=["Authentication"])
app.include_router(scraper.router, tags=["Web Scraping"], dependencies=[Depends(get_current_user)])
app.include_router(scratchpad.router, tags=["Scratchpad"], dependencies=[Depends(get_current_user)])
app.include_router(jobs.router, tags=["Jobs"], dependencies=[Depends(get_current_user)])

@app.get("/")
async def root():
    return {"message": "Welcome to the Universal Agentic Web Scraper API"} 