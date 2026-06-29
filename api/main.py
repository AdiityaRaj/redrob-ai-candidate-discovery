import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import pipeline
from src.utils.logger import logger

def create_app() -> FastAPI:
    """Configures and assembles the enterprise FastAPI application shell."""
    app = FastAPI(
        title="Redrob AI Ranker API Services",
        description="CPU-Optimized Network-Free Candidate Match and Discovery Routing Engine Node",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Allow loose flexible local evaluation interaction hooks
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Injecting the pipeline routes under the specific v1 version endpoints boundary
    app.include_router(pipeline.router, prefix="/api/v1", tags=["Ranking Pipeline"])

    @app.get("/health", tags=["Infrastructure Monitoring"])
    def health_check():
        """Fast endpoint to confirm sandbox readiness status."""
        return {"status": "healthy", "sandbox_network": "OFFLINE_COMPLIANT"}

    return app

app = create_app()

if __name__ == "__main__":
    logger.info("Starting local production Uvicorn web gateway instance...")
    # Bound locally to loop interface for strict isolated validation execution
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
