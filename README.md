# Universal Agentic Web Scraper

A powerful web scraping platform that combines Claude 3.7's intelligence with Firecrawl's web extraction capabilities, built with Django and FastAPI.

## System Architecture

This backend architecture combines Django's robust admin and ORM capabilities with FastAPI's high-performance async processing, creating an ideal system for the Universal Agentic Web Scraper.

```
┌──────────────────────────────────────────────────────────┐
│                      Client Applications                  │
└───────────────────────────────┬──────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────┐
│                        API Gateway                        │
└───────┬─────────────────────────────────────────┬────────┘
        │                                         │
┌───────▼────────┐                       ┌────────▼───────┐
│  Django Admin  │                       │  FastAPI API   │
│  & Web Portal  │                       │    Services    │
└───────┬────────┘                       └────────┬───────┘
        │                                         │
┌───────▼─────────────────────────────────▼───────┐
│                Shared Database Layer             │
└───────┬─────────────────────────────────┬───────┘
        │                                 │
┌───────▼───────┐               ┌────────▼────────┐
│  External API │               │   Task Queue    │
│  Integrations │               │   (Celery/RQ)   │
└───────────────┘               └─────────────────┘
```

## Agent Memory Architecture

The system uses a memory-augmented approach with a central scratchpad that coordinates between different information sources:

```
┌─────────────────────────┐
│                         │
│        Scratchpad       │
│    (Memory & Planning)  │
│                         │
└───────┬─────┬───────────┘
        │     │
        │     │
┌───────▼─────▼───────────┐
│                         │
│   Claude 3.7 (Agent)    │
│  w/ Extended Thinking   │
│                         │
└───────┬─────┬───────────┘
        │     │
        │     │
┌───────▼─────┴───────────┐
│                         │
│  Company    Internet    │
│  Domain     Search      │
│                         │
└─────────────────────────┘
```

## Features

- **Intelligent Web Scraping**: Leverage Claude 3.7's intelligence to plan and execute web scraping tasks
- **Powerful Extraction**: Use Firecrawl for robust web extraction, handling JavaScript, anti-bot measures, and more
- **Advanced Memory System**: Enhanced scratchpad with vector storage for semantic search and session management
- **Source-Aware Storage**: Metadata tagging to track information origins (company domain vs internet search)
- **Extended Thinking**: Claude 3.7's enhanced reasoning with transparent thought processes
- **Asynchronous Jobs**: Long-running jobs are processed in the background using Celery
- **RESTful API**: Access all functionality through a well-documented FastAPI interface
- **Admin Interface**: Manage users, jobs, and system settings through the Django admin portal
- **Modern Frontend**: Sleek React/Next.js frontend for intuitive user interaction

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- Redis (for Celery)
- API keys for Firecrawl and Anthropic

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Amankrah/aws.git
cd aws
```

2. Create a virtual environment:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate
```

3. Install backend dependencies:

```bash
pip install -r requirements.txt
```

4. Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

5. Create a `.env` file in the project root:

```
FIRECRAWL_API_KEY=your_firecrawl_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///db.sqlite3
```

6. Run migrations:

```bash
python manage.py migrate
```

7. Create a superuser:

```bash
python manage.py createsuperuser
```

## Development

### Starting the backend

1. Start the Redis server (required for Celery):

```bash
# Windows (using WSL or Docker)
docker run -p 6379:6379 redis

# Unix/MacOS
redis-server
```

2. Start the Celery worker:

```bash
celery -A core worker --loglevel=info
```

3. Start the Django/FastAPI server:

```bash
uvicorn core.asgi:app --reload
```

### Starting the frontend

```bash
cd frontend
npm run dev
```

### Accessing the application

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/api/docs
- **Admin Interface**: http://localhost:8000/django/admin/

## API Endpoints

The API provides the following main endpoints:

- **Authentication**: `/api/auth/`
  - Register, get current user, refresh API keys

- **Web Scraping**: `/api/scraper/`
  - Start scraping jobs, get job status and results

- **Scratchpad**: `/api/scratchpad/`
  - Store and retrieve temporary data
  - Perform semantic searches
  - Filter by source or session
  - Track operation history

- **Jobs**: `/api/jobs/`
  - List and manage scraping jobs

## Agent-Scratchpad Coordination

The system coordinates between Claude and the Scratchpad in multiple phases:

1. **Planning Phase**: Claude generates scraping plans that are stored in the scratchpad
2. **Execution Phase**: Scraping results are saved to the scratchpad with source metadata
3. **Analysis Phase**: Claude retrieves relevant information from the scratchpad using semantic search
4. **Synthesis Phase**: Claude generates final answers based on all collected information

This coordination allows the agent to effectively utilize both company-specific information and general internet search results.

## Project Structure

```
scraper_project/
├── core/                      # Shared core functionality
├── apps/                      # Django applications
│   ├── users/                 # User management
│   ├── scratchpad/            # Enhanced scratchpad with vector storage
│   ├── crawl_jobs/            # Crawl job management
│   └── admin_portal/          # Admin interface
├── api/                       # FastAPI application
├── services/                  # Business logic services
│   ├── claude_service.py      # Claude 3.7 service with extended thinking
│   ├── scratchpad_service.py  # Memory management with semantic search
│   ├── firecrawl_service.py   # Web extraction capabilities
│   └── extraction_service.py  # Structured data extraction
├── tasks/                     # Async task definitions
│   ├── crawl_tasks.py         # Web crawling tasks
│   ├── agent_tasks.py         # Agent reasoning tasks
│   └── extraction_tasks.py    # Data extraction tasks
└── utils/                     # Utility functions
```

## Key Technologies

- **Django**: Core application framework and ORM
- **FastAPI**: High-performance API endpoints
- **Next.js**: React framework for the frontend
- **Celery**: Asynchronous task processing
- **Claude 3.7**: Advanced AI reasoning with extended thinking
- **Firecrawl**: Powerful web extraction
- **Chroma/HuggingFace**: Vector storage for semantic search
- **PostgreSQL**: Primary database (optional)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Anthropic](https://www.anthropic.com/) for Claude 3.7
- [Firecrawl](https://firecrawl.dev/) for web extraction capabilities
- [Langchain](https://langchain.com/) for vector store integration 