import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import Base, engine
import app.models  # noqa: F401  (registers all models with Base.metadata)
from app.routes import (
    auth,
    farms,
    fields,
    crops,
    irrigation,
    treatments,
    health,
    harvest,
    sales,
    dashboard,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all tables on startup (fine for SQLite / simple Postgres setups;
# swap for Alembic migrations in a production deployment).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="A REST API for managing farms, fields, crops, irrigation, treatments, "
    "crop health, harvests and produce sales.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handling (Level 11)
# ---------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail, "data": None},
    )


def _serialize_validation_errors(errors):
    """Pydantic v2 error dicts can carry a raw Exception instance inside 'ctx'
    (e.g. from a failed @model_validator). Stringify anything non-JSON-safe
    before it reaches JSONResponse.
    """
    serializable = []
    for err in errors:
        err = dict(err)
        ctx = err.get("ctx")
        if isinstance(ctx, dict):
            err["ctx"] = {k: (str(v) if isinstance(v, BaseException) else v) for k, v in ctx.items()}
        serializable.append(err)
    return serializable


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation error",
            "errors": _serialize_validation_errors(exc.errors()),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing request")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "An unexpected error occurred", "data": None},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(farms.router)
app.include_router(fields.router)
app.include_router(crops.router)
app.include_router(irrigation.router)
app.include_router(treatments.router)
app.include_router(health.router)
app.include_router(harvest.router)
app.include_router(sales.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health Check"])
def root():
    return {"message": f"{settings.APP_NAME} is running", "docs": "/docs"}
