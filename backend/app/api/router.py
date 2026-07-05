from fastapi import APIRouter

from app.api.products import router as products_router
from app.api.stores import router as stores_router
from app.api.history import router as history_router
from app.api.stats import router as stats_router
from app.api.alerts import router as alerts_router
from app.auth.router import router as auth_router

router = APIRouter(prefix="/api/v1")

router.include_router(products_router)
router.include_router(stores_router)
router.include_router(history_router)
router.include_router(stats_router)
router.include_router(alerts_router)
router.include_router(auth_router)
