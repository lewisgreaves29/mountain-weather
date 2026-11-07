import asyncio
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.router import api_router
from backend.app.config import get_settings
from backend.app.services.collector import collector
from backend.app.services.secrets import validate_secrets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mountain_weather")

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Validate secrets injected from 1Password Connect
    settings = validate_secrets()
    logger.info("Initializing UK Mountain Weather Dashboard (Env: %s)", settings.app_env)

    # 2. Configure and start background scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        collector.collect_all,
        "interval",
        minutes=settings.poll_interval_minutes,
        id="weather_poll_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Started background weather ingestor (Interval: %d min)", settings.poll_interval_minutes)

    # 3. Trigger initial asynchronous cache warm-up
    async def warm_up():
        try:
            logger.info("Priming weather cache from UK Met Office Open-Meteo model...")
            await collector.collect_all()
            logger.info("Initial weather cache warm-up complete.")
        except Exception as exc:
            logger.error("Initial weather warm-up encountered an error: %s", exc)

    warmup_task = asyncio.create_task(warm_up())

    yield

    # Clean shutdown
    warmup_task.cancel()
    scheduler.shutdown(wait=False)
    logger.info("Scheduler shutdown successfully.")


app = FastAPI(
    title="UK Mountain Weather Service",
    description="Deterministic Met Office weather ingestor and summit ridge hazard engine for K3s.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(api_router)


@app.get("/healthz")
async def health_check():
    """Liveness probe: returns 200 ok."""
    return {"status": "ok"}


@app.get("/readyz")
async def readiness_check():
    """Readiness probe: returns 503 until initial cache warm-up completes, then 200."""
    if not collector.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Initial weather cache warm-up in progress",
        )
    return {"status": "ready"}


# Mount static assets if compiled Vue 3 bundle exists
if (STATIC_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the single-page Vue 3 application."""
    if STATIC_DIR.exists():
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            # If requesting a specific file in static root (e.g. favicon.svg)
            requested_file = STATIC_DIR / full_path
            if full_path and requested_file.is_file():
                return FileResponse(requested_file)
            return FileResponse(index_file)

    # Fallback response if frontend is not built yet
    return Response(
        content="<html><body><h2>UK Mountain Weather Dashboard</h2><p>Backend API active at <a href='/api/v1/weather'>/api/v1/weather</a>. Frontend bundle compiling...</p></body></html>",
        media_type="text/html",
    )


if __name__ == "__main__":
    import uvicorn
    app_settings = get_settings()
    uvicorn.run("backend.app.main:app", host=app_settings.host, port=app_settings.port, reload=True)
