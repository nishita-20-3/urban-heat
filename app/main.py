from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.routers import (
    health_router,
    cities_router,
    grid_router,
    predictions_router,
    recommendations_router,
    interventions_router,
    zones_router,
    areas_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    yield
    # Shutdown actions


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for Land Surface Temperature (LST) predictions, SHAP attribution, municipal zones, and cooling recommendations.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with clean JSON error messages.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


# Register all API routers
app.include_router(health_router)
app.include_router(cities_router)
app.include_router(zones_router)
app.include_router(areas_router)
app.include_router(grid_router)
app.include_router(predictions_router)
app.include_router(recommendations_router)
app.include_router(interventions_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Urban Heat Decision-Support API",
        "docs": "/docs",
        "health": "/health",
    }
