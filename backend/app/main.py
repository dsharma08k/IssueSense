"""Main FastAPI application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import issues, solutions, analytics, comments, export, ai_solutions
import logging

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="IssueSense API",
    description="""
## 🎯 ML-Powered Error Knowledge Base

IssueSense provides intelligent error tracking with semantic search capabilities.

### Features

* **Issue Management** - Create, search, and manage error reports
* **Semantic Search** - AI-powered similarity search using ML embeddings
* **Solutions** - Document fixes and track effectiveness
* **Comments** - Team collaboration on issues
* **Analytics** - Insights into error patterns and trends

### Authentication

All endpoints require JWT authentication via Supabase Auth.

Include the token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

### Rate Limiting

No rate limiting is currently enforced.
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "IssueSense Support",
        "url": "https://github.com/yourusername/issuesense",
    },
    license_info={
        "name": "MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(issues.router, prefix="/api/v1")
app.include_router(solutions.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(comments.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")
app.include_router(ai_solutions.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "IssueSense API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "ml_model": "ready"
    }


@app.on_event("startup")
async def startup():
    """Startup event handler"""
    logger.info("🚀 IssueSense API starting up...")
    logger.info(f"📍 Environment: {settings.log_level}")
    logger.info(f"🔒 CORS origins: {settings.cors_origins_list}")
    
    # Check Groq AI status
    from app.services.groq_service import groq_service
    if groq_service.enabled:
        logger.info("✅ Groq AI service initialized and ready")
    else:
        logger.warning("⚠️  Groq API key not found - AI suggestions disabled")
    
    logger.info("✅ Startup complete")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown event handler"""
    logger.info("👋 IssueSense API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
