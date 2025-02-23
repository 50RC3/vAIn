from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY
from .config import settings
from .endpoints import health, agent, environment, agi
from .dependencies import register_dependencies
import logging
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from uuid import uuid4
import time

# Define logger
logger = logging.getLogger("vAIn")

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="services/api/static"), name="static")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests and their response status."""
    logger.info(f"Request: {request.method} {request.url}")
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} - Time taken: {process_time:.4f}s")
    
    return response

@app.get("/")
async def get_ui():
    return FileResponse("services/api/static/index.html")

# Include the endpoints
app.include_router(health.router)
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
    error_id = generate_error_id()
    logger.exception(f"Error ID {error_id}: Unexpected error occurred")
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error_id": error_id,
            "detail": "Internal Server Error. Please contact support with this error ID."
        },
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

def generate_error_id():
    return f"{int(time.time())}-{str(uuid4())[:8]}"

# Add rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.on_event("startup")
async def startup_event():
    logger.info("Starting vAIn API...")
    # Any startup tasks like initializing DB connections, loading models, etc.

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down vAIn API...")
    # Cleanup tasks like closing DB connections, clearing caches, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
