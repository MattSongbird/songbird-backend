import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your WS router
from app.api.ws_chat import router as ws_router

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Songbird API",
    description="LangGraph-powered AI backend for Songbird Strategies",
    version="1.1.0", # Updated version
)

# CORS setup for frontend
# IMPORTANT: Update allow_origins for production environments!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict this in production to specific frontend domains
    allow_credentials=True, # Allow credentials (cookies, authorization headers)
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# Mount WebSocket router
app.include_router(ws_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup complete.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown complete.")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    # Note: The uvicorn.run command in __main__ is for direct execution.
    # For production, use a command like: uvicorn backend.main:app --host 0.0.0.0 --port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
