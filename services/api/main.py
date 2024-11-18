from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY
from .config import settings
from .endpoints import health, agent, environment, agi
from .dependencies import register_dependencies 
import logging

# Initialize FastAPI application
app = FastAPI(
    title="vAIn API",
    description="Backend API for the vAIn Project, enabling modular communication with AGI components.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Set in config.py
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("vAIn")

# Register Dependencies
register_dependencies(app)

# API Routers
api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
api_router.include_router(environment.router, prefix="/environment", tags=["Environment"])
app.include_router(api_router)
app.include_router(agi.router)

# Custom Error Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error. Please contact support."},
    )

# Application Startup Event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting vAIn API...")
    # Any startup tasks like initializing DB connections, loading models, etc.

# Application Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down vAIn API...")
    # Cleanup tasks like closing DB connections, clearing caches, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "services.api.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
        reload=True,  # For development; remove in production
    )
