from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

from core.config import settings
from db.database import init_db
from api.routers import incidents, auth, external


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="SAFE - Sistema de Alertas y Reportes Urbanos",
    description="API REST para reporte y análisis de incidentes urbanos con H3",
    version="1.0.0",
)
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429, content={"detail": "Rate limit exceeded", "status": "error"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


logger.add(
    "logs/app.log", rotation="10 MB", retention="7 days", level=settings.LOG_LEVEL
)


app.include_router(incidents.router)
app.include_router(auth.router)
app.include_router(external.router)


@app.on_event("startup")
def startup_event():
    logger.info("Starting SAFE API...")
    try:
        init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization skipped: {e}")


@app.get("/")
def root():
    return {
        "message": "SAFE API - Sistema de Alertas y Reportes Urbanos",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
