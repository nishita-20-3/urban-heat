from app.routers.health import router as health_router
from app.routers.cities import router as cities_router
from app.routers.grid import router as grid_router
from app.routers.predictions import router as predictions_router
from app.routers.recommendations import router as recommendations_router
from app.routers.interventions import router as interventions_router
from app.routers.zones import router as zones_router
from app.routers.areas import router as areas_router

__all__ = [
    "health_router",
    "cities_router",
    "grid_router",
    "predictions_router",
    "recommendations_router",
    "interventions_router",
    "zones_router",
    "areas_router",
]
